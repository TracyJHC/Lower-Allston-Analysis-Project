# Database Inventory and Dashboard Plan

## Executive Summary

The ABCDC database contains comprehensive spatial and demographic data for Allston-Brighton, including voters, buildings, census tracts, and geographic boundaries. This document inventories all available data and provides recommendations for a coherent dashboard.

## Database Overview

### Tables and Row Counts

| Table | Rows | Description |
|-------|------|-------------|
| **voters** | 43,759 | Registered voters with demographics |
| **buildings** | 10,272 | Building structures with property data |
| **census_tracts** | 22 | Census tracts with income data |
| **precincts** | 29 | Electoral precincts (16 in Ward 21, 13 in Ward 22) |
| **precinct_census_tract_mapping** | 117 | Spatial relationships between precincts and tracts |
| **geo_precincts** | 29 | Precinct boundaries (PostGIS geometry) |
| **geo_boundary** | 1 | Allston-Brighton boundary |
| **geo_parks** | 1,099 | Parks and open spaces |
| **geo_roads** | 141 | Road segments |
| **voters_buildings_map** | 27,769 | Voter-to-building linkages |

---

## Detailed Data Inventory

### 1. VOTERS TABLE (43,759 records)

**Key Fields:**
- `res_id` (PK): Unique voter ID
- `last_name`, `first_name`: Voter name
- `date_of_birth`, `age`: Age demographics
- `is_elderly`: Boolean flag (62+ years)
- `ward_id`, `precinct_id`: Geographic assignment
- `street_number`, `street_name`, `apartment`: Address components
- `normalized_address`: Standardized address
- `latitude`, `longitude`: Geocoded coordinates
- `occupation`: Employment data

**Statistics:**
- **Ward 21**: 23,781 voters (4,199 elderly, avg age 40.3)
- **Ward 22**: 19,978 voters (3,197 elderly, avg age 40.7)
- **Total Elderly**: 7,396 voters (16.9%)
- **Geographic Coverage**: All 29 precincts

**Use Cases:**
- Demographic analysis by ward/precinct
- Elderly population mapping
- Voter distribution visualization
- Address-based analysis

---

### 2. BUILDINGS TABLE (10,272 records)

**Key Fields:**
- `struct_id` (PK): Unique building identifier
- `parcel_id`: Links to parcels
- `st_num`, `st_num2`, `st_name`: Address components
- `owner`, `owner_occ`: Ownership information
- `bldg_type`, `structure_class`: Building classification
- `yr_built`, `yr_remodel`: Construction dates
- `res_units`, `com_units`, `rc_units`: Unit counts
- `bed_rms`, `full_bth`, `hlf_bth`, `kitchens`: Room counts
- `total_value`, `gross_tax`, `land_value`, `bldg_value`: Financial data
- `land_sf`, `gross_area`, `living_area`: Size metrics
- `geometry`: PostGIS MultiPolygon (10,272 buildings have geometry)

**Statistics:**
- **Buildings with geometry**: 10,272 (100%)
- **Buildings with voters mapped**: 5,589 (54.4%)
- **Total residential units**: 19,218
- **Total commercial units**: 127
- **Average year built**: 1971
- **Unique parcels**: 499

**Use Cases:**
- Property value analysis
- Building age and condition assessment
- Residential vs commercial unit distribution
- Ownership patterns
- Spatial building density

---

### 3. CENSUS TRACTS TABLE (22 records)

**Key Fields:**
- `tract_id` (PK): Census tract identifier (e.g., "25025000101")
- `tract_name`: Human-readable name
- `state_code`, `county_code`, `tract_code`: Geographic codes
- `median_income`: Household median income (DECIMAL)
- `geometry`: PostGIS Polygon (all 22 tracts have geometry)

**Statistics:**
- **Total tracts**: 22
- **Tracts with income data**: 22 (100%)
- **Income range**: $33,229 - $151,466 (median)
- **Spatial coverage**: All of Allston-Brighton

**Use Cases:**
- Income inequality analysis
- Economic geography visualization
- Socioeconomic mapping
- Integration with precinct data

---

### 4. PRECINCTS TABLE (29 records)

**Key Fields:**
- `ward_id`, `precinct_id` (composite PK): Ward and precinct number
- `precinct_name`: Display name

**Statistics:**
- **Ward 21 (Allston)**: 16 precincts
- **Ward 22 (Brighton)**: 13 precincts
- **Total**: 29 precincts

**Precinct-Level Voter Data (Sample):**
- Precinct 21-1: 1,766 voters (165 elderly, avg age 36.4)
- Precinct 21-2: 541 voters (22 elderly, avg age 30.0)
- Precinct 21-3: 1,206 voters (138 elderly, avg age 36.2)
- ... (all 29 precincts have voter data)

**Use Cases:**
- Electoral analysis
- Precinct-level demographics
- Voting district visualization
- Resource allocation

---

### 5. PRECINCT_CENSUS_TRACT_MAPPING (117 records)

**Key Fields:**
- `mapping_id` (PK): Auto-increment
- `ward_id`, `precinct_id`: Precinct reference
- `tract_id`: Census tract reference
- `overlap_percentage`: Percentage of precinct covered by tract
- `overlap_type`: One of: majority, significant, partial, minor, proximity

