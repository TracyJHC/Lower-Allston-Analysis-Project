# Looker Studio Charts Plan for ABCDC Project

## Data Workflow

1. **Export CSV from Local Database:**
   - Run: `fa25-team-a/web_app/scripts/export/export_for_bigquery_local.sh`
   - Exports elderly census tract data to: `data/processed/bigquery_exports/elderly_census_tracts_one_to_one.csv`
   - Total elderly counted: **4,799** (from one-to-one mapped elderly with spatial intersections)

2. **Upload to BigQuery:**
   - Upload CSV to Cloud Storage: `gsutil cp [CSV_FILE] gs://abcdc-data/`
   - Import to BigQuery with schema:
     ```
     geo_id:STRING
     tract_name:STRING
     median_income:FLOAT
     tract_geom:STRING
     elderly_count:INTEGER
     avg_age:FLOAT
     ```
   - Convert `tract_geom` to GEOGRAPHY type using `ST_GEOGFROMGEOJSON()`

3. **Connect Looker Studio to BigQuery:**
   - Create data source from BigQuery table
   - Use for all visualizations

---

## Required Deliverables (5-7 Visualizations)

### 1. **Elderly Resident Distribution Map**
**Type:** Geo Chart / Filled Map
**Purpose:** Show where elderly residents are located across Allston-Brighton by census tract
**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`
**Key Metrics:**
- Elderly population by census tract
- Density heatmap of elderly residents
- Median income by tract
- Average age by tract

**Data Fields:**
- `geo_id` - Census tract ID
- `tract_name` - Census tract name
- `tract_geom` - GEOGRAPHY type (for map boundaries)
- `elderly_count` - Number of elderly per tract
- `median_income` - Median income for tract
- `avg_age` - Average age of elderly in tract

**Visualization:**
- Filled map (choropleth) with census tracts colored by elderly count
- Color scale: Light (low count) to Dark (high count)
- Tooltip showing: tract name, elderly count, median income, avg age
- Filter by income category (low/moderate/high)

---

### 2. **Elderly Demographics & Tenure Analysis**
**Type:** Combo Chart (Bar + Line) + Pie Chart
**Purpose:** Analyze residential tenure, ownership status, and demographics
**Data Source:** `voters` + `buildings` + `property_ownership`
**Key Metrics:**
- Elderly count by age group (62-69, 70-79, 80-89, 90+)
- Homeowner vs Renter breakdown
- Elderly by precinct/ward
- Average age by precinct

**SQL Query:**
```sql
SELECT 
    p.precinct_id,
    p.ward_id,
    COUNT(DISTINCT v.res_id) as elderly_count,
    COUNT(DISTINCT CASE WHEN b.owner IS NOT NULL THEN v.res_id END) as homeowners,
    COUNT(DISTINCT CASE WHEN b.owner IS NULL THEN v.res_id END) as renters,
    AVG(v.age) as avg_age,
    CASE 
        WHEN v.age BETWEEN 62 AND 69 THEN '62-69'
        WHEN v.age BETWEEN 70 AND 79 THEN '70-79'
        WHEN v.age BETWEEN 80 AND 89 THEN '80-89'
        WHEN v.age >= 90 THEN '90+'
    END as age_group
FROM voters v
JOIN precincts p ON v.precinct_id = p.precinct_id
LEFT JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
LEFT JOIN buildings b ON vbm.struct_id = b.struct_id
WHERE v.is_elderly = true
GROUP BY p.precinct_id, p.ward_id, age_group
```

**Visualizations:**
- Bar chart: Elderly count by precinct
- Pie chart: Homeowner vs Renter distribution
- Line chart: Age distribution (62-69, 70-79, 80-89, 90+)
- Scorecard: Total elderly, % homeowners, % renters

---

### 3. **Income & Housing Affordability Analysis**
**Type:** Bar Chart + Table + Scorecard
**Purpose:** Analyze income levels and housing affordability barriers
**Data Source:** `census_tracts` + `voters` + `precinct_census_tract_mapping`
**Key Metrics:**
- Median income by census tract
- Elderly population in low-income tracts (<$50k median income)
- Elderly concentration in high vs low-income areas
- Income distribution across precincts

**SQL Query:**
```sql
SELECT 
    ct.tract_id,
    ct.tract_name,
    ct.median_income,
    COUNT(DISTINCT v.res_id) as elderly_count,
    CASE 
        WHEN ct.median_income < 50000 THEN 'Low Income'
        WHEN ct.median_income < 75000 THEN 'Moderate Income'
        ELSE 'Higher Income'
    END as income_category
