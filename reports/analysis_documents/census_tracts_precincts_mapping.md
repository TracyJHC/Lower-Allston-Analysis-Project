# Census Tracts and Precincts Mapping Documentation

## Overview

This document describes the process of setting up census tract data and mapping precincts to census tracts in the Allston-Brighton ABCDC database. This includes:

1. **Schema Updates**: Converting the `precincts` table to use a composite primary key
2. **Data Population**: Loading all 29 precincts from Allston-Brighton (Wards 21 and 22)
3. **Census Data Loading**: Loading census tract geometries and income data
4. **Spatial Mapping**: Creating relationships between precincts and census tracts using spatial joins

## Prerequisites

- PostgreSQL database with PostGIS extension enabled
- Python 3 with required packages: `geopandas`, `pandas`, `psycopg`, `shapely`
- Census data files:
  - `2020_Census_Tracts_in_Boston_Reduced.shp` (or full shapefile)
  - `tracts_median_income.csv`
- Precinct GeoJSON file: `allston_brighton_precincts.geojson`

## Database Schema Changes

### Issue Identified

The original `precincts` table had:
- `precinct_id` as PRIMARY KEY (integer)
- Only 16 precincts loaded (8 per ward)
- **Problem**: Precinct numbers repeat across wards (e.g., Precinct 1 exists in both Ward 21 and Ward 22)

### Solution: Composite Primary Key

We changed the `precincts` table to use a composite primary key `(ward_id, precinct_id)` to allow precinct numbers to repeat across wards.

#### SQL Commands to Update Schema

```sql
-- 1. Drop existing primary key and foreign key constraints
ALTER TABLE precincts DROP CONSTRAINT precincts_pkey CASCADE;
ALTER TABLE voters DROP CONSTRAINT IF EXISTS voters_precinct_id_fkey;

-- 2. Create new composite primary key
ALTER TABLE precincts ADD PRIMARY KEY (ward_id, precinct_id);

-- 3. Update voters foreign key to use composite key
ALTER TABLE voters ADD CONSTRAINT voters_precinct_fkey 
    FOREIGN KEY (ward_id, precinct_id) 
    REFERENCES precincts(ward_id, precinct_id);
```

### Census Tracts Table

The `census_tracts` table includes PostGIS geometry:

```sql
CREATE TABLE census_tracts (
    tract_id VARCHAR(20) PRIMARY KEY,
    tract_name VARCHAR(200),
    state_code VARCHAR(2),
    county_code VARCHAR(3),
    tract_code VARCHAR(6),
    median_income DECIMAL(12,2),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_census_tracts_geoid ON census_tracts(tract_id);
CREATE INDEX idx_census_tracts_geometry ON census_tracts USING GIST(geometry);
CREATE INDEX idx_census_tracts_income ON census_tracts(median_income);
CREATE INDEX idx_census_tracts_state_county ON census_tracts(state_code, county_code);
```

### Precinct-Census Tract Mapping Table

```sql
CREATE TABLE precinct_census_tract_mapping (
    mapping_id SERIAL PRIMARY KEY,
    ward_id INTEGER NOT NULL,
    precinct_id INTEGER NOT NULL,
    tract_id VARCHAR(20),
    overlap_percentage DECIMAL(5,2),
    overlap_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id, precinct_id) REFERENCES precincts(ward_id, precinct_id),
    FOREIGN KEY (tract_id) REFERENCES census_tracts(tract_id),
    UNIQUE(ward_id, precinct_id, tract_id)
);

-- Create indexes
CREATE INDEX idx_precinct_tract_precinct 
    ON precinct_census_tract_mapping(ward_id, precinct_id);
CREATE INDEX idx_precinct_tract_tract 
    ON precinct_census_tract_mapping(tract_id);
```

## Data Population Steps

### Step 1: Populate All Precincts

The database initially had only 16 precincts. We need to load all 29 precincts from Allston-Brighton:

- **Ward 21 (Allston)**: 16 precincts (1-16)
- **Ward 22 (Brighton)**: 13 precincts (1-13)

#### SQL Command to Insert Missing Precincts

```sql
-- Insert all precincts from geo_precincts table
INSERT INTO precincts (precinct_id, ward_id, precinct_name)
SELECT DISTINCT 
    precinct::integer,
    ward::integer,
    'Precinct ' || precinct
FROM geo_precincts
ON CONFLICT (ward_id, precinct_id) DO NOTHING;
```

#### Verification

