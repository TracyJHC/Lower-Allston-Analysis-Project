#!/usr/bin/env python3
"""
Test script to scrape property details from Boston.gov for a few sample parcels
"""

import requests
import pandas as pd
import time
from bs4 import BeautifulSoup
import json

def test_scrape_parcel(parcel_id):
    """
    Test scraping a single parcel from Boston.gov
    """
    print(f"🔍 Testing scrape for parcel: {parcel_id}")
    
    try:
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        params = {'parcel': parcel_id}
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
                    
                    # Extract key information
                    property_info = extract_basic_info(details_soup)
                    print(f"📋 Extracted info: {json.dumps(property_info, indent=2)}")
                    return property_info
                else:
                    print(f"❌ Details page failed: {details_response.status_code}")
            else:
                print("❌ No details link found")
                # Print the page content to debug
                print("📄 Page content preview:")
                print(soup.get_text()[:500])
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def extract_basic_info(soup):
    """
    Extract basic property information from the details page
    """
    info = {}
    
    try:
        # Look for key-value pairs in the page
        text = soup.get_text()
        
        # Extract common patterns
        patterns = {
            'address': r'Address:\s*([^\n]+)',
            'property_type': r'Property Type:\s*([^\n]+)',
            'owner': r'Owner on[^:]*:\s*([^\n]+)',
            'total_value': r'Total Assessed Value:\s*([^\n]+)',
            'building_value': r'Building value:\s*([^\n]+)',
            'land_value': r'Land Value:\s*([^\n]+)',
            'year_built': r'Year Built:\s*([^\n]+)',
            'living_area': r'Living Area:\s*([^\n]+)'
        }
        
        for key, pattern in patterns.items():
            import re
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info[key] = match.group(1).strip()
        
        # Also try to find tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    if 'Address' in key:
                        info['address'] = value
                    elif 'Property Type' in key:
                        info['property_type'] = value
                    elif 'Owner' in key and 'Mailing' not in key:
                        info['owner'] = value
                    elif 'Total Assessed Value' in key:
                        info['total_value'] = value
                    elif 'Building value' in key:
                        info['building_value'] = value
                    elif 'Land Value' in key:
                        info['land_value'] = value
                    elif 'Year Built' in key:
                        info['year_built'] = value
                    elif 'Living Area' in key:
                        info['living_area'] = value
        
    except Exception as e:
        print(f"⚠️ Error extracting info: {e}")
        info['extraction_error'] = str(e)
    
    return info

def main():
    """
    Test scraping with a few sample parcels
    """
    print("🧪 Testing Boston.gov parcel scraping...")
    
    # Load some sample parcels from our mapping
    try:
        df = pd.read_csv('data/processed/gis_layers/building_parcel_mapping.csv')
        sample_parcels = df['OFFICIAL_PAR_ID'].dropna().head(3).tolist()
        print(f"📊 Testing with {len(sample_parcels)} sample parcels")
    except:
        # Fallback test parcels
        sample_parcels = ['2100004000', '2204999000', '2205022000']
        print(f"📊 Using fallback test parcels: {sample_parcels}")
    
    results = []
    
    for i, parcel_id in enumerate(sample_parcels):
        print(f"\n{'='*50}")
        print(f"Test {i+1}/{len(sample_parcels)}")
        
        # Clean parcel ID
        clean_parcel_id = str(int(float(parcel_id)))
        
        result = test_scrape_parcel(clean_parcel_id)
        if result:
            result['parcel_id'] = clean_parcel_id
            results.append(result)
        
        # Add delay between requests
        if i < len(sample_parcels) - 1:
            print("⏳ Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'data/processed/test_parcel_scraping_results.csv'
        results_df.to_csv(output_file, index=False)
        print(f"\n✅ Test completed! Results saved to: {output_file}")
        print(f"📋 Summary:")
        print(results_df[['parcel_id', 'address', 'property_type', 'owner', 'total_value']].to_string())
    else:
        print("\n❌ No successful scrapes")

if __name__ == "__main__":
    main()
