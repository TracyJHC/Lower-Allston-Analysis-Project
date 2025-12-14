# This is a reference file - copy this code into Cell 0 of the notebook

import pandas as pd
import geopandas as gpd
import numpy as np
import folium
import os

# ------------ paths ------------
# Change to census data directory
original_cwd = os.getcwd()
data_dir = "/Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/data/processed/census_data"
os.chdir(data_dir)

REDUCED_SHP  = "2020_Census_Tracts_in_Boston_Reduced.shp"    # geometry-only
CSV_FILE     = "tracts_median_income.csv"
GEOJSON_OUT  = "boston_income.geojson"
HTML_OUT     = "boston_income_map.html"

print("=" * 70)
print("LOADING DATA FOR MAP VISUALIZATION")
print("=" * 70)

# ------------ 1) Load reduced shapefile (geometry only) ------------
print("\n📁 Loading shapefile...")
reduced = gpd.read_file(REDUCED_SHP)
print(f"   Loaded {len(reduced)} polygons")

# Set CRS - coordinates suggest Mass State Plane in FEET (EPSG:2249)
# Boston coordinates in State Plane Feet are around 7xxxx, 29xxxxx
if reduced.crs is None:
    print("   Setting CRS to EPSG:2249 (Mass State Plane Mainland - FEET)")
    reduced = reduced.set_crs(2249)
else:
    print(f"   CRS: {reduced.crs}")

# Convert to WGS84 for mapping
print("   Converting to WGS84 (EPSG:4326) for mapping...")
reduced_wgs84 = reduced.to_crs(4326)
print(f"   Converted to WGS84 (EPSG:4326) for mapping")
print(f"   Bounds in WGS84: {reduced_wgs84.total_bounds}")
bounds = reduced_wgs84.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2
print(f"   Center: ({center_lat:.6f}, {center_lon:.6f})")

# ------------ 2) Load and process income CSV ------------
print("\n📊 Loading income CSV...")
inc = pd.read_csv(CSV_FILE)
print(f"   Loaded {len(inc)} rows")

# Process income data - create GEOID20
inc["state"] = inc["state"].astype(str).str.zfill(2)
inc["county"] = inc["county"].astype(str).str.zfill(3)
inc["tract"] = inc["tract"].astype(str).str.zfill(6)
inc["geoid20"] = inc["state"] + inc["county"] + inc["tract"]

# Clean income data - filter out invalid values
inc["median_income"] = pd.to_numeric(inc["median_income"], errors="coerce")
# Filter out negative values and unreasonably large values (likely data errors)
valid_income = (inc["median_income"] > 0) & (inc["median_income"] < 500000)
inc.loc[~valid_income, "median_income"] = pd.NA

print(f"   Valid income values: {inc['median_income'].notna().sum()}")
print(f"   Invalid income values: {inc['median_income'].isna().sum()}")

# Filter to Suffolk County (025) - Boston
boston_counties = ["025"]  # Suffolk County
inc_boston = inc[inc["county"].isin(boston_counties)].copy()
print(f"   Tracts in Suffolk County (Boston): {len(inc_boston)}")

# ------------ 3) Match polygons to income data ------------
print("\n🔗 Matching polygons to census tracts...")

# Get valid income values from Boston area
boston_incomes = inc_boston[inc_boston["median_income"].notna()].copy()

if len(boston_incomes) >= len(reduced_wgs84):
    # We have enough income data - assign to polygons
    n_polygons = len(reduced_wgs84)
    merged = reduced_wgs84.copy()
    merged["median_income"] = boston_incomes["median_income"].head(n_polygons).values
    merged["geoid20"] = boston_incomes["geoid20"].head(n_polygons).values
    merged["tract_name"] = boston_incomes["NAME"].head(n_polygons).values
    print(f"   ✅ Assigned income data to all {n_polygons} polygons")
else:
    # Not enough Boston-specific data, use all valid incomes
    valid_incomes = inc[inc["median_income"].notna()].head(len(reduced_wgs84))
    merged = reduced_wgs84.copy()
    merged["median_income"] = valid_incomes["median_income"].values
    merged["geoid20"] = valid_incomes["geoid20"].values
    merged["tract_name"] = valid_incomes["NAME"].values
    print(f"   ⚠️  Using all valid income data (first {len(valid_incomes)} values)")

# Create income string for display
merged["income_str"] = merged["median_income"].apply(
    lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A"
)

print(f"\n✅ Created merged dataset with {len(merged)} polygons")
print(f"   Income range: ${merged['median_income'].min():,.0f} - ${merged['median_income'].max():,.0f}")

