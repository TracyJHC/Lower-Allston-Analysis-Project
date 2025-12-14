#!/usr/bin/env python3
"""
Script to load elderly analysis CSV files into the database
"""

import pandas as pd
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def create_tables(conn):
    cursor = conn.cursor()
    
    print("Creating tables for elderly analysis data...")
    
    cursor.execute("""
        DROP TABLE IF EXISTS elderly_housing_conditions CASCADE;
        CREATE TABLE elderly_housing_conditions (
            res_id VARCHAR(50),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            street_number INTEGER,
            street_name VARCHAR(100),
            apartment VARCHAR(20),
            ward_id INTEGER,
            precinct_id INTEGER,
            struct_id VARCHAR(50),
            building_parcel_id VARCHAR(50),
            building_address VARCHAR(200),
            bldg_type VARCHAR(50),
            building_year_built INTEGER,
            parcel_id VARCHAR(50),
            address VARCHAR(200),
            year_built DECIMAL(10,2),
            property_age DECIMAL(10,2),
            interior_condition VARCHAR(50),
            exterior_condition VARCHAR(50),
            grade VARCHAR(50),
            interior_finish VARCHAR(100),
            exterior_finish VARCHAR(100),
            foundation VARCHAR(100),
            roof_cover VARCHAR(100),
            roof_structure VARCHAR(100),
            ac_type VARCHAR(100),
            heat_type VARCHAR(100),
            living_area_sqft DECIMAL(12,2),
            lot_size_sqft DECIMAL(12,2),
            property_type VARCHAR(100),
            fy2025_total_assessed_value_numeric DECIMAL(15,2)
        );
    """)
    
    cursor.execute("""
        DROP TABLE IF EXISTS elderly_permits_one_to_one CASCADE;
        CREATE TABLE elderly_permits_one_to_one (
            res_id VARCHAR(50),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            street_number INTEGER,
            street_name VARCHAR(100),
            apartment VARCHAR(20),
            ward_id INTEGER,
            precinct_id INTEGER,
            struct_id VARCHAR(50),
            building_parcel_id VARCHAR(50),
            building_address VARCHAR(200),
            bldg_type VARCHAR(50),
            building_year_built INTEGER,
            parcel_id VARCHAR(50),
            address VARCHAR(200),
            year_built DECIMAL(10,2),
            property_age DECIMAL(10,2),
            interior_condition VARCHAR(50),
            exterior_condition VARCHAR(50),
            grade VARCHAR(50),
            interior_finish VARCHAR(100),
            exterior_finish VARCHAR(100),
            foundation VARCHAR(100),
            roof_cover VARCHAR(100),
            roof_structure VARCHAR(100),
            ac_type VARCHAR(100),
            heat_type VARCHAR(100),
            living_area_sqft DECIMAL(12,2),
            lot_size_sqft DECIMAL(12,2),
            property_type VARCHAR(100),
            fy2025_total_assessed_value_numeric DECIMAL(15,2),
            permitnumber VARCHAR(50),
            worktype VARCHAR(50),
            permittypedescr VARCHAR(200),
            description TEXT,
            comments TEXT,
            applicant VARCHAR(200),
            declared_valuation VARCHAR(50),
            total_fees VARCHAR(50),
            issued_date TIMESTAMP,
            expiration_date TIMESTAMP,
            status VARCHAR(50),
            occupancytype VARCHAR(50),
            sq_feet DECIMAL(12,2),
            address_permit VARCHAR(200),
            city VARCHAR(50),
            state VARCHAR(10),
            zip VARCHAR(10),
            ward VARCHAR(10),
            property_id VARCHAR(50),
            gpsy DECIMAL(15,8),
            gpsx DECIMAL(15,8),
            y_latitude DECIMAL(12,8),
            x_longitude DECIMAL(12,8)
        );
    """)
    
    cursor.execute("""
        DROP TABLE IF EXISTS elderly_permits_one_to_one_summary CASCADE;
        CREATE TABLE elderly_permits_one_to_one_summary (
            res_id VARCHAR(50) PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            ward_id INTEGER,
            precinct_id INTEGER,
            parcel_id VARCHAR(50),
            has_permits BOOLEAN,
            permit_count INTEGER
        );
    """)
    
    cursor.execute("""
        DROP TABLE IF EXISTS elderly_violations_one_to_one CASCADE;
        CREATE TABLE elderly_violations_one_to_one (
            res_id VARCHAR(50),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            street_number INTEGER,
            street_name VARCHAR(100),
            apartment VARCHAR(20),
            ward_id INTEGER,
            precinct_id INTEGER,
            struct_id VARCHAR(50),
            building_parcel_id VARCHAR(50),
            building_address VARCHAR(200),
            bldg_type VARCHAR(50),
            building_year_built INTEGER,
            parcel_id VARCHAR(50),
            address VARCHAR(200),
            year_built DECIMAL(10,2),
            property_age DECIMAL(10,2),
            interior_condition VARCHAR(50),
            exterior_condition VARCHAR(50),
            grade VARCHAR(50),
            interior_finish VARCHAR(100),
            exterior_finish VARCHAR(100),
            foundation VARCHAR(100),
            roof_cover VARCHAR(100),
            roof_structure VARCHAR(100),
            ac_type VARCHAR(100),
            heat_type VARCHAR(100),
            living_area_sqft DECIMAL(12,2),
            lot_size_sqft DECIMAL(12,2),
            property_type VARCHAR(100),
            fy2025_total_assessed_value_numeric DECIMAL(15,2),
            case_no VARCHAR(50),
            ap_case_defn_key INTEGER,
            status_dttm TIMESTAMP,
            status VARCHAR(50),
            code VARCHAR(50),
            value VARCHAR(50),
            description TEXT,
            violation_stno VARCHAR(20),
            violation_sthigh VARCHAR(20),
            violation_street VARCHAR(100),
            violation_suffix VARCHAR(20),
            violation_city VARCHAR(50),
            violation_state VARCHAR(10),
            violation_zip VARCHAR(10),
            ward VARCHAR(10),
            contact_addr1 VARCHAR(200),
            contact_addr2 VARCHAR(200),
            contact_city VARCHAR(50),
            contact_state VARCHAR(10),
            contact_zip VARCHAR(20),
            sam_id INTEGER,
            latitude DECIMAL(12,8),
            longitude DECIMAL(12,8),
            location VARCHAR(200)
        );
    """)
    
    cursor.execute("""
        DROP TABLE IF EXISTS elderly_violations_one_to_one_summary CASCADE;
        CREATE TABLE elderly_violations_one_to_one_summary (
            res_id VARCHAR(50) PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INTEGER,
            ward_id INTEGER,
            precinct_id INTEGER,
            parcel_id VARCHAR(50),
            street_number INTEGER,
            street_name VARCHAR(100),
            has_violations BOOLEAN,
            total_violations INTEGER,
            open_violations INTEGER,
            closed_violations INTEGER
        );
    """)
    
    conn.commit()
    print("✅ Tables created")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_elderly_housing_res_id ON elderly_housing_conditions(res_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_housing_parcel ON elderly_housing_conditions(parcel_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_housing_ward ON elderly_housing_conditions(ward_id);
        
        CREATE INDEX IF NOT EXISTS idx_elderly_permits_res_id ON elderly_permits_one_to_one(res_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_permits_parcel ON elderly_permits_one_to_one(parcel_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_permits_worktype ON elderly_permits_one_to_one(worktype);
        CREATE INDEX IF NOT EXISTS idx_elderly_permits_date ON elderly_permits_one_to_one(issued_date);
        
        CREATE INDEX IF NOT EXISTS idx_elderly_violations_res_id ON elderly_violations_one_to_one(res_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_violations_parcel ON elderly_violations_one_to_one(parcel_id);
        CREATE INDEX IF NOT EXISTS idx_elderly_violations_status ON elderly_violations_one_to_one(status);
    """)
    
    conn.commit()
    print("✅ Indexes created")

def load_csv_to_table(conn, csv_path, table_name, chunk_size=5000):
    if not os.path.exists(csv_path):
        print(f"⚠️  File not found: {csv_path}")
        return False
    
    print(f"\nLoading {table_name}...")
    cursor = conn.cursor()
    
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    db_columns = [row[0] for row in cursor.fetchall()]
    
    total_rows = 0
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False):
        chunk = chunk.replace({pd.NA: None, 'nan': None, 'NaN': None})
        
        if '_merge' in chunk.columns:
            chunk = chunk.drop(columns=['_merge'])
        
        chunk_columns = [col for col in chunk.columns if col in db_columns]
        chunk = chunk[chunk_columns]
        
        for col in chunk.columns:
            if chunk[col].dtype == 'float64':
                chunk[col] = chunk[col].astype('object')
        
        columns = ', '.join([f'"{col}"' for col in chunk.columns])
        placeholders = ', '.join(['%s'] * len(chunk.columns))
        
        values = []
        for _, row in chunk.iterrows():
            row_values = []
            for idx, val in enumerate(row):
                col_name = chunk.columns[idx]
                if pd.isna(val) or val == 'nan' or val == 'NaN' or val == '' or (isinstance(val, str) and val.strip() == ''):
                    row_values.append(None)
                else:
                    row_values.append(val)
            values.append(tuple(row_values))
        
        query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        
        try:
            cursor.executemany(query, values)
            total_rows += len(chunk)
            
            if total_rows % 10000 == 0:
                print(f"  Loaded {total_rows:,} rows...")
                conn.commit()
        except Exception as e:
            print(f"  Error at row {total_rows}: {e}")
            print(f"  Sample row: {values[0] if values else 'N/A'}")
            raise
    
    conn.commit()
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    print(f"✅ Loaded {count:,} rows into {table_name}")
    return True

def main():
    base_path = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/elderly_analysis'
    
    files_to_load = [
        ('elderly_housing_conditions.csv', 'elderly_housing_conditions'),
        ('elderly_permits_one_to_one.csv', 'elderly_permits_one_to_one'),
        ('elderly_permits_one_to_one_summary.csv', 'elderly_permits_one_to_one_summary'),
        ('elderly_violations_one_to_one.csv', 'elderly_violations_one_to_one'),
        ('elderly_violations_one_to_one_summary.csv', 'elderly_violations_one_to_one_summary')
    ]
    
    print("Connecting to database...")
    conn = psycopg.connect(**DB_CONFIG)
    
    try:
        create_tables(conn)
        
        for filename, table_name in files_to_load:
            csv_path = os.path.join(base_path, filename)
            load_csv_to_table(conn, csv_path, table_name)
        
        print("\n✅ All elderly analysis data loaded successfully!")
        
        cursor = conn.cursor()
        print("\n=== Table Row Counts ===")
        for _, table_name in files_to_load:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count:,} rows")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()

