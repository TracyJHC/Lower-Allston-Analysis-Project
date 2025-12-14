#!/usr/bin/env python3
"""
Create a clean, properly structured dataset from scraped parcel data
"""

import pandas as pd
import numpy as np
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_currency_value(value: str) -> Optional[float]:
    """
    Clean currency values by removing $ and commas, converting to float
    """
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    # Remove $ and commas, handle negative values
    cleaned = str(value).replace('$', '').replace(',', '').strip()
    
    # Handle empty strings after cleaning
    if cleaned == '' or cleaned == 'nan':
        return None
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert currency value: {value}")
        return None

def clean_sqft_value(value: str) -> Optional[float]:
    """
    Clean square footage values by removing 'sq ft' and commas
    """
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    # Remove 'sq ft' and commas
    cleaned = str(value).replace('sq ft', '').replace(',', '').strip()
    
    if cleaned == '' or cleaned == 'nan':
        return None
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert sqft value: {value}")
        return None

def clean_numeric_value(value: str) -> Optional[float]:
    """
    Clean general numeric values by removing commas
    """
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    cleaned = str(value).replace(',', '').strip()
    
    if cleaned == '' or cleaned == 'nan':
        return None
    
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert numeric value: {value}")
        return None

def clean_boolean_value(value: str) -> Optional[bool]:
    """
    Clean boolean values (Yes/No -> True/False)
    """
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    cleaned = str(value).strip().lower()
    
    if cleaned in ['yes', 'y', 'true', '1']:
        return True
    elif cleaned in ['no', 'n', 'false', '0']:
        return False
    else:
        logger.warning(f"Could not convert boolean value: {value}")
        return None

def clean_year_value(value: str) -> Optional[int]:
    """
    Clean year values
    """
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    cleaned = str(value).strip()
    
    if cleaned == '' or cleaned == 'nan':
        return None
    
    try:
        year = int(float(cleaned))
        # Basic validation for reasonable year range
        if 1800 <= year <= 2030:
            return year
        else:
            logger.warning(f"Year value out of reasonable range: {year}")
            return None
    except (ValueError, TypeError):
        logger.warning(f"Could not convert year value: {value}")
        return None

def parse_value_history(value_history_str: str) -> Optional[Dict]:
    """
    Parse the value history JSON string into a structured format
    """
    if pd.isna(value_history_str) or value_history_str == '' or value_history_str == 'nan':
        return None
    
    try:
        # Parse the JSON string
        history_data = json.loads(value_history_str)
        
        # Extract key metrics
        if not history_data or len(history_data) == 0:
            return None
        
        # Get the most recent values
        latest = history_data[0] if history_data else {}
        
        # Calculate some derived metrics
        values = []
        for entry in history_data:
            if 'assessed_value' in entry:
                val = clean_currency_value(entry['assessed_value'])
                if val is not None:
                    values.append(val)
        
        if not values:
            return None
        
        return {
            'latest_assessed_value': clean_currency_value(latest.get('assessed_value', '')),
            'latest_property_type': latest.get('property_type', ''),
            'latest_fiscal_year': latest.get('fiscal_year', ''),
            'value_trend_5yr': calculate_value_trend(values[:5]) if len(values) >= 5 else None,
            'value_trend_10yr': calculate_value_trend(values[:10]) if len(values) >= 10 else None,
            'max_value': max(values),
            'min_value': min(values),
            'value_volatility': np.std(values) if len(values) > 1 else 0,
            'years_of_data': len(values)
        }
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning(f"Could not parse value history: {e}")
        return None

def calculate_value_trend(values: list) -> Optional[float]:
    """
    Calculate percentage change from first to last value
    """
    if len(values) < 2:
        return None
    
    first_val = values[-1]  # First chronologically (oldest)
    last_val = values[0]    # Last chronologically (newest)
    
    if first_val == 0:
        return None
    
    return ((last_val - first_val) / first_val) * 100

