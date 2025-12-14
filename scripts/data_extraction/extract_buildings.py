#!/usr/bin/env python3
"""
Extract building footprints from MassGIS database for Allston-Brighton.

This script extracts the STRUCTURES_POLY layer from MassGIS and filters
it to only include buildings within the Allston-Brighton boundary.

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging
from shapely.geometry import box

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Allston-Brighton bounds
AB_BOUNDS = {
    'west': -71.17,
    'east': -71.10,
    'south': 42.32,
    'north': 42.38
}

def get_allston_brighton_boundary():
    """Get Allston-Brighton boundary for filtering."""
    boundary_file = Path("data/processed/gis_layers/allston_brighton_boundary.geojson")
    
    if boundary_file.exists():
        logger.info("Loading Allston-Brighton boundary...")
        boundary_gdf = gpd.read_file(boundary_file)
        return boundary_gdf
    else:
        logger.warning("Boundary not found, using bounding box...")
        boundary_box = box(
            AB_BOUNDS['west'], 
            AB_BOUNDS['south'],
            AB_BOUNDS['east'],
            AB_BOUNDS['north']
        )
        boundary_gdf = gpd.GeoDataFrame(
            [{'name': 'Allston-Brighton', 'geometry': boundary_box}],
            crs='EPSG:4326'
        )
        return boundary_gdf

def extract_buildings():
    """Extract building footprints for Allston-Brighton."""
    logger.info("="*60)
    logger.info("EXTRACTING BUILDING FOOTPRINTS")
    logger.info("="*60)
    
    # Get boundary
    boundary = get_allston_brighton_boundary()
    boundary_geom = boundary.geometry.iloc[0]
    
    # Path to the vector database
    vector_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_Vector_GISDATA.gdb")
    
    if not vector_gdb.exists():
        logger.error("Vector database not found!")
        return None
    
    try:
        logger.info("Loading building footprints from MassGIS...")
        buildings = gpd.read_file(vector_gdb, layer='STRUCTURES_POLY')
        logger.info(f"Loaded {len(buildings):,} total building footprints")
        
        # Convert to WGS84
        if buildings.crs != 'EPSG:4326':
            logger.info("Converting buildings to WGS84...")
            buildings = buildings.to_crs('EPSG:4326')
        
        # Filter to Allston-Brighton using spatial intersection
        logger.info("Filtering buildings to Allston-Brighton...")
        buildings_ab = buildings[buildings.geometry.intersects(boundary_geom)]
        logger.info(f"Found {len(buildings_ab):,} buildings in Allston-Brighton")
        
        if len(buildings_ab) > 0:
            # Save buildings
            output_file = Path("data/processed/gis_layers/allston_brighton_buildings.geojson")
            buildings_ab.to_file(output_file, driver='GeoJSON')
            logger.info(f"✓ Saved to: {output_file}")
            
            # Create building points (centroids) for map display
            logger.info("Creating building points (centroids)...")
            building_points = buildings_ab.copy()
            building_points['geometry'] = building_points.geometry.centroid
            
            # Add some useful attributes
            building_points['building_id'] = range(len(building_points))
            building_points['area_sqft'] = buildings_ab.geometry.area * 10.764  # Convert from sq meters to sq ft
            
            # Save building points
            points_file = Path("data/processed/gis_layers/allston_brighton_building_points.geojson")
            building_points.to_file(points_file, driver='GeoJSON')
            logger.info(f"✓ Saved building points to: {points_file}")
            
            return building_points
        else:
            logger.warning("No buildings found in Allston-Brighton")
            return None
            
    except Exception as e:
        logger.error(f"Error extracting buildings: {e}")
        return None

def main():
    """Main function."""
    logger.info("Extracting building footprints for Allston-Brighton...")
    
    buildings = extract_buildings()
    
    if buildings is not None:
        logger.info(f"\n✓ Successfully extracted {len(buildings):,} building points")
        logger.info("Building data ready for map visualization!")
    else:
        logger.error("Failed to extract building data")

if __name__ == "__main__":
    main()
