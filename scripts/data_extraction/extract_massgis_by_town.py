#!/usr/bin/env python3
"""
Extract MassGIS data by town/municipality.

This script provides a reusable method to extract data from the massive
MassGIS statewide database by filtering for specific towns (Boston).

This is much more reliable than trying to use the terrible MassGIS website!

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

def get_town_boundary(town_name="BOSTON"):
    """
    Get the boundary polygon for a specific town from MassGIS.
    
    Args:
        town_name: Name of the town (e.g., "BOSTON", "CAMBRIDGE")
    
    Returns:
        GeoDataFrame with town boundary
    """
    logger.info(f"Getting boundary for {town_name}...")
    
    vector_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_Vector_GISDATA.gdb")
    
    try:
        # Read town boundaries layer (TOWNSSURVEY_POLYM is the correct layer)
        towns = gpd.read_file(vector_gdb, layer="TOWNSSURVEY_POLYM")
        logger.info(f"  Loaded {len(towns)} towns")
        
        # Filter for specific town
        town = towns[towns['TOWN'].str.upper() == town_name.upper()].copy()
        
        if len(town) > 0:
            logger.info(f"  ✓ Found {town_name}")
            return town
        else:
            logger.error(f"  ✗ {town_name} not found")
            logger.info(f"  Available towns: {sorted(towns['TOWN'].unique())[:10]}...")
            return None
            
    except Exception as e:
        logger.error(f"Error getting town boundary: {e}")
        return None

def extract_parcels_by_town(town_boundary, town_name="BOSTON"):
    """
    Extract property parcels for a specific town.
    
    This is the key function - extracts from 2.2 million statewide parcels!
    
    Args:
        town_boundary: GeoDataFrame with town boundary polygon
        town_name: Name of town for output file
    
    Returns:
        GeoDataFrame with town's parcels
    """
    logger.info(f"\nExtracting parcels for {town_name}...")
    logger.info("  (This may take a few minutes - 2.2M parcels to process!)")
    
    parcels_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_L3_Parcels.gdb")
    
    try:
        # Read parcels (this is the big one - 2.2M parcels!)
        parcels = gpd.read_file(parcels_gdb, layer="L3_TAXPAR_POLY")
        logger.info(f"  Loaded {len(parcels):,} total parcels")
        
        # Check if parcels have a town field we can filter on
        if 'TOWN_ID' in parcels.columns or 'TOWN' in parcels.columns:
            # Easy filter by town attribute
            town_col = 'TOWN_ID' if 'TOWN_ID' in parcels.columns else 'TOWN'
            
            # Get town ID from boundary
            if 'TOWN_ID' in town_boundary.columns:
                town_id = town_boundary['TOWN_ID'].iloc[0]
                town_parcels = parcels[parcels[town_col] == town_id].copy()
            else:
                town_parcels = parcels[parcels[town_col].str.upper() == town_name.upper()].copy()
            
            logger.info(f"  ✓ Filtered by town attribute: {len(town_parcels):,} parcels")
        else:
            # Spatial filter (slower but works)
            logger.info("  Using spatial intersection (this takes longer)...")
            
            # Ensure same CRS
            if parcels.crs != town_boundary.crs:
                town_boundary = town_boundary.to_crs(parcels.crs)
            
            # Spatial join
            town_parcels = gpd.sjoin(parcels, town_boundary, predicate='intersects')
            logger.info(f"  ✓ Spatial filter complete: {len(town_parcels):,} parcels")
        
        # Save to file
        output_dir = Path("data/processed/gis_layers/parcels")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{town_name.lower()}_parcels.geojson"
        town_parcels.to_file(output_file, driver="GeoJSON")
        logger.info(f"  ✓ Saved to: {output_file}")
        
        return town_parcels
        
    except Exception as e:
        logger.error(f"Error extracting parcels: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_layer_by_town(gdb_path, layer_name, town_boundary, output_name):
    """
    Generic function to extract any layer filtered by town boundary.
    
    This is reusable for ANY layer in the MassGIS database!
    
    Args:
        gdb_path: Path to GeoDatabase
        layer_name: Name of layer to extract
        town_boundary: GeoDataFrame with town boundary
        output_name: Name for output file
    
    Returns:
        GeoDataFrame with filtered data
    """
    logger.info(f"\nExtracting: {layer_name}")
    
    try:
        # Read the layer
        gdf = gpd.read_file(gdb_path, layer=layer_name)
        logger.info(f"  Total features: {len(gdf):,}")
        
        # Ensure same CRS
        if gdf.crs != town_boundary.crs:
            town_boundary = town_boundary.to_crs(gdf.crs)
        
        # Spatial join to filter
        filtered = gpd.sjoin(gdf, town_boundary, predicate='intersects')
        logger.info(f"  Town features: {len(filtered):,}")
        
        if len(filtered) > 0:
            # Save to file
            output_dir = Path("data/processed/gis_layers")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{output_name}.geojson"
            
            # Drop the join index columns
            filtered = filtered.drop(columns=['index_right'], errors='ignore')
            
            filtered.to_file(output_file, driver="GeoJSON")
            logger.info(f"  ✓ Saved to: {output_file}")
            
            return filtered
        else:
            logger.warning(f"  ✗ No features found")
            return None
            
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return None

def main():
    """
    Main function - Extract key layers for Allston-Brighton/Boston.
    """
    logger.info("="*60)
    logger.info("MASSGIS DATA EXTRACTION BY TOWN")
    logger.info("="*60)
    logger.info("Because the MassGIS website sucks, use this instead!")
    logger.info("="*60 + "\n")
    
    # Step 1: Get Boston boundary
    boston = get_town_boundary("BOSTON")
    
    if boston is None:
        logger.error("Could not get Boston boundary. Exiting.")
        return
    
    # Step 2: Extract parcels (the most important layer)
    parcels = extract_parcels_by_town(boston, "BOSTON")
    
    # Step 3: Extract other useful layers
    vector_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_Vector_GISDATA.gdb")
    
    useful_layers = {
        'OPENSPACE_POLY': 'boston_parks_openspace',
        'CENSUS2020TIGERMAJROADS_ARC': 'boston_major_roads',
    }
    
    extracted = {}
    for layer_name, output_name in useful_layers.items():
        data = extract_layer_by_town(vector_gdb, layer_name, boston, output_name)
        if data is not None:
            extracted[output_name] = data
    
    # Create summary
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION COMPLETE!")
    logger.info("="*60)
    
    summary_file = Path("data/processed/gis_layers/boston_extraction_summary.md")
    with open(summary_file, 'w') as f:
        f.write("# MassGIS Boston Data Extraction\n\n")
        f.write("## Why This Exists\n\n")
        f.write("The MassGIS website is terrible for downloading data.\n")
        f.write("This script extracts data directly from the statewide database,\n")
        f.write("filtered specifically for Boston/Allston-Brighton.\n\n")
        
        f.write("## Extracted Layers\n\n")
        
        if parcels is not None:
            f.write(f"### Boston Parcels\n")
            f.write(f"- Features: {len(parcels):,}\n")
            f.write(f"- File: `parcels/boston_parcels.geojson`\n")
            f.write(f"- Source: L3_TAXPAR_POLY (from 2.2M statewide parcels)\n\n")
        
        for name, data in extracted.items():
            f.write(f"### {name}\n")
            f.write(f"- Features: {len(data):,}\n")
            f.write(f"- File: `{name}.geojson`\n\n")
        
        f.write("## How to Use This Script for Other Towns\n\n")
        f.write("```python\n")
        f.write("# Change the town name:\n")
        f.write('town = get_town_boundary("CAMBRIDGE")  # or BROOKLINE, SOMERVILLE, etc.\n')
        f.write('parcels = extract_parcels_by_town(town, "CAMBRIDGE")\n')
        f.write("```\n\n")
        
        f.write("## Available Layers to Extract\n\n")
        f.write("The MassGIS Vector database has 662 layers including:\n")
        f.write("- Roads, streets, highways\n")
        f.write("- Parks, open space, conservation land\n")
        f.write("- Water bodies, wetlands\n")
        f.write("- Transit (MBTA lines, stations)\n")
        f.write("- Zoning districts\n")
        f.write("- Building footprints\n")
        f.write("- Census boundaries\n")
        f.write("- and 650+ more...\n\n")
        
        f.write("Use `extract_layer_by_town()` to get any layer you want!\n")
    
    logger.info(f"Summary saved to: {summary_file}")
    logger.info("\nFiles created in: data/processed/gis_layers/")
    
    if parcels is not None:
        logger.info(f"  ✓ boston_parcels.geojson ({len(parcels):,} parcels)")
    
    for name in extracted.keys():
        logger.info(f"  ✓ {name}.geojson")
    
    logger.info("\n" + "="*60)
    logger.info("FUTURE USE:")
    logger.info("="*60)
    logger.info("This script is reusable for:")
    logger.info("  - Any town in Massachusetts")
    logger.info("  - Any layer in the MassGIS database")
    logger.info("  - Better than using the terrible MassGIS website!")
    logger.info("="*60)

if __name__ == "__main__":
    main()
