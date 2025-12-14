#!/usr/bin/env python3
"""
Extract key GIS layers for Allston-Brighton mapping.

This script extracts the most important layers from MassGIS
and filters them to just the Allston-Brighton area.

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

# Allston-Brighton approximate bounds
BOUNDS = {
    'min_lon': -71.17,
    'max_lon': -71.10,
    'min_lat': 42.33,
    'max_lat': 42.37
}

def extract_layer(gdb_path, layer_name, output_name):
    """
    Extract a specific layer and filter to Allston-Brighton area.
    """
    logger.info(f"\nExtracting: {layer_name}")
    
    try:
        # Read the layer
        gdf = gpd.read_file(gdb_path, layer=layer_name)
        logger.info(f"  Total features: {len(gdf):,}")
        
        # Filter to Allston-Brighton bounds
        mask = (
            (gdf.geometry.bounds['minx'] >= BOUNDS['min_lon']) &
            (gdf.geometry.bounds['maxx'] <= BOUNDS['max_lon']) &
            (gdf.geometry.bounds['miny'] >= BOUNDS['min_lat']) &
            (gdf.geometry.bounds['maxy'] <= BOUNDS['max_lat'])
        )
        
        ab_gdf = gdf[mask].copy()
        logger.info(f"  Allston-Brighton features: {len(ab_gdf):,}")
        
        if len(ab_gdf) > 0:
            # Save to file
            output_dir = Path("data/processed/gis_layers")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{output_name}.geojson"
            ab_gdf.to_file(output_file, driver="GeoJSON")
            logger.info(f"  ✓ Saved to: {output_file}")
            
            return ab_gdf
        else:
            logger.warning(f"  ✗ No features found in Allston-Brighton area")
            return None
            
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        return None

def main():
    """Main function to extract key layers."""
    
    logger.info("="*60)
    logger.info("EXTRACTING KEY LAYERS FOR ALLSTON-BRIGHTON")
    logger.info("="*60)
    
    # Database paths
    parcels_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_L3_Parcels.gdb")
    vector_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_Vector_GISDATA.gdb")
    
    # Key layers to extract
    layers_to_extract = {
        # Parcels
        (parcels_gdb, 'L3_TAXPAR_POLY', 'parcels_allston_brighton'):
            "Property parcels with tax info",
        
        # Open space
        (vector_gdb, 'OPENSPACE_POLY', 'parks_openspace'):
            "Parks and open spaces",
        
        # Roads
        (vector_gdb, 'CENSUS2020TIGERMAJROADS_ARC', 'major_roads'):
            "Major roads from Census 2020",
    }
    
    extracted_data = {}
    
    for (gdb, layer, output_name), description in layers_to_extract.items():
        logger.info(f"\n{description}")
        data = extract_layer(gdb, layer, output_name)
        if data is not None:
            extracted_data[output_name] = data
    
    # Create summary
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION COMPLETE")
    logger.info("="*60)
    
    summary_file = Path("data/processed/gis_layers/extraction_summary.md")
    with open(summary_file, 'w') as f:
        f.write("# GIS Data Extraction Summary\n\n")
        f.write("## Extracted Layers for Allston-Brighton\n\n")
        
        for name, data in extracted_data.items():
            f.write(f"### {name}\n")
            f.write(f"- Features: {len(data):,}\n")
            f.write(f"- File: `{name}.geojson`\n")
            f.write(f"- Columns: {', '.join(data.columns[:10])}\n\n")
        
        f.write("## Usage\n\n")
        f.write("These layers can be loaded in:\n")
        f.write("- Python (geopandas, folium, plotly)\n")
        f.write("- QGIS\n")
        f.write("- ArcGIS\n")
        f.write("- Web mapping applications\n")
    
    logger.info(f"\nSummary saved to: {summary_file}")
    logger.info(f"\nExtracted files location: data/processed/gis_layers/")
    
    # Show what was extracted
    logger.info("\nExtracted layers:")
    for name in extracted_data.keys():
        logger.info(f"  ✓ {name}.geojson")

if __name__ == "__main__":
    main()