def parse_owners_list(owners_str: str) -> Optional[Dict]:
    """
    Parse the current owners list JSON string
    """
    if pd.isna(owners_str) or owners_str == '' or owners_str == 'nan':
        return None
    
    try:
        # Parse the JSON string
        owners_data = json.loads(owners_str)
        
        if not owners_data or len(owners_data) == 0:
            return None
        
        # Extract owner information
        owners = []
        for owner in owners_data:
            if isinstance(owner, str) and owner.strip():
                owners.append(owner.strip())
        
        return {
            'owner_count': len(owners),
            'primary_owner': owners[0] if owners else None,
            'all_owners': owners
        }
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.warning(f"Could not parse owners list: {e}")
        return None

def clean_parcel_dataset(input_file: str, output_file: str) -> pd.DataFrame:
    """
    Clean and structure the scraped parcel dataset
    """
    logger.info(f"🚀 Starting dataset cleaning from {input_file}")
    
    # Load the raw data
    logger.info("📊 Loading raw data...")
    df = pd.read_csv(input_file)
    logger.info(f"📊 Loaded {len(df):,} records")
    
    # Create a copy for cleaning
    clean_df = df.copy()
    
    # Basic info
    logger.info("🔍 Dataset overview:")
    logger.info(f"   - Total records: {len(clean_df):,}")
    logger.info(f"   - Successfully scraped: {clean_df['scraped_successfully'].sum():,}")
    logger.info(f"   - Failed scrapes: {(~clean_df['scraped_successfully']).sum():,}")
    
    # Filter to only successfully scraped records
    clean_df = clean_df[clean_df['scraped_successfully'] == True].copy()
    logger.info(f"📊 Working with {len(clean_df):,} successfully scraped records")
    
    # Clean basic identifiers
    logger.info("🧹 Cleaning basic identifiers...")
    clean_df['parcel_id'] = clean_df['parcel_id'].astype(str)
    clean_df['parcel_id_display'] = clean_df['parcel_id_display'].astype(str)
    
    # Clean owner information
    logger.info("🧹 Cleaning owner information...")
    clean_df['owner_name'] = clean_df['owner_name'].fillna('Unknown')
    clean_df['owner_mailing_address'] = clean_df['owner_mailing_address'].fillna('Unknown')
    
    # Clean property information
    logger.info("🧹 Cleaning property information...")
    clean_df['property_type'] = clean_df['property_type'].fillna('Unknown')
    clean_df['classification_code'] = clean_df['classification_code'].fillna('Unknown')
    clean_df['address'] = clean_df['address'].fillna('Unknown')
    
    # Clean lot and living area (square footage)
    logger.info("🧹 Cleaning area measurements...")
    clean_df['lot_size_sqft'] = clean_df['lot_size'].apply(clean_sqft_value)
    clean_df['living_area_sqft'] = clean_df['living_area'].apply(clean_sqft_value)
    
    # Clean year built
    logger.info("🧹 Cleaning year built...")
    clean_df['year_built'] = clean_df['year_built'].apply(clean_year_value)
    
    # Clean financial values
    logger.info("🧹 Cleaning financial values...")
    financial_columns = [
        'fy2025_building_value', 'fy2025_land_value', 'fy2025_total_assessed_value',
        'estimated_tax', 'community_preservation', 'total_first_half_tax'
    ]
    
    for col in financial_columns:
        clean_df[f'{col}_numeric'] = clean_df[col].apply(clean_currency_value)
    
    # Clean tax rates
    logger.info("🧹 Cleaning tax rates...")
    clean_df['residential_tax_rate_numeric'] = clean_df['residential_tax_rate'].apply(clean_currency_value)
    clean_df['commercial_tax_rate_numeric'] = clean_df['commercial_tax_rate'].apply(clean_currency_value)
    
    # Clean boolean fields
    logger.info("🧹 Cleaning boolean fields...")
    clean_df['residential_exemption_bool'] = clean_df['residential_exemption'].apply(clean_boolean_value)
    clean_df['personal_exemption_bool'] = clean_df['personal_exemption'].apply(clean_boolean_value)
    
    # Clean building characteristics
    logger.info("🧹 Cleaning building characteristics...")
    building_columns = [
        'total_rooms', 'bedrooms', 'bathrooms', 'half_bathrooms', 'kitchens',
        'fireplaces', 'parking_spots', 'story_height'
    ]
    
    for col in building_columns:
        clean_df[f'{col}_numeric'] = clean_df[col].apply(clean_numeric_value)
    
    # Clean categorical building features
    categorical_columns = [
        'land_use', 'building_style', 'kitchen_type', 'ac_type', 'heat_type',
        'interior_condition', 'interior_finish', 'view', 'grade',
        'roof_cover', 'roof_structure', 'exterior_finish', 'exterior_condition',
        'foundation', 'outbuilding_type', 'outbuilding_quality', 'outbuilding_condition'
    ]
    
    for col in categorical_columns:
        clean_df[col] = clean_df[col].fillna('Unknown')
    
    # Clean outbuilding size
    clean_df['outbuilding_size_numeric'] = clean_df['outbuilding_size'].apply(clean_sqft_value)
    
    # Parse complex JSON fields
    logger.info("🧹 Parsing complex JSON fields...")
    
    # Parse value history
    clean_df['value_history_parsed'] = clean_df['value_history'].apply(parse_value_history)
    
    # Parse owners list
    clean_df['owners_parsed'] = clean_df['current_owners_list'].apply(parse_owners_list)
    
    # Extract key metrics from parsed data
    logger.info("🧹 Extracting key metrics from parsed data...")
    
    # Value history metrics
    clean_df['latest_assessed_value'] = clean_df['value_history_parsed'].apply(
        lambda x: x['latest_assessed_value'] if x and 'latest_assessed_value' in x else None
    )
    clean_df['value_trend_5yr'] = clean_df['value_history_parsed'].apply(
        lambda x: x['value_trend_5yr'] if x and 'value_trend_5yr' in x else None
    )
    clean_df['value_trend_10yr'] = clean_df['value_history_parsed'].apply(
        lambda x: x['value_trend_10yr'] if x and 'value_trend_10yr' in x else None
    )
    clean_df['value_volatility'] = clean_df['value_history_parsed'].apply(
        lambda x: x['value_volatility'] if x and 'value_volatility' in x else None
    )
    clean_df['years_of_data'] = clean_df['value_history_parsed'].apply(
        lambda x: x['years_of_data'] if x and 'years_of_data' in x else None
    )
    
    # Owner metrics
    clean_df['owner_count'] = clean_df['owners_parsed'].apply(
        lambda x: x['owner_count'] if x and 'owner_count' in x else None
    )
    clean_df['primary_owner'] = clean_df['owners_parsed'].apply(
        lambda x: x['primary_owner'] if x and 'primary_owner' in x else None
    )
    
    # Clean timestamps
    logger.info("🧹 Cleaning timestamps...")
    clean_df['scrape_timestamp'] = pd.to_datetime(clean_df['scrape_timestamp'], errors='coerce')
    clean_df['assessment_date'] = pd.to_datetime(clean_df['assessment_date'], errors='coerce')
    
    # Create derived features
    logger.info("🧹 Creating derived features...")
    
    # Property age
    current_year = datetime.now().year
    clean_df['property_age'] = current_year - clean_df['year_built']
    clean_df['property_age'] = clean_df['property_age'].apply(lambda x: x if x >= 0 else None)
    
    # Value per square foot
    clean_df['value_per_sqft'] = clean_df['fy2025_total_assessed_value_numeric'] / clean_df['living_area_sqft']
    clean_df['value_per_sqft'] = clean_df['value_per_sqft'].replace([np.inf, -np.inf], np.nan)
    
    # Lot efficiency (living area / lot size)
    clean_df['lot_efficiency'] = clean_df['living_area_sqft'] / clean_df['lot_size_sqft']
    clean_df['lot_efficiency'] = clean_df['lot_efficiency'].replace([np.inf, -np.inf], np.nan)
    
    # Property type categories
    clean_df['is_residential'] = clean_df['property_type'].str.contains('Family|Condominium|Apartment', case=False, na=False)
    clean_df['is_commercial'] = clean_df['property_type'].str.contains('Commercial|Office|Retail|Industrial', case=False, na=False)
    clean_df['is_exempt'] = clean_df['property_type'].str.contains('Exempt', case=False, na=False)
    
    # Select final columns for the clean dataset
    logger.info("🧹 Selecting final columns...")
    
    final_columns = [
        # Identifiers
        'parcel_id', 'parcel_id_display', 'address',
        
        # Owner information
        'owner_name', 'owner_mailing_address', 'owner_count', 'primary_owner',
        
        # Property basics
        'property_type', 'classification_code', 'is_residential', 'is_commercial', 'is_exempt',
        'year_built', 'property_age',
        
        # Physical characteristics
        'lot_size_sqft', 'living_area_sqft', 'value_per_sqft', 'lot_efficiency',
        'land_use', 'building_style',
        
        # Building details
        'total_rooms_numeric', 'bedrooms_numeric', 'bathrooms_numeric', 'half_bathrooms_numeric',
        'kitchens_numeric', 'kitchen_type', 'fireplaces_numeric', 'parking_spots_numeric',
        'story_height_numeric',
        
        # Building features
        'ac_type', 'heat_type', 'interior_condition', 'interior_finish',
        'view', 'grade', 'roof_cover', 'roof_structure',
        'exterior_finish', 'exterior_condition', 'foundation',
        
        # Outbuildings
        'outbuilding_type', 'outbuilding_size_numeric', 'outbuilding_quality', 'outbuilding_condition',
        
        # Financial information
        'fy2025_building_value_numeric', 'fy2025_land_value_numeric', 'fy2025_total_assessed_value_numeric',
        'residential_tax_rate_numeric', 'commercial_tax_rate_numeric',
        'estimated_tax_numeric', 'community_preservation_numeric', 'total_first_half_tax_numeric',
        
        # Exemptions
        'residential_exemption_bool', 'personal_exemption_bool',
        
        # Value history
        'latest_assessed_value', 'value_trend_5yr', 'value_trend_10yr', 'value_volatility', 'years_of_data',
        
        # Metadata
        'scrape_timestamp', 'assessment_date', 'exemption_notes'
    ]
    
    # Create the final clean dataset
    clean_final_df = clean_df[final_columns].copy()
    
    # Generate data quality report
    logger.info("📊 Generating data quality report...")
    
    quality_report = {
        'total_records': len(clean_final_df),
        'completeness_by_column': {},
        'data_types': {},
        'missing_data_summary': {}
    }
    
    for col in clean_final_df.columns:
        non_null_count = clean_final_df[col].notna().sum()
        completeness = (non_null_count / len(clean_final_df)) * 100
        quality_report['completeness_by_column'][col] = {
            'non_null_count': non_null_count,
            'completeness_pct': round(completeness, 2),
            'data_type': str(clean_final_df[col].dtype)
        }
    
    # Save the clean dataset
    logger.info(f"💾 Saving clean dataset to {output_file}")
    clean_final_df.to_csv(output_file, index=False)
    
    # Save quality report
    quality_report_file = output_file.replace('.csv', '_quality_report.json')
    with open(quality_report_file, 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        quality_report_serializable = convert_numpy_types(quality_report)
        json.dump(quality_report_serializable, f, indent=2)
    
    # Print summary
    logger.info("✅ Dataset cleaning completed!")
    logger.info(f"📊 Final dataset: {len(clean_final_df):,} records")
    logger.info(f"💾 Saved to: {output_file}")
    logger.info(f"📋 Quality report: {quality_report_file}")
    
    # Print completeness summary
    logger.info("📊 Data completeness summary:")
    for col, stats in quality_report['completeness_by_column'].items():
        if stats['completeness_pct'] < 50:  # Only show columns with < 50% completeness
            logger.info(f"   - {col}: {stats['completeness_pct']:.1f}% complete")
    
    return clean_final_df

def main():
    """
    Main function to run the dataset cleaning process
    """
    input_file = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/parcel_scraping_progress.csv'
    output_file = '/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/all_parcels_clean_dataset.csv'
    
    try:
        clean_df = clean_parcel_dataset(input_file, output_file)
        logger.info("🎉 Dataset cleaning completed successfully!")
        
        # Show sample of the clean data
        logger.info("📋 Sample of clean data:")
        print(clean_df.head())
        
        return clean_df
        
    except Exception as e:
        logger.error(f"❌ Error during dataset cleaning: {e}")
        raise

if __name__ == "__main__":
    main()
