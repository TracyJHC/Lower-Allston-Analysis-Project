#!/usr/bin/env python3
"""
Load real Allston-Brighton data into the database (Fixed version)
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

def setup_precincts_and_wards(conn):
    """Create wards and precincts from the actual data"""
    print("🗺️ Setting up wards and precincts...")
    
    cursor = conn.cursor()
    
    # Clear existing data in correct order
    cursor.execute("DELETE FROM street_elderly_analysis")
    cursor.execute("DELETE FROM precinct_elderly_analysis")
    cursor.execute("DELETE FROM ward_elderly_analysis")
    cursor.execute("DELETE FROM property_ownership")
    cursor.execute("DELETE FROM property_assessments")
    cursor.execute("DELETE FROM parcels")
    cursor.execute("DELETE FROM voters")
    cursor.execute("DELETE FROM precincts")
    cursor.execute("DELETE FROM wards")
    
    # Insert wards
    cursor.execute("INSERT INTO wards (ward_id, ward_name) VALUES (21, 'Allston'), (22, 'Brighton')")
    
    # Get unique precincts from voter data
    df = pd.read_csv('../data/processed/voter_list_cleaned.csv')
    unique_precincts = df[['Ward', 'Precinct']].drop_duplicates()
    
    for _, row in unique_precincts.iterrows():
        cursor.execute(
            "INSERT INTO precincts (precinct_id, ward_id, precinct_name) VALUES (%s, %s, %s) ON CONFLICT (precinct_id) DO NOTHING",
            (row['Precinct'], row['Ward'], f"Precinct {row['Precinct']}")
        )
    
    conn.commit()
    print(f"✅ Created {len(unique_precincts)} precincts")

def load_voters(conn):
    """Load voter data from CSV"""
    print("📊 Loading voters...")
    
    # Read the cleaned voter data
    df = pd.read_csv('../data/processed/voter_list_cleaned.csv')
    
    # Calculate age and elderly status
    df['date_of_birth'] = pd.to_datetime(df['DOB'])
    df['age'] = (pd.Timestamp.now() - df['date_of_birth']).dt.days // 365
    df['is_elderly'] = df['age'] >= 62
    
    cursor = conn.cursor()
    
    # Clear existing voters
    cursor.execute("DELETE FROM voters")
    
    # Insert voters in batches
    batch_size = 1000
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        for _, row in batch.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO voters (res_id, last_name, first_name, date_of_birth, occupation,
                                     street_number, street_suffix, street_name, apartment, zip_code,
                                     ward_id, precinct_id, full_address, normalized_address,
                                     latitude, longitude, is_elderly, age)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row['Res ID'],
                    row['Last Name'],
                    row['First Name'],
                    row['date_of_birth'].date(),
                    row['Occupation'],
                    row['Street .'] if pd.notna(row['Street .']) else None,
                    row['Sffx'] if pd.notna(row['Sffx']) else '',
                    row['Street Name'],
                    row['Apt .'] if pd.notna(row['Apt .']) else '',
                    str(row['Zip']),
                    row['Ward'],
                    row['Precinct'],
                    f"{row['Street .']} {row['Street Name']}",
                    f"{row['Street .']} {row['Street Name']}, Boston, MA {row['Zip']}",
                    None,  # latitude
                    None,  # longitude
                    row['is_elderly'],
                    row['age']
                ))
            except Exception as e:
                print(f"⚠️ Skipping voter {row['Res ID']}: {e}")
                continue
        
        conn.commit()
        print(f"✅ Processed {min(i + batch_size, len(df))} voters...")
    
    print(f"✅ Loaded voters successfully")

def load_properties(conn):
    """Load property assessment data"""
    print("🏠 Loading properties...")
    
    df = pd.read_csv('../data/processed/gis_layers/allston_brighton_assessments.csv')
    
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM property_ownership")
    cursor.execute("DELETE FROM property_assessments")
    cursor.execute("DELETE FROM parcels")
    
    # Process properties in batches
    batch_size = 500
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        
        for _, row in batch.iterrows():
            try:
                # Insert property
                cursor.execute("""
                    INSERT INTO parcels (parcel_id, prop_id, loc_id, site_address, addr_num,
                                       full_street, location, city, zip_code, zoning,
                                       year_built, building_area, lot_size, units, residential_area,
                                       style, num_rooms, lot_units, stories_num, stories,
                                       latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(row['PROP_ID']),
                    str(row['PROP_ID']),
                    row['LOC_ID'] if pd.notna(row['LOC_ID']) else None,
                    row['SITE_ADDR'] if pd.notna(row['SITE_ADDR']) else '',
                    int(row['ADDR_NUM']) if pd.notna(row['ADDR_NUM']) and str(row['ADDR_NUM']).replace(' ', '').isdigit() else None,
                    row['FULL_STR'] if pd.notna(row['FULL_STR']) else '',
                    row['LOCATION'] if pd.notna(row['LOCATION']) else '',
                    row['CITY'] if pd.notna(row['CITY']) else '',
                    str(row['ZIP']) if pd.notna(row['ZIP']) else '',
                    row['ZONING'] if pd.notna(row['ZONING']) else '',
                    int(row['YEAR_BUILT']) if pd.notna(row['YEAR_BUILT']) else None,
                    float(row['BLD_AREA']) if pd.notna(row['BLD_AREA']) else None,
                    float(row['LOT_SIZE']) if pd.notna(row['LOT_SIZE']) else None,
                    int(row['UNITS']) if pd.notna(row['UNITS']) else None,
                    float(row['RES_AREA']) if pd.notna(row['RES_AREA']) else None,
                    row['STYLE'] if pd.notna(row['STYLE']) else '',
                    float(row['NUM_ROOMS']) if pd.notna(row['NUM_ROOMS']) else None,
                    row['LOT_UNITS'] if pd.notna(row['LOT_UNITS']) else '',
                    int(row['STORIES_NUM']) if pd.notna(row['STORIES_NUM']) else None,
                    row['STORIES'] if pd.notna(row['STORIES']) else '',
                    None,  # latitude
                    None   # longitude
                ))
                
                # Insert assessment
                cursor.execute("""
                    INSERT INTO property_assessments (parcel_id, fiscal_year, building_value, land_value, other_value,
                                                   total_value, last_sale_date, last_sale_price, use_code)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(row['PROP_ID']),
                    int(row['FY']) if pd.notna(row['FY']) else None,
                    float(row['BLDG_VAL']) if pd.notna(row['BLDG_VAL']) else None,
                    float(row['LAND_VAL']) if pd.notna(row['LAND_VAL']) else None,
                    float(row['OTHER_VAL']) if pd.notna(row['OTHER_VAL']) else None,
                    float(row['TOTAL_VAL']) if pd.notna(row['TOTAL_VAL']) else None,
                    pd.to_datetime(row['LS_DATE'], format='%Y%m%d').date() if pd.notna(row['LS_DATE']) else None,
                    float(row['LS_PRICE']) if pd.notna(row['LS_PRICE']) else None,
                    row['USE_CODE'] if pd.notna(row['USE_CODE']) else ''
                ))
                
                # Insert ownership
                cursor.execute("""
                    INSERT INTO property_ownership (parcel_id, owner_name, owner_address, owner_city, owner_state,
                                                  owner_zip, owner_country, last_sale_book, last_sale_page, registration_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(row['PROP_ID']),
                    row['OWNER1'] if pd.notna(row['OWNER1']) else '',
                    row['OWN_ADDR'] if pd.notna(row['OWN_ADDR']) else '',
                    row['OWN_CITY'] if pd.notna(row['OWN_CITY']) else '',
                    row['OWN_STATE'] if pd.notna(row['OWN_STATE']) else '',
                    str(row['OWN_ZIP']) if pd.notna(row['OWN_ZIP']) else '',
                    row['OWN_CO'] if pd.notna(row['OWN_CO']) else '',
                    row['LS_BOOK'] if pd.notna(row['LS_BOOK']) else '',
                    row['LS_PAGE'] if pd.notna(row['LS_PAGE']) else '',
                    row['REG_ID'] if pd.notna(row['REG_ID']) else ''
                ))
                
            except Exception as e:
                print(f"⚠️ Skipping property {row['PROP_ID']}: {e}")
                continue
        
        conn.commit()
        print(f"✅ Processed {min(i + batch_size, len(df))} properties...")
    
    print(f"✅ Loaded properties successfully")

