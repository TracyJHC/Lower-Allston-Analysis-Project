"""
Data loading utilities for the ABCDC Web Application
"""
import os
import json
import pandas as pd
from config.config import Config

def load_geojson_file(file_path):
    """Load a GeoJSON file and return the data"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading GeoJSON file {file_path}: {e}")
        return None

def load_csv_file(file_path):
    """Load a CSV file and return a pandas DataFrame"""
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        return None
    except Exception as e:
        print(f"Error loading CSV file {file_path}: {e}")
        return None

def get_geospatial_data():
    """Load all geospatial data files"""
    geospatial_path = Config.GEOSPATIAL_DATA_DIR
    
    # Load buildings GeoJSON (try enhanced version first, fallback to original)
    enhanced_buildings_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'enhanced_buildings.geojson')
    buildings_file = os.path.join(geospatial_path, 'allston_brighton_buildings.geojson')
    
    buildings_geojson = load_geojson_file(enhanced_buildings_file)
    if not buildings_geojson:
        buildings_geojson = load_geojson_file(buildings_file)
    
    # Load other geospatial files
    parcels_geojson = load_geojson_file(os.path.join(geospatial_path, 'allston_brighton_parcels.geojson'))
    boundary_geojson = load_geojson_file(os.path.join(geospatial_path, 'allston_brighton_boundary.geojson'))
    
    # Load precincts GeoJSON (try enhanced version first, fallback to original)
    enhanced_precincts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'precincts_elderly.geojson')
    precincts_file = os.path.join(geospatial_path, 'allston_brighton_precincts.geojson')
    
    precincts_geojson = load_geojson_file(enhanced_precincts_file)
    if not precincts_geojson:
        precincts_geojson = load_geojson_file(precincts_file)
    
    return {
        'buildings': buildings_geojson,
        'parcels': parcels_geojson,
        'boundary': boundary_geojson,
        'precincts': precincts_geojson
    }

def get_building_property_data():
    """Load building property data from CSV"""
    csv_path = os.path.join(Config.DATA_DIR, 'processed', 'building_property_with_suffix.csv')
    return load_csv_file(csv_path)
