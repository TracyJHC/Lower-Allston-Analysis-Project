#!/usr/bin/env python3
"""
Create interactive Allston-Brighton map with MassGIS data and MBTA stops.

Features:
- Allston-Brighton boundary
- Parks and open spaces (clickable)
- Major roads (clickable)
- MBTA transit stops (clickable)
- Property parcels

Author: Team A
Date: October 2025
"""

import geopandas as gpd
import pandas as pd
import folium
from folium import plugins
from pathlib import Path
import logging
from shapely.geometry import box
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Allston-Brighton bounds
AB_BOUNDS = {
    'west': -71.17,
    'east': -71.10,
    'south': 42.32,
    'north': 42.38
}

def get_allston_brighton_boundary():
    """
    Load the actual Allston-Brighton boundary from MassGIS ward data.
    """
    boundary_file = Path("data/processed/gis_layers/allston_brighton_boundary.geojson")
    
    if boundary_file.exists():
        logger.info("  Loading real Allston-Brighton boundary from MassGIS wards...")
        boundary_gdf = gpd.read_file(boundary_file)
        return boundary_gdf
    else:
        logger.warning("  Real boundary not found, using bounding box...")
        # Fallback to bounding box
        boundary_box = box(
            AB_BOUNDS['west'], 
            AB_BOUNDS['south'],
            AB_BOUNDS['east'],
            AB_BOUNDS['north']
        )
        boundary_gdf = gpd.GeoDataFrame(
            [{'name': 'Allston-Brighton', 'geometry': boundary_box}],
            crs='EPSG:4326'
        )
        return boundary_gdf

def zoom_to_precinct(feature, map_obj):
    """
    JavaScript function to zoom to a specific precinct.
    """
    # Get the bounds of the clicked feature
    bounds = feature['geometry']['coordinates']
    # This will be handled by JavaScript in the map
    pass

def extract_mbta_stops():
    """
    Extract MBTA transit stops from MassGIS database.
    """
    logger.info("Extracting MBTA stops...")
    
    vector_gdb = Path("data/raw/statewide_viewer_fgdb/MassGIS_Vector_GISDATA.gdb")
    
    if not vector_gdb.exists():
        logger.warning("  Vector database not found")
        return None
    
    try:
        # Read MBTA bus stops directly
        stops = gpd.read_file(vector_gdb, layer='MBTABUSSTOPS_PT')
        logger.info(f"  Loaded {len(stops)} total MBTA stops")
        
        # Convert to WGS84
        if stops.crs != 'EPSG:4326':
            stops = stops.to_crs('EPSG:4326')
        
        # Get Allston-Brighton boundary for proper filtering
        boundary = get_allston_brighton_boundary()
        boundary_geom = boundary.geometry.iloc[0]
        
        # Filter stops within Allston-Brighton boundary
        stops_within = stops[stops.geometry.within(boundary_geom)]
        
        if len(stops_within) > 0:
            logger.info(f"  ✓ Found {len(stops_within)} stops in Allston-Brighton")
            return stops_within
        else:
            logger.warning("  No MBTA stops found in Allston-Brighton")
            return None
        
    except Exception as e:
        logger.error(f"  Error: {e}")
        return None

