#!/usr/bin/env python3
"""
Extract 2025 Allston-Brighton property data from MassGIS database.

This script focuses specifically on Allston-Brighton properties with the most recent
assessment data and property details.

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

def extract_allston_brighton_properties():
    """Extract property data specifically for Allston-Brighton."""
    logger.info("="*60)
    logger.info("EXTRACTING ALLSTON-BRIGHTON PROPERTY DATA")
    logger.info("="*60)
    
    # Get boundary
    boundary = get_allston_brighton_boundary()
    boundary_geom = boundary.geometry.iloc[0]
    
    # 1. Extract property parcels for Allston-Brighton
    logger.info("\n1. Extracting property parcels...")
    parcels_file = Path("data/processed/gis_layers/parcels/boston_parcels.geojson")
    
    if parcels_file.exists():
        logger.info("  Loading Boston parcels...")
        parcels = gpd.read_file(parcels_file)
        logger.info(f"  Loaded {len(parcels):,} total Boston parcels")
        logger.info(f"  Parcels CRS: {parcels.crs}")
        logger.info(f"  Boundary CRS: {boundary.crs}")
        
        # Convert parcels to same CRS as boundary if needed
        if parcels.crs != boundary.crs:
            logger.info("  Converting parcels to WGS84...")
            parcels = parcels.to_crs(boundary.crs)
        
        # Filter to Allston-Brighton
        ab_parcels = parcels[parcels.geometry.within(boundary_geom)]
        logger.info(f"  ✓ Found {len(ab_parcels):,} parcels in Allston-Brighton")
        
        # Save Allston-Brighton parcels
        ab_parcels_file = Path("data/processed/gis_layers/allston_brighton_parcels.geojson")
        ab_parcels.to_file(ab_parcels_file, driver='GeoJSON')
        logger.info(f"  ✓ Saved to: {ab_parcels_file}")
        
    else:
        logger.error("  Boston parcels file not found!")
        return None
    
    # 2. Extract property assessment data for Allston-Brighton
    logger.info("\n2. Extracting property assessment data...")
    
    # Path to the assessment database
    assess_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_L3_Parcels.gdb")
    
    if assess_gdb.exists():
        try:
            # Read assessment data
            logger.info("  Loading assessment data...")
            assessments = gpd.read_file(assess_gdb, layer='L3_ASSESS')
            logger.info(f"  Loaded {len(assessments):,} assessment records")
            
            # Check if it's a GeoDataFrame with geometry
            if hasattr(assessments, 'geometry') and assessments.geometry is not None:
                # Convert to WGS84 if needed
                if assessments.crs != 'EPSG:4326':
                    assessments = assessments.to_crs('EPSG:4326')
                
                # Filter to Allston-Brighton using spatial join
                logger.info("  Filtering to Allston-Brighton...")
                ab_assessments = assessments[assessments.geometry.within(boundary_geom)]
                logger.info(f"  ✓ Found {len(ab_assessments):,} assessment records in Allston-Brighton")
            else:
                # Assessment data doesn't have geometry, filter by city/address
                logger.info("  Assessment data has no geometry, filtering by location...")
                
                # Filter by city if available
                if 'CITY' in assessments.columns:
                    boston_assessments = assessments[assessments['CITY'].str.contains('BOSTON', case=False, na=False)]
                    logger.info(f"  Found {len(boston_assessments):,} Boston assessment records")
                    
                    # Further filter by address patterns for Allston-Brighton
                    if 'SITE_ADDR' in boston_assessments.columns:
                        # Look for Allston-Brighton street patterns
                        ab_streets = ['ALLSTON', 'BRIGHTON', 'COMMONWEALTH', 'BEACON', 'HARVARD', 'BROOKLINE']
                        ab_mask = boston_assessments['SITE_ADDR'].str.contains('|'.join(ab_streets), case=False, na=False)
                        ab_assessments = boston_assessments[ab_mask]
                        logger.info(f"  ✓ Found {len(ab_assessments):,} Allston-Brighton assessment records")
                    else:
                        ab_assessments = boston_assessments
                        logger.info(f"  Using all Boston assessment records: {len(ab_assessments):,}")
                else:
                    ab_assessments = assessments
                    logger.info(f"  No city filter available, using all records: {len(ab_assessments):,}")
            
            # Get the most recent data (FY 2025)
            if 'FY' in ab_assessments.columns:
                latest_fy = ab_assessments['FY'].max()
                logger.info(f"  Latest fiscal year: {latest_fy}")
                
                # Filter to most recent year
                recent_assessments = ab_assessments[ab_assessments['FY'] == latest_fy]
                logger.info(f"  ✓ {len(recent_assessments):,} records from FY {latest_fy}")
            else:
                recent_assessments = ab_assessments
                logger.info("  No FY column found, using all records")
            
            # Save Allston-Brighton assessment data
            ab_assessments_file = Path("data/processed/gis_layers/allston_brighton_assessments.csv")
            recent_assessments.to_csv(ab_assessments_file, index=False)
            logger.info(f"  ✓ Saved to: {ab_assessments_file}")
            
            # Create summary statistics
            logger.info("\n3. Creating property summary...")
            
            # Property value statistics
            if 'TOTAL_VAL' in recent_assessments.columns:
                total_val_stats = recent_assessments['TOTAL_VAL'].describe()
                logger.info(f"\n  Property Value Statistics (FY {latest_fy}):")
                logger.info(f"    Count: {total_val_stats['count']:,.0f}")
                logger.info(f"    Mean: ${total_val_stats['mean']:,.0f}")
                logger.info(f"    Median: ${total_val_stats['50%']:,.0f}")
                logger.info(f"    Min: ${total_val_stats['min']:,.0f}")
                logger.info(f"    Max: ${total_val_stats['max']:,.0f}")
            
            # Property use analysis
            if 'USE_CODE' in recent_assessments.columns:
                use_counts = recent_assessments['USE_CODE'].value_counts().head(10)
                logger.info(f"\n  Top 10 Property Use Codes:")
                for use_code, count in use_counts.items():
                    logger.info(f"    {use_code}: {count:,} properties")
            
            # Zoning analysis
            if 'ZONING' in recent_assessments.columns:
                zoning_counts = recent_assessments['ZONING'].value_counts().head(10)
                logger.info(f"\n  Top 10 Zoning Classifications:")
                for zoning, count in zoning_counts.items():
                    logger.info(f"    {zoning}: {count:,} properties")
            
            # Building age analysis
            if 'YEAR_BUILT' in recent_assessments.columns:
                year_built_stats = recent_assessments['YEAR_BUILT'].describe()
                logger.info(f"\n  Building Age Statistics:")
                logger.info(f"    Mean year built: {year_built_stats['mean']:.0f}")
                logger.info(f"    Oldest building: {year_built_stats['min']:.0f}")
                logger.info(f"    Newest building: {year_built_stats['max']:.0f}")
            
            return recent_assessments
            
        except Exception as e:
            logger.error(f"  Error reading assessment data: {e}")
            return None
    else:
        logger.error("  Assessment database not found!")
        return None

def main():
    """Main function."""
    logger.info("ALLSTON-BRIGHTON PROPERTY DATA EXTRACTION")
    logger.info("="*60)
    
    # Extract property data
    ab_properties = extract_allston_brighton_properties()
    
    if ab_properties is not None:
        logger.info("\n" + "="*60)
        logger.info("EXTRACTION COMPLETE!")
        logger.info("="*60)
        logger.info(f"\n📊 Allston-Brighton Property Data Summary:")
        logger.info(f"   • Total properties: {len(ab_properties):,}")
        logger.info(f"   • Data files saved in: data/processed/gis_layers/")
        logger.info(f"   • Ready for analysis and mapping!")
        logger.info("="*60)
    else:
        logger.error("Failed to extract property data!")

if __name__ == "__main__":
    main()
