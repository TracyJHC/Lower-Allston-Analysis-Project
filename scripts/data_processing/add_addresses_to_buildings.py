#!/usr/bin/env python3
"""
Add addresses to building footprints by spatial intersection with assessment data.

This script takes the building footprints and links them to address information
from the property assessment data using spatial intersection.

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging
from shapely.geometry import Point

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_assessment_data():
    """Load property assessment data with addresses."""
    logger.info("Loading property assessment data...")
    
    assessments_file = Path("data/processed/gis_layers/allston_brighton_assessments.csv")
    
    if not assessments_file.exists():
        logger.error("Assessment data file not found!")
        return None
    
    # Load assessments
    assessments = pd.read_csv(assessments_file)
    logger.info(f"Loaded {len(assessments):,} assessment records")
    
    # Create GeoDataFrame from assessments
    # We need to geocode the addresses or use existing coordinates
    # For now, let's check if there are coordinates in the assessment data
    if 'LATITUDE' in assessments.columns and 'LONGITUDE' in assessments.columns:
        logger.info("Using existing coordinates from assessments...")
        
        # Filter out records without coordinates
        assessments_with_coords = assessments.dropna(subset=['LATITUDE', 'LONGITUDE'])
        logger.info(f"Found {len(assessments_with_coords):,} assessments with coordinates")
        
        # Create geometry from coordinates
        geometry = [Point(xy) for xy in zip(assessments_with_coords['LONGITUDE'], 
                                           assessments_with_coords['LATITUDE'])]
        
        assessments_gdf = gpd.GeoDataFrame(
            assessments_with_coords, 
            geometry=geometry, 
            crs='EPSG:4326'
        )
        
        return assessments_gdf
    else:
        logger.warning("No coordinate columns found in assessment data")
        return None

def add_addresses_to_buildings():
    """Add address information to building footprints."""
    logger.info("="*60)
    logger.info("ADDING ADDRESSES TO BUILDING FOOTPRINTS")
    logger.info("="*60)
    
    # Load building points
    buildings_file = Path("data/processed/gis_layers/allston_brighton_building_points.geojson")
    if not buildings_file.exists():
        logger.error("Building points file not found!")
        return None
    
    buildings = gpd.read_file(buildings_file)
    logger.info(f"Loaded {len(buildings):,} building points")
    
    # Load assessment data
    assessments = load_assessment_data()
    if assessments is None:
        logger.error("Could not load assessment data")
        return None
    
    # Perform spatial join to find nearest assessment for each building
    logger.info("Performing spatial join to link buildings with addresses...")
    
    # Use spatial join with nearest neighbor
    buildings_with_addresses = gpd.sjoin_nearest(
        buildings, 
        assessments[['SITE_ADDR', 'ADDR_NUM', 'FULL_STR', 'LOCATION', 'CITY', 'ZIP', 'geometry']], 
        how='left',
        distance_col='distance'
    )
    
    # Remove the distance column and index_right
    buildings_with_addresses = buildings_with_addresses.drop(columns=['distance'], errors='ignore')
    buildings_with_addresses = buildings_with_addresses.drop(columns=['index_right'], errors='ignore')
    
    logger.info(f"Successfully linked {len(buildings_with_addresses):,} buildings with address data")
    
    # Check how many buildings got addresses
    buildings_with_addresses['has_address'] = buildings_with_addresses['SITE_ADDR'].notna()
    address_count = buildings_with_addresses['has_address'].sum()
    logger.info(f"✓ {address_count:,} buildings now have addresses")
    logger.info(f"  {len(buildings_with_addresses) - address_count:,} buildings without addresses")
    
    # Save updated building data with addresses
    output_file = Path("data/processed/gis_layers/allston_brighton_buildings_with_addresses.geojson")
    buildings_with_addresses.to_file(output_file, driver='GeoJSON')
    logger.info(f"✓ Saved buildings with addresses to: {output_file}")
    
    # Show sample of buildings with addresses
    logger.info("\nSample buildings with addresses:")
    logger.info("="*50)
    sample_buildings = buildings_with_addresses[buildings_with_addresses['has_address']].head(5)
    for idx, building in sample_buildings.iterrows():
        logger.info(f"Building {building['building_id']}: {building['SITE_ADDR']}")
    
    return buildings_with_addresses

def main():
    """Main function."""
    logger.info("Adding addresses to building footprints...")
    
    buildings_with_addresses = add_addresses_to_buildings()
    
    if buildings_with_addresses is not None:
        logger.info(f"\n✓ Successfully added addresses to building data")
        logger.info("Building data now includes address information!")
    else:
        logger.error("Failed to add addresses to buildings")

if __name__ == "__main__":
    main()