FROM census_tracts ct
JOIN precinct_census_tract_mapping pctm ON ct.tract_id = pctm.tract_id
JOIN voters v ON pctm.precinct_id = v.precinct_id AND v.is_elderly = true
GROUP BY ct.tract_id, ct.tract_name, ct.median_income
ORDER BY ct.median_income ASC
```

**Visualizations:**
- Bar chart: Elderly count by income category
- Table: Census tracts with median income and elderly count
- Scorecard: % of elderly in low-income tracts
- Combo chart: Income vs Elderly concentration

---

### 4. **Building Condition & Property Analysis**
**Type:** Table + Bar Chart + Scorecard
**Purpose:** Identify barriers in current living situations (building condition, property value)
**Data Source:** `buildings` + `property_assessments` + `voters_buildings_map` + `voters`
**Key Metrics:**
- Buildings with elderly residents by property value
- Building age distribution
- Property value ranges for elderly-occupied buildings
- Buildings needing improvements (if data available)

**SQL Query:**
```sql
SELECT 
    b.struct_id,
    b.st_num || ' ' || b.st_name as building_address,
    b.year_built,
    pa.total_value,
    COUNT(DISTINCT v.res_id) as elderly_residents,
    CASE 
        WHEN pa.total_value < 500000 THEN 'Low Value'
        WHEN pa.total_value < 1000000 THEN 'Moderate Value'
        ELSE 'High Value'
    END as value_category
FROM buildings b
JOIN voters_buildings_map vbm ON b.struct_id = vbm.struct_id
JOIN voters v ON vbm.res_id = v.res_id AND v.is_elderly = true
LEFT JOIN property_assessments pa ON b.parcel_id = pa.parcel_id AND pa.fiscal_year = (SELECT MAX(fiscal_year) FROM property_assessments)
GROUP BY b.struct_id, b.st_num, b.st_name, b.year_built, pa.total_value
ORDER BY elderly_residents DESC
```

**Visualizations:**
- Table: Top buildings by elderly resident count with property values
- Bar chart: Elderly residents by property value category
- Scorecard: Average property value, oldest building, newest building
- Histogram: Building age distribution

---

### 5. **Store Proximity & Accessibility Analysis**
**Type:** Map + Bar Chart + Scorecard
**Purpose:** Assess access to essential services (stores, groceries) for elderly residents
**Data Source:** `stores` + `voter_store_nearby` + `voters`
**Key Metrics:**
- Elderly residents with nearby stores (within 1km)
- Average distance to nearest store
- Store type distribution (grocery, pharmacy, etc.)
- Elderly without nearby stores (accessibility gap)

**SQL Query:**
```sql
SELECT 
    s.store_type,
    COUNT(DISTINCT s.store_id) as store_count,
    COUNT(DISTINCT vsn.res_id) as elderly_served,
    AVG(vsn.distance_meters) as avg_distance_meters,
    COUNT(DISTINCT CASE WHEN vsn.distance_meters <= 500 THEN vsn.res_id END) as within_500m,
    COUNT(DISTINCT CASE WHEN vsn.distance_meters <= 1000 THEN vsn.res_id END) as within_1km
FROM stores s
LEFT JOIN voter_store_nearby vsn ON s.store_id = vsn.store_id
LEFT JOIN voters v ON vsn.res_id = v.res_id AND v.is_elderly = true
GROUP BY s.store_type
ORDER BY elderly_served DESC
```

**Visualizations:**
- Map: Stores + Elderly residents (colored by distance)
- Bar chart: Elderly served by store type
- Scorecard: % with stores within 500m, 1km
- Table: Store accessibility metrics

---

### 6. **Housing Readiness & Eligibility Assessment**
**Type:** Scorecard + Bar Chart + Table
**Purpose:** Identify elderly who may qualify for new affordable senior housing
**Data Source:** `voters` + `census_tracts` + `buildings` + `property_assessments`
**Key Metrics:**
- Elderly in low-income census tracts (potential eligibility)
- Elderly in high-value properties (may not qualify)
- Elderly renters (higher priority for housing)
- Elderly in older buildings (may need relocation)

**SQL Query:**
```sql
SELECT 
    CASE 
        WHEN ct.median_income < 50000 AND v.is_elderly = true THEN 'High Priority'
        WHEN ct.median_income < 75000 AND v.is_elderly = true THEN 'Medium Priority'
        ELSE 'Lower Priority'
    END as eligibility_tier,
    COUNT(DISTINCT v.res_id) as elderly_count,
    COUNT(DISTINCT CASE WHEN b.owner IS NULL THEN v.res_id END) as renters,
    COUNT(DISTINCT CASE WHEN b.year_built < 1950 THEN v.res_id END) as in_old_buildings
