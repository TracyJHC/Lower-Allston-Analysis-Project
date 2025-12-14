#!/usr/bin/env python3
"""
Batch reverse geocoding for all buildings.
Processes buildings in batches to avoid overwhelming the service.
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reverse_geocode_batch(lat, lon):
    """Simple reverse geocoding using Nominatim API."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1&zoom=18"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Allston-Brighton-Analysis/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        return data
        
    except Exception as e:
        logger.warning(f"Geocoding failed for [{lat}, {lon}]: {e}")
        return None

def process_buildings_batch(start_idx=0, batch_size=100):
    """
    Process a batch of buildings starting from start_idx.
    This allows you to process buildings in smaller chunks.
    """
    logger.info(f"Processing buildings {start_idx} to {start_idx + batch_size - 1}")
    
    # Load building points
    buildings_file = Path("data/processed/gis_layers/allston_brighton_building_points.geojson")
    
    with open(buildings_file, 'r') as f:
        data = json.load(f)
    
    total_buildings = len(data['features'])
    end_idx = min(start_idx + batch_size, total_buildings)
    
    logger.info(f"Processing {end_idx - start_idx} buildings (total: {total_buildings})")
    
    results = []
    successful = 0
    failed = 0
    
    for i in range(start_idx, end_idx):
        building = data['features'][i]
        props = building['properties']
        coords = building['geometry']['coordinates']
        
        lon, lat = coords[0], coords[1]
        building_id = props.get('building_id', i)
        struct_id = props.get('STRUCT_ID', 'Unknown')
        area_sqft = props.get('AREA_SQ_FT', 'Unknown')
        
        # Progress update
        if (i - start_idx + 1) % 10 == 0:
            logger.info(f"  Processed {i - start_idx + 1}/{end_idx - start_idx} in this batch")
        
        # Reverse geocode
        address_data = reverse_geocode_batch(lat, lon)
        
        if address_data and 'address' in address_data:
            addr = address_data['address']
            
            result = {
                'building_id': building_id,
                'struct_id': struct_id,
                'latitude': lat,
                'longitude': lon,
                'area_sqft': area_sqft,
                'full_address': address_data.get('display_name', ''),
                'house_number': addr.get('house_number', ''),
                'street': addr.get('road', addr.get('street', '')),
                'suburb': addr.get('suburb', ''),
                'city': addr.get('city', addr.get('town', '')),
                'state': addr.get('state', ''),
                'postcode': addr.get('postcode', ''),
                'country': addr.get('country', '')
            }
            
            results.append(result)
            successful += 1
            
            if successful % 5 == 0:
                logger.info(f"    ✓ Successfully geocoded {successful} buildings in this batch")
        else:
            failed += 1
        
        # Rate limiting - sleep every 5 requests
        if (i - start_idx + 1) % 5 == 0:
            time.sleep(2)
    
    logger.info(f"Batch complete: {successful} successful, {failed} failed")
    return results

def main():
    """Main function - process all buildings in batches."""
    logger.info("="*60)
    logger.info("FULL BATCH REVERSE GEOCODING - ALL BUILDINGS")
    logger.info("="*60)
    
    # Process all 10,282 buildings in batches of 100
    all_results = []
    batch_size = 100
    total_buildings = 10282
    
    for start_idx in range(0, total_buildings, batch_size):
        batch_num = (start_idx // batch_size) + 1
        total_batches = (total_buildings + batch_size - 1) // batch_size
        
        logger.info(f"\n{'='*50}")
        logger.info(f"PROCESSING BATCH {batch_num}/{total_batches}")
        logger.info(f"Buildings {start_idx} to {min(start_idx + batch_size, total_buildings) - 1}")
        logger.info(f"{'='*50}")
        
        # Process this batch
        batch_results = process_buildings_batch(start_idx, batch_size)
        
        if batch_results:
            all_results.extend(batch_results)
            logger.info(f"✓ Batch {batch_num} complete: {len(batch_results)} buildings geocoded")
        else:
            logger.warning(f"✗ Batch {batch_num} failed or returned no results")
        
        # Save intermediate results every 5 batches
        if batch_num % 5 == 0:
            intermediate_file = f"data/processed/intermediate_geocoded_batch_{batch_num}.json"
            with open(intermediate_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            logger.info(f"💾 Saved intermediate results: {len(all_results)} total buildings")
        
        # Longer pause between batches to be respectful
        if batch_num < total_batches:
            logger.info("⏳ Waiting 30 seconds before next batch...")
            time.sleep(30)
    
    # Final save of all results
    if all_results:
        output_file = Path("data/processed/all_geocoded_buildings_final.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        logger.info(f"\n🎉 ALL PROCESSING COMPLETE!")
        logger.info(f"✓ Successfully geocoded {len(all_results)} out of {total_buildings} buildings")
        logger.info(f"✓ Final results saved to: {output_file}")
        logger.info(f"📊 Success rate: {len(all_results)/total_buildings*100:.1f}%")
        
        # Show sample results
        logger.info(f"\nSample addresses found:")
        for i, result in enumerate(all_results[:5]):
            logger.info(f"  {i+1}. {result.get('full_address', 'No address')}")
    else:
        logger.error("No buildings were successfully geocoded")

if __name__ == "__main__":
    main()
