#!/usr/bin/env python3
"""
Test the fixed scraper with a few sample parcels
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_comprehensive_parcel_details(parcel_id, session=None):
    """
    Comprehensive scraping that captures ALL property information
    """
    try:
        logger.info(f"🔍 Testing scraping for parcel: {parcel_id}")
        
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        search_url = f"{base_url}?parcel={parcel_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Use session for connection pooling
        if session is None:
            response = requests.get(search_url, headers=headers, timeout=30)
        else:
            response = session.get(search_url, headers=headers, timeout=30)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the details link
        details_link = soup.find('a', href=lambda x: x and 'pid=' in x)
        if not details_link:
            logger.warning(f"No details link found for parcel {parcel_id}")
            return {
                'parcel_id': parcel_id,
                'scraped_successfully': False,
                'error': 'No details link found'
            }
        
        logger.info(f"✅ Found details link: {details_link['href']}")
        
        # Get the details page
        details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
        if session is None:
            details_response = requests.get(details_url, headers=headers, timeout=30)
        else:
            details_response = session.get(details_url, headers=headers, timeout=30)
        
        details_response.raise_for_status()
        
        details_soup = BeautifulSoup(details_response.content, 'html.parser')
        
        # Extract basic information to test
        info = {
            'parcel_id': parcel_id,
            'scraped_successfully': True,
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Extract basic fields
        tables = details_soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if key_text == 'Address:':
                        info['address'] = value
                    elif key_text == 'Property Type:':
                        info['property_type'] = value
                    elif key_text == 'FY2025 Total Assessed Value:':
                        info['fy2025_total_assessed_value'] = value
        
        logger.info(f"✅ Successfully scraped parcel {parcel_id}")
        return info
        
    except Exception as e:
        logger.error(f"Error scraping parcel {parcel_id}: {e}")
        return {
            'parcel_id': parcel_id,
            'scraped_successfully': False,
            'error': str(e),
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        }

def load_parcel_list():
    """
    Load the list of unique parcel IDs from building_parcel_mapping.csv
    """
    try:
        mapping_file = 'data/processed/gis_layers/building_parcel_mapping.csv'
        df = pd.read_csv(mapping_file)
        
        # Get unique parcel IDs and convert to proper format
        unique_parcels = df['OFFICIAL_PAR_ID'].dropna().unique()
        
        # Convert to string and remove .0 suffix if present
        parcel_ids = []
        for parcel_id in unique_parcels:
            # Convert to string and remove .0 if it exists
            parcel_str = str(parcel_id)
            if parcel_str.endswith('.0'):
                parcel_str = parcel_str[:-2]
            parcel_ids.append(parcel_str)
        
        logger.info(f"📊 Loaded {len(parcel_ids)} unique parcel IDs")
        logger.info(f"📋 Sample parcel IDs: {parcel_ids[:5]}")
        
        return parcel_ids
        
    except Exception as e:
        logger.error(f"Error loading parcel list: {e}")
        return []

def test_fixed_scraper():
    """
    Test the fixed scraper with a few sample parcels
    """
    logger.info("🧪 Testing fixed scraper...")
    
    # Load parcel list
    parcel_ids = load_parcel_list()
    if not parcel_ids:
        logger.error("❌ No parcel IDs found")
        return
    
    # Test with first 3 parcels
    test_parcels = parcel_ids[:3]
    logger.info(f"🔍 Testing with parcels: {test_parcels}")
    
    results = []
    session = requests.Session()
    
    try:
        for i, parcel_id in enumerate(test_parcels):
            logger.info(f"\n{'='*50}")
            logger.info(f"Test {i+1}/{len(test_parcels)}")
            
            result = scrape_comprehensive_parcel_details(parcel_id, session)
            results.append(result)
            
            # Add delay between requests
            if i < len(test_parcels) - 1:
                logger.info("⏳ Waiting 3 seconds...")
                time.sleep(3)
        
        # Save results
        if results:
            results_df = pd.DataFrame(results)
            output_file = 'data/processed/test_fixed_scraper_results.csv'
            results_df.to_csv(output_file, index=False)
            logger.info(f"✅ Test completed! Results saved to: {output_file}")
            
            # Show summary
            successful = results_df['scraped_successfully'].sum()
            failed = len(results_df) - successful
            logger.info(f"📊 Summary: {successful} successful, {failed} failed")
            
            # Show sample data
            logger.info(f"\n📋 Sample results:")
            print(results_df[['parcel_id', 'address', 'property_type', 'fy2025_total_assessed_value', 'scraped_successfully']].to_string())
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    test_fixed_scraper()
