#!/usr/bin/env python3
"""
Script to create the buildings table and load data
"""

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

def create_buildings_table():
    """Create the buildings table"""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Creating buildings table...")
        
        # Create the buildings table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS buildings (
            struct_id VARCHAR(50) PRIMARY KEY,
            parcel_id VARCHAR(50),
            suffix VARCHAR(10),
            pid VARCHAR(50),
            st_num VARCHAR(20),
            st_num2 VARCHAR(20),
            st_name VARCHAR(100),
            unit_num VARCHAR(20),
            city VARCHAR(50),
            zip_code VARCHAR(10),
            owner_occ VARCHAR(10),
            owner VARCHAR(200),
            mail_addressee VARCHAR(200),
            mail_street_address VARCHAR(200),
            mail_city VARCHAR(50),
            mail_state VARCHAR(50),
            mail_zip_code VARCHAR(10),
            bldg_type VARCHAR(50),
            total_value DECIMAL(12,2),
            gross_tax DECIMAL(12,2),
            yr_built INTEGER,
            yr_remodel INTEGER,
            structure_class VARCHAR(50),
            bed_rms DECIMAL(5,1),
            full_bth DECIMAL(5,1),
            hlf_bth DECIMAL(5,1),
            kitchens DECIMAL(5,1),
            tt_rms DECIMAL(5,1),
            res_units INTEGER,
            com_units INTEGER,
            rc_units INTEGER,
            land_sf DECIMAL(12,2),
            gross_area DECIMAL(12,2),
            living_area DECIMAL(12,2),
            land_value DECIMAL(12,2),
            bldg_value DECIMAL(12,2),
            sfyi_value DECIMAL(12,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        
        # Create indexes
        print("Creating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_buildings_parcel ON buildings (parcel_id);",
            "CREATE INDEX IF NOT EXISTS idx_buildings_owner ON buildings (owner);",
            "CREATE INDEX IF NOT EXISTS idx_buildings_address ON buildings (st_name, st_num);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        conn.close()
        
        print("✅ Buildings table created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating buildings table: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Main function to create table and load data"""
    print("Setting up buildings table and loading data...")
    print("=" * 60)
    
    # Step 1: Create the table
    if not create_buildings_table():
        print("Failed to create buildings table. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Now loading buildings data...")
    
    # Step 2: Load the data
    try:
        # Import and run the data loader
        from load_buildings_data import load_buildings_data
        success = load_buildings_data()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 Setup complete! Buildings data loaded successfully!")
            print("\nYou can now:")
            print("1. Start the Flask app: python app.py")
            print("2. Visit http://localhost:5000/buildings to view the data")
        else:
            print("\n❌ Failed to load buildings data")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