**Statistics:**
- **Total mappings**: 117
- **Precincts mapped**: 29 (100% coverage)
- **Tracts mapped**: 17 unique tracts
- **Overlap types**: Mix of direct intersections and proximity mappings

**Use Cases:**
- Cross-referencing electoral and census geography
- Socioeconomic analysis by precinct
- Income overlays on precinct maps

---

### 6. GEOGRAPHIC BOUNDARIES

#### geo_boundary (1 record)
- Allston-Brighton boundary polygon
- Used for area calculations and filtering

#### geo_precincts (29 records)
- Precinct boundary polygons (PostGIS)
- All 29 precincts have geometry

#### geo_parks (1,099 records)
- Parks and open spaces
- Spatial features for amenity analysis

#### geo_roads (141 records)
- Road segments
- Transportation network data

**Use Cases:**
- Boundary visualization
- Spatial filtering
- Proximity analysis
- Amenity mapping

---

### 7. VOTERS_BUILDINGS_MAP (27,769 records)

**Key Fields:**
- `res_id`: Voter reference
- `struct_id`: Building reference
- Mapping between voters and buildings at street address level

**Statistics:**
- **Total mappings**: 27,769
- **Voters mapped**: 27,769 (63.4% of all voters)
- **Buildings with mapped voters**: 5,589

**Use Cases:**
- Building-level voter demographics
- Elderly concentration by building
- Housing policy analysis
- Resource targeting

---

## Current Web App Features

### Existing Pages/Routes

1. **Home Page (`/`)**
   - Statistics cards (voters, elderly, buildings)
   - Charts: Elderly vs non-elderly, by ward, by precinct
   - Top buildings by elderly voters
   - Quick action buttons

2. **Voters Page (`/voters`)**
   - Paginated voter list
   - Filters: ward, elderly only
   - Basic display

3. **Buildings Page (`/buildings`)**
   - Paginated building list
   - Filters: owner, address, value range, owner-occupied
   - Basic display

4. **Properties Page (`/properties`)**
   - Property assessment data
   - Value filtering

5. **API Endpoints (`/api/*`)**
   - `/api/elderly_by_ward`: Elderly population by ward
   - `/api/properties_near_elderly`: Properties near elderly (function-based)
   - `/api/parcels`: Parcel data

---

## Recommended Dashboard Enhancements

### 1. SPATIAL MAP DASHBOARD (Priority: HIGH)

**New Route: `/map` or `/dashboard`**

**Features:**
- Interactive map using Leaflet or Mapbox
- Multiple layers:
  - Precinct boundaries (toggleable)
  - Census tract boundaries with income choropleth
  - Building locations (clustered)
  - Voter density heatmap
  - Elderly voter concentration
  - Parks and roads
- Layer controls
- Click interactions:
  - Precinct: Show voter stats, census tract info
  - Census tract: Show income, overlapping precincts
  - Building: Show details, mapped voters, elderly count
- Legend and filters

**Data Needed:**
- GeoJSON exports of all spatial layers
- API endpoints for dynamic data loading

---

### 2. CENSUS TRACT ANALYSIS PAGE (Priority: HIGH)

**New Route: `/census`**

**Features:**
- Census tract table with:
  - Tract ID, name
  - Median income (with color coding)
  - Area (sq km)
  - Overlapping precincts
  - Linked precinct demographics
- Income distribution chart
- Tract-to-precinct mapping visualization
- Click to view detail page

**Data Available:**
- All 22 census tracts with income
- 117 precinct-tract mappings
- Precinct demographics

---

### 3. PRECINCT DETAIL PAGES (Priority: MEDIUM)

**New Route: `/precincts/<ward_id>/<precinct_id>`**

**Features:**
- Precinct overview:
  - Total voters
  - Elderly count and percentage
  - Average age
  - Age distribution chart
- Mapped census tracts:
  - List of overlapping tracts
  - Income ranges
  - Overlap percentages
- Top buildings:
  - Buildings with most elderly voters
  - Building details
- Voter distribution map
- Elderly concentration heatmap

**Data Available:**
- All precinct data
- Voter demographics
- Census tract mappings
- Building mappings

---

### 4. ELDERLY ANALYSIS DASHBOARD (Priority: HIGH)

**New Route: `/elderly-analysis`**

**Features:**
- Elderly population by:
  - Ward (comparison)
  - Precinct (detailed breakdown)
  - Census tract (income correlation)
- Age segmentation:
  - 62-69, 70-79, 80-89, 90+
- Building concentration:
  - Top buildings by elderly count
  - Buildings with high elderly percentage
- Geographic distribution:
  - Heatmap of elderly density
  - Clusters of elderly populations
- Income correlation:
  - Elderly population vs. median income by tract

**Data Available:**
- 7,396 elderly voters
- Age data in voters table
- Building mappings
- Census tract income data

---

### 5. BUILDING ANALYSIS PAGE (Priority: MEDIUM)

**Enhancement to `/buildings`**

