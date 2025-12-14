# Buildings Data Integration

This document describes the new buildings functionality added to the ABCDC web application.

## Overview

The buildings feature integrates detailed building property data from `building_property_with_suffix.csv` into the web application, allowing users to view and search through building information including addresses, owners, and property details.

## Database Schema

A new `buildings` table has been added to store the building data with the following key columns:

### Address Information
- `st_num` - Street number
- `st_num2` - Secondary street number  
- `st_name` - Street name
- `unit_num` - Unit number
- `city` - City
- `zip_code` - ZIP code

### Owner Information
- `owner_occ` - Owner occupied (Y/N)
- `owner` - Owner name
- `mail_addressee` - Mailing addressee
- `mail_street_address` - Mailing street address
- `mail_city` - Mailing city
- `mail_state` - Mailing state
- `mail_zip_code` - Mailing ZIP code

### Property Details
- `bldg_type` - Building type
- `total_value` - Total property value
- `gross_tax` - Gross tax amount
- `yr_built` - Year built
- `yr_remodel` - Year remodeled
- `structure_class` - Structure class
- `bed_rms` - Number of bedrooms
- `full_bth` - Number of full bathrooms
- `hlf_bth` - Number of half bathrooms
- `kitchens` - Number of kitchens
- `tt_rms` - Total rooms
- `res_units` - Residential units
- `com_units` - Commercial units
- `rc_units` - Other units

## Setup Instructions

### 1. Update Database Schema

First, update your database with the new schema:

```bash
cd /Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/web_app
psql -h localhost -U postgres -d abcdc_allston_brighton -f complete_schema.sql
```

### 2. Load Buildings Data

Run the data loader to populate the buildings table:

```bash
# Option 1: Use the helper script
python run_data_loader.py

# Option 2: Run directly
python load_buildings_data.py
```

### 3. Start the Web Application

```bash
python app.py
```

## Usage

### Buildings Page

Visit `/buildings` to view the buildings data with the following features:

- **Filtering**: Search by owner name, address, or property value range
- **Pagination**: Browse through large datasets with 50 records per page
- **Sorting**: Results are sorted by total value (highest first)
- **Detailed View**: Click "View Details" to see comprehensive building information

### Navigation

The buildings page is accessible through:
- Main navigation menu: "Buildings"
- Home page quick action button
- Direct URL: `http://localhost:5000/buildings`

### Home Page Integration

The home page now displays:
- Total buildings count in the statistics cards
- Quick action button to access buildings data

## Data Processing

The data loader (`load_buildings_data.py`) performs the following operations:

1. **Data Cleaning**: Removes commas and dollar signs from numeric values
2. **Null Handling**: Converts empty strings and 'N/A' values to NULL
3. **Type Conversion**: Properly converts numeric fields to appropriate data types
4. **Batch Insertion**: Efficiently inserts data in batches for better performance

## File Structure

```
web_app/
├── complete_schema.sql          # Updated database schema
├── load_buildings_data.py      # Data loader script
├── run_data_loader.py          # Helper script to run loader
├── app.py                      # Updated Flask application
├── templates/
│   ├── base.html              # Updated navigation
│   ├── index.html             # Updated home page
│   └── buildings.html         # New buildings page template
└── BUILDINGS_README.md        # This documentation
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Ensure your database is running and credentials are correct in `.env` file
2. **CSV File Not Found**: Verify the path to `building_property_with_suffix.csv` is correct
3. **Permission Errors**: Ensure the database user has INSERT permissions on the buildings table

### Data Quality

The loader handles various data quality issues:
- Missing or malformed numeric values
- Empty string values
- Inconsistent formatting (commas, dollar signs)
- Null values in required fields

## Future Enhancements

Potential improvements for the buildings feature:
- Advanced search and filtering options
- Export functionality (CSV, PDF)
- Map integration showing building locations
- Owner contact information management
- Property value trend analysis
- Building condition assessments
