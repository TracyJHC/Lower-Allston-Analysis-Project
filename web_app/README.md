# ABCDC Web Application

A Flask-based web application for visualizing and analyzing Allston-Brighton Community Development Corporation data.

## Project Structure

```
web_app/
├── app.py                 # Main Flask application
├── config/               # Configuration files
│   ├── __init__.py
│   ├── config.py         # Application configuration
│   ├── database.py       # Database utilities
│   └── complete_schema.sql # Database schema
├── routes/               # Route modules
│   ├── __init__.py
│   ├── main.py          # Main routes (home, map)
│   ├── data.py          # Data routes (voters, properties, buildings)
│   ├── api.py           # API routes
│   └── api_geojson.py   # GeoJSON API endpoints for map data
├── utils/               # Utility modules
│   ├── __init__.py
│   └── data_loader.py   # Data loading utilities
├── scripts/             # Data loading and processing scripts
│   ├── create_enhanced_buildings.py
│   ├── create_precinct_elderly_geojson.py
│   ├── export_for_looker.py          # Export data for Looker Studio
│   ├── export_database_for_cloud_sql.py
│   ├── load_buildings_data.py
│   ├── load_census_data.py           # Load census tracts data
│   ├── load_geocoded_voters.py
│   ├── load_geospatial_layers.py
│   ├── load_real_data_fixed.py
│   ├── load_real_data.py
│   ├── load_stores.py                    # Load store/retailer locations
│   ├── find_nearby_stores.py             # Map stores to nearby voters
│   ├── map_precincts_to_census_tracts.py  # Spatial mapping script
│   ├── find_missing_precinct_mappings.py
│   ├── populate_precinct_elderly_analysis.py
│   ├── run_data_loader.py
│   └── setup_and_load_buildings.py
├── static/              # Static files
│   ├── css/            # CSS files
│   ├── js/             # JavaScript files (sidebar.js, theme-toggle.js)
│   └── images/         # Image files
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── map.html
│   ├── voters.html
│   ├── properties.html
│   ├── buildings.html
│   ├── census_tracts.html  # Census tracts visualization
│   ├── analysis.html
│   ├── parcels.html
│   └── building_details.html
├── looker_exports/      # CSV exports for Looker Studio
│   ├── elderly_by_ward.csv
│   ├── elderly_by_precinct.csv
│   ├── census_tracts_income.csv
│   ├── buildings_summary.csv
│   └── [additional export files]
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   Create a `.env` file with your database configuration:
   ```
   DB_HOST=localhost
   DB_NAME=abcdc_spatial
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   FLASK_DEBUG=True
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   SECRET_KEY=your-secret-key
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

## Features

- **Interactive Map**: Visualize buildings, precincts, census tracts, boundaries, stores, and elderly voters with layer controls
  - Default base layer: CartoDB Positron (light, clean style)
  - All Elderly layer: Shows all elderly voters with coordinates (5,713 total)
    - Orange markers: Mapped to buildings (5,388)
    - Red markers: Not mapped to buildings (325)
- **Data Views**: Browse voters, properties, buildings, census tracts, and stores with filtering and sorting
- **Store Locations**: View retail stores and grocery locations on the map with store type and address information
- **Store-Voter Mapping**: Find nearby stores for each elderly voter based on distance calculations
- **Analysis**: View elderly population analysis by ward, precinct, and census tract with income data
- **API Endpoints**: RESTful API and GeoJSON endpoints for data access
- **Looker Studio Integration**: Export scripts and documentation for connecting to Looker Studio dashboards
- **Theme Toggle**: Light/dark mode with system preference detection
- **Responsive Design**: Mobile-friendly sidebar navigation and responsive layouts

### Address Cleaning and Voter→Building Linkage
- Addresses are standardized in the database (trimmed whitespace, removed trailing `.0`, `INITCAP` street names, normalized spacing).
- A canonical base key `<number> <Street Name>` links voters to buildings at street-address level (units excluded by design).
- Building keys expand `st_num` and `st_num2` when both exist to cover number ranges.
- Links are stored in `voters_buildings_map` with indexes on `res_id` and `struct_id` for fast lookup.
- The map consumes these links to join voter distributions with buildings for visualization.

### Store Locations and Voter-Store Mapping
- **Stores Table**: Retail stores and grocery locations loaded from CSV with coordinates, store type, and address information.
- **Store Loading**: Use `scripts/load_stores.py` to load store data from `data/processed/voter_data/Allston_Brighton_Retailer_Locator_upDated(no_end_date).csv`.
- **Voter-Store Mapping**: Use `scripts/find_nearby_stores.py` to find nearby stores for each elderly voter:
  - Calculates distance using Haversine formula
  - Uses voter coordinates (direct or via building geometry)
  - Default: finds stores within 2000 meters, up to 10 stores per voter
  - Results stored in `voter_store_nearby` table with distance in meters
- **Map Visualization**: Stores appear as green markers on the interactive map with popups showing store name, type, and address.
- **Coverage**: Currently maps stores to 3,641 elderly voters (out of 5,713 with coordinates), with average distance of 707 meters.
- **Elderly Voter Geocoding**: 
  - 5,713 elderly voters (75.9%) now have coordinates
  - Coordinates sourced from: building geometry (3,503), parcel geometry (1,517), direct geocoding (643)
  - 5,388 (94.3%) of geocoded elderly are mapped to buildings
  - All elderly with coordinates are visible on the map via "All Elderly" layer

## Development

The application is organized into modules:
- `config/`: Configuration and database utilities
- `routes/`: Route handlers organized by functionality
- `utils/`: Utility functions for data loading
- `scripts/`: Data processing and loading scripts

## Data Sources

- Building data from property assessments
- Voter registration data
- Store/retailer location data (Allston-Brighton Retailer Locator)
- Geospatial data (parcels, precincts, boundaries, census tracts)
- Census tract income data
- Elderly population analysis
- `voters_buildings_map` table enabling voter↔building overlays on the map
- `voter_store_nearby` table linking voters to nearby stores with distances
- `precinct_census_tract_mapping` table linking precincts to census tracts for income analysis

## Looker Studio Integration

The application includes scripts and documentation for exporting data to Looker Studio:

- **Export Script**: `scripts/export_for_looker.py` exports 9 key datasets to CSV files
- **Setup Guide**: See `docs/looker_studio_setup_guide.md` for connection instructions
- **Exported Data**: CSV files are saved in `looker_exports/` directory
- **Cloud SQL Support**: Scripts for exporting and importing to Google Cloud SQL

Run the export script:
```bash
python scripts/export_for_looker.py
```

## Loading Store Data

To load store locations and create voter-store mappings:

1. **Load Stores**:
   ```bash
   source venv/bin/activate
   python scripts/load_stores.py
   ```
   This loads store data from `data/processed/voter_data/Allston_Brighton_Retailer_Locator_upDated(no_end_date).csv` into the `stores` table.

2. **Find Nearby Stores for Voters**:
   ```bash
   python scripts/find_nearby_stores.py
   ```
   Options:
   - `--max-distance`: Maximum distance in meters (default: 2000)
   - `--max-stores`: Maximum stores per voter (default: 10)
   - `--all-voters`: Process all voters, not just elderly (default: elderly only)
   
   Example:
   ```bash
   python scripts/find_nearby_stores.py --max-distance 1500 --max-stores 5
   ```

3. **View Stores on Map**:
   - Navigate to `/map` in the web application
   - Click the "Stores" button to load store locations
   - Stores appear as green markers with popups showing store details