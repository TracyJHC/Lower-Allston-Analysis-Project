#!/usr/bin/env python3
"""
Test enhanced scraping to capture all the rich property information
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json
import re

def test_enhanced_scrape(parcel_id):
    """
    Test enhanced scraping with all the additional fields
    """
    print(f"🔍 Enhanced scraping for parcel: {parcel_id}")
    
    try:
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        search_url = f"{base_url}?parcel={parcel_id}"
        
        print(f"📡 Fetching: {search_url}")
        
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=30)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the details link
            details_link = soup.find('a', href=lambda x: x and 'pid=' in x)
            if details_link:
                print(f"✅ Found details link: {details_link['href']}")
                
                # Get the details page
                details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
                print(f"📡 Fetching details: {details_url}")
                
                details_response = requests.get(details_url, headers=headers, timeout=30)
                if details_response.status_code == 200:
                    details_soup = BeautifulSoup(details_response.content, 'html.parser')
                    
                    # Extract comprehensive information
                    property_info = extract_comprehensive_info(details_soup)
                    print(f"📋 Enhanced extracted info:")
                    print(json.dumps(property_info, indent=2))
                    return property_info
                else:
                    print(f"❌ Details page failed: {details_response.status_code}")
            else:
                print("❌ No details link found")
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def extract_comprehensive_info(soup):
    """
    Extract comprehensive property information including all the fields you mentioned
    """
    info = {}
    
    try:
        # Get all text content
        text = soup.get_text()
        
        # Enhanced patterns to capture all the information you mentioned
        patterns = {
            # Basic property info
            'address': r'Address:\s*([^\n\r]+)',
            'property_type': r'Property Type:\s*([^\n\r]+)',
            'classification_code': r'Classification Code:\s*([^\n\r]+)',
            'lot_size': r'Lot Size:\s*([^\n\r]+)',
            'living_area': r'Living Area:\s*([^\n\r]+)',
            'year_built': r'Year Built:\s*([^\n\r]+)',
            
            # Owner information
            'owner_name': r'Owner on[^:]*:\s*([^\n\r]+)',
            'owner_mailing_address': r'Owner\'s Mailing Address:\s*([^\n\r]+)',
            'current_owners': r'Current Owner/s\s*([^\n\r]+(?:\n[^\n\r]+)*)',
            'owner_trustees': r'TRUSTEE[^\n\r]*',
            
            # Exemptions
            'residential_exemption': r'Residential Exemption:\s*([^\n\r]+)',
            'personal_exemption': r'Personal Exemption:\s*([^\n\r]+)',
            'abatement_eligibility': r'This type of parcel is not eligible for[^\n\r]*',
            'exemption_notes': r'Applications for Abatements[^\n\r]*',
            
            # Current values
            'building_value': r'Building value:\s*([^\n\r]+)',
            'land_value': r'Land Value:\s*([^\n\r]+)',
            'total_assessed_value': r'Total Assessed Value:\s*([^\n\r]+)',
            
            # Fiscal year specific values
            'fiscal_year_building_value': r'FY\d+ Building value:\s*([^\n\r]+)',
            'fiscal_year_land_value': r'FY\d+ Land Value:\s*([^\n\r]+)',
            'fiscal_year_total_value': r'FY\d+ Total Assessed Value:\s*([^\n\r]+)',
            
            # Tax rates
            'residential_tax_rate': r'Residential:\s*([^\n\r]+)',
            'commercial_tax_rate': r'Commercial:\s*([^\n\r]+)',
            
            # Tax calculations
            'estimated_tax': r'Estimated Tax:\s*([^\n\r]+)',
            'community_preservation': r'Community Preservation:\s*([^\n\r]+)',
            'total_first_half_tax': r'Total, First Half:\s*([^\n\r]+)',
            
            # Assessment dates
            'assessment_date': r'Assessment as of[^:]*:\s*([^\n\r]+)',
            'statutory_lien_date': r'statutory lien date[^\n]*',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                info[key] = match.group(1).strip()
        
        # Also extract from tables for more comprehensive coverage
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key_text = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Map all possible table fields
                    if 'address' in key_text:
                        info['address'] = value
                    elif 'property type' in key_text:
                        info['property_type'] = value
                    elif 'classification code' in key_text:
                        info['classification_code'] = value
                    elif 'lot size' in key_text:
                        info['lot_size'] = value
                    elif 'living area' in key_text:
                        info['living_area'] = value
                    elif 'year built' in key_text:
                        info['year_built'] = value
                    elif 'owner' in key_text and 'mailing' not in key_text:
                        info['owner_name'] = value
                    elif 'mailing address' in key_text:
                        info['owner_mailing_address'] = value
                    elif 'residential exemption' in key_text:
                        info['residential_exemption'] = value
                    elif 'personal exemption' in key_text:
                        info['personal_exemption'] = value
                    elif 'building value' in key_text:
                        info['building_value'] = value
                    elif 'land value' in key_text:
                        info['land_value'] = value
                    elif 'total assessed value' in key_text:
                        info['total_assessed_value'] = value
                    elif 'estimated tax' in key_text:
                        info['estimated_tax'] = value
                    elif 'community preservation' in key_text:
                        info['community_preservation'] = value
                    elif 'total, first half' in key_text:
                        info['total_first_half_tax'] = value
                    elif 'fy' in key_text and 'building value' in key_text:
                        info['fiscal_year_building_value'] = value
                    elif 'fy' in key_text and 'land value' in key_text:
                        info['fiscal_year_land_value'] = value
                    elif 'fy' in key_text and 'total assessed value' in key_text:
                        info['fiscal_year_total_value'] = value
                    elif 'residential' in key_text and 'rate' in key_text:
                        info['residential_tax_rate'] = value
                    elif 'commercial' in key_text and 'rate' in key_text:
                        info['commercial_tax_rate'] = value
                    elif 'assessment as of' in key_text:
                        info['assessment_date'] = value
                    elif 'current owner' in key_text:
                        info['current_owners'] = value
                    elif 'trustee' in key_text:
                        info['owner_trustees'] = value
                    elif 'not eligible' in key_text:
                        info['abatement_eligibility'] = value
                    elif 'applications for abatements' in key_text:
                        info['exemption_notes'] = value
        
        # Extract value history
        value_history = extract_value_history_enhanced(soup)
        if value_history:
            info['value_history'] = value_history
            
    except Exception as e:
        print(f"⚠️ Error extracting comprehensive info: {e}")
        info['extraction_error'] = str(e)
    
    return info

def extract_value_history_enhanced(soup):
    """
    Extract value history with enhanced patterns
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
                    print(f"📊 Found value history table with {len(rows)-1} entries")
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
        
        print(f"📈 Extracted {len(value_history)} value history entries")
        return value_history if value_history else None
        
    except Exception as e:
        print(f"⚠️ Error extracting value history: {e}")
        return None

