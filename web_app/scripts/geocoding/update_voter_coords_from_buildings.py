#!/usr/bin/env python3
"""
Script to update voter coordinates from building geometry centroids
for voters who are mapped to buildings but don't have coordinates
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

def update_voter_coords_from_buildings():
    try:
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Finding voters mapped to buildings without coordinates...")
        cursor.execute("""
            SELECT COUNT(DISTINCT v.res_id)
            FROM voters v
            JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
            JOIN buildings b ON vbm.struct_id = b.struct_id
            WHERE b.geometry IS NOT NULL
            AND (v.latitude IS NULL OR v.longitude IS NULL)
        """)
        voters_to_update = cursor.fetchone()[0]
        print(f"Found {voters_to_update:,} voters to update")
        
        if voters_to_update == 0:
            print("No voters need updating!")
            conn.close()
            return True
        
        print("Updating voter coordinates from building geometry centroids...")
        cursor.execute("""
            UPDATE voters v
            SET 
                latitude = ST_Y(ST_Centroid(b.geometry)),
                longitude = ST_X(ST_Centroid(b.geometry))
            FROM voters_buildings_map vbm
            JOIN buildings b ON vbm.struct_id = b.struct_id
            WHERE v.res_id = vbm.res_id
            AND b.geometry IS NOT NULL
            AND (v.latitude IS NULL OR v.longitude IS NULL)
        """)
        
        updated_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Successfully updated {updated_count:,} voters with coordinates from building geometry")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM voters 
            WHERE latitude IS NOT NULL 
            AND longitude IS NOT NULL
        """)
        total_with_coords = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM voters")
        total_voters = cursor.fetchone()[0]
        
        print(f"\n📊 Updated Statistics:")
        print(f"   Total voters with coordinates: {total_with_coords:,} ({total_with_coords/total_voters*100:.1f}%)")
        
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
        
        print(f"   Elderly voters with coordinates: {elderly_with_coords:,} ({elderly_with_coords/total_elderly*100:.1f}%)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating voter coordinates: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = update_voter_coords_from_buildings()
    sys.exit(0 if success else 1)

