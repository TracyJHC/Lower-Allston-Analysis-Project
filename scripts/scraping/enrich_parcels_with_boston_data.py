#!/usr/bin/env python3
"""
Enrich parcel data by scraping property details from Boston.gov
"""

import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import urlencode
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def scrape_parcel_details(parcel_id):
    """
    Scrape property details from Boston.gov for a given parcel ID
    """
    try:
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        
        # Search parameters
        params = {'parcel': parcel_id}
        search_url = f"{base_url}?{urlencode(params)}"
        
        logger.info(f"Fetching details for parcel {parcel_id}")
        
        # Make request with headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract property details
        property_data = {
            'parcel_id': parcel_id,
            'scraped_successfully': True,
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Look for the details link
        details_link = soup.find('a', href=lambda x: x and 'pid=' in x)
        if not details_link:
            logger.warning(f"No details link found for parcel {parcel_id}")
            return {**property_data, 'scraped_successfully': False}
        
        # Get the details page
        details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
        details_response = requests.get(details_url, headers=headers, timeout=30)
        details_response.raise_for_status()
        
        details_soup = BeautifulSoup(details_response.content, 'html.parser')
        
        # Extract property information from the details page
        property_data.update(extract_property_details(details_soup))
        
        return property_data
        
    except Exception as e:
        logger.error(f"Error scraping parcel {parcel_id}: {e}")
        return {
            'parcel_id': parcel_id,
            'scraped_successfully': False,
            'error': str(e),
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        }

def extract_property_details(soup):
    """
    Extract property details from the Boston.gov details page
    """
    details = {}
    
    try:
        # Find the main content table
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower().replace(':', '')
                    value = cells[1].get_text(strip=True)
                    
                    # Map common fields
                    if 'address' in key:
                        details['address'] = value
                    elif 'property type' in key:
                        details['property_type'] = value
                    elif 'classification code' in key:
                        details['classification_code'] = value
                    elif 'lot size' in key:
                        details['lot_size'] = value
                    elif 'living area' in key:
                        details['living_area'] = value
                    elif 'year built' in key:
                        details['year_built'] = value
                    elif 'owner' in key and 'mailing' not in key:
                        details['owner_name'] = value
                    elif 'mailing address' in key:
                        details['owner_mailing_address'] = value
                    elif 'residential exemption' in key:
                        details['residential_exemption'] = value
                    elif 'personal exemption' in key:
                        details['personal_exemption'] = value
                    elif 'building value' in key:
                        details['building_value'] = value
                    elif 'land value' in key:
                        details['land_value'] = value
                    elif 'total assessed value' in key:
                        details['total_assessed_value'] = value
                    elif 'estimated tax' in key:
                        details['estimated_tax'] = value
                    elif 'community preservation' in key:
                        details['community_preservation'] = value
                    elif 'total, first half' in key:
                        details['total_first_half_tax'] = value
        
        # Extract value history if available
        value_history = extract_value_history(soup)
        if value_history:
            details['value_history'] = value_history
            
    except Exception as e:
        logger.error(f"Error extracting property details: {e}")
        details['extraction_error'] = str(e)
    
    return details

def extract_value_history(soup):
    """
    Extract value history from the page
    """
    try:
        # Look for value history table
        value_history = []
        
        # Find tables that might contain value history
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:  # Has header and data rows
                # Check if this looks like a value history table
                header_row = rows[0]
                header_text = header_row.get_text().lower()
                if 'fiscal year' in header_text and 'assessed value' in header_text:
                    # This is likely the value history table
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            try:
                                year = cells[0].get_text(strip=True)
                                prop_type = cells[1].get_text(strip=True)
                                value = cells[2].get_text(strip=True)
                                
                                if year.isdigit() and value.startswith('$'):
                                    value_history.append({
                                        'fiscal_year': int(year),
                                        'property_type': prop_type,
                                        'assessed_value': value
                                    })
                            except:
                                continue
                    break
        
        return value_history if value_history else None
        
    except Exception as e:
        logger.error(f"Error extracting value history: {e}")
        return None

def enrich_parcels_with_boston_data():
    """
    Main function to enrich parcel data with Boston.gov details
    """
    logger.info("🚀 Starting parcel enrichment process...")
    
    # Load building-parcel mapping
    mapping_file = 'data/processed/gis_layers/building_parcel_mapping.csv'
    df = pd.read_csv(mapping_file)
    
    logger.info(f"📊 Loaded {len(df):,} building-parcel mappings")
    
    # Get unique parcel IDs
    unique_parcels = df['OFFICIAL_PAR_ID'].dropna().unique()
    logger.info(f"🏠 Found {len(unique_parcels):,} unique parcels to enrich")
    
    # Create results list
    enriched_data = []
    
    # Process parcels in batches
    batch_size = 10  # Small batches to be respectful
    delay_between_requests = 2  # 2 seconds between requests
    
    for i, parcel_id in enumerate(unique_parcels):
        try:
            # Clean parcel ID (remove .0 if present)
            clean_parcel_id = str(int(float(parcel_id)))
            
            logger.info(f"Processing parcel {i+1}/{len(unique_parcels)}: {clean_parcel_id}")
            
            # Scrape property details
            parcel_details = scrape_parcel_details(clean_parcel_id)
            enriched_data.append(parcel_details)
            
            # Add delay between requests to be respectful
            if i < len(unique_parcels) - 1:  # Don't delay after the last request
                time.sleep(delay_between_requests)
                
        except Exception as e:
            logger.error(f"Error processing parcel {parcel_id}: {e}")
            enriched_data.append({
                'parcel_id': parcel_id,
                'scraped_successfully': False,
                'error': str(e),
                'scrape_timestamp': pd.Timestamp.now().isoformat()
            })
    
    # Save enriched data
    enriched_df = pd.DataFrame(enriched_data)
    output_file = 'data/processed/gis_layers/enriched_parcel_details.csv'
    enriched_df.to_csv(output_file, index=False)
    
    # Generate summary
    successful_scrapes = enriched_df['scraped_successfully'].sum()
    logger.info(f"✅ Enrichment completed!")
    logger.info(f"📊 Successfully scraped: {successful_scrapes:,}/{len(enriched_df):,} parcels")
    logger.info(f"💾 Results saved to: {output_file}")
    
    # Show sample of successful scrapes
    successful_data = enriched_df[enriched_df['scraped_successfully'] == True]
    if len(successful_data) > 0:
        logger.info("📋 Sample of enriched data:")
        sample_cols = ['parcel_id', 'address', 'property_type', 'owner_name', 'total_assessed_value']
        available_cols = [col for col in sample_cols if col in successful_data.columns]
        print(successful_data[available_cols].head().to_string())
    
    return enriched_df

if __name__ == "__main__":
    enriched_data = enrich_parcels_with_boston_data()