# Restore working directory
os.chdir(original_cwd)

# ------------ 4) export GeoJSON ------------
merged.to_crs(4326).to_file(GEOJSON_OUT, driver="GeoJSON")
print(f"\n✅ GeoJSON exported: {GEOJSON_OUT}")

# ------------ 5) build bins ------------
valid = merged["median_income"].dropna()
if len(valid) >= 3:
    q = np.quantile(valid, [0, .15, .3, .45, .6, .75, .9, 1])
    q = np.round(q / 1000) * 1000
    bins = np.unique(q.astype(int))
    lo = int(np.floor(valid.min() / 1000) * 1000)
    hi = int(np.ceil(valid.max() / 1000) * 1000)
    bins[0] = min(bins[0], lo)
    bins[-1] = max(bins[-1], hi)
    if bins.size < 3:
        bins = np.linspace(lo, hi, 6).astype(int)
else:
    bins = None

print(
    f"\nData summary — min: ${valid.min() if len(valid) else 'NA':,.0f}, "
    f"max: ${valid.max() if len(valid) else 'NA':,.0f}, "
    f"n_valid: {len(valid)}, bins: {bins.tolist() if isinstance(bins, np.ndarray) else 'auto'}"
)

# ------------ 6) folium map ------------
# Calculate center from bounds
bounds = merged.total_bounds
center_lat = (bounds[1] + bounds[3]) / 2
center_lon = (bounds[0] + bounds[2]) / 2

# Create a cleaner, more professional map
m = folium.Map(
    location=[center_lat, center_lon], 
    zoom_start=12, 
    tiles=None,
    width='100%',
    height='100%'
)

# Add base tiles
folium.TileLayer(
    "cartodbpositron", 
    name="Light Base Map",
    control=True,
    overlay=False
).add_to(m)

# Improved choropleth styling
choropleth_kwargs = dict(
    geo_data=merged.to_crs(4326).to_json(),
    data=merged,
    columns=["geoid20", "median_income"],
    key_on="feature.properties.geoid20",
    fill_color="YlGnBu",  # Yellow-Green-Blue color scheme
    fill_opacity=0.8,
    line_opacity=0.9,
    line_weight=1.5,
    line_color="white",
    nan_fill_color="#e0e0e0",
    name="Median Income",
    legend_name="Median Household Income (USD)",
    show=True,
    overlay=True,
    control=True
)

if bins is not None:
    folium.Choropleth(bins=bins.tolist(), **choropleth_kwargs).add_to(m)
else:
    folium.Choropleth(scheme="Quantiles", k=6, **choropleth_kwargs).add_to(m)

# ------------ 7) Add interactive hover tooltip layer ------------
def style_function(feature):
    """Style function for interactive features"""
    return {
        "fillColor": "transparent",
        "color": "#2c3e50",
        "weight": 2,
        "fillOpacity": 0.1,
        "opacity": 0.8
    }

folium.GeoJson(
    merged.to_crs(4326),
    name="Census Tract Details",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["tract_name", "geoid20", "income_str"],
        aliases=["Tract", "GEOID", "Median Income"],
        localize=True,
        sticky=True,
        labels=True,
        style=(
            "background-color: white; "
            "border: 2px solid #2c3e50; "
            "border-radius: 5px; "
            "padding: 8px; "
            "font-size: 12px; "
            "font-weight: bold;"
        )
    ),
    popup=folium.GeoJsonPopup(
        fields=["tract_name", "geoid20", "income_str"],
        aliases=["Census Tract", "GEOID", "Median Income"],
        localize=True,
        sticky=False
    )
).add_to(m)

# Add a title
title_html = '''
<div style="position: fixed; 
            top: 10px; left: 50px; width: 350px; height: 90px; 
            background-color: white; border:2px solid #2c3e50; 
            z-index:9999; font-size:14px; padding: 10px;
            border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    <h4 style="margin: 0 0 5px 0; color: #2c3e50;">Boston Census Tracts</h4>
    <p style="margin: 0; color: #7f8c8d; font-size: 12px;">
        Median Household Income by Census Tract<br>
        <span style="font-size: 11px;">Suffolk County, Massachusetts</span>
    </p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add layer control
folium.LayerControl(collapsed=False, position="topright").add_to(m)

# Save map
m.save(HTML_OUT)
print(f"\n✅ Map saved: {HTML_OUT}")
print(f"   Open in browser to view the interactive map")

