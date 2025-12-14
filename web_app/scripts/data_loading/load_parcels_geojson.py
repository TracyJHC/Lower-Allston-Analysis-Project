#!/usr/bin/env python3
"""
Script to load parcels GeoJSON into the database
"""

import psycopg
import json
import os
from dotenv import load_dotenv
import sys

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def ensure_parcels_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            parcel_id VARCHAR(50) PRIMARY KEY,
            prop_id VARCHAR(50),
            loc_id VARCHAR(50),
            site_address VARCHAR(200),
            addr_num INTEGER,
            full_street VARCHAR(100),
            location VARCHAR(100),
            city VARCHAR(50),
            zip_code VARCHAR(10),
            zoning VARCHAR(20),
            year_built INTEGER,
            building_area DECIMAL(10,2),
            lot_size DECIMAL(10,2),
            units INTEGER,
            residential_area DECIMAL(10,2),
            style VARCHAR(50),
            num_rooms DECIMAL(5,1),
            lot_units VARCHAR(10),
            stories_num INTEGER,
            stories VARCHAR(10),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            geometry GEOMETRY(MULTIPOLYGON, 4326),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_parcels_geometry 
        ON parcels USING GIST(geometry)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_parcels_coords 
        ON parcels (latitude, longitude)
    """)
    
    conn.commit()
    print("✅ Parcels table created/verified")

def load_parcels_geojson():
    geojson_path = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/geospatial_data/allston_brighton_parcels.geojson'
    
    if not os.path.exists(geojson_path):
        print(f"Error: GeoJSON file not found at {geojson_path}")
        return False
    
    try:
        print("Loading GeoJSON file...")
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
        
        features = geojson_data.get('features', [])
        print(f"Found {len(features)} parcel features")
        
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        
        ensure_parcels_table(conn)
        
        cursor = conn.cursor()
        
        print("Clearing existing parcels data...")
        cursor.execute("DELETE FROM parcels")
        conn.commit()
        
        print("Loading parcels into database...")
        inserted = 0
        skipped = 0
        
        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry')
            
            parcel_id = str(props.get('MAP_PAR_ID', ''))
            if not parcel_id or not geom:
                skipped += 1
                continue
            
            geom_json = json.dumps(geom)
            
            lat = None
            lon = None
            if geom and geom.get('type') == 'MultiPolygon':
                coords = geom.get('coordinates', [])
                if coords and len(coords) > 0 and len(coords[0]) > 0 and len(coords[0][0]) > 0:
                    first_point = coords[0][0][0]
                    lon, lat = first_point[0], first_point[1]
            
            try:
                cursor.execute("""
                    INSERT INTO parcels (
                        parcel_id, loc_id, geometry, latitude, longitude
                    ) VALUES (
                        %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326), %s, %s
                    )
                    ON CONFLICT (parcel_id) DO UPDATE
                    SET geometry = EXCLUDED.geometry,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                """, (
                    parcel_id,
                    props.get('LOC_ID'),
                    geom_json,
                    lat,
                    lon
                ))
                inserted += 1
                
                if inserted % 1000 == 0:
                    print(f"  Processed {inserted} parcels...")
                    
            except Exception as e:
                print(f"  Warning: Error inserting parcel {parcel_id}: {e}")
                skipped += 1
                continue
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM parcels")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parcels WHERE geometry IS NOT NULL")
        with_geom = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parcels WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        with_coords = cursor.fetchone()[0]
        
        print(f"\n✅ Successfully loaded {count} parcels")
        print(f"   - Parcels with geometry: {with_geom:,}")
        print(f"   - Parcels with coordinates: {with_coords:,}")
        print(f"   - Skipped: {skipped:,}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error loading parcels: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = load_parcels_geojson()
    sys.exit(0 if success else 1)

