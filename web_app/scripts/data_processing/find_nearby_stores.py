#!/usr/bin/env python3
"""
Script to find nearby stores for each voter based on their coordinates
"""

import psycopg
import os
from dotenv import load_dotenv
import sys
import math

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def ensure_mapping_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voter_store_nearby (
            mapping_id SERIAL PRIMARY KEY,
            res_id VARCHAR(50) NOT NULL,
            store_id INTEGER NOT NULL,
            distance_meters DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (res_id) REFERENCES voters(res_id),
            FOREIGN KEY (store_id) REFERENCES stores(store_id),
            UNIQUE(res_id, store_id)
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_voter_store_nearby_voter 
        ON voter_store_nearby (res_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_voter_store_nearby_store 
        ON voter_store_nearby (store_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_voter_store_nearby_distance 
        ON voter_store_nearby (distance_meters)
    """)
    
    conn.commit()
    print("✅ Voter-store mapping table created/verified")

def find_nearby_stores(max_distance_meters=2000, max_stores_per_voter=10, elderly_only=True):
    try:
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        
        ensure_mapping_table(conn)
        
        cursor = conn.cursor()
        
        print("Clearing existing mappings...")
        cursor.execute("DELETE FROM voter_store_nearby")
        conn.commit()
        
        print("Fetching voters with coordinates (direct or via buildings)...")
        if elderly_only:
            cursor.execute("""
                SELECT DISTINCT ON (v.res_id)
                    v.res_id,
                    COALESCE(
                        v.latitude, 
                        (SELECT ST_Y(ST_Centroid(b2.geometry))
                         FROM voters_buildings_map vbm2
                         JOIN buildings b2 ON vbm2.struct_id = b2.struct_id
                         WHERE vbm2.res_id = v.res_id
                         AND b2.geometry IS NOT NULL
                         LIMIT 1)
                    ) as latitude,
                    COALESCE(
                        v.longitude,
                        (SELECT ST_X(ST_Centroid(b2.geometry))
                         FROM voters_buildings_map vbm2
                         JOIN buildings b2 ON vbm2.struct_id = b2.struct_id
                         WHERE vbm2.res_id = v.res_id
                         AND b2.geometry IS NOT NULL
                         LIMIT 1)
                    ) as longitude
                FROM voters v
                WHERE v.is_elderly = true
                AND (
                    (v.latitude IS NOT NULL AND v.longitude IS NOT NULL)
                    OR EXISTS (
                        SELECT 1
                        FROM voters_buildings_map vbm
                        JOIN buildings b ON vbm.struct_id = b.struct_id
                        WHERE vbm.res_id = v.res_id
                        AND b.geometry IS NOT NULL
                    )
                )
            """)
            print("   (Filtering for elderly voters only, using building coordinates if voter coordinates unavailable)")
        else:
            cursor.execute("""
                SELECT DISTINCT ON (v.res_id)
                    v.res_id,
                    COALESCE(
                        v.latitude, 
                        (SELECT ST_Y(ST_Centroid(b2.geometry))
                         FROM voters_buildings_map vbm2
                         JOIN buildings b2 ON vbm2.struct_id = b2.struct_id
                         WHERE vbm2.res_id = v.res_id
                         AND b2.geometry IS NOT NULL
                         LIMIT 1)
                    ) as latitude,
                    COALESCE(
                        v.longitude,
                        (SELECT ST_X(ST_Centroid(b2.geometry))
                         FROM voters_buildings_map vbm2
                         JOIN buildings b2 ON vbm2.struct_id = b2.struct_id
                         WHERE vbm2.res_id = v.res_id
                         AND b2.geometry IS NOT NULL
                         LIMIT 1)
                    ) as longitude
                FROM voters v
                WHERE (
                    (v.latitude IS NOT NULL AND v.longitude IS NOT NULL)
                    OR EXISTS (
                        SELECT 1
                        FROM voters_buildings_map vbm
                        JOIN buildings b ON vbm.struct_id = b.struct_id
                        WHERE vbm.res_id = v.res_id
                        AND b.geometry IS NOT NULL
                    )
                )
            """)
        voters = cursor.fetchall()
        print(f"Found {len(voters)} voters with coordinates (direct or via buildings)")
        
        print("Fetching stores with coordinates...")
        cursor.execute("""
            SELECT store_id, latitude, longitude 
            FROM stores 
            WHERE latitude IS NOT NULL 
            AND longitude IS NOT NULL
        """)
        stores = cursor.fetchall()
        print(f"Found {len(stores)} stores with coordinates")
        
        print("Calculating distances and finding nearby stores...")
        mappings = []
        processed = 0
        
        for voter_res_id, voter_lat, voter_lon in voters:
            voter_distances = []
            
            for store_id, store_lat, store_lon in stores:
                distance = haversine_distance(
                    float(voter_lat), float(voter_lon),
                    float(store_lat), float(store_lon)
                )
                
                if distance <= max_distance_meters:
                    voter_distances.append((store_id, distance))
            
            voter_distances.sort(key=lambda x: x[1])
            
            for store_id, distance in voter_distances[:max_stores_per_voter]:
                mappings.append({
                    'res_id': voter_res_id,
                    'store_id': store_id,
                    'distance_meters': round(distance, 2)
                })
            
            processed += 1
            if processed % 1000 == 0:
                print(f"Processed {processed}/{len(voters)} voters...")
        
        print(f"Found {len(mappings)} voter-store mappings")
        
        print("Inserting mappings into database...")
        insert_query = """
            INSERT INTO voter_store_nearby (res_id, store_id, distance_meters)
            VALUES (%(res_id)s, %(store_id)s, %(distance_meters)s)
            ON CONFLICT (res_id, store_id) DO UPDATE
            SET distance_meters = EXCLUDED.distance_meters
        """
        
        cursor.executemany(insert_query, mappings)
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM voter_store_nearby")
        count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT res_id) as voters_with_stores,
                AVG(distance_meters) as avg_distance,
                MIN(distance_meters) as min_distance,
                MAX(distance_meters) as max_distance
            FROM voter_store_nearby
        """)
        stats = cursor.fetchone()
        
        print(f"✅ Successfully created {count} voter-store mappings")
        print(f"   - Voters with nearby stores: {stats[0]}")
        print(f"   - Average distance: {stats[1]:.2f} meters")
        print(f"   - Min distance: {stats[2]:.2f} meters")
        print(f"   - Max distance: {stats[3]:.2f} meters")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error finding nearby stores: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Find nearby stores for voters')
    parser.add_argument('--max-distance', type=int, default=2000,
                       help='Maximum distance in meters (default: 2000)')
    parser.add_argument('--max-stores', type=int, default=10,
                       help='Maximum stores per voter (default: 10)')
    parser.add_argument('--all-voters', action='store_true',
                       help='Process all voters, not just elderly (default: elderly only)')
    
    args = parser.parse_args()
    
    success = find_nearby_stores(
        max_distance_meters=args.max_distance,
        max_stores_per_voter=args.max_stores,
        elderly_only=not args.all_voters
    )
    sys.exit(0 if success else 1)

