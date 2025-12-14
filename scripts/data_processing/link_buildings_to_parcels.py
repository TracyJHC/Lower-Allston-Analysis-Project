#!/usr/bin/env python3
"""
Link building footprints to property parcels using spatial intersection.

This script takes each building (STRUCT_ID) and finds which parcel (MAP_PAR_ID) 
it intersects with, creating a mapping between buildings and parcels.

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

def link_buildings_to_parcels():
    """
    Link each building to its corresponding parcel using spatial intersection.
    
    Returns:
        GeoDataFrame with buildings linked to parcels
    """
    logger.info("="*60)
    logger.info("LINKING BUILDINGS TO PARCELS")
    logger.info("="*60)
    
    # Load buildings
    buildings_file = Path("data/processed/gis_layers/allston_brighton_buildings.geojson")
    if not buildings_file.exists():
        logger.error("Buildings file not found!")
        return None
    
    buildings = gpd.read_file(buildings_file)
    logger.info(f"Loaded {len(buildings):,} buildings")
    
    # Load parcels
    parcels_file = Path("data/processed/gis_layers/allston_brighton_parcels.geojson")
    if not parcels_file.exists():
        logger.error("Parcels file not found!")
        return None
    
    parcels = gpd.read_file(parcels_file)
    logger.info(f"Loaded {len(parcels):,} parcels")
    
    # Ensure same CRS
    if buildings.crs != parcels.crs:
        logger.info("Converting buildings to parcels CRS...")
        buildings = buildings.to_crs(parcels.crs)
    
    # Perform spatial join - buildings intersecting with parcels
    logger.info("Performing spatial join to link buildings with parcels...")
    
    # Use spatial join with intersection
    # Keep parcels as GeoDataFrame for spatial join
    parcels_subset = parcels[['MAP_PAR_ID', 'LOC_ID', 'POLY_TYPE', 'MAP_NO', 'TOWN_ID', 'geometry']].copy()
    
    buildings_with_parcels = gpd.sjoin(
        buildings, 
        parcels_subset, 
        how='left',
        predicate='intersects'
    )
    
    # Remove the index_right column
    buildings_with_parcels = buildings_with_parcels.drop(columns=['index_right'], errors='ignore')
    
    logger.info(f"Successfully processed {len(buildings_with_parcels):,} buildings")
    
    # Check how many buildings got linked to parcels
    buildings_with_parcels['has_parcel'] = buildings_with_parcels['MAP_PAR_ID'].notna()
    parcel_count = buildings_with_parcels['has_parcel'].sum()
    logger.info(f"✓ {parcel_count:,} buildings linked to parcels")
    logger.info(f"  {len(buildings_with_parcels) - parcel_count:,} buildings without parcel links")
    
    # Show some statistics
    if parcel_count > 0:
        # Count unique parcels
        unique_parcels = buildings_with_parcels['MAP_PAR_ID'].nunique()
        logger.info(f"  Buildings linked to {unique_parcels:,} unique parcels")
        
        # Show buildings per parcel distribution
        buildings_per_parcel = buildings_with_parcels.groupby('MAP_PAR_ID').size()
        logger.info(f"  Average buildings per parcel: {buildings_per_parcel.mean():.2f}")
        logger.info(f"  Max buildings on single parcel: {buildings_per_parcel.max()}")
    
    # Save the linked data
    output_file = Path("data/processed/gis_layers/allston_brighton_buildings_with_parcels.geojson")
    buildings_with_parcels.to_file(output_file, driver='GeoJSON')
    logger.info(f"✓ Saved linked data to: {output_file}")
    
    # Create a simple mapping table (STRUCT_ID -> MAP_PAR_ID)
    mapping_data = buildings_with_parcels[['STRUCT_ID', 'MAP_PAR_ID', 'LOC_ID', 'AREA_SQ_FT']].copy()
    mapping_data = mapping_data.dropna(subset=['MAP_PAR_ID'])  # Only keep buildings with parcels
    
    mapping_file = Path("data/processed/gis_layers/building_parcel_mapping.csv")
    mapping_data.to_csv(mapping_file, index=False)
    logger.info(f"✓ Saved mapping table to: {mapping_file}")
    
    return buildings_with_parcels

def main():
    """Main function."""
    logger.info("Starting building-to-parcel linking process...")
    
    result = link_buildings_to_parcels()
    
    if result is not None:
        logger.info(f"\n✓ Successfully linked buildings to parcels!")
        logger.info("Building-to-parcel mapping complete!")
    else:
        logger.error("Failed to link buildings to parcels")

if __name__ == "__main__":
    main()
