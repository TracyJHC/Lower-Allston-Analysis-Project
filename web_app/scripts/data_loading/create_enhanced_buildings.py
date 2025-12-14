#!/usr/bin/env python3
"""
Script to create enhanced building GeoJSON with property data for proper color coding
"""

import json
import pandas as pd
import os

def create_enhanced_buildings_geojson():
    """Create enhanced building GeoJSON with property assessment data"""
    
    # Paths
    geojson_path = '../data/processed/geospatial_data/allston_brighton_buildings.geojson'
    csv_path = 'data/building_property_with_suffix.csv'
    output_path = 'data/enhanced_buildings.geojson'
    
    print("Loading building geometries...")
    with open(geojson_path, 'r') as f:
        buildings_geojson = json.load(f)
    
    print("Loading property data...")
    property_df = pd.read_csv(csv_path)
    
    print(f"Found {len(buildings_geojson['features'])} buildings in GeoJSON")
    print(f"Found {len(property_df)} properties in CSV")
    
    # Debug: Check first few STRUCT_IDs
    print("Sample GeoJSON STRUCT_IDs:", [f['properties'].get('STRUCT_ID') for f in buildings_geojson['features'][:3]])
    print("Sample CSV STRUCT_IDs:", property_df['STRUCT_ID'].head(3).tolist())
    
    # Create a lookup dictionary for property data by STRUCT_ID
    property_lookup = {}
    for _, row in property_df.iterrows():
        struct_id = row['STRUCT_ID']
        if pd.isna(struct_id):
            continue
        # Convert total_value to numeric, handling commas and empty values
        total_value = row.get('TOTAL_VALUE', 0)
        if pd.notna(total_value) and total_value != '':
            try:
                # Remove commas and convert to float, then to int
                total_value = int(float(str(total_value).replace(',', '')))
            except (ValueError, TypeError):
                total_value = 0
        else:
            total_value = 0
            
        property_lookup[struct_id] = {
            'total_value': total_value,
            'owner': row.get('OWNER', 'Unknown'),
            'st_num': row.get('ST_NUM', ''),
            'st_name': row.get('ST_NAME', ''),
            'site_address': str(row.get('ST_NUM', '')) + ' ' + str(row.get('ST_NAME', '')) if pd.notna(row.get('ST_NUM')) and pd.notna(row.get('ST_NAME')) else 'Building',
            'bldg_type': row.get('BLDG_TYPE', 'Unknown'),
            'yr_built': row.get('YR_BUILT', 'Unknown'),
            'owner_occ': row.get('OWN_OCC', 'N'),
            'living_area': row.get('LIVING_AREA', 0),
            'land_sf': row.get('LAND_SF', 0)
        }
    
    print("Merging property data with building geometries...")
    enhanced_features = []
    matched_count = 0
    
    for feature in buildings_geojson['features']:
        struct_id = feature['properties'].get('STRUCT_ID')
        
        # Create enhanced properties
        enhanced_props = feature['properties'].copy()
        
        if struct_id in property_lookup:
            # Add property data
            prop_data = property_lookup[struct_id]
            enhanced_props.update(prop_data)
            matched_count += 1
        else:
            # No property data available
            enhanced_props.update({
                'total_value': 0,
                'owner': 'Unknown',
                'st_num': '',
                'st_name': '',
                'site_address': 'Building',
                'bldg_type': 'Unknown',
                'yr_built': 'Unknown',
                'owner_occ': 'N',
                'living_area': 0,
                'land_sf': 0
            })
        
        # Create enhanced feature
        enhanced_feature = {
            'type': 'Feature',
            'properties': enhanced_props,
            'geometry': feature['geometry']
        }
        enhanced_features.append(enhanced_feature)
    
    # Create enhanced GeoJSON
    enhanced_geojson = {
        'type': 'FeatureCollection',
        'name': 'allston_brighton_buildings_enhanced',
        'crs': buildings_geojson.get('crs', {}),
        'features': enhanced_features
    }
    
    # Save enhanced GeoJSON
    print(f"Saving enhanced GeoJSON with {matched_count} buildings matched to property data...")
    with open(output_path, 'w') as f:
        json.dump(enhanced_geojson, f, indent=2)
    
    print(f"Enhanced GeoJSON saved to: {output_path}")
    print(f"Buildings with property data: {matched_count}")
    print(f"Buildings without property data: {len(enhanced_features) - matched_count}")
    
    return output_path

if __name__ == "__main__":
    create_enhanced_buildings_geojson()
