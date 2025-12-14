#!/usr/bin/env python3
"""
Script to add missing parcels from property assessment data
that weren't in the GeoJSON file
"""

import psycopg
import pandas as pd
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

def geocode_address(st_num, st_name, city, zip_code):
    try:
        from geopy.geocoders import Nominatim
        import time
        
        geolocator = Nominatim(user_agent='abcdc_geocoder')
        
        address = f"{int(st_num) if pd.notna(st_num) else ''} {st_name}, {city}, MA {int(zip_code) if pd.notna(zip_code) else ''}"
        address = address.strip().replace('  ', ' ')
        
        time.sleep(1)
        location = geolocator.geocode(address, timeout=10)
        
        if location:
            return location.latitude, location.longitude
        return None, None
    except ImportError:
        return None, None
    except Exception:
        return None, None

def add_missing_parcels():
    csv_path = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/raw/fy2025-property-assessment-data_12_30_2024.csv'
    
    missing_parcel_ids = [
        '2101511000', '2101580000', '2101582000', '2101583000',
        '2101591000', '2101592000', '2101593000', '2101597000',
        '2102132000', '2102565022', '2102565024'
    ]
    
    try:
        print("Loading property assessment data...")
        df = pd.read_csv(csv_path, low_memory=False)
        df['PID'] = df['PID'].astype(str)
        
        missing_parcels = df[df['PID'].isin(missing_parcel_ids)]
        print(f"Found {len(missing_parcels)} parcels in property assessment data")
        
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Adding missing parcels to database...")
        added = 0
        geocoded = 0
        
        for _, row in missing_parcels.iterrows():
            parcel_id = str(row['PID'])
            
            st_num = row.get('ST_NUM')
            st_name = row.get('ST_NAME', '')
            city = row.get('CITY', 'Boston')
            zip_code = row.get('ZIP_CODE', '')
            
            address = f"{int(st_num) if pd.notna(st_num) else ''} {st_name}, {city}, MA"
            
            lat, lon = None, None
            
            try:
                lat, lon = geocode_address(st_num, st_name, city, zip_code)
                if lat and lon:
                    geocoded += 1
                    print(f"  ✅ Geocoded {parcel_id}: {address} -> ({lat:.6f}, {lon:.6f})")
                else:
                    print(f"  ⚠️  Could not geocode {parcel_id}: {address} (adding without coordinates)")
            except Exception as e:
                print(f"  ⚠️  Geocoding error for {parcel_id}: {e} (adding without coordinates)")
            
            try:
                cursor.execute("""
                    INSERT INTO parcels (parcel_id, loc_id, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (parcel_id) DO UPDATE
                    SET latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude
                """, (
                    parcel_id,
                    str(row.get('GIS_ID', '')),
                    lat,
                    lon
                ))
                added += 1
            except Exception as e:
                print(f"  ❌ Error inserting {parcel_id}: {e}")
        
        conn.commit()
        
        print(f"\n✅ Added {added} parcels to database")
        print(f"✅ Geocoded {geocoded} parcels")
        
        if geocoded > 0:
            print("\nUpdating voter coordinates from newly added parcels...")
            cursor.execute("""
                UPDATE voters v
                SET 
                    latitude = p.latitude,
                    longitude = p.longitude
                FROM voters_buildings_map vbm
                JOIN buildings b ON vbm.struct_id = b.struct_id
                JOIN parcels p ON b.parcel_id = p.parcel_id
                WHERE v.res_id = vbm.res_id
                AND b.geometry IS NULL
                AND p.latitude IS NOT NULL
                AND p.longitude IS NOT NULL
                AND (v.latitude IS NULL OR v.longitude IS NULL)
            """)
            
            updated_voters = cursor.rowcount
            conn.commit()
            print(f"✅ Updated {updated_voters} voters with coordinates from newly added parcels")
        
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
    success = add_missing_parcels()
    sys.exit(0 if success else 1)
