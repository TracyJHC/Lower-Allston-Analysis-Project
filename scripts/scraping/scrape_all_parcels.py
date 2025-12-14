#!/usr/bin/env python3
"""
Production script to scrape comprehensive property data from Boston.gov for all parcels
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re
import logging
from pathlib import Path
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/processed/parcel_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def scrape_comprehensive_parcel_details(parcel_id, session=None):
    """
    Comprehensive scraping that captures ALL property information
    """
    try:
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
            return {
                'parcel_id': parcel_id,
                'scraped_successfully': False,
                'error': 'No details link found'
            }
        
        # Get the details page
        details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
        if session is None:
            details_response = requests.get(details_url, headers=headers, timeout=30)
        else:
            details_response = session.get(details_url, headers=headers, timeout=30)
        
        details_response.raise_for_status()
        
        details_soup = BeautifulSoup(details_response.content, 'html.parser')
        
        # Extract comprehensive information
        property_data = extract_all_information(details_soup)
        property_data.update({
            'parcel_id': parcel_id,
            'scraped_successfully': True,
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        })
        
        return property_data
        
    except Exception as e:
        logger.error(f"Error scraping parcel {parcel_id}: {e}")
        return {
            'parcel_id': parcel_id,
            'scraped_successfully': False,
            'error': str(e),
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        }

def extract_all_information(soup):
    """
    Extract ALL property information from the Boston.gov details page
    """
    info = {}
    
    try:
        # Extract from tables (more reliable than regex)
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # Map all possible fields
                    if key_text == 'Parcel ID:':
                        info['parcel_id_display'] = value
                    elif key_text == 'Address:':
                        info['address'] = value
                    elif key_text == 'Property Type:':
                        info['property_type'] = value
                    elif key_text == 'Classification Code:':
                        info['classification_code'] = value
                    elif key_text == 'Lot Size:':
                        info['lot_size'] = value
                    elif key_text == 'Living Area:':
                        info['living_area'] = value
                    elif key_text == 'Year Built:':
                        info['year_built'] = value
                    elif 'Owner on' in key_text:
                        info['owner_name'] = value
                    elif key_text == "Owner's Mailing Address:":
                        info['owner_mailing_address'] = value
                    elif key_text == 'Residential Exemption:':
                        info['residential_exemption'] = value
                    elif key_text == 'Personal Exemption:':
                        info['personal_exemption'] = value
                    # Tax and Value fields
                    elif key_text == 'FY2025 Building value:':
                        info['fy2025_building_value'] = value
                    elif key_text == 'FY2025 Land Value:':
                        info['fy2025_land_value'] = value
                    elif key_text == 'FY2025 Total Assessed Value:':
                        info['fy2025_total_assessed_value'] = value
                    elif key_text == '- Residential:':
                        info['residential_tax_rate'] = value
                    elif key_text == '- Commercial:':
                        info['commercial_tax_rate'] = value
                    elif key_text == 'Estimated Tax:':
                        info['estimated_tax'] = value
                    elif key_text == 'Community Preservation:':
                        info['community_preservation'] = value
                    elif key_text == 'Total, First Half:':
                        info['total_first_half_tax'] = value
                    # Building attributes
                    elif key_text == 'Land Use:':
                        info['land_use'] = value
                    elif key_text == 'Style:':
                        info['building_style'] = value
                    elif key_text == 'Total Rooms:':
                        info['total_rooms'] = value
                    elif key_text == 'Bedrooms:':
                        info['bedrooms'] = value
                    elif key_text == 'Bathrooms:':
                        info['bathrooms'] = value
                    elif key_text == 'Half Bathrooms:':
                        info['half_bathrooms'] = value
                    elif key_text == 'Number of Kitchens:':
                        info['kitchens'] = value
                    elif key_text == 'Kitchen Type:':
                        info['kitchen_type'] = value
                    elif key_text == 'Fireplaces:':
                        info['fireplaces'] = value
                    elif key_text == 'AC Type:':
                        info['ac_type'] = value
                    elif key_text == 'Heat Type:':
                        info['heat_type'] = value
                    elif key_text == 'Interior Condition:':
                        info['interior_condition'] = value
                    elif key_text == 'Interior Finish:':
                        info['interior_finish'] = value
                    elif key_text == 'View:':
                        info['view'] = value
                    elif key_text == 'Grade:':
                        info['grade'] = value
                    elif key_text == 'Parking Spots:':
                        info['parking_spots'] = value
                    elif key_text == 'Story Height:':
                        info['story_height'] = value
                    elif key_text == 'Roof Cover:':
                        info['roof_cover'] = value
                    elif key_text == 'Roof Structure:':
                        info['roof_structure'] = value
                    elif key_text == 'Exterior Finish:':
                        info['exterior_finish'] = value
                    elif key_text == 'Exterior Condition:':
                        info['exterior_condition'] = value
                    elif key_text == 'Foundation:':
                        info['foundation'] = value
                    # Outbuildings
                    elif key_text == 'Type:':
                        info['outbuilding_type'] = value
                    elif key_text == 'Size/sqft:':
                        info['outbuilding_size'] = value
                    elif key_text == 'Quality:':
                        info['outbuilding_quality'] = value
                    elif key_text == 'Condition:':
                        info['outbuilding_condition'] = value
        
        # Extract value history
        value_history = extract_value_history_comprehensive(soup)
        if value_history:
            info['value_history'] = json.dumps(value_history)
        
        # Extract current owners (multiple owners)
        current_owners = extract_current_owners(soup)
        if current_owners:
            info['current_owners_list'] = json.dumps(current_owners)
        
        # Extract assessment date
        text = soup.get_text()
        assessment_date = extract_assessment_date(text)
        if assessment_date:
            info['assessment_date'] = assessment_date
        
        # Extract exemption notes
        exemption_notes = extract_exemption_notes(text)
        if exemption_notes:
            info['exemption_notes'] = exemption_notes
        
    except Exception as e:
        logger.error(f"Error extracting comprehensive info: {e}")
        info['extraction_error'] = str(e)
    
    return info

def extract_value_history_comprehensive(soup):
    """
    Extract complete value history from the page
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
                    # This is the value history table
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

