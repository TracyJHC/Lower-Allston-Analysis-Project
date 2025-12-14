#!/usr/bin/env python3
"""
Script to update building and voter coordinates from parcel geometry
for buildings that don't have geometry
"""

import psycopg
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

def update_building_coords_from_parcels():
    try:
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Checking parcels table...")
        cursor.execute("SELECT COUNT(*) FROM parcels WHERE geometry IS NOT NULL")
        parcels_with_geom = cursor.fetchone()[0]
        
        if parcels_with_geom == 0:
            print("❌ No parcels with geometry found. Please run load_parcels_geojson.py first.")
            conn.close()
            return False
        
        print(f"Found {parcels_with_geom:,} parcels with geometry")
        
        print("\n=== STEP 1: Check buildings that can use parcel coordinates ===\n")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT b.struct_id)
            FROM buildings b
            JOIN parcels p ON b.parcel_id = p.parcel_id
            WHERE b.geometry IS NULL
            AND p.geometry IS NOT NULL
        """)
        buildings_with_parcels = cursor.fetchone()[0]
        print(f"Buildings without geometry that have parcels with geometry: {buildings_with_parcels:,}")
        
        print("\n=== STEP 2: Update voter coordinates from parcel geometry ===\n")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT v.res_id)
            FROM voters v
            JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
            JOIN buildings b ON vbm.struct_id = b.struct_id
            JOIN parcels p ON b.parcel_id = p.parcel_id
            WHERE b.geometry IS NULL
            AND p.geometry IS NOT NULL
            AND (v.latitude IS NULL OR v.longitude IS NULL)
        """)
        voters_to_update = cursor.fetchone()[0]
        print(f"Voters mapped to buildings without geometry that can use parcel coordinates: {voters_to_update:,}")
        
        if voters_to_update > 0:
            print("Updating voter coordinates from parcel centroids...")
            cursor.execute("""
                UPDATE voters v
                SET 
                    latitude = ST_Y(ST_Centroid(p.geometry)),
                    longitude = ST_X(ST_Centroid(p.geometry))
                FROM voters_buildings_map vbm
                JOIN buildings b ON vbm.struct_id = b.struct_id
                JOIN parcels p ON b.parcel_id = p.parcel_id
                WHERE v.res_id = vbm.res_id
                AND b.geometry IS NULL
                AND p.geometry IS NOT NULL
                AND (v.latitude IS NULL OR v.longitude IS NULL)
            """)
            
            updated_voters = cursor.rowcount
            conn.commit()
            print(f"✅ Updated {updated_voters:,} voters with coordinates from parcels")
        else:
            print("No voters need updating")
        
        print("\n=== FINAL STATISTICS ===\n")
        
        cursor.execute("SELECT COUNT(*) FROM voters WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
        total_with_coords = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM voters")
        total_voters = cursor.fetchone()[0]
        
        print(f"Total voters with coordinates: {total_with_coords:,} ({total_with_coords/total_voters*100:.1f}%)")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM voters 
            WHERE is_elderly = true
            AND latitude IS NOT NULL 
            AND longitude IS NOT NULL
        """)
        elderly_with_coords = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM voters WHERE is_elderly = true")
        total_elderly = cursor.fetchone()[0]
        
        print(f"Elderly voters with coordinates: {elderly_with_coords:,} ({elderly_with_coords/total_elderly*100:.1f}%)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating coordinates: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = update_building_coords_from_parcels()
    sys.exit(0 if success else 1)

