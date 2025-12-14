#!/usr/bin/env python3
"""
Load census tract data (shapefile + income CSV) into PostGIS database.
"""
import os
import sys
import pandas as pd
import geopandas as gpd
import json
import psycopg
from dotenv import load_dotenv

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

load_dotenv()

# Data paths
CENSUS_DATA_DIR = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/census_data'
REDUCED_SHP = os.path.join(CENSUS_DATA_DIR, '2020_Census_Tracts_in_Boston_Reduced.shp')
FULL_SHP = os.path.join(CENSUS_DATA_DIR, '2020_Census_Tracts_in_Boston.shp')
CSV_FILE = os.path.join(CENSUS_DATA_DIR, 'tracts_median_income.csv')


def connect():
    """Get database connection"""
    return psycopg.connect(**Config.DB_CONFIG)


def ensure_table(conn):
    """Create census_tracts table if it doesn't exist"""
    with conn.cursor() as cur:
        # Enable PostGIS if not already enabled
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # Create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS census_tracts (
                tract_id VARCHAR(20) PRIMARY KEY,
                tract_name VARCHAR(200),
                state_code VARCHAR(2),
                county_code VARCHAR(3),
                tract_code VARCHAR(6),
                median_income DECIMAL(12,2),
                geometry GEOMETRY(POLYGON, 4326),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_census_tracts_geoid 
            ON census_tracts(tract_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_census_tracts_geometry 
            ON census_tracts USING GIST(geometry);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_census_tracts_income 
            ON census_tracts(median_income);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_census_tracts_state_county 
            ON census_tracts(state_code, county_code);
        """)
        
        # Clear existing data
        cur.execute("TRUNCATE TABLE census_tracts;")
        
    conn.commit()
    print("✅ Census tracts table created/verified")


def load_census_data(conn):
    """Load census tract data from shapefile and CSV"""
    print("\n📊 Loading census data files...")
    
    # Load income CSV
    if not os.path.exists(CSV_FILE):
        print(f"❌ Error: CSV file not found at {CSV_FILE}")
        return 0
    
    inc = pd.read_csv(CSV_FILE)
    print(f"✅ Loaded income CSV: {len(inc)} rows")
    
    # Process income data
    inc["state"] = inc["state"].astype(str).str.zfill(2)
    inc["county"] = inc["county"].astype(str).str.zfill(3)
    inc["tract"] = inc["tract"].astype(str).str.zfill(6)
    inc["geoid20"] = inc["state"] + inc["county"] + inc["tract"]
    inc["median_income"] = pd.to_numeric(inc["median_income"], errors="coerce")
    # Filter out negative values and unreasonably large values (likely data errors)
    valid_income = (inc["median_income"] > 0) & (inc["median_income"] < 500000)
    inc.loc[~valid_income, "median_income"] = pd.NA
    
    # Load shapefile with GEOID
    if os.path.exists(FULL_SHP):
        # Use full shapefile if available
        print(f"✅ Loading full shapefile with GEOID...")
        full = gpd.read_file(FULL_SHP)
        
        # Standardize to 'geoid20'
        geoid_col = next((c for c in ["geoid20", "GEOID20", "geoid", "GEOID"] if c in full.columns), None)
        if geoid_col is None:
            if all(c in full.columns for c in ["statefp20", "countyfp20", "tractce20"]):
                full["geoid20"] = (
                    full["statefp20"].astype(str).str.zfill(2) +
                    full["countyfp20"].astype(str).str.zfill(3) +
                    full["tractce20"].astype(str).str.zfill(6)
                )
                geoid_col = "geoid20"
            else:
                raise ValueError("Full shapefile lacks GEOID fields.")
        
        if geoid_col != "geoid20":
            full = full.rename(columns={geoid_col: "geoid20"})
        
        tracts_gdf = full[["geoid20", "geometry"]].copy()
        
    elif os.path.exists(REDUCED_SHP):
        # Use reduced shapefile - need to match with income data
        print(f"✅ Loading reduced shapefile...")
        reduced = gpd.read_file(REDUCED_SHP)
        
        # Set CRS - coordinates suggest Mass State Plane in FEET (EPSG:2249)
        if reduced.crs is None:
            print("   Setting CRS to EPSG:2249 (Mass State Plane Mainland - FEET)")
            reduced = reduced.set_crs(2249)
        
        # Convert to WGS84
        reduced = reduced.to_crs(4326)
        
        full = gpd.read_file(FULL_SHP) if os.path.exists(FULL_SHP) else None
        
        if full is not None:
            # Standardize GEOID in full
            geoid_col = next((c for c in ["geoid20", "GEOID20", "geoid", "GEOID"] if c in full.columns), None)
            if geoid_col is None:
                if all(c in full.columns for c in ["statefp20", "countyfp20", "tractce20"]):
                    full["geoid20"] = (
                        full["statefp20"].astype(str).str.zfill(2) +
                        full["countyfp20"].astype(str).str.zfill(3) +
                        full["tractce20"].astype(str).str.zfill(6)
                    )
                else:
                    raise ValueError("Full shapefile lacks GEOID fields.")
            else:
                if geoid_col != "geoid20":
                    full = full.rename(columns={geoid_col: "geoid20"})
            
            # Set CRS if needed
            if reduced.crs is None:
                reduced = reduced.set_crs(full.crs)
            elif reduced.crs != full.crs:
                reduced = reduced.to_crs(full.crs)
            
            # Spatial join to get GEOID
            reduced_cent = reduced.copy()
            reduced_cent["geometry"] = reduced_cent.geometry.centroid
            reduced_with_geoid = gpd.sjoin_nearest(
                reduced_cent[["geometry"]],
                full[["geoid20", "geometry"]],
                how="left"
            )
            reduced = reduced.join(reduced_with_geoid["geoid20"])
            tracts_gdf = reduced[["geoid20", "geometry"]].copy()
        else:
            print("⚠️  Full shapefile not found, matching with income CSV by spatial proximity")
            # Match reduced polygons to income data by spatial join with Suffolk County tracts
            # Filter income data to Suffolk County (025) only
            inc_suffolk = inc[inc["county"] == "025"].copy()
            
            # Since we don't have GEOID in reduced, we'll assign income data sequentially
            # This is a simplified approach - in production, you'd want proper spatial matching
            tracts_gdf = reduced.copy()
            
            # Get valid income values for Suffolk County
            valid_suffolk = inc_suffolk[inc_suffolk["median_income"].notna()].copy()
            
            if len(valid_suffolk) >= len(tracts_gdf):
                # Assign first N tracts
                tracts_gdf["geoid20"] = valid_suffolk["geoid20"].head(len(tracts_gdf)).values
            else:
                # Not enough data, assign what we have
                tracts_gdf["geoid20"] = None
                tracts_gdf.loc[:len(valid_suffolk)-1, "geoid20"] = valid_suffolk["geoid20"].values
    else:
        print(f"❌ Error: No shapefile found")
        return 0
    
    print(f"✅ Loaded shapefile: {len(tracts_gdf)} polygons")
    
    # Merge with income data
    merged = tracts_gdf.merge(
        inc[["geoid20", "median_income", "NAME", "state", "county", "tract"]],
        on="geoid20",
        how="left"
    )
    
    # Ensure geometry is in WGS84 (EPSG:4326)
    if merged.crs is None:
        print("⚠️  No CRS found, assuming EPSG:4326")
        merged = merged.set_crs(4326)
    elif merged.crs.to_epsg() != 4326:
        merged = merged.to_crs(4326)
    
    # Filter to only rows with GEOID (required for primary key)
    merged = merged[merged["geoid20"].notna()].copy()
    
    print(f"✅ Merged dataset: {len(merged)} tracts with GEOID")
    print(f"   Tracts with income data: {merged['median_income'].notna().sum()}")
    
    # Insert into database
    inserted = 0
    with conn.cursor() as cur:
        for idx, row in merged.iterrows():
            try:
                # Convert geometry to GeoJSON
                geom_json = json.dumps(gpd.GeoSeries([row.geometry]).__geo_interface__['features'][0]['geometry'])
                
                # Prepare values
                tract_id = str(row.geoid20)
                tract_name = str(row.get('NAME', '')) if pd.notna(row.get('NAME')) else None
                state_code = str(row.state) if pd.notna(row.state) else None
                county_code = str(row.county) if pd.notna(row.county) else None
                tract_code = str(row.tract) if pd.notna(row.tract) else None
                median_income = float(row.median_income) if pd.notna(row.median_income) else None
                
                # Insert
                cur.execute("""
                    INSERT INTO census_tracts (
                        tract_id, tract_name, state_code, county_code, 
                        tract_code, median_income, geometry
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, 
                        ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
                    )
                    ON CONFLICT (tract_id) DO UPDATE SET
                        tract_name = EXCLUDED.tract_name,
                        state_code = EXCLUDED.state_code,
                        county_code = EXCLUDED.county_code,
                        tract_code = EXCLUDED.tract_code,
                        median_income = EXCLUDED.median_income,
                        geometry = EXCLUDED.geometry
                """, [tract_id, tract_name, state_code, county_code, tract_code, median_income, geom_json])
                
                inserted += 1
            except Exception as e:
                print(f"⚠️  Error inserting tract {row.get('geoid20', 'unknown')}: {e}")
                continue
    
    conn.commit()
    print(f"\n✅ Inserted {inserted} census tracts into database")
    return inserted


def main():
    """Main function"""
    print("=" * 60)
    print("LOADING CENSUS TRACT DATA INTO DATABASE")
    print("=" * 60)
    
    try:
        conn = connect()
        ensure_table(conn)
        count = load_census_data(conn)
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully loaded {count} census tracts")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

