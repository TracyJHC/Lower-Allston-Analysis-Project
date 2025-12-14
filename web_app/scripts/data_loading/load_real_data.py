#!/usr/bin/env python3
"""
Load real Allston-Brighton data into the database
"""

import psycopg
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'abcdc_spatial'),
    'user': os.getenv('DB_USER', 'Studies'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': os.getenv('DB_PORT', '5432')
}

def load_voters():
    """Load voter data from CSV"""
    print("📊 Loading voters...")
    
    # Read the cleaned voter data
    df = pd.read_csv('../data/processed/voter_list_cleaned.csv')
    
    # Calculate age and elderly status
    df['date_of_birth'] = pd.to_datetime(df['DOB'])
    df['age'] = (pd.Timestamp.now() - df['date_of_birth']).dt.days // 365
    df['is_elderly'] = df['age'] >= 62
    
    # Clean and prepare data
    voters_data = []
    for _, row in df.iterrows():
        voters_data.append({
            'res_id': row['Res ID'],
            'last_name': row['Last Name'],
            'first_name': row['First Name'],
            'date_of_birth': row['date_of_birth'].date(),
            'occupation': row['Occupation'],
            'street_number': row['Street .'],
            'street_suffix': row['Sffx'] if pd.notna(row['Sffx']) else '',
            'street_name': row['Street Name'],
            'apartment': row['Apt .'] if pd.notna(row['Apt .']) else '',
            'zip_code': str(row['Zip']),
            'ward_id': row['Ward'],
            'precinct_id': row['Precinct'],
            'full_address': f"{row['Street .']} {row['Street Name']}",
            'normalized_address': f"{row['Street .']} {row['Street Name']}, Boston, MA {row['Zip']}",
            'latitude': None,  # Will be populated later if we have geocoded data
            'longitude': None,
            'is_elderly': row['is_elderly'],
            'age': row['age']
        })
    
    return voters_data

def load_properties():
    """Load property assessment data"""
    print("🏠 Loading properties...")
    
    df = pd.read_csv('../data/processed/gis_layers/allston_brighton_assessments.csv')
    
    properties_data = []
    assessments_data = []
    ownership_data = []
    
    for _, row in df.iterrows():
        # Property data
        properties_data.append({
            'parcel_id': row['PROP_ID'],
            'prop_id': row['PROP_ID'],
            'loc_id': row['LOC_ID'],
            'site_address': row['SITE_ADDR'],
            'addr_num': row['ADDR_NUM'] if pd.notna(row['ADDR_NUM']) else None,
            'full_street': row['FULL_STR'],
            'location': row['LOCATION'],
            'city': row['CITY'],
            'zip_code': str(row['ZIP']),
            'zoning': row['ZONING'] if pd.notna(row['ZONING']) else '',
            'year_built': row['YEAR_BUILT'] if pd.notna(row['YEAR_BUILT']) else None,
            'building_area': row['BLD_AREA'] if pd.notna(row['BLD_AREA']) else None,
            'lot_size': row['LOT_SIZE'] if pd.notna(row['LOT_SIZE']) else None,
            'units': row['UNITS'] if pd.notna(row['UNITS']) else None,
            'residential_area': row['RES_AREA'] if pd.notna(row['RES_AREA']) else None,
            'style': row['STYLE'] if pd.notna(row['STYLE']) else '',
            'num_rooms': row['NUM_ROOMS'] if pd.notna(row['NUM_ROOMS']) else None,
            'lot_units': row['LOT_UNITS'] if pd.notna(row['LOT_UNITS']) else '',
            'stories_num': row['STORIES_NUM'] if pd.notna(row['STORIES_NUM']) else None,
            'stories': row['STORIES'] if pd.notna(row['STORIES']) else '',
            'latitude': None,  # Will be populated from geocoded data
            'longitude': None
        })
        
        # Assessment data
        assessments_data.append({
            'parcel_id': row['PROP_ID'],
            'fiscal_year': row['FY'],
            'building_value': row['BLDG_VAL'] if pd.notna(row['BLDG_VAL']) else None,
            'land_value': row['LAND_VAL'] if pd.notna(row['LAND_VAL']) else None,
            'other_value': row['OTHER_VAL'] if pd.notna(row['OTHER_VAL']) else None,
            'total_value': row['TOTAL_VAL'] if pd.notna(row['TOTAL_VAL']) else None,
            'last_sale_date': pd.to_datetime(row['LS_DATE'], format='%Y%m%d').date() if pd.notna(row['LS_DATE']) else None,
            'last_sale_price': row['LS_PRICE'] if pd.notna(row['LS_PRICE']) else None,
            'use_code': row['USE_CODE'] if pd.notna(row['USE_CODE']) else ''
        })
        
        # Ownership data
        ownership_data.append({
            'parcel_id': row['PROP_ID'],
            'owner_name': row['OWNER1'] if pd.notna(row['OWNER1']) else '',
            'owner_address': row['OWN_ADDR'] if pd.notna(row['OWN_ADDR']) else '',
            'owner_city': row['OWN_CITY'] if pd.notna(row['OWN_CITY']) else '',
            'owner_state': row['OWN_STATE'] if pd.notna(row['OWN_STATE']) else '',
            'owner_zip': str(row['OWN_ZIP']) if pd.notna(row['OWN_ZIP']) else '',
            'owner_country': row['OWN_CO'] if pd.notna(row['OWN_CO']) else '',
            'last_sale_book': row['LS_BOOK'] if pd.notna(row['LS_BOOK']) else '',
            'last_sale_page': row['LS_PAGE'] if pd.notna(row['LS_PAGE']) else '',
            'registration_id': row['REG_ID'] if pd.notna(row['REG_ID']) else ''
        })
    
    return properties_data, assessments_data, ownership_data

