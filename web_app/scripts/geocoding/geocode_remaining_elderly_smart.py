#!/usr/bin/env python3
"""
Smart script to geocode remaining elderly voters
- First checks homeowners_geocoded.csv for existing coordinates
- Only geocodes addresses not found in the CSV
"""

import psycopg
import pandas as pd
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

def load_geocoded_addresses():
    csv_path = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/voter_data/homeowners_geocoded.csv'
    
    if not os.path.exists(csv_path):
        return {}
    
    df = pd.read_csv(csv_path)
    df = df[df['latitude'].notna() & df['longitude'].notna()]
    
    address_map = {}
    for _, row in df.iterrows():
        st_num = str(int(row['Street .'])) if pd.notna(row['Street .']) else ''
        st_name = str(row['Street Name']).strip().upper() if pd.notna(row['Street Name']) else ''
        address_key = f"{st_num} {st_name}".strip()
        
        if address_key and address_key not in address_map:
            address_map[address_key] = (row['latitude'], row['longitude'])
    
    print(f"Loaded {len(address_map):,} geocoded addresses from CSV")
    return address_map

def geocode_address(address, city='Boston', state='MA', zip_code=None):
    try:
        from geopy.geocoders import Nominatim
        
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
        return None, None
    except Exception:
        return None, None

def geocode_remaining_elderly():
    try:
        print("Loading geocoded addresses from CSV...")
        geocoded_addresses = load_geocoded_addresses()
        
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n=== CATEGORY 1: Elderly not mapped to buildings ===\n")
        
        cursor.execute("""
            SELECT 
                v.res_id,
                v.street_number || ' ' || v.street_name as address,
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
                b.zip_code,
                COUNT(DISTINCT v.res_id) as elderly_count
            FROM buildings b
            JOIN voters_buildings_map vbm ON b.struct_id = vbm.struct_id
            JOIN voters v ON vbm.res_id = v.res_id
            WHERE v.is_elderly = true
            AND (v.latitude IS NULL OR v.longitude IS NULL)
            AND b.geometry IS NULL
            GROUP BY b.struct_id, b.st_num, b.st_name, b.zip_code
            ORDER BY elderly_count DESC
        """)
        buildings_no_geom = cursor.fetchall()
        print(f"Found {len(buildings_no_geom):,} buildings without geometry")
        
        print("\n=== Step 1: Update from CSV geocoded addresses ===\n")
        
        updated_from_csv = 0
        for res_id, address, zip_code in unmapped_elderly:
            if not address:
                continue
            
            address_key = address.upper().strip()
            if address_key in geocoded_addresses:
                lat, lon = geocoded_addresses[address_key]
                cursor.execute("""
                    UPDATE voters
                    SET latitude = %s, longitude = %s
                    WHERE res_id = %s
                """, (lat, lon, res_id))
                updated_from_csv += 1
        
        conn.commit()
        print(f"✅ Updated {updated_from_csv:,} voters from CSV geocoded addresses")
        
        remaining_unmapped = len(unmapped_elderly) - updated_from_csv
        print(f"Remaining to geocode: {remaining_unmapped:,}")
        
        print("\n=== Step 2: Geocode buildings ===\n")
        
        building_coords = {}
        geocoded_buildings = 0
        
        for struct_id, address, zip_code, elderly_count in buildings_no_geom:
            if not address or address.strip() == '':
                continue
            
            address_key = address.upper().strip()
            
            if address_key in geocoded_addresses:
                lat, lon = geocoded_addresses[address_key]
                building_coords[struct_id] = (lat, lon)
                print(f"  ✅ {struct_id}: Found in CSV ({elderly_count} elderly)")
            else:
                zip_val = str(int(zip_code)) if zip_code else None
                print(f"  Geocoding {struct_id}: {address}... ({elderly_count} elderly)")
                lat, lon = geocode_address(address, 'Boston', 'MA', zip_val)
                
                if lat and lon:
                    building_coords[struct_id] = (lat, lon)
                    geocoded_buildings += 1
                    print(f"    ✅ Got coordinates: ({lat:.6f}, {lon:.6f})")
                else:
                    print(f"    ❌ Failed to geocode")
        
        print(f"\n✅ Geocoded {geocoded_buildings} buildings (others found in CSV)")
        
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
            print(f"✅ Updated {updated_from_buildings:,} elderly voters from building coordinates")
        
        print(f"\n=== Step 3: Geocode remaining individual voters ===\n")
        print(f"Remaining: {remaining_unmapped:,} voters")
        
        if remaining_unmapped > 0:
            cursor.execute("""
                SELECT 
                    v.res_id,
                    v.street_number || ' ' || v.street_name as address,
                    v.zip_code
                FROM voters v
                WHERE v.is_elderly = true
                AND (v.latitude IS NULL OR v.longitude IS NULL)
                AND NOT EXISTS (
                    SELECT 1 FROM voters_buildings_map vbm WHERE vbm.res_id = v.res_id
                )
                ORDER BY v.res_id
            """)
            remaining_voters = cursor.fetchall()
            
            estimated_time = remaining_unmapped * 1.1 / 60
            print(f"Estimated time: ~{estimated_time:.1f} minutes")
            print("Starting geocoding...\n")
            
            geocoded_voters = 0
            failed_voters = 0
            
            for i, (res_id, address, zip_code) in enumerate(remaining_voters, 1):
                if not address or address.strip() == '':
                    continue
                
                address_key = address.upper().strip()
                if address_key in geocoded_addresses:
                    lat, lon = geocoded_addresses[address_key]
                else:
                    zip_val = str(int(zip_code)) if zip_code else None
                    lat, lon = geocode_address(address, 'Boston', 'MA', zip_val)
                
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
                    print(f"Progress: {i}/{remaining_unmapped} ({i/remaining_unmapped*100:.1f}%) - Geocoded: {geocoded_voters}, Failed: {failed_voters}")
            
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

