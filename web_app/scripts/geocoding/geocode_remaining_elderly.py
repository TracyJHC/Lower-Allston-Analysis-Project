#!/usr/bin/env python3
"""
Script to geocode remaining elderly voters who don't have coordinates
"""

import psycopg
import os
from dotenv import load_dotenv
import sys
import time

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def geocode_address(address, city='Boston', state='MA', zip_code=None):
    try:
        from geopy.geocoders import Nominatim
        from geopy.exc import GeocoderTimedOut
        
        geolocator = Nominatim(user_agent='abcdc_geocoder')
        
        full_address = f"{address}, {city}, {state}"
        if zip_code:
            full_address += f" {zip_code}"
        
        time.sleep(1.1)
        location = geolocator.geocode(full_address, timeout=15)
        
        if location:
            return location.latitude, location.longitude
        return None, None
    except ImportError:
        print("  Error: geopy not installed. Run: pip install geopy")
        return None, None
    except Exception as e:
        return None, None

def geocode_remaining_elderly():
    try:
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n=== CATEGORY 1: Elderly not mapped to buildings ===\n")
        
        cursor.execute("""
            SELECT 
                v.res_id,
                v.street_number || ' ' || v.street_name as address,
                'Boston' as city,
                v.zip_code
            FROM voters v
            WHERE v.is_elderly = true
            AND (v.latitude IS NULL OR v.longitude IS NULL)
            AND NOT EXISTS (
                SELECT 1 FROM voters_buildings_map vbm WHERE vbm.res_id = v.res_id
            )
            ORDER BY v.res_id
        """)
        unmapped_elderly = cursor.fetchall()
        print(f"Found {len(unmapped_elderly):,} elderly voters not mapped to buildings")
        
        print("\n=== CATEGORY 2: Elderly mapped to buildings without geometry ===\n")
        
        cursor.execute("""
            SELECT DISTINCT
                b.struct_id,
                b.st_num || ' ' || b.st_name as address,
                b.city,
                b.zip_code,
                COUNT(DISTINCT v.res_id) as elderly_count
            FROM buildings b
            JOIN voters_buildings_map vbm ON b.struct_id = vbm.struct_id
            JOIN voters v ON vbm.res_id = v.res_id
            WHERE v.is_elderly = true
            AND (v.latitude IS NULL OR v.longitude IS NULL)
            AND b.geometry IS NULL
            GROUP BY b.struct_id, b.st_num, b.st_name, b.city, b.zip_code
            ORDER BY elderly_count DESC
        """)
        buildings_no_geom = cursor.fetchall()
        print(f"Found {len(buildings_no_geom):,} buildings without geometry")
        total_elderly_in_buildings = sum(b[4] for b in buildings_no_geom)
        print(f"Total elderly voters in these buildings: {total_elderly_in_buildings:,}")
        
        print("\n=== Geocoding buildings first (will apply to all voters in building) ===\n")
        
        building_coords = {}
        geocoded_buildings = 0
        
        for struct_id, address, city, zip_code, elderly_count in buildings_no_geom:
            if not address or address.strip() == '':
                continue
            
            city_val = city or 'Boston'
            zip_val = str(int(zip_code)) if zip_code else None
            
            print(f"Geocoding {struct_id}: {address}, {city_val}... ({elderly_count} elderly)")
            lat, lon = geocode_address(address, city_val, 'MA', zip_val)
            
            if lat and lon:
                building_coords[struct_id] = (lat, lon)
                geocoded_buildings += 1
                print(f"  ✅ Got coordinates: ({lat:.6f}, {lon:.6f})")
            else:
                print(f"  ❌ Failed to geocode")
        
        print(f"\n✅ Geocoded {geocoded_buildings}/{len(buildings_no_geom)} buildings")
        
        if building_coords:
            print("\nUpdating voters mapped to geocoded buildings...")
            for struct_id, (lat, lon) in building_coords.items():
                cursor.execute("""
                    UPDATE voters v
                    SET latitude = %s, longitude = %s
                    FROM voters_buildings_map vbm
                    WHERE v.res_id = vbm.res_id
                    AND vbm.struct_id = %s
                    AND v.is_elderly = true
                    AND (v.latitude IS NULL OR v.longitude IS NULL)
                """, (lat, lon, struct_id))
            
            updated_from_buildings = cursor.rowcount
            conn.commit()
            print(f"✅ Updated {updated_from_buildings:,} elderly voters from building geocoding")
        
        print("\n=== Geocoding individual elderly voters not mapped to buildings ===\n")
        print(f"This will take a while ({len(unmapped_elderly):,} voters)...")
        print("Processing in batches of 100...\n")
        
        geocoded_voters = 0
        failed_voters = 0
        
        for i, (res_id, address, city, zip_code) in enumerate(unmapped_elderly, 1):
            if not address or address.strip() == '':
                continue
            
            city_val = city or 'Boston'
            zip_val = str(int(zip_code)) if zip_code else None
            
            if i % 100 == 0:
                print(f"Progress: {i}/{len(unmapped_elderly)} ({i/len(unmapped_elderly)*100:.1f}%)")
            
            lat, lon = geocode_address(address, city_val, 'MA', zip_val)
            
            if lat and lon:
                cursor.execute("""
                    UPDATE voters
                    SET latitude = %s, longitude = %s
                    WHERE res_id = %s
                """, (lat, lon, res_id))
                geocoded_voters += 1
            else:
                failed_voters += 1
            
            if i % 50 == 0:
                conn.commit()
        
        conn.commit()
        
        print(f"\n✅ Geocoded {geocoded_voters:,} individual elderly voters")
        print(f"❌ Failed to geocode {failed_voters:,} voters")
        
        print("\n=== FINAL STATISTICS ===\n")
        
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
        print(f"Elderly voters without coordinates: {total_elderly - elderly_with_coords:,} ({(total_elderly - elderly_with_coords)/total_elderly*100:.1f}%)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = geocode_remaining_elderly()
    sys.exit(0 if success else 1)