```sql
-- Check total precinct count (should be 29)
SELECT 
    ward_id, 
    COUNT(*) as precinct_count 
FROM precincts 
GROUP BY ward_id 
ORDER BY ward_id;

-- Expected output:
-- ward_id | precinct_count
-- ---------+---------------
--      21 |             16
--      22 |             13
```

### Step 2: Load Census Tract Data

Use the Python script to load census tract geometries and income data:

```bash
cd /Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/web_app/scripts
python3 load_census_data.py
```

#### What the script does:

1. Loads shapefile with geometries (sets CRS to EPSG:2249, converts to EPSG:4326)
2. Loads income CSV and creates GEOID20
3. Cleans income data (filters invalid values)
4. Merges geometry with income data
5. Inserts into `census_tracts` table

#### Verification

```sql
-- Check census tracts loaded
SELECT COUNT(*) as total_tracts FROM census_tracts;
-- Expected: 22 tracts

-- Check tracts with income data
SELECT 
    COUNT(*) as tracts_with_income,
    COUNT(*) - COUNT(median_income) as tracts_without_income
FROM census_tracts;
```

### Step 3: Create Precinct-Census Tract Mappings

Use the Python script to perform spatial joins:

```bash
cd /Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/web_app/scripts
python3 map_precincts_to_census_tracts.py
```

#### What the script does:

1. Loads precinct geometries from GeoJSON or database
2. Loads census tract geometries from database
3. Performs spatial joins:
   - First tries direct `ST_Intersects`
   - Falls back to 500m buffer for precincts without direct intersections
4. Calculates overlap percentages:
   - For direct intersections: area-based overlap
   - For proximity matches: distance-based overlap
5. Inserts mappings into `precinct_census_tract_mapping` table

#### Verification

```sql
-- Check all precincts are mapped
SELECT 
    COUNT(DISTINCT ward_id || '-' || precinct_id) as precincts_mapped,
    COUNT(*) as total_mappings,
    COUNT(DISTINCT tract_id) as tracts_mapped
FROM precinct_census_tract_mapping;

-- Expected:
-- precincts_mapped: 29
-- total_mappings: ~117 (multiple tracts per precinct)
-- tracts_mapped: 22

-- Check for unmapped precincts
SELECT p.ward_id, p.precinct_id, p.precinct_name
FROM precincts p
LEFT JOIN precinct_census_tract_mapping m 
    ON p.ward_id = m.ward_id AND p.precinct_id = m.precinct_id
WHERE m.mapping_id IS NULL;
-- Should return 0 rows
```

## Spatial Analysis Details

### Coordinate Reference Systems

- **Input Shapefile**: EPSG:2249 (Massachusetts State Plane Mainland - FEET)
- **Database Storage**: EPSG:4326 (WGS84 - Geographic)
- **Spatial Calculations**: EPSG:32619 (UTM Zone 19N) for accurate area/distance

### Geometry Alignment Issues

Some precincts may not directly intersect with census tracts due to:
- Boundary digitization differences
- Different data sources
- Coordinate system transformations

**Solution**: The mapping script uses a 500-meter buffer to find nearby tracts for precincts without direct intersections. These are marked with `overlap_type = 'proximity'`.

### Overlap Types

- **majority**: >90% overlap
- **significant**: 50-90% overlap
- **partial**: 10-50% overlap
- **minor**: <10% overlap
- **proximity**: Within 500m but no direct intersection

## Verification Queries

### Complete Status Check

```sql
-- Overall statistics
SELECT 
    'Precincts' as source,
    COUNT(*) as count
FROM precincts
UNION ALL
SELECT 
    'Census Tracts',
    COUNT(*)
FROM census_tracts
UNION ALL
SELECT 
    'Mappings',
    COUNT(*)
FROM precinct_census_tract_mapping
UNION ALL
SELECT 
    'Precincts with Mappings',
    COUNT(DISTINCT ward_id || '-' || precinct_id)
FROM precinct_census_tract_mapping;
```

### Precincts by Ward

```sql
SELECT 
    p.ward_id,
    COUNT(DISTINCT p.precinct_id) as total_precincts,
    COUNT(DISTINCT m.mapping_id) as mappings_count,
    COUNT(DISTINCT m.tract_id) as unique_tracts
FROM precincts p
LEFT JOIN precinct_census_tract_mapping m 
    ON p.ward_id = m.ward_id AND p.precinct_id = m.precinct_id
GROUP BY p.ward_id
ORDER BY p.ward_id;
```