def extract_current_owners(soup):
    """
    Extract current owners (can be multiple)
    """
    try:
        owners = []
        
        # Look for "Current Owner/s" section
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text(strip=True)
                    if 'Current Owner/s' in key_text:
                        # Found the owners section, collect all owner names
                        for owner_row in rows[rows.index(row)+1:]:
                            owner_cells = owner_row.find_all(['td', 'th'])
                            if len(owner_cells) >= 2:
                                owner_name = owner_cells[1].get_text(strip=True)
                                if owner_name and owner_name not in ['', 'Current Owner/s']:
                                    owners.append(owner_name)
                        break
        
        return owners if owners else None
        
    except Exception as e:
        logger.error(f"Error extracting current owners: {e}")
        return None

def extract_assessment_date(text):
    """
    Extract assessment date from text
    """
    try:
        # Look for "Assessment as of" pattern
        pattern = r'Assessment as of ([^,]+),'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        return None
    except:
        return None

def extract_exemption_notes(text):
    """
    Extract exemption and abatement notes
    """
    try:
        # Look for exemption notes
        if 'Applications for Abatements' in text:
            start = text.find('Applications for Abatements')
            end = text.find('Attributes', start)
            if end == -1:
                end = start + 200
            return text[start:end].strip()
        return None
    except:
        return None

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

def save_progress(results, output_file):
    """
    Save progress to CSV file
    """
    try:
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        logger.info(f"💾 Progress saved: {len(results)} parcels processed")
    except Exception as e:
        logger.error(f"Error saving progress: {e}")

def scrape_all_parcels():
    """
    Main function to scrape all parcels
    """
    logger.info("🚀 Starting comprehensive parcel scraping for all parcels...")
    
    # Load parcel list
    parcel_ids = load_parcel_list()
    if not parcel_ids:
        logger.error("❌ No parcel IDs found")
        return
    
    # Setup output file
    output_file = 'data/processed/all_parcels_comprehensive_data.csv'
    progress_file = 'data/processed/parcel_scraping_progress.csv'
    
    # Check if we have existing progress
    start_index = 0
    if os.path.exists(progress_file):
        try:
            progress_df = pd.read_csv(progress_file)
            start_index = len(progress_df)
            logger.info(f"📋 Resuming from index {start_index}")
        except:
            pass
    
    # Initialize results list
    results = []
    
    # Create session for connection pooling
    session = requests.Session()
    
    try:
        for i, parcel_id in enumerate(parcel_ids[start_index:], start=start_index):
            logger.info(f"🔍 Processing parcel {i+1}/{len(parcel_ids)}: {parcel_id}")
            
            # Scrape parcel details
            result = scrape_comprehensive_parcel_details(parcel_id, session)
            results.append(result)
            
            # Log success/failure
            if result.get('scraped_successfully'):
                logger.info(f"✅ Successfully scraped parcel {parcel_id}")
            else:
                logger.warning(f"⚠️ Failed to scrape parcel {parcel_id}: {result.get('error', 'Unknown error')}")
            
            # Save progress every 50 parcels
            if (i + 1) % 50 == 0:
                save_progress(results, progress_file)
                logger.info(f"📊 Progress: {i+1}/{len(parcel_ids)} parcels processed")
            
            # Add delay between requests to be respectful
            time.sleep(2)  # 2 second delay between requests
        
        # Save final results
        save_progress(results, output_file)
        logger.info(f"🎉 Scraping completed! Results saved to: {output_file}")
        
        # Generate summary
        results_df = pd.DataFrame(results)
        successful = results_df['scraped_successfully'].sum()
        failed = len(results_df) - successful
        
        logger.info(f"📊 Final Summary:")
        logger.info(f"  ✅ Successful: {successful}")
        logger.info(f"  ❌ Failed: {failed}")
        logger.info(f"  📈 Success Rate: {(successful/len(results_df)*100):.1f}%")
        
        # Show sample of captured fields
        logger.info(f"\n📋 Captured fields summary:")
        for col in results_df.columns:
            non_null_count = results_df[col].notna().sum()
            if non_null_count > 0:
                logger.info(f"  - {col}: {non_null_count}/{len(results_df)} parcels")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Scraping interrupted by user")
        save_progress(results, progress_file)
        logger.info(f"💾 Progress saved to: {progress_file}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        save_progress(results, progress_file)
        logger.info(f"💾 Progress saved to: {progress_file}")
    finally:
        session.close()

if __name__ == "__main__":
    scrape_all_parcels()
