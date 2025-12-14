#!/usr/bin/env python3
"""
Match building STRUCT_IDs directly to assessment PROP_IDs to find exact matches.

This script attempts to find direct matches between building STRUCT_IDs and 
assessment PROP_IDs to create a 1:1 mapping.

Author: Team A
Date: October 2025
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def match_buildings_to_assessments():
    """
    Try to match building STRUCT_IDs directly to assessment PROP_IDs.
    
    Returns:
        DataFrame with matched buildings and assessments
    """
    logger.info("="*60)
    logger.info("MATCHING BUILDINGS TO ASSESSMENTS BY ID")
    logger.info("="*60)
    
    # Load buildings
    buildings_file = Path("data/processed/gis_layers/allston_brighton_buildings.geojson")
    if not buildings_file.exists():
        logger.error("Buildings file not found!")
        return None
    
    buildings = gpd.read_file(buildings_file)
    logger.info(f"Loaded {len(buildings):,} buildings")
    
    # Load assessments
    assessments_file = Path("data/processed/gis_layers/allston_brighton_assessments.csv")
    if not assessments_file.exists():
        logger.error("Assessments file not found!")
        return None
    
    assessments = pd.read_csv(assessments_file)
    logger.info(f"Loaded {len(assessments):,} assessments")
    
    # Extract unique STRUCT_IDs from buildings
    building_struct_ids = set(buildings['STRUCT_ID'].unique())
    logger.info(f"Found {len(building_struct_ids):,} unique STRUCT_IDs in buildings")
    
    # Extract unique PROP_IDs from assessments
    assessment_prop_ids = set(assessments['PROP_ID'].unique())
    logger.info(f"Found {len(assessment_prop_ids):,} unique PROP_IDs in assessments")
    
    # Try different matching strategies
    logger.info("\nTrying different matching strategies...")
    
    # Strategy 1: Direct exact match
    direct_matches = building_struct_ids.intersection(assessment_prop_ids)
    logger.info(f"Strategy 1 - Direct exact matches: {len(direct_matches):,}")
    
    # Strategy 2: Check if STRUCT_ID contains PROP_ID or vice versa
    partial_matches = []
    for struct_id in building_struct_ids:
        for prop_id in assessment_prop_ids:
            if struct_id in str(prop_id) or str(prop_id) in struct_id:
                partial_matches.append((struct_id, prop_id))
    
    logger.info(f"Strategy 2 - Partial matches: {len(partial_matches):,}")
    
    # Strategy 3: Check if they share common patterns
    # Look for patterns like "2204999000" vs "Bos_2204999000_B0"
    pattern_matches = []
    for struct_id in building_struct_ids:
        # Extract numeric part from STRUCT_ID
        struct_numeric = ''.join(filter(str.isdigit, struct_id))
        for prop_id in assessment_prop_ids:
            prop_numeric = ''.join(filter(str.isdigit, str(prop_id)))
            if struct_numeric and prop_numeric and struct_numeric in prop_numeric:
                pattern_matches.append((struct_id, prop_id))
    
    logger.info(f"Strategy 3 - Pattern matches: {len(pattern_matches):,}")
    
    # Show some examples of each type
    if direct_matches:
        logger.info(f"\nDirect match examples: {list(direct_matches)[:5]}")
    
    if partial_matches:
        logger.info(f"\nPartial match examples: {partial_matches[:5]}")
    
    if pattern_matches:
        logger.info(f"\nPattern match examples: {pattern_matches[:5]}")
    
    # Create comprehensive matching results
    all_matches = []
    
    # Add direct matches
    for struct_id in direct_matches:
        all_matches.append({
            'STRUCT_ID': struct_id,
            'PROP_ID': struct_id,
            'MATCH_TYPE': 'direct',
            'CONFIDENCE': 'high'
        })
    
    # Add partial matches
    for struct_id, prop_id in partial_matches:
        all_matches.append({
            'STRUCT_ID': struct_id,
            'PROP_ID': prop_id,
            'MATCH_TYPE': 'partial',
            'CONFIDENCE': 'medium'
        })
    
    # Add pattern matches
    for struct_id, prop_id in pattern_matches:
        all_matches.append({
            'STRUCT_ID': struct_id,
            'PROP_ID': prop_id,
            'MATCH_TYPE': 'pattern',
            'CONFIDENCE': 'low'
        })
    
    # Convert to DataFrame
    matches_df = pd.DataFrame(all_matches)
    
    if len(matches_df) > 0:
        logger.info(f"\nTotal matches found: {len(matches_df):,}")
        logger.info(f"Match type distribution:")
        logger.info(matches_df['MATCH_TYPE'].value_counts().to_string())
        
        # Save results
        output_file = Path("data/processed/gis_layers/building_assessment_matches.csv")
        matches_df.to_csv(output_file, index=False)
        logger.info(f"✓ Saved matches to: {output_file}")
        
        return matches_df
    else:
        logger.warning("No matches found between STRUCT_IDs and PROP_IDs")
        return None

def main():
    """Main function."""
    logger.info("Starting building-to-assessment matching process...")
    
    result = match_buildings_to_assessments()
    
    if result is not None:
        logger.info(f"\n✓ Successfully found matches between buildings and assessments!")
        logger.info("Building-to-assessment matching complete!")
    else:
        logger.error("No matches found between buildings and assessments")

if __name__ == "__main__":
    main()
