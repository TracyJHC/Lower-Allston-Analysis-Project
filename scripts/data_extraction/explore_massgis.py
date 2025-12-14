#!/usr/bin/env python3
"""
Explore MassGIS database to see what data is available.

This script lists all available layers in the MassGIS database
and shows sample data from each.

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import fiona
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def explore_database(gdb_path, db_name):
    """
    Explore a GeoDatabase and list all available layers.
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Exploring: {db_name}")
    logger.info(f"{'='*60}")
    
    try:
        # List all layers
        layers = fiona.listlayers(str(gdb_path))
        logger.info(f"Total layers found: {len(layers)}\n")
        
        # Show all layers
        logger.info("Available layers:")
        for i, layer in enumerate(layers, 1):
            logger.info(f"  {i}. {layer}")
        
        return layers
        
    except Exception as e:
        logger.error(f"Error reading database: {e}")
        return []

def examine_layer(gdb_path, layer_name):
    """
    Examine a specific layer in detail.
    """
    logger.info(f"\n{'-'*60}")
    logger.info(f"Examining layer: {layer_name}")
    logger.info(f"{'-'*60}")
    
    try:
        # Read the layer
        gdf = gpd.read_file(gdb_path, layer=layer_name)
        
        logger.info(f"Total features: {len(gdf):,}")
        logger.info(f"Columns: {list(gdf.columns)}")
        
        # Show geometry type
        if 'geometry' in gdf.columns:
            geom_types = gdf.geometry.geom_type.unique()
            logger.info(f"Geometry types: {list(geom_types)}")
        
        # Show sample data
        if len(gdf) > 0:
            logger.info("\nSample data (first 2 rows):")
            print(gdf.head(2))
        
        return gdf
        
    except Exception as e:
        logger.error(f"Error reading layer: {e}")
        return None

def main():
    """Main function to explore MassGIS databases."""
    
    # Paths to the databases
    base_path = Path("/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/raw/statewide_viewer_fgdb")
    
    parcels_gdb = base_path / "MassGIS_L3_Parcels.gdb"
    vector_gdb = base_path / "MassGIS_Vector_GISDATA.gdb"
    
    logger.info("MassGIS Database Explorer")
    logger.info("="*60)
    
    # Check if databases exist
    if not parcels_gdb.exists():
        logger.error(f"Parcels database not found: {parcels_gdb}")
        return
    
    if not vector_gdb.exists():
        logger.error(f"Vector database not found: {vector_gdb}")
        return
    
    # Explore parcels database
    parcel_layers = explore_database(parcels_gdb, "PARCELS DATABASE")
    
    # Examine the first few parcel layers
    if parcel_layers:
        logger.info("\n\nExamining parcel layers in detail...")
        for layer in parcel_layers[:3]:  # First 3 layers
            examine_layer(parcels_gdb, layer)
    
    # Explore vector database
    vector_layers = explore_database(vector_gdb, "VECTOR DATABASE")
    
    # Look for specific useful layers
    if vector_layers:
        logger.info("\n\n" + "="*60)
        logger.info("USEFUL LAYERS FOR ALLSTON-BRIGHTON:")
        logger.info("="*60)
        
        # Search for relevant layers
        keywords = {
            'Roads': ['road', 'street', 'highway'],
            'Transit': ['transit', 'mbta', 'rail', 'subway', 'bus'],
            'Parks': ['park', 'open', 'recreation'],
            'Water': ['water', 'river', 'stream', 'pond'],
            'Buildings': ['building', 'structure'],
            'Boundaries': ['boundary', 'municipal', 'neighborhood'],
            'Zoning': ['zoning', 'land use']
        }
        
        found_layers = {}
        for category, search_terms in keywords.items():
            found = []
            for layer in vector_layers:
                if any(term in layer.lower() for term in search_terms):
                    found.append(layer)
            if found:
                found_layers[category] = found
        
        # Display found layers
        for category, layers in found_layers.items():
            logger.info(f"\n{category} Layers:")
            for layer in layers[:5]:  # Show first 5
                logger.info(f"  - {layer}")
        
        # Examine a few interesting layers in detail
        logger.info("\n\nExamining sample useful layers...")
        interesting_layers = [
            'GISDATA.ROADS_MAJOR_BOSTONMPO',  # Major roads
            'GISDATA.OPENSPACE_POLY',         # Parks
            'GISDATA.TOWNS_POLYM'             # Town boundaries
        ]
        
        for layer in interesting_layers:
            if layer in vector_layers:
                examine_layer(vector_gdb, layer)
    
    # Create summary file
    summary_file = Path("data/processed/gis_layers/massgis_inventory.txt")
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, 'w') as f:
        f.write("MassGIS Database Inventory\n")
        f.write("="*60 + "\n\n")
        
        f.write("PARCELS DATABASE\n")
        f.write(f"Total layers: {len(parcel_layers)}\n")
        for layer in parcel_layers:
            f.write(f"  - {layer}\n")
        
        f.write(f"\n\nVECTOR DATABASE\n")
        f.write(f"Total layers: {len(vector_layers)}\n")
        f.write(f"\nUseful layers by category:\n\n")
        
        for category, layers in found_layers.items():
            f.write(f"{category}:\n")
            for layer in layers:
                f.write(f"  - {layer}\n")
            f.write("\n")
    
    logger.info(f"\n\nInventory saved to: {summary_file}")
    logger.info("\nNext steps:")
    logger.info("1. Review the inventory to find layers you want")
    logger.info("2. Use specific layer names to extract data for Allston-Brighton")
    logger.info("3. Filter by geographic bounds to get only your area")

if __name__ == "__main__":
    main()