**New Features:**
- Map view toggle
- Building detail pages (`/buildings/<struct_id>`)
- Voter mapping:
  - Show mapped voters per building
  - Elderly count per building
- Building clusters:
  - Group by address/parcel
  - Aggregate statistics
- Filters:
  - Buildings with elderly voters
  - Buildings by value range
  - Buildings by year built
- Export functionality

**Data Available:**
- 10,272 buildings with geometry
- 5,589 buildings with mapped voters
- 27,769 voter mappings

---

### 6. INCOME & DEMOGRAPHICS CORRELATION (Priority: MEDIUM)

**New Route: `/income-analysis`**

**Features:**
- Income distribution by census tract
- Precinct income estimates (weighted by overlap)
- Elderly population vs. income scatter plot
- Income quartiles mapping
- Building values vs. census income correlation

**Data Available:**
- Census tract median income ($33K - $151K)
- Building values
- Precinct-tract mappings

---

### 7. COMPARATIVE ANALYSIS (Priority: LOW)

**New Route: `/compare`**

**Features:**
- Side-by-side comparison:
  - Two precincts
  - Two census tracts
  - Two buildings
- Key metrics comparison
- Visual charts comparison

---

## API Endpoints Needed

### New Endpoints to Create:

1. **Spatial Data APIs:**
   - `/api/geojson/precincts` - Precinct boundaries as GeoJSON
   - `/api/geojson/census-tracts` - Census tract boundaries with income
   - `/api/geojson/buildings` - Building geometries (with filters)
   - `/api/geojson/voters` - Voter points (with clustering options)

2. **Analysis APIs:**
   - `/api/precincts/<ward_id>/<precinct_id>` - Precinct detail
   - `/api/census-tracts/<tract_id>` - Census tract detail
   - `/api/buildings/<struct_id>` - Building detail with voters
   - `/api/elderly-by-precinct` - Elderly demographics by precinct
   - `/api/income-distribution` - Income data for charts

3. **Statistics APIs:**
   - `/api/stats/overview` - Overall database statistics
   - `/api/stats/ward/<ward_id>` - Ward-level statistics
   - `/api/stats/precinct/<ward_id>/<precinct_id>` - Precinct statistics

4. **Search APIs:**
   - `/api/search/voters?q=<query>` - Search voters
   - `/api/search/buildings?q=<query>` - Search buildings
   - `/api/search/addresses?q=<query>` - Address search

---

## Data Relationships Summary

```
wards (2)
  └── precincts (29)
       ├── voters (43,759)
       │    └── voters_buildings_map (27,769)
       │         └── buildings (10,272)
       └── precinct_census_tract_mapping (117)
            └── census_tracts (22)
                 └── precinct_census_tract_mapping (back reference)
```

**Key Relationships:**
- Voters → Precincts (ward_id, precinct_id)
- Voters → Buildings (via voters_buildings_map)
- Precincts → Census Tracts (via precinct_census_tract_mapping)
- All spatial layers have PostGIS geometry

---

## Implementation Priority

### Phase 1: Core Spatial Visualization (Week 1-2)
1. Interactive map with multiple layers
2. Census tract choropleth with income
3. Precinct boundary overlay
4. Basic click interactions

### Phase 2: Analysis Pages (Week 3-4)
1. Census tract analysis page
2. Enhanced elderly analysis dashboard
3. Precinct detail pages

### Phase 3: Enhanced Features (Week 5-6)
1. Building detail pages
2. Income correlation analysis
3. Advanced filters and search

### Phase 4: Polish (Week 7-8)
1. Comparative analysis
2. Export functionality
3. Performance optimization
4. Mobile responsiveness

---

## Technical Recommendations

### Frontend
- **Mapping Library**: Leaflet.js (lightweight) or Mapbox GL JS (more features)
- **Charts**: Chart.js (already in use) or D3.js for advanced visualizations
- **UI Framework**: Bootstrap (already in use) - enhance with custom components

### Backend
- **API Structure**: RESTful endpoints returning JSON
- **GeoJSON**: Generate on-demand or cache for performance
- **Caching**: Consider Redis for frequently accessed data
- **Pagination**: Keep for large datasets

### Database
- **Indexes**: Already well-indexed, verify query performance
- **Views**: Create materialized views for complex aggregations
- **Functions**: PostGIS functions for spatial queries

---

## Summary

**Available Data:**
- ✅ 43,759 voters with demographics
- ✅ 10,272 buildings with property data
- ✅ 22 census tracts with income data
- ✅ 29 precincts with full coverage
- ✅ 117 spatial mappings
- ✅ 27,769 voter-building linkages
- ✅ 1,099 parks and 141 road segments
- ✅ Complete spatial geometry for all features

**Current Features:**
- Basic list views (voters, buildings, properties)
- Simple charts on home page
- Limited API endpoints

**Recommended Enhancements:**
- Interactive spatial map dashboard
- Census tract analysis
- Enhanced elderly analysis
- Precinct detail pages
- Building detail pages
- Income-demographics correlation
- Comprehensive API layer

The database is rich with data and relationships. The recommended dashboard will provide comprehensive visualization and analysis capabilities for the ABCDC's affordable senior housing initiative.