def create_allston_brighton_map():
    """
    Create comprehensive Allston-Brighton map with all layers.
    """
    logger.info("Creating Allston-Brighton interactive map...")
    
    # Get the real boundary for proper centering
    boundary = get_allston_brighton_boundary()
    bounds = boundary.total_bounds
    
    # Calculate center from real boundary
    center_lat = (bounds[3] + bounds[1]) / 2  # (north + south) / 2
    center_lon = (bounds[2] + bounds[0]) / 2  # (east + west) / 2
    
    # Create map - balanced zoom level
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,  # Balanced zoom - shows Allston-Brighton with some context
        tiles='CartoDB positron'
    )
    
    # Add base map options
    folium.TileLayer('OpenStreetMap', name='Street Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite'
    ).add_to(m)
    
    gis_dir = Path("data/processed/gis_layers")
    
    # 1. Add Precinct Boundaries (colored by precinct)
    logger.info("Adding precinct boundaries...")
    precincts_file = gis_dir / "allston_brighton_precincts.geojson"
    if precincts_file.exists():
        precincts = gpd.read_file(precincts_file)
        logger.info(f"  Loaded {len(precincts)} precincts")
        
        # Create a color palette for precincts
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        import numpy as np
        
        # Generate distinct colors
        n_precincts = len(precincts)
        colors = plt.cm.Set3(np.linspace(0, 1, n_precincts))
        color_list = [mcolors.rgb2hex(color) for color in colors]
        
        # Add color to each precinct
        precincts['color'] = [color_list[i] for i in range(len(precincts))]
        
        precincts_layer = folium.FeatureGroup(
            name='🗳️ Voting Precincts',
            show=True,
            overlay=True
        )
        
        folium.GeoJson(
            precincts.to_json(),
            style_function=lambda feature: {
                'fillColor': feature['properties']['color'],
                'color': '#2c3e50',
                'weight': 2,
                'opacity': 0.8,
                'fillOpacity': 0.6,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['WP_NAME', 'WARD', 'PRECINCT'],
                aliases=['Precinct', 'Ward', 'Precinct #'],
                localize=True,
                sticky=True,
                labels=True
            ),
            popup=folium.Popup(
                html="<b>Voting Precinct</b><br>Click to see details",
                max_width=200
            )
        ).add_to(precincts_layer)
        
        precincts_layer.add_to(m)
        logger.info(f"  ✓ Added {len(precincts)} colored precincts")
    
    # 2. Add Allston-Brighton Boundary (optional layer, off by default)
    logger.info("Adding Allston-Brighton boundary...")
    boundary = get_allston_brighton_boundary()
    
    boundary_layer = folium.FeatureGroup(
        name='🔴 Allston-Brighton Boundary',
        show=False  # Off by default since precincts show the detail
    )
    
    folium.GeoJson(
        boundary.to_json(),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#e74c3c',
            'weight': 3,
            'opacity': 0.8,
            'dashArray': '10, 5'
        },
        tooltip='Allston-Brighton Boundary'
    ).add_to(boundary_layer)
    
    boundary_layer.add_to(m)
    
    # 3. Add Parks and Open Spaces (clickable)
    parks_file = gis_dir / "boston_parks_openspace.geojson"
    if parks_file.exists():
        logger.info("Loading parks...")
        try:
            parks = gpd.read_file(parks_file)
            
            # Convert to WGS84
            if parks.crs != 'EPSG:4326':
                parks = parks.to_crs('EPSG:4326')
                logger.info(f"  Converted parks from {parks.crs} to EPSG:4326")
            
            # Filter to Allston-Brighton
            parks_ab = parks.cx[AB_BOUNDS['west']:AB_BOUNDS['east'], 
                               AB_BOUNDS['south']:AB_BOUNDS['north']].copy()
            
            logger.info(f"  Filtered to Allston-Brighton: {len(parks_ab)} parks")
            
            if len(parks_ab) > 0:
                # Simplify geometry
                parks_ab['geometry'] = parks_ab.geometry.simplify(0.00001)
                
                # Convert ALL columns to string to avoid timestamp issues
                for col in parks_ab.columns:
                    if col != 'geometry':
                        parks_ab[col] = parks_ab[col].astype(str)
                
                logger.info(f"  Converted {len(parks_ab.columns)} columns to string to avoid JSON serialization issues")
                
                # Create tooltip fields
                tooltip_fields = []
                tooltip_aliases = []
                
                if 'SITE_NAME' in parks_ab.columns:
                    tooltip_fields.append('SITE_NAME')
                    tooltip_aliases.append('Park Name')
                
                if 'OWNERSHIP' in parks_ab.columns:
                    tooltip_fields.append('OWNERSHIP')
                    tooltip_aliases.append('Owner')
                
                if 'ACRES' in parks_ab.columns:
                    tooltip_fields.append('ACRES')
                    tooltip_aliases.append('Size (acres)')
                
                # Add parks layer
                parks_layer = folium.FeatureGroup(
                    name=f'🌳 Parks & Open Space ({len(parks_ab)})', 
                    show=True,
                    overlay=True
                )
                
                folium.GeoJson(
                    parks_ab.to_json(),
                    style_function=lambda x: {
                        'fillColor': '#2ecc71',
                        'color': '#27ae60',
                        'weight': 1.5,
                        'fillOpacity': 0.6,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=tooltip_fields if tooltip_fields else None,
                        aliases=tooltip_aliases if tooltip_aliases else None,
                        localize=True,
                        sticky=True,
                        labels=True
                    ) if tooltip_fields else folium.Tooltip('Park')
                ).add_to(parks_layer)
                
                parks_layer.add_to(m)
                logger.info(f"  ✓ Added {len(parks_ab)} parks (clickable)")
                logger.info(f"  Parks layer added to map successfully")
                
        except Exception as e:
            logger.warning(f"  ✗ Error: {e}")
    
    # 4. Add Major Roads (clickable)
    roads_file = gis_dir / "boston_major_roads.geojson"
    if roads_file.exists():
        logger.info("Loading roads...")
        try:
            roads = gpd.read_file(roads_file)
            
            # Convert to WGS84
            if roads.crs != 'EPSG:4326':
                roads = roads.to_crs('EPSG:4326')
                logger.info(f"  Converted roads from {roads.crs} to EPSG:4326")
            
            # Filter to Allston-Brighton
            roads_ab = roads.cx[AB_BOUNDS['west']:AB_BOUNDS['east'], 
                               AB_BOUNDS['south']:AB_BOUNDS['north']].copy()
            
            logger.info(f"  Filtered to Allston-Brighton: {len(roads_ab)} road segments")
            
            if len(roads_ab) > 0:
                # Convert ALL columns to string to avoid timestamp issues
                for col in roads_ab.columns:
                    if col != 'geometry':
                        roads_ab[col] = roads_ab[col].astype(str)
                
                logger.info(f"  Converted {len(roads_ab.columns)} columns to string to avoid JSON serialization issues")
                
                # Prepare tooltip
                tooltip_fields = []
                tooltip_aliases = []
                
                if 'FULLNAME' in roads_ab.columns:
                    tooltip_fields.append('FULLNAME')
                    tooltip_aliases.append('Road Name')
                
                roads_layer = folium.FeatureGroup(
                    name=f'🛣️ Major Roads ({len(roads_ab)})', 
                    show=True,
                    overlay=True
                )
                
                folium.GeoJson(
                    roads_ab.to_json(),
                    style_function=lambda x: {
                        'color': '#e67e22',
                        'weight': 2.5,
                        'opacity': 0.8,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=tooltip_fields if tooltip_fields else None,
                        aliases=tooltip_aliases if tooltip_aliases else None,
                        localize=True,
                        sticky=True
                    ) if tooltip_fields else folium.Tooltip('Road')
                ).add_to(roads_layer)
                
                roads_layer.add_to(m)
                logger.info(f"  ✓ Added {len(roads_ab)} roads (clickable)")
                logger.info(f"  Roads layer added to map successfully")
                
        except Exception as e:
            logger.warning(f"  ✗ Error: {e}")
    
    # 5. Add MBTA & Bus Stops (smaller, filtered to boundary)
    mbta_stops = extract_mbta_stops()
    
    if mbta_stops is not None and len(mbta_stops) > 0:
        # Filter stops to only those within Allston-Brighton boundary
        boundary = get_allston_brighton_boundary()
        boundary_geom = boundary.geometry.iloc[0]
        
        # Filter stops within boundary
        stops_within = mbta_stops[mbta_stops.geometry.within(boundary_geom)]
        logger.info(f"Adding {len(stops_within)} transit stops within Allston-Brighton...")
        
        if len(stops_within) > 0:
            mbta_layer = folium.FeatureGroup(
                name=f'🚇 Transit Stops ({len(stops_within)})', 
                show=True,
                overlay=True
            )
            
            for idx, stop in stops_within.iterrows():
                # Get stop info
                stop_name = stop.get('STATION', stop.get('NAME', stop.get('STOP_NAME', 'Transit Stop')))
                stop_type = stop.get('LINE', stop.get('TYPE', 'Transit'))
                
                # Create popup HTML
                popup_html = f"""
                <div style="font-family: Arial; font-size: 12px;">
                    <h4 style="margin: 0 0 10px 0; color: #2c3e50;">🚇 {stop_name}</h4>
                    <p style="margin: 5px 0;"><strong>Type:</strong> {stop_type}</p>
                    <p style="margin: 5px 0; font-size: 10px; color: #7f8c8d;">
                        Lat: {stop.geometry.y:.6f}<br>
                        Lon: {stop.geometry.x:.6f}
                    </p>
                </div>
                """
                
                # Add visible marker
                folium.CircleMarker(
                    location=[stop.geometry.y, stop.geometry.x],
                    radius=4,  # Larger for visibility
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{stop_name}",
                    color='#8e44ad',
                    fill=True,
                    fillColor='#9b59b6',
                    fillOpacity=0.8,
                    weight=2
                ).add_to(mbta_layer)
            
            mbta_layer.add_to(m)
            logger.info(f"  ✓ Added {len(stops_within)} transit stops (smaller, within boundary)")
        else:
            logger.warning("  No transit stops found within Allston-Brighton boundary")
    else:
        logger.info("  ℹ No MBTA stops found - will add placeholder layer")
        
        # Add placeholder for future MBTA data
        placeholder_layer = folium.FeatureGroup(
            name='🚇 Transit Stops (Coming Soon)', 
            show=False
        )
        placeholder_layer.add_to(m)
    
    # 6. Add Property Parcels (optional, off by default)
    parcels_file = gis_dir / "parcels" / "boston_parcels.geojson"
    if parcels_file.exists():
        logger.info("Loading parcels...")
        try:
            # Read parcels with bbox filter
            parcels = gpd.read_file(
                parcels_file,
                bbox=(AB_BOUNDS['west'], AB_BOUNDS['south'], 
                      AB_BOUNDS['east'], AB_BOUNDS['north'])
            )
            
            # Convert to WGS84 if needed
            if parcels.crs != 'EPSG:4326':
                parcels = parcels.to_crs('EPSG:4326')
            
            if len(parcels) > 0:
                logger.info(f"  Found {len(parcels)} parcels in Allston-Brighton")
                
                # Simplify
                parcels['geometry'] = parcels.geometry.simplify(0.00002)
                
                parcels_layer = folium.FeatureGroup(
                    name=f'🏘️ Property Parcels ({len(parcels)})',
                    show=False  # Off by default
                )
                
                # Sample only first 1000 for performance
                parcels_sample = parcels.head(1000) if len(parcels) > 1000 else parcels
                
                folium.GeoJson(
                    parcels_sample.to_json(),
                    style_function=lambda x: {
                        'fillColor': 'transparent',
                        'color': '#3498db',
                        'weight': 0.5,
                        'opacity': 0.4,
                    },
                    tooltip='Property Parcel (click for details)'
                ).add_to(parcels_layer)
                
                parcels_layer.add_to(m)
                logger.info(f"  ✓ Added parcels (showing {len(parcels_sample)} of {len(parcels)})")
                
        except Exception as e:
            logger.warning(f"  ✗ Error loading parcels: {e}")
    
    # 7. Add Building Points (new layer)
    buildings_file = gis_dir / "allston_brighton_building_points.geojson"
    if buildings_file.exists():
        logger.info("Loading building points...")
        try:
            buildings = gpd.read_file(buildings_file)
            logger.info(f"  Loaded {len(buildings)} building points")
            
            if len(buildings) > 0:
                # Convert ALL columns to string to avoid timestamp issues
                for col in buildings.columns:
                    if col != 'geometry':
                        buildings[col] = buildings[col].astype(str)
                
                buildings_layer = folium.FeatureGroup(
                    name=f'🏢 Buildings ({len(buildings):,})', 
                    show=True,
                    overlay=True
                )
                
                # Add building points as small circles
                for idx, building in buildings.iterrows():
                    # Get building info
                    building_id = building.get('building_id', idx)
                    area_sqft = building.get('area_sqft', 'Unknown')
                    
                    # Create popup HTML
                    popup_html = f"""
                    <div style="font-family: Arial; font-size: 12px;">
                        <h4 style="margin: 0 0 10px 0; color: #2c3e50;">🏢 Building #{building_id}</h4>
                        <p style="margin: 5px 0;"><strong>Area:</strong> {area_sqft} sq ft</p>
                        <p style="margin: 5px 0; font-size: 10px; color: #7f8c8d;">
                            Lat: {building.geometry.y:.6f}<br>
                            Lon: {building.geometry.x:.6f}
                        </p>
                    </div>
                    """
                    
                    # Add building marker
                    folium.CircleMarker(
                        location=[building.geometry.y, building.geometry.x],
                        radius=2,  # Small dots for buildings
                        popup=folium.Popup(popup_html, max_width=200),
                        tooltip=f"Building #{building_id}",
                        color='#34495e',
                        fill=True,
                        fillColor='#2c3e50',
                        fillOpacity=0.7,
                        weight=1
                    ).add_to(buildings_layer)
                
                buildings_layer.add_to(m)
                logger.info(f"  ✓ Added {len(buildings):,} building points")
                
        except Exception as e:
            logger.warning(f"  ✗ Error loading buildings: {e}")
    else:
        logger.info("  ℹ Building points file not found")
    
    # Add tools
    plugins.Geocoder(position='topright').add_to(m)
    plugins.MeasureControl(position='topleft', primary_length_unit='miles').add_to(m)
    plugins.Fullscreen(position='topright').add_to(m)
    
    # Add layer control
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # JavaScript removed for simplicity
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 30px; right: 30px; width: 150px; 
                background-color: white; z-index:9999; font-size:9px;
                border:1px solid grey; border-radius: 4px; padding: 6px;
                box-shadow: 0 0 8px rgba(0,0,0,0.15);">
    <h3 style="margin-top:0; color:#2c3e50; font-size:10px;">Legend</h3>
    <p style="margin:2px 0;"><span style="color:#e74c3c; font-size:12px;">┅</span> Boundary</p>
    <p style="margin:2px 0;"><span style="color:#2ecc71; font-size:12px;">●</span> Parks</p>
    <p style="margin:2px 0;"><span style="color:#e67e22; font-size:12px;">━</span> Roads</p>
    <p style="margin:2px 0;"><span style="color:#9b59b6; font-size:12px;">◉</span> Transit</p>
    <p style="margin:2px 0;"><span style="color:#2c3e50; font-size:12px;">●</span> Buildings</p>
    <p style="margin:2px 0;"><span style="color:#3498db; font-size:12px;">▢</span> Parcels</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Title removed as requested
    
    # Save map
    output_file = Path("reports/figures/allston_brighton_map.html")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(output_file))
    
    logger.info(f"\n✓ Map saved to: {output_file}")
    logger.info(f"  File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")
    
    return output_file

def main():
    """Main function."""
    
    logger.info("="*60)
    logger.info("CREATING ALLSTON-BRIGHTON INTERACTIVE MAP")
    logger.info("="*60 + "\n")
    
    output_file = create_allston_brighton_map()
    
    logger.info("\n" + "="*60)
    logger.info("MAP CREATED SUCCESSFULLY!")
    logger.info("="*60)
    logger.info(f"\n📍 Open this file in your browser:")
    logger.info(f"   {output_file.absolute()}")
    logger.info("\n🎯 Map features:")
    logger.info("   • Allston-Brighton boundary outline")
    logger.info("   • Parks and open spaces (clickable)")
    logger.info("   • Major roads (clickable)")
    logger.info("   • MBTA transit stops (clickable)")
    logger.info("   • Building points (10,282 buildings)")
    logger.info("   • Property parcels (optional layer)")
    logger.info("   • Multiple base map options")
    logger.info("   • Search, measure, and fullscreen tools")
    logger.info("\n💡 Click on any feature to see details!")
    logger.info("="*60)

if __name__ == "__main__":
    main()
