# Looker Studio Visualization Plan
## ABCDC Affordable Senior Housing Initiative

**Project:** Allston Brighton Community Development Corporation: Harvard Allston Project  
**Date:** November 2025  
**Purpose:** Data-driven visualizations to support elderly resident outreach and affordable senior housing planning

---

## Data Workflow

1. **Export from Local Database:**
   - Run script: `fa25-team-a/web_app/scripts/export/export_for_bigquery_local.sh`
   - Exports to: `data/processed/bigquery_exports/elderly_census_tracts_one_to_one.csv`
   - Contains: 4,799 elderly residents mapped to census tracts

2. **Upload to BigQuery:**
   - Upload CSV to Cloud Storage: `gs://abcdc-data/`
   - Import to BigQuery with schema (see Step 3 in step-by-step guide)
   - Convert `tract_geom` from STRING to GEOGRAPHY type

3. **Connect Looker Studio:**
   - Connect to BigQuery table as data source
   - Create visualizations from BigQuery data

---

## Project Context

### Key Questions to Answer
1. Who are the elderly residents in Allston-Brighton, and where are they located?
2. How many qualify for new affordable senior housing opportunities?
3. What barriers exist in their current living situations (financial, building condition, etc)?
4. How are elderly distributed across income levels and census tracts?
5. What would be the impact on the housing market if they transitioned to senior housing?

### Project Goals
- Identify elderly residents eligible for affordable senior housing
- Build foundation for equitable outreach and data-informed planning
- Assess housing readiness and forecast impact of new developments
- Support strategic outreach to aging residents

**Data Summary:**
- Total elderly in dataset: **4,799** residents
- Mapped to census tracts with spatial intersections
- Includes income, age, and geographic data

## 5-7 Core Visualizations for Looker Studio

### 1. Elderly Resident Distribution Map
**Purpose:** Answer "Who are the elderly residents and where are they located?"

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualization:**
- **Chart Type:** Geo Chart - Filled Map (Choropleth)
- **Geographic Dimension:** `tract_geom` (GEOGRAPHY type)
- **Dimension:** `tract_name`
- **Metrics:** `elderly_count`
- **Color by:** `elderly_count` (color scale: light to dark)
- **Tooltip:** Tract name, elderly count, median income, average age
- **Map Style:** Filled map with census tract boundaries

**Filters:**
- Income Category (Low/Moderate/Higher)
- Elderly Count Range
- Census Tract

**Why This Matters:** Shows geographic distribution by census tract for targeted outreach planning

---

### 2. Income & Elderly Distribution Analysis
**Purpose:** Answer "How are elderly distributed across income levels?" and "Which tracts have high elderly concentration?"

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Scorecard:** 
  - Total elderly (4,799)
  - Low income elderly count
  - Average median income
- **Bar Chart:** Elderly count by income category
  - Low Income (<$50k)
  - Moderate Income ($50-75k)
  - Higher Income (>$75k)
- **Bar Chart:** Top census tracts by elderly count
- **Table:** All tracts with elderly count, income, and age data
- **Combo Chart:** Income vs Elderly concentration

**Filters:**
- Income Category
- Elderly Count Range
- Census Tract

**Why This Matters:** Identifies income-based eligibility and high-concentration areas for outreach

---

### 3. Income vs Elderly Concentration Analysis
**Purpose:** Answer "What is the relationship between income and elderly concentration?"

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Scatter Chart:** Income vs Elderly Count
  - X-axis: `median_income`
  - Y-axis: `elderly_count`
  - Color by: Income Category
- **Combo Chart:** Income category breakdown
  - Bar: Elderly count by category
  - Line: Average income by category
- **Scorecard:** 
  - Average median income
  - Maximum elderly in single tract

**Filters:**
- Income Category
- Elderly Count Range

**Why This Matters:** Shows correlation between income levels and elderly concentration for planning

---

### 4. Age Distribution Analysis
**Purpose:** Understand age distribution of elderly across census tracts

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Bar Chart:** Average age by census tract
  - Top 15 tracts sorted by average age
