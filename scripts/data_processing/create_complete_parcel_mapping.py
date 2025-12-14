#!/usr/bin/env python3
"""
Create complete building-to-parcel mapping with ALL connections.

This script creates a comprehensive mapping showing every building-parcel
connection, including multiple buildings on the same parcel.

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

def create_complete_parcel_mapping():
    """
    Create complete building-to-parcel mapping with ALL connections.
    
    Returns:
        DataFrame with all building-parcel connections
    """
    logger.info("="*60)
    logger.info("CREATING COMPLETE BUILDING-PARCEL MAPPING")
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
    logger.info("Performing spatial join to link ALL buildings with parcels...")
    
    # Keep parcels as GeoDataFrame for spatial join
    parcels_subset = parcels[['MAP_PAR_ID', 'LOC_ID', 'POLY_TYPE', 'MAP_NO', 'TOWN_ID', 'geometry']].copy()
    
    # Use spatial join with intersection - this will create ALL connections
    buildings_with_parcels = gpd.sjoin(
        buildings, 
        parcels_subset, 
        how='left',
        predicate='intersects'
    )
    
    # Remove the index_right column
    buildings_with_parcels = buildings_with_parcels.drop(columns=['index_right'], errors='ignore')
    
    logger.info(f"Successfully processed {len(buildings_with_parcels):,} building-parcel connections")
    
    # Analyze results - show ALL connections, not just unique
    linked_connections = buildings_with_parcels['MAP_PAR_ID'].notna().sum()
    unlinked_connections = len(buildings_with_parcels) - linked_connections
    
    logger.info(f"✓ {linked_connections:,} building-parcel connections found")
    logger.info(f"  {unlinked_connections:,} buildings without parcel links")
    
    # Show detailed statistics
    if linked_connections > 0:
        unique_buildings = buildings_with_parcels['STRUCT_ID'].nunique()
        unique_parcels = buildings_with_parcels['MAP_PAR_ID'].nunique()
        total_connections = linked_connections
        
        logger.info(f"  - {unique_buildings:,} unique buildings")
        logger.info(f"  - {unique_parcels:,} unique parcels")
        logger.info(f"  - {total_connections:,} total connections")
        
        # Show buildings per parcel distribution
        buildings_per_parcel = buildings_with_parcels.groupby('MAP_PAR_ID').size()
        logger.info(f"  - Average buildings per parcel: {buildings_per_parcel.mean():.2f}")
        logger.info(f"  - Max buildings on single parcel: {buildings_per_parcel.max()}")
        
        # Show parcels with multiple buildings
        multi_building_parcels = buildings_per_parcel[buildings_per_parcel > 1]
        logger.info(f"  - Parcels with multiple buildings: {len(multi_building_parcels):,}")
        
        # Show some examples of parcels with multiple buildings
        if len(multi_building_parcels) > 0:
            logger.info(f"  - Examples of multi-building parcels:")
            for parcel_id, count in multi_building_parcels.head(5).items():
                logger.info(f"    Parcel {parcel_id}: {count} buildings")
    
    # Save the complete mapping
    output_dir = Path("data/processed/gis_layers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as GeoJSON
    output_geojson = output_dir / "complete_building_parcel_mapping.geojson"
    buildings_with_parcels.to_file(output_geojson, driver='GeoJSON')
    logger.info(f"✓ Saved complete mapping to: {output_geojson}")
    
    # Create a detailed CSV with all connections
    mapping_data = buildings_with_parcels[['STRUCT_ID', 'MAP_PAR_ID', 'LOC_ID', 'AREA_SQ_FT', 'SOURCE']].copy()
    mapping_data = mapping_data.dropna(subset=['MAP_PAR_ID'])  # Only keep buildings with parcels
    
    mapping_csv = output_dir / "complete_building_parcel_mapping.csv"
    mapping_data.to_csv(mapping_csv, index=False)
    logger.info(f"✓ Saved detailed mapping to: {mapping_csv}")
    
    # Create summary statistics
    summary_stats = {
        'total_buildings': len(buildings),
        'total_parcels': len(parcels),
        'total_connections': len(mapping_data),
        'unique_buildings_linked': mapping_data['STRUCT_ID'].nunique(),
        'unique_parcels_linked': mapping_data['MAP_PAR_ID'].nunique(),
        'buildings_without_parcels': len(buildings) - mapping_data['STRUCT_ID'].nunique(),
        'avg_buildings_per_parcel': mapping_data.groupby('MAP_PAR_ID').size().mean(),
        'max_buildings_per_parcel': mapping_data.groupby('MAP_PAR_ID').size().max()
    }
    
    summary_file = output_dir / "complete_mapping_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Complete Building-Parcel Mapping Summary\n")
        f.write("="*50 + "\n\n")
        for key, value in summary_stats.items():
            f.write(f"{key}: {value:,}\n")
    
    logger.info(f"✓ Saved summary to: {summary_file}")
    
    return buildings_with_parcels

def main():
    """Main function."""
    logger.info("Starting complete building-parcel mapping...")
    
    result = create_complete_parcel_mapping()
    
    if result is not None:
        logger.info(f"\n✓ Successfully created complete building-parcel mapping!")
        logger.info("All building-parcel connections mapped!")
    else:
        logger.error("Failed to create complete mapping")

if __name__ == "__main__":
    main()
