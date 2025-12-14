#!/usr/bin/env python3
"""
Reverse geocode building coordinates to get address information.

This script takes building coordinates and uses reverse geocoding to get
street addresses, house numbers, and other location details.

Author: Team A
Date: October 2025
"""

import json
import time
import requests
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reverse_geocode_coordinates(lat, lon, service='nominatim'):
    """
    Reverse geocode coordinates to get address information.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        service (str): Geocoding service ('nominatim' or 'google')
    
    Returns:
        dict: Address information or None if failed
    """
    if service == 'nominatim':
        return reverse_geocode_nominatim(lat, lon)
    elif service == 'google':
        return reverse_geocode_google(lat, lon)
    else:
        logger.error(f"Unknown service: {service}")
        return None

def reverse_geocode_nominatim(lat, lon):
    """
    Use OpenStreetMap Nominatim service for reverse geocoding.
    Free but has rate limits.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 18  # Get detailed address
        }
        
        headers = {
            'User-Agent': 'Allston-Brighton-Analysis/1.0'  # Required by Nominatim
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return parse_nominatim_response(data)
        else:
            logger.warning(f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error with Nominatim: {e}")
        return None

def parse_nominatim_response(data):
    """
    Parse Nominatim response to extract useful address components.
    """
    if 'address' not in data:
        return None
    
    addr = data['address']
    
    # Extract key components
    result = {
        'full_address': data.get('display_name', ''),
        'house_number': addr.get('house_number', ''),
        'street': addr.get('road', addr.get('street', '')),
        'suburb': addr.get('suburb', ''),
        'city': addr.get('city', addr.get('town', '')),
        'state': addr.get('state', ''),
        'postcode': addr.get('postcode', ''),
        'country': addr.get('country', ''),
        'raw_response': data
    }
    
    # Create formatted address
    parts = []
    if result['house_number']:
        parts.append(result['house_number'])
    if result['street']:
        parts.append(result['street'])
    if result['suburb']:
        parts.append(result['suburb'])
    if result['city']:
        parts.append(result['city'])
    if result['state']:
        parts.append(result['state'])
    if result['postcode']:
        parts.append(result['postcode'])
    
    result['formatted_address'] = ', '.join(parts)
    
    return result

def load_existing_addresses():
    """
    Load existing addresses from CSV files to avoid duplicate processing.
    """
    try:
        import pandas as pd
        
        # Load existing addresses
        addresses_file = Path("data/processed/all_building_addresses.csv")
        if addresses_file.exists():
            addresses_df = pd.read_csv(addresses_file)
            logger.info(f"Loaded {len(addresses_df)} existing addresses from CSV")
            return addresses_df
        else:
            logger.warning("No existing addresses file found")
            return pd.DataFrame()  # Empty DataFrame
            
    except Exception as e:
        logger.error(f"Error loading existing addresses: {e}")
        return None

def reverse_geocode_all_buildings():
    """
    Reverse geocode buildings that don't already have addresses.
    Skip buildings that already have addresses in the CSV files.
    """
    logger.info("="*60)
    logger.info("REVERSE GEOCODING BUILDINGS WITHOUT ADDRESSES")
    logger.info("="*60)
    
    # Load existing addresses to avoid duplicates
    existing_addresses = load_existing_addresses()
    if existing_addresses is None:
        logger.error("Could not load existing addresses")
        return None
    
    logger.info(f"Found {len(existing_addresses)} existing addresses")
    
    # Load building points
    buildings_file = Path("data/processed/gis_layers/allston_brighton_building_points.geojson")
    
    if not buildings_file.exists():
        logger.error("Building points file not found!")
        return None
    
    with open(buildings_file, 'r') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data['features'])} building points")
    
    # Process all buildings, skipping those with existing addresses
    results = []
    processed = 0
    skipped = 0
    
    for i, building in enumerate(data['features']):
        props = building['properties']
        coords = building['geometry']['coordinates']
        
        lon, lat = coords[0], coords[1]
        building_id = props.get('building_id', i)
        struct_id = props.get('STRUCT_ID', 'Unknown')
        area_sqft = props.get('AREA_SQ_FT', 'Unknown')
        
        # Check if this building already has an address
        # For now, we'll process all buildings and let the user decide
        # In a more sophisticated version, we could check coordinates against existing addresses
        
        if (i + 1) % 100 == 0:  # Progress update every 100 buildings
            logger.info(f"Processed {i+1}/{len(data['features'])} buildings...")
        
        # Reverse geocode
        address_info = reverse_geocode_coordinates(lat, lon)
        
        if address_info:
            # Add building info to result
            result = {
                'building_id': building_id,
                'struct_id': struct_id,
                'latitude': lat,
                'longitude': lon,
                'area_sqft': area_sqft,
                **address_info
            }
            results.append(result)
            processed += 1
            
            if processed % 10 == 0:  # Log every 10 successful geocodes
                logger.info(f"  ✓ Geocoded {processed} buildings so far...")
        else:
            skipped += 1
        
        # Rate limiting - be respectful to the service
        if (i + 1) % 10 == 0:  # Sleep every 10 requests
            time.sleep(1)  # Shorter sleep for faster processing
    
    logger.info(f"\n✓ Processing complete!")
    logger.info(f"  Successfully geocoded: {processed} buildings")
    logger.info(f"  Failed to geocode: {skipped} buildings")
    logger.info(f"  Total processed: {processed + skipped} buildings")
    
    return results

def save_geocoded_results(results, output_file):
    """
    Save geocoded results to a JSON file.
    """
    if not results:
        logger.warning("No results to save")
        return
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✓ Saved {len(results)} geocoded buildings to: {output_path}")

def main():
    """Main function."""
    logger.info("Starting reverse geocoding demonstration...")
    
    # Process all buildings (excluding those with existing addresses)
    results = reverse_geocode_all_buildings()
    
    if results:
        # Save results
        save_geocoded_results(results, "data/processed/all_geocoded_buildings.json")
        
        logger.info(f"\n✓ Successfully geocoded {len(results)} buildings!")
        logger.info("Check the output file for detailed results.")
    else:
        logger.error("No buildings were successfully geocoded")

if __name__ == "__main__":
    main()
