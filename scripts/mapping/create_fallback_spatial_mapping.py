#!/usr/bin/env python3
"""
Create fallback spatial mapping for buildings without official parcel assignments.

This script uses spatial intersection for the remaining 2,189 buildings that
don't have LOCAL_ID values, then combines with the official mapping.

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_parcel_id_from_local_id(local_id):
    """Extract parcel ID from LOCAL_ID field."""
    if pd.isna(local_id) or local_id is None:
        return None
    
    # Pattern: Bos_XXXXXXXX_B[0-9]+ (handles B0, B1, B2, etc.)
    match = re.search(r'Bos_(\d+)_B\d+', str(local_id))
    if match:
        return match.group(1)
    
    return None

def create_fallback_spatial_mapping():
    """
    Create fallback spatial mapping for buildings without official assignments.
    
    Returns:
        DataFrame with complete building-parcel connections
    """
    logger.info("="*60)
    logger.info("CREATING FALLBACK SPATIAL MAPPING")
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
    
    # Load existing official mapping
    official_mapping_file = Path("data/processed/gis_layers/official_building_parcel_mapping.csv")
    if not official_mapping_file.exists():
        logger.error("Official mapping file not found!")
        return None
    
    official_mapping = pd.read_csv(official_mapping_file)
    logger.info(f"Loaded {len(official_mapping):,} official mappings")
    
    # Identify buildings that need fallback mapping
    mapped_struct_ids = set(official_mapping['STRUCT_ID'])
    buildings_needing_fallback = buildings[~buildings['STRUCT_ID'].isin(mapped_struct_ids)]
    
    logger.info(f"Buildings needing fallback mapping: {len(buildings_needing_fallback):,}")
    
    if len(buildings_needing_fallback) == 0:
        logger.info("All buildings already have official mappings!")
        return official_mapping
    
    # Ensure same CRS for spatial operations
    if buildings_needing_fallback.crs != parcels.crs:
        logger.info("Converting buildings to parcels CRS...")
        buildings_needing_fallback = buildings_needing_fallback.to_crs(parcels.crs)
    
    # Perform spatial join for fallback buildings
    logger.info("Performing spatial intersection for fallback buildings...")
    
    # Keep parcels as GeoDataFrame for spatial join
    parcels_subset = parcels[['MAP_PAR_ID', 'LOC_ID', 'POLY_TYPE', 'MAP_NO', 'TOWN_ID', 'geometry']].copy()
    
    # Use spatial join with intersection
    fallback_mapping = gpd.sjoin(
        buildings_needing_fallback, 
        parcels_subset, 
        how='left',
        predicate='intersects'
    )
    
    # Remove the index_right column
    fallback_mapping = fallback_mapping.drop(columns=['index_right'], errors='ignore')
    
    # Filter to only buildings that got linked to parcels
    fallback_mapping = fallback_mapping[fallback_mapping['MAP_PAR_ID'].notna()]
    
    logger.info(f"Fallback spatial mapping found {len(fallback_mapping):,} connections")
    
    # Create fallback mapping DataFrame
    fallback_df = fallback_mapping[['STRUCT_ID', 'MAP_PAR_ID', 'LOC_ID', 'AREA_SQ_FT', 'SOURCE']].copy()
    fallback_df['MAPPING_METHOD'] = 'SPATIAL_INTERSECTION'
    
    # Add parcel information
    parcel_lookup = parcels.drop_duplicates(subset=['MAP_PAR_ID']).set_index('MAP_PAR_ID')[['LOC_ID', 'POLY_TYPE', 'MAP_NO', 'TOWN_ID']].to_dict('index')
    
    fallback_df['PARCEL_LOC_ID'] = fallback_df['MAP_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('LOC_ID', None)
    )
    fallback_df['PARCEL_POLY_TYPE'] = fallback_df['MAP_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('POLY_TYPE', None)
    )
    fallback_df['PARCEL_MAP_NO'] = fallback_df['MAP_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('MAP_NO', None)
    )
    fallback_df['PARCEL_TOWN_ID'] = fallback_df['MAP_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('TOWN_ID', None)
    )
    
    # Add LOCAL_ID and OFFICIAL_PAR_ID columns (empty for fallback)
    fallback_df['LOCAL_ID'] = None
    fallback_df['OFFICIAL_PAR_ID'] = None
    
    # Combine official and fallback mappings
    logger.info("Combining official and fallback mappings...")
    
    # Add mapping method to official mapping
    official_mapping['MAPPING_METHOD'] = 'OFFICIAL_LOCAL_ID'
    
    # Ensure both DataFrames have the same columns
    # Check what columns are available in official_mapping
    logger.info(f"Official mapping columns: {list(official_mapping.columns)}")
    logger.info(f"Fallback mapping columns: {list(fallback_df.columns)}")
    
    # Use only columns that exist in both DataFrames
    common_columns = ['STRUCT_ID', 'AREA_SQ_FT', 'SOURCE', 'MAPPING_METHOD']
    
    # Add columns that exist in both
    for col in ['MAP_PAR_ID', 'LOC_ID', 'PARCEL_LOC_ID', 'PARCEL_POLY_TYPE', 'PARCEL_MAP_NO', 'PARCEL_TOWN_ID', 'LOCAL_ID', 'OFFICIAL_PAR_ID']:
        if col in official_mapping.columns and col in fallback_df.columns:
            common_columns.append(col)
    
    logger.info(f"Using common columns: {common_columns}")
    
    # Reorder columns to match
    official_mapping = official_mapping[common_columns]
    fallback_df = fallback_df[common_columns]
    
    # Combine mappings
    complete_mapping = pd.concat([official_mapping, fallback_df], ignore_index=True)
    
    logger.info(f"Complete mapping created with {len(complete_mapping):,} total connections")
    
    # Analyze results
    official_count = len(official_mapping)
    fallback_count = len(fallback_df)
    total_buildings = len(buildings)
    mapped_buildings = complete_mapping['STRUCT_ID'].nunique()
    unmapped_buildings = total_buildings - mapped_buildings
    
    logger.info(f"✓ {official_count:,} buildings with official parcel assignments")
    logger.info(f"✓ {fallback_count:,} buildings with spatial fallback assignments")
    logger.info(f"✓ {mapped_buildings:,} total buildings mapped ({mapped_buildings/total_buildings*100:.1f}%)")
    logger.info(f"  {unmapped_buildings:,} buildings still unmapped")
    
    # Save the complete mapping
    output_dir = Path("data/processed/gis_layers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    complete_mapping_csv = output_dir / "complete_building_parcel_mapping_final.csv"
    complete_mapping.to_csv(complete_mapping_csv, index=False)
    logger.info(f"✓ Saved complete mapping to: {complete_mapping_csv}")
    
    # Create summary statistics
    summary_stats = {
        'total_buildings': total_buildings,
        'buildings_with_official_parcels': official_count,
        'buildings_with_spatial_parcels': fallback_count,
        'total_mapped_buildings': mapped_buildings,
        'unmapped_buildings': unmapped_buildings,
        'coverage_percentage': mapped_buildings/total_buildings*100,
        'unique_parcels_linked': complete_mapping['OFFICIAL_PAR_ID'].nunique() if 'OFFICIAL_PAR_ID' in complete_mapping.columns else 0
    }
    
    summary_file = output_dir / "complete_mapping_summary_final.txt"
    with open(summary_file, 'w') as f:
        f.write("Complete Building-Parcel Mapping Summary (Final)\n")
        f.write("="*60 + "\n\n")
        for key, value in summary_stats.items():
            if 'percentage' in key:
                f.write(f"{key}: {value:.1f}%\n")
            else:
                f.write(f"{key}: {value:,}\n")
    
    logger.info(f"✓ Saved summary to: {summary_file}")
    
    return complete_mapping

def main():
    """Main function."""
    logger.info("Starting complete building-parcel mapping with fallback...")
    
    result = create_fallback_spatial_mapping()
    
    if result is not None:
        logger.info(f"\n✓ Successfully created complete building-parcel mapping!")
        logger.info("All buildings mapped using official + spatial methods!")
    else:
        logger.error("Failed to create complete mapping")

if __name__ == "__main__":
    main()
