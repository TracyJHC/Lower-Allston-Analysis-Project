#!/usr/bin/env python3
"""
Script to load store/retailer location data from CSV into the database
"""

import pandas as pd
import psycopg
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def clean_string_value(value):
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()

def clean_numeric_value(value):
    if pd.isna(value) or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_date(date_str):
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        if '/' in str(date_str):
            return datetime.strptime(str(date_str), '%m/%d/%Y').date()
        return pd.to_datetime(date_str).date()
    except:
        return None

def ensure_stores_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            store_id SERIAL PRIMARY KEY,
            record_id VARCHAR(50) UNIQUE,
            store_name VARCHAR(200),
            store_type VARCHAR(100),
            street_number VARCHAR(20),
            street_name VARCHAR(100),
            additional_address VARCHAR(200),
            city VARCHAR(50),
            state VARCHAR(10),
            zip_code VARCHAR(10),
            zip4 VARCHAR(10),
            county VARCHAR(50),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            authorization_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_stores_coords ON stores (latitude, longitude)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_stores_type ON stores (store_type)
    """)
    
    conn.commit()
    print("✅ Stores table created/verified")

def load_stores():
    csv_path = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/voter_data/Allston_Brighton_Retailer_Locator_upDated(no_end_date).csv'
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return False
    
    try:
        print("Reading CSV file...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from CSV")
        
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        
        ensure_stores_table(conn)
        
        cursor = conn.cursor()
        
        print("Clearing existing stores data...")
        cursor.execute("DELETE FROM stores")
        
        print("Preparing data for insertion...")
        records_to_insert = []
        
        for _, row in df.iterrows():
            record = {
                'record_id': clean_string_value(row.get('Record ID')),
                'store_name': clean_string_value(row.get('Store Name')),
                'store_type': clean_string_value(row.get('Store Type')),
                'street_number': clean_string_value(row.get('Street Number')),
                'street_name': clean_string_value(row.get('Street Name')),
                'additional_address': clean_string_value(row.get('Additional Address')),
                'city': clean_string_value(row.get('City')),
                'state': clean_string_value(row.get('State')),
                'zip_code': clean_string_value(row.get('Zip Code')),
                'zip4': clean_string_value(row.get('Zip4')),
                'county': clean_string_value(row.get('County')),
                'latitude': clean_numeric_value(row.get('Latitude')),
                'longitude': clean_numeric_value(row.get('Longitude')),
                'authorization_date': parse_date(row.get('Authorization Date')),
                'end_date': parse_date(row.get('End Date'))
            }
            
            if record['record_id'] and record['latitude'] and record['longitude']:
                records_to_insert.append(record)
        
        print(f"Prepared {len(records_to_insert)} records for insertion")
        
        insert_query = """
            INSERT INTO stores (
                record_id, store_name, store_type, street_number, street_name,
                additional_address, city, state, zip_code, zip4, county,
                latitude, longitude, authorization_date, end_date
            ) VALUES (
                %(record_id)s, %(store_name)s, %(store_type)s, %(street_number)s,
                %(street_name)s, %(additional_address)s, %(city)s, %(state)s,
                %(zip_code)s, %(zip4)s, %(county)s, %(latitude)s, %(longitude)s,
                %(authorization_date)s, %(end_date)s
            )
        """
        
        print("Inserting data into database...")
        cursor.executemany(insert_query, records_to_insert)
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM stores")
        count = cursor.fetchone()[0]
        
        print(f"✅ Successfully loaded {count} store records into the database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error loading stores data: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = load_stores()
    sys.exit(0 if success else 1)

