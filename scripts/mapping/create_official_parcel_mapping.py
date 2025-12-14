#!/usr/bin/env python3
"""
Create official building-to-parcel mapping using LOCAL_ID field.

This script uses the LOCAL_ID field from buildings to get the official
parcel assignment instead of spatial intersection.

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
    """
    Extract parcel ID from LOCAL_ID field.
    
    Examples:
    - Bos_2100004000_B0 -> 2100004000
    - Bos_2100003000_B0 -> 2100003000
    """
    if pd.isna(local_id) or local_id is None:
        return None
    
    # Pattern: Bos_XXXXXXXX_B[0-9]+ (handles B0, B1, B2, etc.)
    match = re.search(r'Bos_(\d+)_B\d+', str(local_id))
    if match:
        return match.group(1)
    
    return None

def create_official_parcel_mapping():
    """
    Create official building-to-parcel mapping using LOCAL_ID field.
    
    Returns:
        DataFrame with official building-parcel connections
    """
    logger.info("="*60)
    logger.info("CREATING OFFICIAL BUILDING-PARCEL MAPPING")
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
    
    # Extract parcel IDs from LOCAL_ID
    logger.info("Extracting official parcel assignments from LOCAL_ID...")
    
    buildings['OFFICIAL_PAR_ID'] = buildings['LOCAL_ID'].apply(extract_parcel_id_from_local_id)
    
    # Count how many buildings have official parcel assignments
    buildings_with_parcels = buildings['OFFICIAL_PAR_ID'].notna().sum()
    buildings_without_parcels = len(buildings) - buildings_with_parcels
    
    logger.info(f"✓ {buildings_with_parcels:,} buildings have official parcel assignments")
    logger.info(f"  {buildings_without_parcels:,} buildings without official parcel assignments")
    
    # Create the official mapping
    official_mapping = buildings[['STRUCT_ID', 'OFFICIAL_PAR_ID', 'AREA_SQ_FT', 'SOURCE', 'LOCAL_ID']].copy()
    official_mapping = official_mapping.dropna(subset=['OFFICIAL_PAR_ID'])
    
    logger.info(f"Created {len(official_mapping):,} official building-parcel connections")
    
    # Verify against parcel data
    logger.info("Verifying against parcel data...")
    
    # Get unique parcel IDs from our mapping
    mapping_parcel_ids = set(official_mapping['OFFICIAL_PAR_ID'].unique())
    parcel_ids = set(parcels['MAP_PAR_ID'].astype(str).unique())
    
    # Find matches
    matching_parcels = mapping_parcel_ids.intersection(parcel_ids)
    missing_parcels = mapping_parcel_ids - parcel_ids
    
    logger.info(f"✓ {len(matching_parcels):,} parcel IDs match our parcel data")
    if missing_parcels:
        logger.warning(f"  {len(missing_parcels):,} parcel IDs not found in parcel data")
        logger.warning(f"  Missing parcels: {list(missing_parcels)[:10]}...")
    
    # Add parcel information to mapping
    logger.info("Adding parcel information to mapping...")
    
    # Create parcel lookup (handle duplicate MAP_PAR_IDs)
    parcel_lookup = parcels.drop_duplicates(subset=['MAP_PAR_ID']).set_index('MAP_PAR_ID')[['LOC_ID', 'POLY_TYPE', 'MAP_NO', 'TOWN_ID']].to_dict('index')
    
    # Add parcel details to mapping
    official_mapping['PARCEL_LOC_ID'] = official_mapping['OFFICIAL_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('LOC_ID', None)
    )
    official_mapping['PARCEL_POLY_TYPE'] = official_mapping['OFFICIAL_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('POLY_TYPE', None)
    )
    official_mapping['PARCEL_MAP_NO'] = official_mapping['OFFICIAL_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('MAP_NO', None)
    )
    official_mapping['PARCEL_TOWN_ID'] = official_mapping['OFFICIAL_PAR_ID'].map(
        lambda x: parcel_lookup.get(x, {}).get('TOWN_ID', None)
    )
    
    # Save the official mapping
    output_dir = Path("data/processed/gis_layers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    mapping_csv = output_dir / "official_building_parcel_mapping.csv"
    official_mapping.to_csv(mapping_csv, index=False)
    logger.info(f"✓ Saved official mapping to: {mapping_csv}")
    
    # Create summary statistics
    summary_stats = {
        'total_buildings': len(buildings),
        'buildings_with_official_parcels': len(official_mapping),
        'buildings_without_official_parcels': buildings_without_parcels,
        'unique_parcels_linked': official_mapping['OFFICIAL_PAR_ID'].nunique(),
        'matching_parcels': len(matching_parcels),
        'missing_parcels': len(missing_parcels)
    }
    
    summary_file = output_dir / "official_mapping_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Official Building-Parcel Mapping Summary\n")
        f.write("="*50 + "\n\n")
        for key, value in summary_stats.items():
            f.write(f"{key}: {value:,}\n")
    
    logger.info(f"✓ Saved summary to: {summary_file}")
    
    # Show some examples
    logger.info("\n=== EXAMPLES OF OFFICIAL MAPPING ===")
    for i, row in official_mapping.head(5).iterrows():
        logger.info(f"Building {row['STRUCT_ID']} -> Parcel {row['OFFICIAL_PAR_ID']}")
    
    return official_mapping

def main():
    """Main function."""
    logger.info("Starting official building-parcel mapping...")
    
    result = create_official_parcel_mapping()
    
    if result is not None:
        logger.info(f"\n✓ Successfully created official building-parcel mapping!")
        logger.info("Official parcel assignments mapped!")
    else:
        logger.error("Failed to create official mapping")

if __name__ == "__main__":
    main()
