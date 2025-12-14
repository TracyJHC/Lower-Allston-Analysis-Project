#!/usr/bin/env python3
"""
Find precincts that don't have census tract mappings and identify nearby tracts.
This script helps identify precincts that may have geometry alignment issues.
"""
import os
import sys
import psycopg
from dotenv import load_dotenv

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config

load_dotenv()


def connect():
    """Get database connection"""
    return psycopg.connect(**Config.DB_CONFIG)


def find_missing_mappings():
    """Find precincts without census tract intersections"""
    print("=" * 70)
    print("FINDING PRECINCTS WITHOUT CENSUS TRACT MAPPINGS")
    print("=" * 70)
    
    conn = connect()
    
    try:
        with conn.cursor() as cur:
            # Find precincts that don't intersect with any census tract
            query = """
                SELECT 
                    p.ward_id,
                    p.precinct_id,
                    p.precinct_name,
                    COUNT(ct.tract_id) as overlapping_tracts
                FROM precincts p
                JOIN geo_precincts gp 
                    ON p.ward_id = gp.ward::integer 
                    AND p.precinct_id = gp.precinct::integer
                LEFT JOIN census_tracts ct 
                    ON ST_Intersects(gp.geom, ct.geometry)
                GROUP BY p.ward_id, p.precinct_id, p.precinct_name
                HAVING COUNT(ct.tract_id) = 0
                ORDER BY p.ward_id, p.precinct_id;
            """
            
            cur.execute(query)
            missing = cur.fetchall()
            
            if not missing:
                print("\n✅ All precincts have at least one overlapping census tract!")
                return
            
            print(f"\n⚠️  Found {len(missing)} precinct(s) without direct intersections:")
            print("-" * 70)
            
            for ward_id, precinct_id, precinct_name, _ in missing:
                print(f"\n📍 {precinct_name} (Ward {ward_id}, Precinct {precinct_id})")
                
                # Find nearest census tracts
                nearest_query = """
                    SELECT 
                        ct.tract_id,
                        ct.tract_name,
                        ROUND(ST_Distance(gp.geom::geography, ct.geometry::geography)::numeric, 2) as distance_meters
                    FROM geo_precincts gp
                    CROSS JOIN census_tracts ct
                    WHERE gp.ward::integer = %s 
                        AND gp.precinct::integer = %s
                    ORDER BY ST_Distance(gp.geom::geography, ct.geometry::geography)
                    LIMIT 5;
                """
                
                cur.execute(nearest_query, (ward_id, precinct_id))
                nearest = cur.fetchall()
                
                print(f"   Nearest census tracts:")
                for tract_id, tract_name, distance_m in nearest:
                    print(f"      - {tract_id} ({tract_name}): {distance_m}m away")
                
                # Check if within reasonable distance (e.g., 500m)
                if nearest and nearest[0][2] < 500:
                    print(f"   💡 Suggestion: This precinct is within 500m of tract {nearest[0][0]}")
                    print(f"      Consider using ST_DWithin for mapping with a 500m buffer")
            
            print("\n" + "=" * 70)
            print("SUMMARY")
            print("=" * 70)
            print(f"Total precincts missing mappings: {len(missing)}")
            print(f"Total precincts: 29")
            print(f"Precincts with mappings: {29 - len(missing)}")
            
    finally:
        conn.close()


if __name__ == '__main__':
    find_missing_mappings()