- **Histogram:** Elderly count by age group
  - 62-69, 70-79, 80-89, 90+
- **Scorecard:** 
  - Minimum average age
  - Maximum average age
  - Overall average age
- **Table:** Tracts with age breakdown

**Filters:**
- Age Group
- Census Tract

**Why This Matters:** Age distribution helps plan age-appropriate services and housing

---

### 5. Detailed Census Tract Analysis
**Purpose:** Provide detailed view of all census tracts with elderly data

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Table:** Complete tract details
  - Columns: geo_id, tract_name, income category, elderly_count, median_income, avg_age
  - Sortable by any column
  - Paginated for easy navigation
- **Filters:** 
  - Income category
  - Elderly count range
  - Tract name search

**Why This Matters:** Provides detailed data for analysis and planning

---

### 6. Income and Affordability Analysis
**Purpose:** Assess financial barriers and eligibility

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Bar Chart:** Elderly count by income category
  - Low Income (<$50k)
  - Moderate Income ($50-75k)
  - Higher Income (>$75k)
- **Table:** Census tracts with median income and elderly count
- **Scorecard:** 
  - Total elderly in low-income tracts
  - Average median income across all tracts
- **Map:** Census tracts colored by median income (from Visualization 1, different color scheme)
- **Combo Chart:** Income vs Elderly concentration by tract

**Filters:**
- Income Category
- Census Tract

**Why This Matters:** Low-income elderly are priority for affordable housing eligibility

---

### 7. ABCDC Outreach Opportunity Areas (Priority Map)
**Purpose:** Identify areas for targeted outreach based on elderly concentration and income

**Data Source:** BigQuery table `elderly_census_tracts_one_to_one`

**Visualizations:**
- **Map:** Census tracts colored by priority score
  - Combines: high elderly count + low income
  - Use same filled map as Visualization 1, but color by calculated priority
- **Table:** Top 10 census tracts for outreach (sorted by priority score)
- **Bar Chart:** Priority score by tract
- **Scorecard:** 
  - High-priority tracts (low income + high elderly)
  - Total elderly in priority areas
  - Average income in priority areas

**Priority Score Formula (calculated field):**
- High elderly count (weight: 60%)
- Low income (weight: 40%)
- Formula: `(elderly_count / MAX(elderly_count)) * 60 + ((100000 - median_income) / 100000) * 40`

**Filters:**
- Income Category
- Priority Level
- Elderly Count Range

**Why This Matters:** Directly identifies census tracts where ABCDC should focus outreach efforts

---

## Additional Recommended Visualizations

### 8. Impact Analysis: Housing Market Transition
**Purpose:** Answer "What would be the impact if they transitioned to senior housing?"

**Data Sources:** `voters` + `buildings` + `property_assessments`

**Visualizations:**
- **Table:** Properties that would become available (if elderly homeowners moved)
- **Bar Chart:** Estimated property value of potential available units
- **Scorecard:** 
  - Total units potentially available
  - Estimated market value
- **Map:** Properties that could become available (elderly homeowners)

**Why This Matters:** Helps forecast neighborhood impact of housing transitions

---

## Dashboard Structure Recommendations

### Page 1: Executive Summary
- Elderly concentration map
- Key scorecards (total elderly, eligible, with barriers)
- Priority outreach areas

### Page 2: Eligibility & Barriers
- Housing eligibility dashboard
- Income analysis
- Housing condition analysis

### Page 3: Current Living Situation
- Tenure and ownership analysis
- Building improvements (permits)
- Property violations (liens)

### Page 4: Outreach Strategy
- Priority areas map
- Combined opportunity analysis
- Top precincts for outreach

---

## Key Metrics to Highlight

### Scorecards to Include:
1. **Total elderly residents:** 4,799 (from one-to-one mapped with spatial intersections)
2. **Elderly in low-income tracts:** [calculate from income < $50k]
3. **Average median income:** [across all tracts]
4. **High-priority tracts:** [low income + high elderly count]
5. **Average age of elderly:** [across all tracts]
6. **Maximum elderly in single tract:** [highest concentration]
7. **Tracts with elderly:** [count of tracts with elderly > 0]

