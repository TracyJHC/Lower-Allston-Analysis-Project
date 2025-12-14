#!/usr/bin/env python3
"""
Map precincts to census tracts using spatial joins.
This creates a relationship table linking precincts with census tracts.
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
PRECINCTS_GEOJSON = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/geospatial_data/allston_brighton_precincts.geojson'


def connect():
    """Get database connection"""
    return psycopg.connect(**Config.DB_CONFIG)


def ensure_table(conn):
    """Create precinct_census_tract_mapping table if it doesn't exist"""
    with conn.cursor() as cur:
        # Enable PostGIS if not already enabled
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # Create mapping table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS precinct_census_tract_mapping (
                mapping_id SERIAL PRIMARY KEY,
                ward_id INTEGER NOT NULL,
                precinct_id INTEGER NOT NULL,
                tract_id VARCHAR(20),
                overlap_percentage DECIMAL(5,2),
                overlap_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ward_id, precinct_id) REFERENCES precincts(ward_id, precinct_id),
                FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id),
                UNIQUE(ward_id, precinct_id, tract_id)
            );
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_precinct_tract_precinct 
            ON precinct_census_tract_mapping(ward_id, precinct_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_precinct_tract_tract 
            ON precinct_census_tract_mapping(tract_id);
        """)
        
        # Clear existing data
        cur.execute("TRUNCATE TABLE precinct_census_tract_mapping;")
        
    conn.commit()
    print("✅ Precinct-census tract mapping table created/verified")


def load_precincts_from_db(conn):
    """Load precincts from database"""
    query = """
        SELECT precinct_id, precinct_name, ward_id
        FROM precincts
        ORDER BY precinct_id
    """
    with conn.cursor() as cur:
        cur.execute(query)
        precincts = cur.fetchall()
    
    if not precincts:
        print("⚠️  No precincts found in database. Please load precincts first.")
        return None
    
    print(f"✅ Found {len(precincts)} precincts in database")
    return precincts


def get_precinct_geometry(conn, precinct_id):
    """Get precinct geometry from geo_precincts table"""
    query = """
        SELECT geom 
        FROM geo_precincts 
        WHERE precinct = %s OR precinct::text = %s
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(query, [str(precinct_id), str(precinct_id)])
        result = cur.fetchone()
        if result:
            return result[0]
    return None


def get_precinct_geometry_from_geojson(precinct_id):
    """Get precinct geometry from GeoJSON file"""
    if not os.path.exists(PRECINCTS_GEOJSON):
        return None
    
    try:
        gdf = gpd.read_file(PRECINCTS_GEOJSON)
        # Try to find precinct by ID or name
        if 'PRECINCT' in gdf.columns:
            precinct = gdf[gdf['PRECINCT'] == str(precinct_id)]
        elif 'precinct' in gdf.columns:
            precinct = gdf[gdf['precinct'] == str(precinct_id)]
        else:
            return None
        
        if len(precinct) > 0:
            return precinct.geometry.iloc[0]
    except Exception as e:
        print(f"⚠️  Error loading precinct from GeoJSON: {e}")
    
    return None


def map_precincts_to_tracts(conn):
    """Map precincts to census tracts using spatial joins"""
    print("\n🗺️  Mapping precincts to census tracts...")
    
    # Get all census tracts with geometry
    query = """
        SELECT tract_id, tract_name, geometry
        FROM census_tracts
        WHERE geometry IS NOT NULL
    """
    
    with conn.cursor() as cur:
        cur.execute(query)
        tracts = cur.fetchall()
    
    if not tracts:
        print("⚠️  No census tracts with geometry found. Please load census data first.")
        return 0
    
    print(f"✅ Found {len(tracts)} census tracts with geometry")
    
    # Get precincts from database
    precincts = load_precincts_from_db(conn)
    if not precincts:
        return 0
    
    # Load precincts GeoJSON for geometry
    if os.path.exists(PRECINCTS_GEOJSON):
        print(f"✅ Loading precinct geometries from GeoJSON...")
        precincts_gdf = gpd.read_file(PRECINCTS_GEOJSON)
        if precincts_gdf.crs != 'EPSG:4326':
            precincts_gdf = precincts_gdf.to_crs(4326)
        print(f"   Loaded {len(precincts_gdf)} precinct boundaries")
    else:
        print(f"⚠️  Precincts GeoJSON not found at {PRECINCTS_GEOJSON}")
        print("   Will try to use geometry from geo_precincts table")
        precincts_gdf = None
    
    # Create GeoDataFrame for census tracts using read_postgis
    # This properly handles PostGIS geometry conversion
    tracts_query = """
        SELECT tract_id, tract_name, geometry
        FROM census_tracts
        WHERE geometry IS NOT NULL
    """
    tracts_gdf = gpd.read_postgis(tracts_query, conn, geom_col='geometry', crs=4326)
    
    if tracts_gdf.empty:
        print("⚠️  No valid tract geometries found")
        return 0
    
    # Perform spatial joins
    mappings = []
    inserted = 0
    
    with conn.cursor() as cur:
        for precinct_id, precinct_name, ward_id in precincts:
            try:
                # Get precinct geometry
                if precincts_gdf is not None:
                    # Find precinct in GeoJSON
                    if 'PRECINCT' in precincts_gdf.columns:
                        precinct_geom = precincts_gdf[precincts_gdf['PRECINCT'] == str(precinct_id)]
                    elif 'precinct' in precincts_gdf.columns:
                        precinct_geom = precincts_gdf[precincts_gdf['precinct'] == str(precinct_id)]
                    else:
                        continue
                    
                    if len(precinct_geom) == 0:
                        continue
                    
                    precinct_geometry = precinct_geom.geometry.iloc[0]
                else:
                    # Try to get from database
                    precinct_geometry = get_precinct_geometry(conn, precinct_id)
                    if not precinct_geometry:
                        continue
                
                # Create temporary GeoDataFrame for this precinct
                precinct_gdf = gpd.GeoDataFrame(
                    [{'precinct_id': precinct_id, 'geometry': precinct_geometry}],
                    crs=4326
                )
                
                # Spatial join: find tracts that intersect with this precinct
                # First try direct intersection
                joined = gpd.sjoin(
                    precinct_gdf,
                    tracts_gdf,
                    how='left',
                    predicate='intersects'
                )
                
                used_buffer = False
                # If no intersections found, try within 500m (for geometry alignment issues)
                if len(joined) == 0 or joined['tract_id'].isna().all():
                    # Create a buffer of 500 meters using a projected CRS (UTM Zone 19N for Boston)
                    # Convert to UTM for accurate buffer calculation
                    precinct_gdf_projected = precinct_gdf.to_crs(32619)  # UTM Zone 19N
                    precinct_gdf_buffered = precinct_gdf_projected.copy()
                    precinct_gdf_buffered['geometry'] = precinct_gdf_buffered.geometry.buffer(500)  # 500 meters
                    precinct_gdf_buffered = precinct_gdf_buffered.to_crs(4326)  # Convert back to WGS84
                    
                    joined = gpd.sjoin(
                        precinct_gdf_buffered,
                        tracts_gdf,
                        how='left',
                        predicate='intersects'
                    )
                    
                    if len(joined) > 0 and not joined['tract_id'].isna().all():
                        used_buffer = True
                        print(f"   ⚠️  Precinct {precinct_id} (Ward {ward_id}) found using 500m buffer")
                
                # Calculate overlap percentage for each tract
                for idx, row in joined.iterrows():
                    if pd.isna(row['tract_id']):
                        continue
                    
                    tract_geom = tracts_gdf[tracts_gdf['tract_id'] == row['tract_id']].geometry.iloc[0]
                    precinct_geom = precinct_geometry
                    
                    # Calculate intersection area
                    intersection = precinct_geom.intersection(tract_geom)
                    
                    # If using buffer and no direct intersection, calculate distance-based overlap
                    if intersection.is_empty and used_buffer:
                        # Calculate distance and use a proximity-based overlap
                        # Convert to projected CRS for accurate distance calculation
                        precinct_proj = gpd.GeoDataFrame([{'geometry': precinct_geom}], crs=4326).to_crs(32619)
                        tract_proj = gpd.GeoDataFrame([{'geometry': tract_geom}], crs=4326).to_crs(32619)
                        distance_m = precinct_proj.geometry.distance(tract_proj.geometry).iloc[0]
                        
                        # For nearby tracts (within 500m), assign a small overlap percentage
                        # This indicates proximity rather than direct overlap
                        if distance_m <= 500:
                            overlap_pct = max(1.0, 100 - (distance_m / 5))  # Scale from 1-100% based on distance
                            overlap_type = 'proximity'
                        else:
                            continue  # Skip if too far
                    elif intersection.is_empty:
                        continue  # Skip if no intersection and not using buffer
                    else:
                        # Calculate overlap percentage (precinct area vs intersection)
                        # Use projected CRS for accurate area calculation
                        precinct_proj = gpd.GeoDataFrame([{'geometry': precinct_geom}], crs=4326).to_crs(32619)
                        intersection_proj = gpd.GeoDataFrame([{'geometry': intersection}], crs=4326).to_crs(32619)
                        precinct_area = precinct_proj.geometry.area.iloc[0]
                        intersection_area = intersection_proj.geometry.area.iloc[0]
                        overlap_pct = (intersection_area / precinct_area) * 100 if precinct_area > 0 else 0
                    
                    # Determine overlap type (if not already set as 'proximity')
                    if 'overlap_type' not in locals() or overlap_type != 'proximity':
                        if overlap_pct > 90:
                            overlap_type = 'majority'
                        elif overlap_pct > 50:
                            overlap_type = 'significant'
                        elif overlap_pct > 10:
                            overlap_type = 'partial'
                        else:
                            overlap_type = 'minor'
                    
                    # Insert mapping
                    cur.execute("""
                        INSERT INTO precinct_census_tract_mapping (
                            ward_id, precinct_id, tract_id, overlap_percentage, overlap_type
                        ) VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (ward_id, precinct_id, tract_id) DO UPDATE SET
                            overlap_percentage = EXCLUDED.overlap_percentage,
                            overlap_type = EXCLUDED.overlap_type
                    """, [ward_id, precinct_id, row['tract_id'], round(overlap_pct, 2), overlap_type])
                    
                    inserted += 1
                    
            except Exception as e:
                print(f"⚠️  Error mapping precinct {precinct_id}: {e}")
                continue
    
    conn.commit()
    print(f"\n✅ Created {inserted} precinct-to-tract mappings")
    return inserted


def main():
    """Main function"""
    print("=" * 70)
    print("MAPPING PRECINCTS TO CENSUS TRACTS")
    print("=" * 70)
    
    try:
        conn = connect()
        ensure_table(conn)
        count = map_precincts_to_tracts(conn)
        conn.close()
        
        print("\n" + "=" * 70)
        print(f"✅ Successfully created {count} mappings")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

