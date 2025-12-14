# Web App Scripts Directory

This directory contains all scripts for the ABCDC web application, organized by function.

## Directory Structure

```
scripts/
├── data_loading/          # Scripts for loading data into the database
├── data_processing/       # Scripts for processing and transforming data
├── elderly_analysis/      # Scripts specific to elderly population analysis
├── geocoding/            # Scripts for geocoding addresses and coordinates
├── export/                # Scripts for exporting data (CSV, BigQuery, etc.)
├── cloud_sql/            # Scripts for Cloud SQL operations
├── sql/                   # SQL query files
└── docs/                  # Documentation files
```

## Folder Descriptions

### `data_loading/`
Scripts that load raw data into the database:
- `load_buildings_data.py` - Load building data
- `load_census_data.py` - Load census tract data
- `load_geocoded_voters.py` - Load voter data
- `load_geospatial_layers.py` - Load GeoJSON layers
- `load_parcels_geojson.py` - Load parcel geometries
- `load_stores.py` - Load store data
- `load_elderly_analysis_to_db.py` - Load elderly analysis results
- `setup_and_load_buildings.py` - Setup and load buildings
- `run_data_loader.py` - Main data loader script

### `data_processing/`
Scripts that process and transform data:
- `map_precincts_to_census_tracts.py` - Map precincts to census tracts
- `find_missing_precinct_mappings.py` - Find missing mappings
- `find_nearby_stores.py` - Find stores near voters
- `add_missing_parcels.py` - Add missing parcel data

### `elderly_analysis/`
Scripts for elderly population analysis:
- `get_elderly_housing_conditions.py` - Get housing conditions for elderly
- `get_elderly_permits_one_to_one.py` - Get permits for one-to-one mapped elderly
- `match_elderly_to_permits.py` - Match elderly to building permits
- `match_elderly_to_violations.py` - Match elderly to property violations
- `populate_precinct_elderly_analysis.py` - Populate precinct-level analysis
- `create_precinct_elderly_geojson.py` - Create GeoJSON for elderly by precinct
- `check_elderly_coverage.py` - Check coverage of elderly in census tracts

### `geocoding/`
Scripts for geocoding addresses:
- `geocode_remaining_elderly.py` - Geocode elderly addresses
- `geocode_remaining_elderly_smart.py` - Smart geocoding with fallbacks
- `update_coords_from_parcels.py` - Update coordinates from parcel data
- `update_voter_coords_from_buildings.py` - Update voter coordinates from buildings

### `export/`
Scripts for exporting data:
- `export_for_looker.py` - Export data for Looker Studio
- `export_for_bigquery_local.sh` - Export to CSV for BigQuery (local)
- `export_for_bigquery_visualization.sh` - Export for BigQuery (Cloud Shell)
- `export_database_for_cloud_sql.py` - Export database for Cloud SQL
- `export_database_for_cloud_sql.sh` - Export script for Cloud SQL

### `cloud_sql/`
Scripts for Cloud SQL operations:
- `cloud_shell_import.sh` - Import database via Cloud Shell
- `import_to_cloud_sql.sh` - Import to Cloud SQL

### `sql/`
SQL query files:
- `export_elderly_census_tract_visualization.sql` - Query for census tract visualization
- `check_elderly_coverage.sql` - Coverage analysis queries

### `docs/`
Documentation:
- `cloud_shell_upload_guide.md` - Guide for uploading via Cloud Shell
- `cloud_sql_upload_guide.md` - Guide for Cloud SQL upload
- `setup_cloud_sql_guide.md` - Setup guide for Cloud SQL

## Usage

### Running Scripts

Most Python scripts can be run directly:
```bash
python3 data_loading/load_buildings_data.py
```

Shell scripts should be made executable first:
```bash
chmod +x export/export_for_bigquery_local.sh
./export/export_for_bigquery_local.sh
```

### Database Connection

Scripts use environment variables for database connection:
- `DB_HOST` (default: localhost)
- `DB_NAME` (default: abcdc_spatial)
- `DB_USER` (default: Studies)
- `DB_PASSWORD` (from .env file)
- `DB_PORT` (default: 5432)

## Notes

- All scripts should be run from the project root or with proper path configuration
- Some scripts require PostGIS extension
- Cloud SQL scripts require authentication and proper network access