---

## Data Source Connection in Looker Studio

### Primary Table to Connect:
1. **BigQuery Table:** `abcdc-project.abcdc_data.elderly_census_tracts_one_to_one`
   - Contains: geo_id, tract_name, median_income, tract_geom (GEOGRAPHY), elderly_count, avg_age
   - Total rows: Varies by number of census tracts with elderly
   - Total elderly: 4,799 residents

### Calculated Fields to Create:
1. **Income Category:**
   ```
   IF(median_income < 50000, "Low Income", 
      IF(median_income < 75000, "Moderate Income", "Higher Income"))
   ```

2. **Age Group:**
   ```
   IF(avg_age < 70, "62-69", 
      IF(avg_age < 80, "70-79", 
         IF(avg_age < 90, "80-89", "90+")))
   ```

3. **Priority Score:**
   ```
   (elderly_count / MAX(elderly_count)) * 60 + 
   ((100000 - median_income) / 100000) * 40
   ```

---

## Filter Recommendations

### Global Filters (affect all charts):
- **Income Category** (Low/Moderate/Higher)
- **Elderly Count Range** (slider)
- **Census Tract** (dropdown)

### Page-Specific Filters:
- **Map Page:** Income Category, Elderly Count Range
- **Income Analysis Page:** Income Category, Census Tract
- **Age Analysis Page:** Age Group, Census Tract
- **Outreach Page:** Priority Level, Income Category

---

## Color Scheme Recommendations

- **Elderly:** Orange/Red tones (warm colors)
- **Income:** Green (high) to Red (low)
- **Priority:** Red (high priority) to Green (low priority)
- **Conditions:** Red (poor) to Green (good)
- **Status:** Red (open violations) to Green (closed/no violations)

---

## Implementation Notes

### Data Preparation:
1. Export CSV from local PostgreSQL database using export script
2. Upload CSV to Cloud Storage bucket
3. Import to BigQuery with proper schema
4. Convert `tract_geom` from STRING to GEOGRAPHY type
5. Verify data: 4,799 elderly residents mapped to census tracts

### Performance Tips:
- BigQuery handles this dataset efficiently
- Use calculated fields in Looker Studio for aggregations
- Enable caching for faster dashboard loads
- Consider data extracts if needed for offline access

### Interactivity:
- Enable cross-filtering between charts
- Clicking on one chart should update others
- Use drill-down capabilities for detailed views
- Map click should filter other charts

---

## Success Metrics

These visualizations should help ABCDC:
1. ✅ Identify where elderly residents are concentrated
2. ✅ Determine eligibility for affordable housing
3. ✅ Understand barriers to housing access
4. ✅ Plan targeted outreach campaigns
5. ✅ Forecast impact of housing transitions
6. ✅ Prioritize neighborhoods for engagement

---

## Next Steps

1. **Export data from local database:**
   ```bash
   cd fa25-team-a/web_app/scripts/export
   bash export_for_bigquery_local.sh
   ```

2. **Upload to Cloud Storage:**
   ```bash
   gsutil cp data/processed/bigquery_exports/elderly_census_tracts_one_to_one.csv gs://abcdc-data/
   ```

3. **Import to BigQuery:**
   - Create table from Cloud Storage
   - Use schema: geo_id:STRING, tract_name:STRING, median_income:FLOAT, tract_geom:STRING, elderly_count:INTEGER, avg_age:FLOAT
   - Convert tract_geom to GEOGRAPHY type

4. **Connect Looker Studio to BigQuery:**
   - Create data source from BigQuery table
   - Build visualizations following this plan

5. **Test interactivity and filters:**
   - Verify map displays correctly
   - Test all filters
   - Check cross-filtering

6. **Share with ABCDC for feedback:**
   - Share dashboard link
   - Gather feedback
   - Iterate based on client needs

---

**Last Updated:** November 2025  
**Data Source:** BigQuery - `abcdc-project.abcdc_data.elderly_census_tracts_one_to_one`  
**Total Elderly:** 4,799 residents