def load_analysis_data(conn):
    """Load analysis data from CSV files"""
    print("📈 Loading analysis data...")
    
    cursor = conn.cursor()
    
    # Clear existing analysis data
    cursor.execute("DELETE FROM street_elderly_analysis")
    cursor.execute("DELETE FROM precinct_elderly_analysis")
    cursor.execute("DELETE FROM ward_elderly_analysis")
    
    # Ward analysis
    if os.path.exists('../data/processed/ward_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/ward_elderly_analysis.csv')
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO ward_elderly_analysis (ward_id, elderly_count, mean_age, median_age, min_age, max_age)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (row['Ward'], row['Elderly_Count'], row['Mean_Age'], row['Median_Age'], row['Min_Age'], row['Max_Age']))
            except Exception as e:
                print(f"⚠️ Skipping ward analysis: {e}")
        print("✅ Loaded ward analysis")
    
    # Precinct analysis
    if os.path.exists('../data/processed/precinct_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/precinct_elderly_analysis.csv')
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO precinct_elderly_analysis (ward_id, precinct_id, elderly_count, mean_age)
                    VALUES (%s, %s, %s, %s)
                """, (row['Ward'], row['Precinct'], row['Elderly_Count'], row['Mean_Age']))
            except Exception as e:
                print(f"⚠️ Skipping precinct analysis: {e}")
        print("✅ Loaded precinct analysis")
    
    # Street analysis
    if os.path.exists('../data/processed/street_elderly_analysis.csv'):
        df = pd.read_csv('../data/processed/street_elderly_analysis.csv')
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO street_elderly_analysis (street_name, ward_id, elderly_count, mean_age)
                    VALUES (%s, %s, %s, %s)
                """, (row['Street Name'], row['Ward'], row['Elderly_Count'], row['Mean_Age']))
            except Exception as e:
                print(f"⚠️ Skipping street analysis: {e}")
        print("✅ Loaded street analysis")
    
    conn.commit()

def main():
    """Main function to load all data"""
    print("🚀 Starting data loading process...")
    
    try:
        # Connect to database
        conn = psycopg.connect(**DB_CONFIG)
        print("✅ Connected to database")
        
        # Setup wards and precincts first
        setup_precincts_and_wards(conn)
        
        # Load all data
        load_voters(conn)
        load_properties(conn)
        load_analysis_data(conn)
        
        # Get final counts
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM voters")
        voter_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parcels")
        property_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM property_assessments")
        assessment_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM precincts")
        precinct_count = cursor.fetchone()[0]
        
        print(f"\n🎉 Data loading completed successfully!")
        print(f"📊 Voters: {voter_count}")
        print(f"🏠 Properties: {property_count}")
        print(f"💰 Assessments: {assessment_count}")
        print(f"🗺️ Precincts: {precinct_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