### Census Tracts Coverage

```sql
SELECT 
    ct.tract_id,
    ct.tract_name,
    COUNT(DISTINCT m.ward_id || '-' || m.precinct_id) as precinct_count
FROM census_tracts ct
LEFT JOIN precinct_census_tract_mapping m ON ct.tract_id = m.tract_id
GROUP BY ct.tract_id, ct.tract_name
ORDER BY precinct_count DESC, ct.tract_id;
```

### Precincts with Proximity Mappings

```sql
SELECT 
    m.ward_id,
    m.precinct_id,
    p.precinct_name,
    m.tract_id,
    m.overlap_percentage,
    m.overlap_type
FROM precinct_census_tract_mapping m
JOIN precincts p ON m.ward_id = p.ward_id AND m.precinct_id = p.precinct_id
WHERE m.overlap_type = 'proximity'
ORDER BY m.ward_id, m.precinct_id;
```

## Troubleshooting

### Issue: Precincts not mapping to census tracts

**Check:**
1. Verify geometries exist:
   ```sql
   SELECT COUNT(*) FROM geo_precincts;
   SELECT COUNT(*) FROM census_tracts WHERE geometry IS NOT NULL;
   ```

2. Check CRS:
   ```sql
   SELECT ST_SRID(geom) FROM geo_precincts LIMIT 1;
   SELECT ST_SRID(geometry) FROM census_tracts LIMIT 1;
   -- Both should be 4326
   ```

3. Verify spatial relationships:
   ```sql
   SELECT 
       p.ward_id, 
       p.precinct_id,
       COUNT(ct.tract_id) as intersecting_tracts
   FROM precincts p
   JOIN geo_precincts gp 
       ON p.ward_id = gp.ward::integer AND p.precinct_id = gp.precinct::integer
   LEFT JOIN census_tracts ct 
       ON ST_Intersects(gp.geom, ct.geometry)
   GROUP BY p.ward_id, p.precinct_id
   HAVING COUNT(ct.tract_id) = 0;
   ```

### Issue: Foreign key constraint errors

If you get foreign key errors when running the mapping script:

1. Verify precincts exist:
   ```sql
   SELECT COUNT(*) FROM precincts;
   -- Should be 29
   ```

2. Verify census tracts exist:
   ```sql
   SELECT COUNT(*) FROM census_tracts;
   -- Should be 22
   ```

3. Check foreign key constraints:
   ```sql
   SELECT 
       conname,
       conrelid::regclass as table_name,
       confrelid::regclass as referenced_table
   FROM pg_constraint
   WHERE contype = 'f'
       AND conrelid::regclass::text = 'precinct_census_tract_mapping';
   ```

## File Locations

- **Census Data Loading Script**: `web_app/scripts/load_census_data.py`
- **Mapping Script**: `web_app/scripts/map_precincts_to_census_tracts.py`
- **Schema File**: `web_app/config/complete_schema.sql`
- **Census Data**: `data/processed/census_data/`
- **Precinct GeoJSON**: `data/processed/geospatial_data/allston_brighton_precincts.geojson`

## Quick Reference: Complete Setup

```bash
# 1. Update schema (if needed)
psql -h localhost -U <user> -d abcdc_spatial -f web_app/config/complete_schema.sql

# 2. Populate precincts
psql -h localhost -U <user> -d abcdc_spatial <<EOF
INSERT INTO precincts (precinct_id, ward_id, precinct_name)
SELECT DISTINCT precinct::integer, ward::integer, 'Precinct ' || precinct
FROM geo_precincts
ON CONFLICT (ward_id, precinct_id) DO NOTHING;
EOF

# 3. Load census data
cd web_app/scripts
python3 load_census_data.py

# 4. Create mappings
python3 map_precincts_to_census_tracts.py

# 5. Verify
psql -h localhost -U <user> -d abcdc_spatial -c "
SELECT 
    COUNT(*) as total_precincts,
    (SELECT COUNT(*) FROM census_tracts) as total_tracts,
    (SELECT COUNT(*) FROM precinct_census_tract_mapping) as total_mappings;
"
```

## Summary

- **29 precincts** loaded (16 in Ward 21, 13 in Ward 22)
- **22 census tracts** loaded with geometries and income data
- **117 mappings** created between precincts and census tracts
- **100% coverage**: All precincts have at least one census tract mapping
- **Spatial accuracy**: Uses direct intersections with 500m buffer fallback for alignment issues