def main():
    """
    Test enhanced scraping with a few sample parcels
    """
    print("🧪 Testing enhanced Boston.gov parcel scraping...")
    
    # Test with a few sample parcels
    test_parcels = ['2204999000', '2205022000', '2102767000']
    
    results = []
    
    for i, parcel_id in enumerate(test_parcels):
        print(f"\n{'='*60}")
        print(f"Enhanced Test {i+1}/{len(test_parcels)}")
        
        result = test_enhanced_scrape(parcel_id)
        if result:
            result['parcel_id'] = parcel_id
            results.append(result)
        
        # Add delay between requests
        if i < len(test_parcels) - 1:
            print("⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'data/processed/enhanced_parcel_scraping_results.csv'
        results_df.to_csv(output_file, index=False)
        print(f"\n✅ Enhanced test completed! Results saved to: {output_file}")
        
        # Show summary of captured fields
        print(f"\n📋 Summary of captured fields:")
        for col in results_df.columns:
            non_null_count = results_df[col].notna().sum()
            print(f"  - {col}: {non_null_count}/{len(results_df)} parcels")
        
        # Show sample of rich data
        print(f"\n📊 Sample enriched data:")
        sample_cols = ['parcel_id', 'address', 'property_type', 'owner_name', 'total_assessed_value', 'estimated_tax', 'residential_tax_rate', 'commercial_tax_rate']
        available_cols = [col for col in sample_cols if col in results_df.columns]
        print(results_df[available_cols].to_string())
        
    else:
        print("\n❌ No successful enhanced scrapes")

if __name__ == "__main__":
    main()