def load_analysis_data():
    """Load analysis data from CSV files"""
    print("📈 Loading analysis data...")
    
    # Ward analysis
    ward_analysis = []
    if os.path.exists('../data/processed/ward_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/ward_elderly_analysis.csv')
        for _, row in df.iterrows():
            ward_analysis.append({
                'ward_id': row['Ward'],
                'elderly_count': row['Elderly_Count'],
                'mean_age': row['Mean_Age'],
                'median_age': row['Median_Age'],
                'min_age': row['Min_Age'],
                'max_age': row['Max_Age']
            })
    
    # Precinct analysis
    precinct_analysis = []
    if os.path.exists('../data/processed/precinct_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/precinct_elderly_analysis.csv')
        for _, row in df.iterrows():
            precinct_analysis.append({
                'ward_id': row['Ward'],
                'precinct_id': row['Precinct'],
                'elderly_count': row['Elderly_Count'],
                'mean_age': row['Mean_Age']
            })
    
    # Street analysis
    street_analysis = []
    if os.path.exists('../data/processed/street_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/street_elderly_analysis.csv')
        for _, row in df.iterrows():
            street_analysis.append({
                'street_name': row['Street Name'],
                'ward_id': row['Ward'],
                'elderly_count': row['Elderly_Count'],
                'mean_age': row['Mean_Age']
            })
    
    return ward_analysis, precinct_analysis, street_analysis

def insert_data(conn, table_name, data, columns):
    """Insert data into database"""
    if not data:
        return
    
    cursor = conn.cursor()
    
    # Create placeholders for the values
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    
    # Prepare the insert statement
    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    # Convert data to list of tuples
    values = []
    for row in data:
        values.append(tuple(row[col] for col in columns))
    
    try:
        cursor.executemany(insert_sql, values)
        conn.commit()
        print(f"✅ Inserted {len(values)} records into {table_name}")
    except Exception as e:
        print(f"❌ Error inserting into {table_name}: {e}")
        conn.rollback()

def main():
    """Main function to load all data"""
    print("🚀 Starting data loading process...")
    
    try:
        # Connect to database
        conn = psycopg.connect(**DB_CONFIG)
        print("✅ Connected to database")
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM street_elderly_analysis")
        cursor.execute("DELETE FROM precinct_elderly_analysis") 
        cursor.execute("DELETE FROM ward_elderly_analysis")
        cursor.execute("DELETE FROM property_ownership")
        cursor.execute("DELETE FROM property_assessments")
        cursor.execute("DELETE FROM parcels")
        cursor.execute("DELETE FROM voters")
        conn.commit()
        print("✅ Cleared existing data")
        
        # Load voters
        voters_data = load_voters()
        if voters_data:
            insert_data(conn, 'voters', voters_data, [
                'res_id', 'last_name', 'first_name', 'date_of_birth', 'occupation',
                'street_number', 'street_suffix', 'street_name', 'apartment', 'zip_code',
                'ward_id', 'precinct_id', 'full_address', 'normalized_address',
                'latitude', 'longitude', 'is_elderly', 'age'
            ])
        
        # Load properties
        properties_data, assessments_data, ownership_data = load_properties()
        if properties_data:
            insert_data(conn, 'parcels', properties_data, [
                'parcel_id', 'prop_id', 'loc_id', 'site_address', 'addr_num',
                'full_street', 'location', 'city', 'zip_code', 'zoning',
                'year_built', 'building_area', 'lot_size', 'units', 'residential_area',
                'style', 'num_rooms', 'lot_units', 'stories_num', 'stories',
                'latitude', 'longitude'
            ])
        
        if assessments_data:
            insert_data(conn, 'property_assessments', assessments_data, [
                'parcel_id', 'fiscal_year', 'building_value', 'land_value', 'other_value',
                'total_value', 'last_sale_date', 'last_sale_price', 'use_code'
            ])
        
        if ownership_data:
            insert_data(conn, 'property_ownership', ownership_data, [
                'parcel_id', 'owner_name', 'owner_address', 'owner_city', 'owner_state',
                'owner_zip', 'owner_country', 'last_sale_book', 'last_sale_page', 'registration_id'
            ])
        
        # Load analysis data
        ward_analysis, precinct_analysis, street_analysis = load_analysis_data()
        
        if ward_analysis:
            insert_data(conn, 'ward_elderly_analysis', ward_analysis, [
                'ward_id', 'elderly_count', 'mean_age', 'median_age', 'min_age', 'max_age'
            ])
        
        if precinct_analysis:
            insert_data(conn, 'precinct_elderly_analysis', precinct_analysis, [
                'ward_id', 'precinct_id', 'elderly_count', 'mean_age'
            ])
        
        if street_analysis:
            insert_data(conn, 'street_elderly_analysis', street_analysis, [
                'street_name', 'ward_id', 'elderly_count', 'mean_age'
            ])
        
        # Get final counts
        cursor.execute("SELECT COUNT(*) FROM voters")
        voter_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parcels")
        property_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM property_assessments")
        assessment_count = cursor.fetchone()[0]
        
        print(f"\n🎉 Data loading completed successfully!")
        print(f"📊 Voters: {voter_count}")
        print(f"🏠 Properties: {property_count}")
        print(f"💰 Assessments: {assessment_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
