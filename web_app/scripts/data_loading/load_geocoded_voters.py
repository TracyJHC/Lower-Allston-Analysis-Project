#!/usr/bin/env python3
"""
Load geocoded voter data into the database
"""

import psycopg
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            dbname=os.getenv('DB_NAME', 'abcdc_spatial'),
            user=os.getenv('DB_USER', 'Studies'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def load_geocoded_voters():
    """Load geocoded voter data from CSV into database"""
    print("📊 Loading geocoded voter data...")
    
    # Load the geocoded data
    df = pd.read_csv('../data/processed/voter_data/homeowners_geocoded.csv')
    
    # Calculate age and elderly status
    df['DOB'] = pd.to_datetime(df['DOB'])
    df['age'] = (pd.Timestamp.now() - df['DOB']).dt.days // 365
    df['is_elderly'] = df['age'] >= 62
    
    print(f"Total geocoded voters: {len(df)}")
    print(f"Elderly voters (62+): {df['is_elderly'].sum()}")
    print(f"Voters with coordinates: {df['latitude'].notna().sum()}")
    
    conn = get_db_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Update existing voters with geocoded data
        updated_count = 0
        for _, row in df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                try:
                    cursor.execute("""
                        UPDATE voters 
                        SET latitude = %s, longitude = %s
                        WHERE res_id = %s
                    """, (row['latitude'], row['longitude'], row['Res ID']))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Error updating voter {row['Res ID']}: {e}")
                    continue
        
        conn.commit()
        print(f"✅ Updated {updated_count} voters with geocoded coordinates")
        
        # Verify the update
        cursor.execute("""
            SELECT COUNT(*) FROM voters 
            WHERE is_elderly = true 
            AND latitude IS NOT NULL 
            AND longitude IS NOT NULL
        """)
        geocoded_elderly = cursor.fetchone()[0]
        print(f"✅ Elderly voters with coordinates: {geocoded_elderly}")
        
    except Exception as e:
        print(f"❌ Error loading geocoded data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    load_geocoded_voters()
