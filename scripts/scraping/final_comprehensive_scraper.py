#!/usr/bin/env python3
"""
Final comprehensive scraper that captures ALL the rich property information from Boston.gov
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

def scrape_comprehensive_parcel_details(parcel_id):
    """
    Comprehensive scraping that captures ALL property information
    """
    try:
        logger.info(f"🔍 Comprehensive scraping for parcel: {parcel_id}")
        
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        search_url = f"{base_url}?parcel={parcel_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
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
                'error': 'No details link found'
            }
        
        # Get the details page
        details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
        details_response = requests.get(details_url, headers=headers, timeout=30)
        details_response.raise_for_status()
        
        details_soup = BeautifulSoup(details_response.content, 'html.parser')
        
        # Extract comprehensive information
        property_data = extract_all_information(details_soup)
        property_data.update({
            'parcel_id': parcel_id,
            'scraped_successfully': True,
            'scrape_timestamp': pd.Timestamp.now().isoformat()
        })
        
        logger.info(f"✅ Successfully scraped comprehensive data for parcel {parcel_id}")
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
        # Get all text content
        text = soup.get_text()
        
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
                    logger.info(f"📊 Found value history table with {len(rows)-1} entries")
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

def test_comprehensive_scraping():
    """
    Test the comprehensive scraping with a few sample parcels
    """
    logger.info("🧪 Testing comprehensive Boston.gov parcel scraping...")
    
    # Test with a few sample parcels
    test_parcels = ['2204999000', '2205022000', '2102767000']
    
    results = []
    
    for i, parcel_id in enumerate(test_parcels):
        logger.info(f"\n{'='*60}")
        logger.info(f"Comprehensive Test {i+1}/{len(test_parcels)}")
        
        result = scrape_comprehensive_parcel_details(parcel_id)
        results.append(result)
        
        # Add delay between requests
        if i < len(test_parcels) - 1:
            logger.info("⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'data/processed/comprehensive_parcel_scraping_results.csv'
        results_df.to_csv(output_file, index=False)
        logger.info(f"✅ Comprehensive test completed! Results saved to: {output_file}")
        
        # Show summary of captured fields
        logger.info(f"\n📋 Summary of captured fields:")
        for col in results_df.columns:
            non_null_count = results_df[col].notna().sum()
            logger.info(f"  - {col}: {non_null_count}/{len(results_df)} parcels")
        
        # Show sample of rich data
        logger.info(f"\n📊 Sample comprehensive data:")
        sample_cols = ['parcel_id', 'address', 'property_type', 'owner_name', 'fy2025_total_assessed_value', 
                      'estimated_tax', 'residential_tax_rate', 'commercial_tax_rate', 'building_style', 
                      'total_rooms', 'bedrooms', 'bathrooms']
        available_cols = [col for col in sample_cols if col in results_df.columns]
        print(results_df[available_cols].to_string())
        
        return results_df
    else:
        logger.error("❌ No successful comprehensive scrapes")
        return None

if __name__ == "__main__":
    test_comprehensive_scraping()