FROM voters v
JOIN precinct_census_tract_mapping pctm ON v.precinct_id = pctm.precinct_id
JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
LEFT JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
LEFT JOIN buildings b ON vbm.struct_id = b.struct_id
WHERE v.is_elderly = true
GROUP BY eligibility_tier
```

**Visualizations:**
- Scorecard: High/Medium/Lower priority counts
- Bar chart: Eligibility breakdown
- Table: Detailed eligibility criteria by precinct
- Pie chart: Priority distribution

---

### 7. **Outreach Opportunity Areas**
**Type:** Map + Table + Scorecard
**Purpose:** Identify areas with highest concentration of elderly needing outreach
**Data Source:** `voters` + `precincts` + `census_tracts` + `stores`
**Key Metrics:**
- Precincts with highest elderly density
- Areas with low store accessibility
- Low-income areas with high elderly population
- Combined opportunity score

**SQL Query:**
```sql
SELECT 
    p.precinct_id,
    p.precinct_name,
    p.ward_id,
    COUNT(DISTINCT v.res_id) as elderly_count,
    AVG(ct.median_income) as avg_median_income,
    COUNT(DISTINCT CASE WHEN vsn.distance_meters > 1000 THEN v.res_id END) as elderly_far_from_stores,
    -- Opportunity score (higher = more need)
    (COUNT(DISTINCT v.res_id) * 0.4) + 
    (CASE WHEN AVG(ct.median_income) < 50000 THEN 30 ELSE 0 END) +
    (COUNT(DISTINCT CASE WHEN vsn.distance_meters > 1000 THEN v.res_id END) * 0.3) as opportunity_score
FROM precincts p
JOIN voters v ON p.precinct_id = v.precinct_id AND v.is_elderly = true
LEFT JOIN precinct_census_tract_mapping pctm ON p.precinct_id = pctm.precinct_id
LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
LEFT JOIN voter_store_nearby vsn ON v.res_id = vsn.res_id
GROUP BY p.precinct_id, p.precinct_name, p.ward_id
ORDER BY opportunity_score DESC
```

**Visualizations:**
- Map: Precincts colored by opportunity score
- Table: Top precincts for outreach
- Scorecard: Total opportunity areas, high-priority precincts
- Bar chart: Opportunity score by precinct

---

## Additional Recommended Visualizations (If Time Permits)

### 8. **Geocoding Coverage Dashboard**
- Show % of elderly with coordinates
- Map of geocoded vs non-geocoded
- Coverage by precinct

### 9. **Building Elderly Concentration**
- Buildings with highest elderly resident counts
- Elderly density by building type
- Senior housing complexes identification

### 10. **Temporal Analysis** (if data available)
- Years residents have lived at address
- Building age vs resident age correlation

---

## Implementation Notes

1. **Data Source:** BigQuery table `elderly_census_tracts_one_to_one`
   - Exported from local PostgreSQL database
   - Contains 4,799 elderly residents mapped to census tracts
   - Includes tract geometries for map visualization

2. **Filters:** Add filters for:
   - Income categories (low/moderate/high based on median_income)
   - Census tract (geo_id)
   - Elderly count ranges

3. **Color Scheme:** Use consistent colors:
   - Elderly count: Light blue (low) to Dark blue (high)
   - Income: Green (high) to Red (low)
   - Age: Light orange (younger) to Dark orange (older)

4. **Interactivity:** Enable cross-filtering between charts so clicking one updates others

---

## BigQuery Setup

### After Importing CSV to BigQuery:

1. **Convert Geometry to GEOGRAPHY:**
```sql
CREATE OR REPLACE TABLE `abcdc-project.abcdc_data.elderly_census_tracts_one_to_one` AS
SELECT 
  geo_id,
  tract_name,
  median_income,
  ST_GEOGFROMGEOJSON(tract_geom) as tract_geom,
  elderly_count,
  avg_age
FROM `abcdc-project.abcdc_data.elderly_census_tracts_one_to_one`;
```

2. **Create Calculated Fields in Looker Studio:**
   - Income Category: `IF(median_income < 50000, "Low Income", IF(median_income < 75000, "Moderate Income", "Higher Income"))`
   - Elderly Density: `elderly_count / [tract_area]` (if area data available)

