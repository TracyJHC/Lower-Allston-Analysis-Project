#!/usr/bin/env python3
"""
Script to load building property data from CSV into the database
"""

import pandas as pd
import psycopg
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_allston_brighton'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
    'port': os.getenv('DB_PORT', '5432')
}

def clean_numeric_value(value):
    """Clean numeric values by removing commas and dollar signs"""
    if pd.isna(value) or value == '':
        return None
    
    # Convert to string and clean
    value_str = str(value).replace(',', '').replace('$', '').strip()
    
    # Handle empty strings after cleaning
    if value_str == '' or value_str == 'N/A':
        return None
    
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None

def clean_string_value(value):
    """Clean string values"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()

def load_buildings_data():
    """Load building data from CSV into database"""
    
    # Path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'building_property_with_suffix.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return False
    
    try:
        # Read CSV file
        print("Reading CSV file...")
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} records from CSV")
        
        # Connect to database
        print("Connecting to database...")
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Clear existing data
        print("Clearing existing buildings data...")
        cursor.execute("DELETE FROM buildings")
        
        # Prepare data for insertion
        print("Preparing data for insertion...")
        records_to_insert = []
        
        for _, row in df.iterrows():
            # Clean and prepare the data
            record = {
                'struct_id': clean_string_value(row.get('STRUCT_ID')),
                'parcel_id': clean_string_value(row.get('parcel_id')),
                'suffix': clean_string_value(row.get('suffix')),
                'pid': clean_string_value(row.get('PID')),
                'st_num': clean_string_value(row.get('ST_NUM')),
                'st_num2': clean_string_value(row.get('ST_NUM2')),
                'st_name': clean_string_value(row.get('ST_NAME')),
                'unit_num': clean_string_value(row.get('UNIT_NUM')),
                'city': clean_string_value(row.get('CITY')),
                'zip_code': clean_string_value(row.get('ZIP_CODE')),
                'owner_occ': clean_string_value(row.get('OWN_OCC')),
                'owner': clean_string_value(row.get('OWNER')),
                'mail_addressee': clean_string_value(row.get('MAIL_ADDRESSEE')),
                'mail_street_address': clean_string_value(row.get('MAIL_STREET_ADDRESS')),
                'mail_city': clean_string_value(row.get('MAIL_CITY')),
                'mail_state': clean_string_value(row.get('MAIL_STATE')),
                'mail_zip_code': clean_string_value(row.get('MAIL_ZIP_CODE')),
                'bldg_type': clean_string_value(row.get('BLDG_TYPE')),
                'total_value': clean_numeric_value(row.get('TOTAL_VALUE')),
                'gross_tax': clean_numeric_value(row.get(' GROSS_TAX ')),  # Note the space in column name
                'yr_built': clean_numeric_value(row.get('YR_BUILT')),
                'yr_remodel': clean_numeric_value(row.get('YR_REMODEL')),
                'structure_class': clean_string_value(row.get('STRUCTURE_CLASS')),
                'bed_rms': clean_numeric_value(row.get('BED_RMS')),
                'full_bth': clean_numeric_value(row.get('FULL_BTH')),
                'hlf_bth': clean_numeric_value(row.get('HLF_BTH')),
                'kitchens': clean_numeric_value(row.get('KITCHENS')),
                'tt_rms': clean_numeric_value(row.get('TT_RMS')),
                'res_units': clean_numeric_value(row.get('RES_UNITS')),
                'com_units': clean_numeric_value(row.get('COM_UNITS')),
                'rc_units': clean_numeric_value(row.get('RC_UNITS')),
                'land_sf': clean_numeric_value(row.get('LAND_SF')),
                'gross_area': clean_numeric_value(row.get('GROSS_AREA')),
                'living_area': clean_numeric_value(row.get('LIVING_AREA')),
                'land_value': clean_numeric_value(row.get('LAND_VALUE')),
                'bldg_value': clean_numeric_value(row.get('BLDG_VALUE')),
                'sfyi_value': clean_numeric_value(row.get('SFYI_VALUE'))
            }
            
            # Only insert if we have a struct_id
            if record['struct_id']:
                records_to_insert.append(record)
        
        print(f"Prepared {len(records_to_insert)} records for insertion")
        
        # Insert data in batches
        insert_query = """
            INSERT INTO buildings (
                struct_id, parcel_id, suffix, pid, st_num, st_num2, st_name, unit_num,
                city, zip_code, owner_occ, owner, mail_addressee, mail_street_address,
                mail_city, mail_state, mail_zip_code, bldg_type, total_value, gross_tax,
                yr_built, yr_remodel, structure_class, bed_rms, full_bth, hlf_bth,
                kitchens, tt_rms, res_units, com_units, rc_units, land_sf, gross_area,
                living_area, land_value, bldg_value, sfyi_value
            ) VALUES (
                %(struct_id)s, %(parcel_id)s, %(suffix)s, %(pid)s, %(st_num)s, %(st_num2)s,
                %(st_name)s, %(unit_num)s, %(city)s, %(zip_code)s, %(owner_occ)s, %(owner)s,
                %(mail_addressee)s, %(mail_street_address)s, %(mail_city)s, %(mail_state)s,
                %(mail_zip_code)s, %(bldg_type)s, %(total_value)s, %(gross_tax)s,
                %(yr_built)s, %(yr_remodel)s, %(structure_class)s, %(bed_rms)s, %(full_bth)s,
                %(hlf_bth)s, %(kitchens)s, %(tt_rms)s, %(res_units)s, %(com_units)s,
                %(rc_units)s, %(land_sf)s, %(gross_area)s, %(living_area)s, %(land_value)s,
                %(bldg_value)s, %(sfyi_value)s
            )
        """
        
        print("Inserting data into database...")
        cursor.executemany(insert_query, records_to_insert)
        
        # Commit the transaction
        conn.commit()
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM buildings")
        count = cursor.fetchone()[0]
        
        print(f"Successfully loaded {count} building records into the database")
        
        # Close connection
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error loading buildings data: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = load_buildings_data()
    sys.exit(0 if success else 1)
