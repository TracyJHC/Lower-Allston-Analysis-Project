#!/usr/bin/env python3
"""
Explore the L3_ASSESS layer to understand how it links to structures.

This script examines the L3_ASSESS layer in the parcels database to see
if it contains the assessment data and how it connects to STRUCT_ID.

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def explore_l3_assess():
    """
    Explore the L3_ASSESS layer to understand its structure and connections.
    """
    logger.info("="*60)
    logger.info("EXPLORING L3_ASSESS LAYER")
    logger.info("="*60)
    
    # Path to the parcels database
    parcels_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_L3_Parcels.gdb")
    
    if not parcels_gdb.exists():
        logger.error("Parcels database not found!")
        return None
    
    try:
        logger.info("Loading L3_ASSESS layer...")
        assess = gpd.read_file(parcels_gdb, layer='L3_ASSESS')
        logger.info(f"Loaded {len(assess):,} assessment records")
        
        # Show basic info
        logger.info(f"Columns: {list(assess.columns)}")
        logger.info(f"Shape: {assess.shape}")
        
        # Show first few rows
        logger.info("\nFirst 3 rows:")
        for i, row in assess.head(3).iterrows():
            logger.info(f"Row {i}: {dict(row)}")
        
        # Check for STRUCT_ID references
        struct_columns = [col for col in assess.columns if 'STRUCT' in col.upper()]
        if struct_columns:
            logger.info(f"\nFound STRUCT-related columns: {struct_columns}")
        else:
            logger.info("\nNo STRUCT_ID columns found in L3_ASSESS")
        
        # Check for property ID references
        prop_columns = [col for col in assess.columns if 'PROP' in col.upper() or 'PAR' in col.upper()]
        if prop_columns:
            logger.info(f"Found property-related columns: {prop_columns}")
        
        # Check for parcel ID references
        parcel_columns = [col for col in assess.columns if 'MAP_PAR' in col.upper()]
        if parcel_columns:
            logger.info(f"Found parcel-related columns: {parcel_columns}")
        
        # Show unique values for key columns
        for col in assess.columns:
            if assess[col].dtype == 'object':
                unique_vals = assess[col].unique()[:10]  # First 10 unique values
                logger.info(f"\n{col} unique values (first 10): {unique_vals}")
        
        return assess
        
    except Exception as e:
        logger.error(f"Error exploring L3_ASSESS: {e}")
        return None

def main():
    """Main function."""
    logger.info("Starting L3_ASSESS exploration...")
    
    result = explore_l3_assess()
    
    if result is not None:
        logger.info(f"\n✓ L3_ASSESS exploration complete!")
        logger.info("Found assessment data structure!")
    else:
        logger.error("Failed to explore L3_ASSESS")

if __name__ == "__main__":
    main()
