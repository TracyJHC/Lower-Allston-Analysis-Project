#!/usr/bin/env python3
"""
Enrich all parcels with detailed property information from Boston.gov
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parcel_enrichment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def scrape_parcel_details(parcel_id, max_retries=3):
    """
    Scrape property details from Boston.gov for a given parcel ID
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"🔍 Scraping parcel {parcel_id} (attempt {attempt + 1})")
            
            # Boston.gov assessing search URL
            base_url = "https://www.cityofboston.gov/assessing/search/"
            search_url = f"{base_url}?parcel={parcel_id}"
            
            # Make request with headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(search_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the details link
            details_link = soup.find('a', href=lambda x: x and 'pid=' in x)
            if not details_link:
                logger.warning(f"No details link found for parcel {parcel_id}")
                return {
                    'parcel_id': parcel_id,
                    'scraped_successfully': False,
                    'error': 'No details link found',
                    'scrape_timestamp': datetime.now().isoformat()
                }
            
            # Get the details page
            details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
            details_response = requests.get(details_url, headers=headers, timeout=30)
            details_response.raise_for_status()
            
            details_soup = BeautifulSoup(details_response.content, 'html.parser')
            
            # Extract property information
            property_data = extract_property_details(details_soup)
            property_data.update({
                'parcel_id': parcel_id,
                'scraped_successfully': True,
                'scrape_timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"✅ Successfully scraped parcel {parcel_id}")
            return property_data
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed for parcel {parcel_id} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return {
                    'parcel_id': parcel_id,
                    'scraped_successfully': False,
                    'error': f'Request failed: {str(e)}',
                    'scrape_timestamp': datetime.now().isoformat()
                }
            time.sleep(5)  # Wait before retry
            
        except Exception as e:
            logger.error(f"Unexpected error for parcel {parcel_id}: {e}")
            return {
                'parcel_id': parcel_id,
                'scraped_successfully': False,
                'error': str(e),
                'scrape_timestamp': datetime.now().isoformat()
            }

def extract_property_details(soup):
    """
    Extract property details from the Boston.gov details page
    """
    details = {}
    
    try:
        # Get all text content
        text = soup.get_text()
        
        # Extract key information using regex patterns
        import re
        
        patterns = {
            'address': r'Address:\s*([^\n\r]+)',
            'property_type': r'Property Type:\s*([^\n\r]+)',
            'classification_code': r'Classification Code:\s*([^\n\r]+)',
            'lot_size': r'Lot Size:\s*([^\n\r]+)',
            'living_area': r'Living Area:\s*([^\n\r]+)',
            'year_built': r'Year Built:\s*([^\n\r]+)',
            'owner_name': r'Owner on[^:]*:\s*([^\n\r]+)',
            'owner_mailing_address': r'Owner\'s Mailing Address:\s*([^\n\r]+)',
            'residential_exemption': r'Residential Exemption:\s*([^\n\r]+)',
            'personal_exemption': r'Personal Exemption:\s*([^\n\r]+)',
            'building_value': r'Building value:\s*([^\n\r]+)',
            'land_value': r'Land Value:\s*([^\n\r]+)',
            'total_assessed_value': r'Total Assessed Value:\s*([^\n\r]+)',
            'estimated_tax': r'Estimated Tax:\s*([^\n\r]+)',
            'community_preservation': r'Community Preservation:\s*([^\n\r]+)',
            'total_first_half_tax': r'Total, First Half:\s*([^\n\r]+)',
            # Additional tax and value information
            'fiscal_year_building_value': r'FY\d+ Building value:\s*([^\n\r]+)',
            'fiscal_year_land_value': r'FY\d+ Land Value:\s*([^\n\r]+)',
            'fiscal_year_total_value': r'FY\d+ Total Assessed Value:\s*([^\n\r]+)',
            'residential_tax_rate': r'Residential:\s*([^\n\r]+)',
            'commercial_tax_rate': r'Commercial:\s*([^\n\r]+)',
            'assessment_date': r'Assessment as of[^:]*:\s*([^\n\r]+)',
            'statutory_lien_date': r'statutory lien date[^\n]*',
            # Owner information
            'current_owners': r'Current Owner/s\s*([^\n\r]+(?:\n[^\n\r]+)*)',
            'owner_trustees': r'TRUSTEE[^\n\r]*',
            # Exemption information
            'abatement_eligibility': r'This type of parcel is not eligible for[^\n\r]*',
            'exemption_notes': r'Applications for Abatements[^\n\r]*'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                details[key] = match.group(1).strip()
        
        # Also try to extract from tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Map table keys to our fields
                    if 'address' in key_text:
                        details['address'] = value
                    elif 'property type' in key_text:
                        details['property_type'] = value
                    elif 'classification code' in key_text:
                        details['classification_code'] = value
                    elif 'lot size' in key_text:
                        details['lot_size'] = value
                    elif 'living area' in key_text:
                        details['living_area'] = value
                    elif 'year built' in key_text:
                        details['year_built'] = value
                    elif 'owner' in key_text and 'mailing' not in key_text:
                        details['owner_name'] = value
                    elif 'mailing address' in key_text:
                        details['owner_mailing_address'] = value
                    elif 'residential exemption' in key_text:
                        details['residential_exemption'] = value
                    elif 'personal exemption' in key_text:
                        details['personal_exemption'] = value
                    elif 'building value' in key_text:
                        details['building_value'] = value
                    elif 'land value' in key_text:
                        details['land_value'] = value
                    elif 'total assessed value' in key_text:
                        details['total_assessed_value'] = value
                    elif 'estimated tax' in key_text:
                        details['estimated_tax'] = value
                    elif 'community preservation' in key_text:
                        details['community_preservation'] = value
                    elif 'total, first half' in key_text:
                        details['total_first_half_tax'] = value
                    # Additional tax and value fields
                    elif 'fy' in key_text and 'building value' in key_text:
                        details['fiscal_year_building_value'] = value
                    elif 'fy' in key_text and 'land value' in key_text:
                        details['fiscal_year_land_value'] = value
                    elif 'fy' in key_text and 'total assessed value' in key_text:
                        details['fiscal_year_total_value'] = value
                    elif 'residential' in key_text and 'rate' in key_text:
                        details['residential_tax_rate'] = value
                    elif 'commercial' in key_text and 'rate' in key_text:
                        details['commercial_tax_rate'] = value
                    elif 'assessment as of' in key_text:
                        details['assessment_date'] = value
                    elif 'current owner' in key_text:
                        details['current_owners'] = value
                    elif 'trustee' in key_text:
                        details['owner_trustees'] = value
                    elif 'not eligible' in key_text:
                        details['abatement_eligibility'] = value
                    elif 'applications for abatements' in key_text:
                        details['exemption_notes'] = value
        
        # Extract value history if available
        value_history = extract_value_history(soup)
        if value_history:
            details['value_history'] = json.dumps(value_history)
            
    except Exception as e:
        logger.error(f"Error extracting property details: {e}")
        details['extraction_error'] = str(e)
    
    return details

def extract_value_history(soup):
    """
    Extract value history from the page
    """
    try:
        value_history = []
        
        # Look for value history table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 1:
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
        
        # Also try to extract from text patterns if table extraction failed
        if not value_history:
            text = soup.get_text()
            import re
            
            # Look for value history patterns in text
            history_pattern = r'(\d{4})\s+([^\s]+)\s+(\$[\d,]+\.?\d*)'
            matches = re.findall(history_pattern, text)
            
            for match in matches:
                year, prop_type, value = match
                if year.isdigit() and int(year) >= 1980:  # Reasonable year range
                    value_history.append({
                        'fiscal_year': int(year),
                        'property_type': prop_type,
                        'assessed_value': value
                    })
        
        return value_history if value_history else None
        
    except Exception as e:
        logger.error(f"Error extracting value history: {e}")
        return None

def enrich_all_parcels():
    """
    Main function to enrich all parcels with Boston.gov data
    """
    logger.info("🚀 Starting comprehensive parcel enrichment...")
    
    # Load building-parcel mapping
    mapping_file = 'data/processed/gis_layers/building_parcel_mapping.csv'
    if not os.path.exists(mapping_file):
        logger.error(f"Mapping file not found: {mapping_file}")
        return None
    
    df = pd.read_csv(mapping_file)
    logger.info(f"📊 Loaded {len(df):,} building-parcel mappings")
    
    # Get unique parcel IDs
    unique_parcels = df['OFFICIAL_PAR_ID'].dropna().unique()
    logger.info(f"🏠 Found {len(unique_parcels):,} unique parcels to enrich")
    
    # Check if we already have some enriched data
    enriched_file = 'data/processed/gis_layers/enriched_parcel_details.csv'
    existing_parcels = set()
    
    if os.path.exists(enriched_file):
        try:
            existing_df = pd.read_csv(enriched_file)
            existing_parcels = set(existing_df['parcel_id'].astype(str))
            logger.info(f"📋 Found existing enriched data for {len(existing_parcels):,} parcels")
        except:
            logger.info("📋 No existing enriched data found")
    
    # Filter out already processed parcels
    parcels_to_process = []
    for parcel_id in unique_parcels:
        clean_parcel_id = str(int(float(parcel_id)))
        if clean_parcel_id not in existing_parcels:
            parcels_to_process.append(clean_parcel_id)
    
    logger.info(f"🔄 Need to process {len(parcels_to_process):,} new parcels")
    
    if not parcels_to_process:
        logger.info("✅ All parcels already processed!")
        return pd.read_csv(enriched_file) if os.path.exists(enriched_file) else None
    
    # Process parcels in batches
    batch_size = 50  # Process in smaller batches
    delay_between_requests = 2  # 2 seconds between requests
    enriched_data = []
    
    # Load existing data if available
    if os.path.exists(enriched_file):
        try:
            existing_df = pd.read_csv(enriched_file)
            enriched_data = existing_df.to_dict('records')
            logger.info(f"📋 Loaded {len(enriched_data):,} existing records")
        except:
            logger.info("📋 Starting fresh")
    
    # Process new parcels
    for i, parcel_id in enumerate(parcels_to_process):
        try:
            logger.info(f"Processing parcel {i+1}/{len(parcels_to_process)}: {parcel_id}")
            
            # Scrape property details
            parcel_details = scrape_parcel_details(parcel_id)
            enriched_data.append(parcel_details)
            
            # Save progress every 10 parcels
            if (i + 1) % 10 == 0:
                temp_df = pd.DataFrame(enriched_data)
                temp_df.to_csv(enriched_file, index=False)
                logger.info(f"💾 Saved progress: {len(enriched_data):,} parcels processed")
            
            # Add delay between requests
            if i < len(parcels_to_process) - 1:
                time.sleep(delay_between_requests)
                
        except Exception as e:
            logger.error(f"Error processing parcel {parcel_id}: {e}")
            enriched_data.append({
                'parcel_id': parcel_id,
                'scraped_successfully': False,
                'error': str(e),
                'scrape_timestamp': datetime.now().isoformat()
            })
    
    # Save final results
    enriched_df = pd.DataFrame(enriched_data)
    enriched_df.to_csv(enriched_file, index=False)
    
    # Generate summary
    successful_scrapes = enriched_df['scraped_successfully'].sum()
    logger.info(f"✅ Enrichment completed!")
    logger.info(f"📊 Successfully scraped: {successful_scrapes:,}/{len(enriched_df):,} parcels")
    logger.info(f"💾 Results saved to: {enriched_file}")
    
    # Show sample of successful scrapes
    successful_data = enriched_df[enriched_df['scraped_successfully'] == True]
    if len(successful_data) > 0:
        logger.info("📋 Sample of enriched data:")
        sample_cols = ['parcel_id', 'address', 'property_type', 'owner_name', 'total_assessed_value']
        available_cols = [col for col in sample_cols if col in successful_data.columns]
        print(successful_data[available_cols].head().to_string())
    
    return enriched_df

if __name__ == "__main__":
    enriched_data = enrich_all_parcels()
