#!/usr/bin/env python3
"""
Debug script to understand the page structure and find where tax/value info is located
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_page_structure(parcel_id):
    """
    Debug the page structure to understand where tax and value information is located
    """
    print(f"🔍 Debugging page structure for parcel: {parcel_id}")
    
    try:
        # Boston.gov assessing search URL
        base_url = "https://www.cityofboston.gov/assessing/search/"
        search_url = f"{base_url}?parcel={parcel_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the details link
            details_link = soup.find('a', href=lambda x: x and 'pid=' in x)
            if details_link:
                details_url = f"https://www.cityofboston.gov/assessing/search/{details_link['href']}"
                details_response = requests.get(details_url, headers=headers, timeout=30)
                
                if details_response.status_code == 200:
                    details_soup = BeautifulSoup(details_response.content, 'html.parser')
                    
                    # Get all text content
                    text = details_soup.get_text()
                    
                    print(f"📄 Page text length: {len(text)} characters")
                    
                    # Look for specific patterns we're trying to extract
                    patterns_to_find = [
                        'Building value',
                        'Land Value', 
                        'Total Assessed Value',
                        'Estimated Tax',
                        'Community Preservation',
                        'Total, First Half',
                        'Residential:',
                        'Commercial:',
                        'FY2025',
                        'FY2026',
                        'Tax Rates',
                        'Preliminary Tax'
                    ]
                    
                    print(f"\n🔍 Searching for key patterns:")
                    for pattern in patterns_to_find:
                        if pattern in text:
                            # Find the context around this pattern
                            start = text.find(pattern)
                            context = text[max(0, start-50):start+200]
                            print(f"✅ Found '{pattern}': {context}")
                        else:
                            print(f"❌ Not found: '{pattern}'")
                    
                    # Look for tables that might contain the information
                    print(f"\n📊 Found {len(details_soup.find_all('table'))} tables")
                    
                    tables = details_soup.find_all('table')
                    for i, table in enumerate(tables):
                        print(f"\n📋 Table {i+1}:")
                        rows = table.find_all('tr')
                        print(f"  Rows: {len(rows)}")
                        
                        # Show first few rows
                        for j, row in enumerate(rows[:3]):
                            cells = row.find_all(['td', 'th'])
                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                            print(f"    Row {j+1}: {cell_texts}")
                            
                            # Check if this looks like a value/tax table
                            if any(keyword in ' '.join(cell_texts).lower() for keyword in ['value', 'tax', 'rate', 'fy']):
                                print(f"    ⭐ This looks like a value/tax table!")
                                
                                # Show all rows of this table
                                print(f"    📊 Full table content:")
                                for k, full_row in enumerate(rows):
                                    full_cells = full_row.find_all(['td', 'th'])
                                    full_cell_texts = [cell.get_text(strip=True) for cell in full_cells]
                                    if full_cell_texts:
                                        print(f"      Row {k+1}: {full_cell_texts}")
                    
                    # Look for specific sections
                    print(f"\n🏷️ Looking for specific sections:")
                    section_patterns = [
                        r'Value/Tax',
                        r'Assessment as of',
                        r'FY\d+',
                        r'Tax Rates',
                        r'Preliminary Tax',
                        r'Abatements/Exemptions',
                        r'Current Owner/s',
                        r'Value History'
                    ]
                    
                    for pattern in section_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            print(f"✅ Found section '{pattern}': {len(matches)} matches")
                            # Find context around first match
                            match_start = text.lower().find(pattern.lower())
                            if match_start != -1:
                                context_start = max(0, match_start - 100)
                                context_end = min(len(text), match_start + 500)
                                context = text[context_start:context_end]
                                print(f"   Context: {context[:200]}...")
                        else:
                            print(f"❌ Section not found: '{pattern}'")
                    
                    return True
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """
    Debug page structure for a sample parcel
    """
    print("🔍 Debugging Boston.gov page structure...")
    
    # Test with one parcel
    test_parcel = '2204999000'
    debug_page_structure(test_parcel)

if __name__ == "__main__":
    main()
