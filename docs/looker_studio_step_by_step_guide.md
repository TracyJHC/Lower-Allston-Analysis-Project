# Looker Studio Step-by-Step Implementation Guide
## ABCDC Affordable Senior Housing Initiative

This guide provides step-by-step instructions for creating each visualization in Looker Studio.

---

## Prerequisites

1. ✅ Local PostgreSQL database with elderly data
2. ✅ Export script ready: `fa25-team-a/web_app/scripts/export/export_for_bigquery_local.sh`
3. ✅ Google Cloud Project with BigQuery enabled
4. ✅ Cloud Storage bucket created (e.g., `gs://abcdc-data/`)
5. ✅ Looker Studio account access

---

## Step 1: Export Data from Local Database

1. **Run the export script:**
   ```bash
   cd fa25-team-a/web_app/scripts/export
   bash export_for_bigquery_local.sh
   ```

2. **Verify export:**
   - File created: `fa25-team-a/web_app/data/processed/bigquery_exports/elderly_census_tracts_one_to_one.csv`
   - Contains: geo_id, tract_name, median_income, tract_geom, elderly_count, avg_age
   - Total elderly: **4,799** residents

---

## Step 2: Upload CSV to Cloud Storage

1. **Upload to Cloud Storage:**
   ```bash
   gsutil cp fa25-team-a/web_app/data/processed/bigquery_exports/elderly_census_tracts_one_to_one.csv gs://abcdc-data/
   ```

2. **Verify upload:**
   ```bash
   gsutil ls gs://abcdc-data/elderly_census_tracts_one_to_one.csv
   ```

---

## Step 3: Import to BigQuery

1. **Go to BigQuery Console:**
   - Navigate to [BigQuery Console](https://console.cloud.google.com/bigquery)
   - Select your project: `abcdc-project`

2. **Create Table from Cloud Storage:**
   - Click **Create Table**
   - **Source:** Cloud Storage
   - **Select file from GCS bucket:** `gs://abcdc-data/elderly_census_tracts_one_to_one.csv`
   - **File format:** CSV
   - **Table name:** `elderly_census_tracts_one_to_one`
   - **Dataset:** `abcdc_data` (create if needed)
   - **Header rows to skip:** 1
   - **Schema:** Edit as text, paste:
     ```
     geo_id:STRING
     tract_name:STRING
     median_income:FLOAT
     tract_geom:STRING
     elderly_count:INTEGER
     avg_age:FLOAT
     ```
   - Click **Create Table**

3. **Convert Geometry to GEOGRAPHY:**
   - Run this SQL in BigQuery:
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

---

## Step 4: Connect Looker Studio to BigQuery

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Click **Create** → **Data Source**
3. Search for **BigQuery** and select it
4. Select your project and dataset:
   - **Project:** abcdc-project
   - **Dataset:** abcdc_data
   - **Table:** elderly_census_tracts_one_to_one
5. Click **Connect**
6. Verify fields are loaded correctly

---

## Step 5: Create Your First Report

1. After connecting data source, click **Create Report**
2. Name it: "ABCDC Elderly Housing Analysis"
3. You'll see a blank canvas

---

## Visualization 1: Elderly Resident Distribution Map (Filled Map)

### Data Source:
- BigQuery table: `elderly_census_tracts_one_to_one`

### Step-by-Step:

1. **Add Geo Chart:**
   - Click **Add a chart** → **Geo chart**
   - Drag it to top-left of canvas
   - Resize to about 50% width, 40% height

2. **Configure the Map:**
   - In **Data** panel (right side):
     - **Geographic dimension:** `tract_geom` (GEOGRAPHY type)
     - **Dimension:** `tract_name`
     - **Metric:** `elderly_count`
     - **Color by:** `elderly_count` (use color scale)
   - In **Style** panel:
     - Map type: **Filled map** (choropleth)
     - Color palette: Blue scale (light = low, dark = high)
     - Border: Enable with light gray

3. **Add Tooltip:**
   - In **Data** panel → **Tooltip:**
     - Add: `tract_name`, `elderly_count`, `median_income`, `avg_age`

4. **Add Filter:**
   - Click **Add a control** → **Drop-down list**
   - Place it above the map
   - **Control field:** Create calculated field "Income Category":
     ```
     IF(median_income < 50000, "Low Income", 
        IF(median_income < 75000, "Moderate Income", "Higher Income"))
     ```
   - **Default selection:** All

5. **Add Title:**
   - Click **Add text** → Type: "Elderly Resident Distribution by Census Tract"
   - Place above the map

**Location on Dashboard:** Top-left section

---

## Visualization 2: Income & Elderly Distribution Analysis

### Data Source:
- BigQuery table: `elderly_census_tracts_one_to_one`

### Step-by-Step:

1. **Add Scorecards (Top Row):**
   - Click **Add a chart** → **Scorecard**
   - Create 3 scorecards in a row:
     - **Scorecard 1:** 
       - Metric: SUM(`elderly_count`)
       - Label: "Total Elderly (4,799)"
     - **Scorecard 2:**
       - Metric: SUM(`elderly_count`) where Income Category = "Low Income"
       - Label: "Low Income Elderly"
     - **Scorecard 3:**
       - Metric: AVG(`median_income`)
       - Label: "Average Median Income"

2. **Add Bar Chart (Elderly by Income Category):**
   - Click **Add a chart** → **Bar chart**
   - Place below scorecards, left side
   - **Dimension:** Income Category (calculated field)
   - **Metric:** SUM(`elderly_count`)
   - **Title:** "Elderly Count by Income Category"
   - **Sort:** By metric, Descending

3. **Add Bar Chart (Top Tracts by Elderly Count):**
   - Click **Add a chart** → **Bar chart**
   - Place next to income chart
   - **Dimension:** `tract_name`
   - **Metric:** `elderly_count`
   - **Sort:** By metric, Descending
   - **Limit:** Top 10
   - **Title:** "Top 10 Census Tracts by Elderly Count"

4. **Add Table:**
   - Click **Add a chart** → **Table**
   - Place below the charts
   - **Dimensions:** `geo_id`, `tract_name`, Income Category
   - **Metrics:** `elderly_count`, `median_income`, `avg_age`
   - **Sort by:** `elderly_count` DESC

**Location on Dashboard:** Top-right section (below map)

---

## Visualization 3: Income vs Elderly Concentration Analysis

### Data Source:
- BigQuery table: `elderly_census_tracts_one_to_one`

### Step-by-Step:

1. **Add Scatter Chart:**
   - Click **Add a chart** → **Scatter chart**
   - Place in middle-left section
   - **X-axis:** `median_income`
   - **Y-axis:** `elderly_count`
   - **Dimension:** `tract_name`
   - **Color by:** Income Category
   - **Title:** "Income vs Elderly Concentration"

2. **Add Combo Chart:**
   - Click **Add a chart** → **Combo chart**
   - Place next to scatter chart
   - **Dimension:** Income Category
   - **Metric 1 (Bar):** SUM(`elderly_count`)
   - **Metric 2 (Line):** AVG(`median_income`)
   - **Title:** "Elderly Count & Average Income by Category"

3. **Add Scorecard:**
   - Click **Add a chart** → **Scorecard**
   - Place above charts
   - **Metric:** AVG(`avg_age`)
   - **Label:** "Average Age of Elderly"
   - Create second scorecard:
     - **Metric:** MAX(`elderly_count`)
     - **Label:** "Max Elderly in Single Tract"

**Location on Dashboard:** Middle section

---

## Visualization 4: Age Distribution Analysis

### Data Source:
- BigQuery table: `elderly_census_tracts_one_to_one`

### Step-by-Step:

1. **Add Bar Chart (Average Age by Tract):**
   - Click **Add a chart** → **Bar chart**
   - Place in middle-right section
   - **Dimension:** `tract_name`
   - **Metric:** `avg_age`
   - **Sort:** By metric, Descending
   - **Limit:** Top 15
   - **Title:** "Average Age by Census Tract"

2. **Add Histogram (Age Distribution):**
   - Click **Add a chart** → **Bar chart**
   - Place next to age chart
   - **Dimension:** Create calculated field "Age Group":
     ```
     IF(avg_age < 70, "62-69", 
        IF(avg_age < 80, "70-79", 
           IF(avg_age < 90, "80-89", "90+")))
     ```
   - **Metric:** SUM(`elderly_count`)
   - **Title:** "Elderly Count by Age Group"

3. **Add Scorecard:**
   - Click **Add a chart** → **Scorecard**
   - Place above charts
   - **Metric:** MIN(`avg_age`)
   - **Label:** "Youngest Average Age"
   - Create second:
     - **Metric:** MAX(`avg_age`)
     - **Label:** "Oldest Average Age"

**Location on Dashboard:** Middle-right section

---

## Visualization 5: Detailed Tract Analysis Table

### Data Source:
- BigQuery table: `elderly_census_tracts_one_to_one`

### Step-by-Step:

1. **Add Table:**
   - Click **Add a chart** → **Table**
   - Place in bottom section
   - **Dimensions:** `geo_id`, `tract_name`, Income Category
   - **Metrics:** `elderly_count`, `median_income`, `avg_age`
   - **Sort:** By `elderly_count` DESC
   - **Enable pagination:** Yes
   - **Title:** "Census Tract Details"

2. **Add Filters:**
   - Add filter control for Income Category
   - Add filter control for Elderly Count range

**Location on Dashboard:** Bottom section

---

## Step 6: Add Global Filters

1. **Add Income Category Filter:**
   - Click **Add a control** → **Drop-down list**
   - Place at very top of dashboard
   - **Control field:** Income Category (calculated field)
   - **Default selection:** All
   - **Apply to:** All charts

2. **Add Elderly Count Range Filter:**
   - Click **Add a control** → **Range slider**
   - Place next to income filter
   - **Control field:** `elderly_count`
   - **Default range:** Min to Max

3. **Add Tract Filter:**
   - Click **Add a control** → **Drop-down list**
   - Place next to count filter
   - **Control field:** `tract_name`
   - **Default selection:** All

---

## Step 7: Styling and Layout

### Dashboard Layout:
```
┌─────────────────────────────────────────────────────────┐
│  [Income Filter] [Count Range] [Tract Filter]          │
├─────────────────────────────────────────────────────────┤
│  Elderly Distribution Map    │  Income & Elderly Charts  │
│  (Filled Map - 50% width)   │  Scorecards              │
├─────────────────────────────────────────────────────────┤
│  Income vs Concentration    │  Age Distribution        │
│  Scatter & Combo Charts      │  Charts                  │
├─────────────────────────────────────────────────────────┤
│  Detailed Tract Analysis Table (Full Width)              │
└─────────────────────────────────────────────────────────┘
```

### Color Scheme:
- **Elderly Count:** Blue scale (light = low, dark = high)
- **Income:** Green (high) to Red (low)
- **Age:** Orange scale (light = younger, dark = older)

---

## Step 8: Enable Interactivity

1. **Cross-filtering:**
   - Right-click on any chart
   - Select **Cross-filtering** → **Apply to all charts**
   - Now clicking on one chart will filter others

2. **Drill-down:**
   - For tables, enable drill-down to see details
   - Right-click table → **Drill-down** → Enable

---

## Step 9: Test and Share

1. **Test filters:**
   - Try each filter to ensure charts update correctly
   - Check that cross-filtering works
   - Verify map displays correctly with GEOGRAPHY field

2. **Share dashboard:**
   - Click **Share** (top right)
   - Add ABCDC team members
   - Set permissions (View or Edit)

---

## Troubleshooting

### Charts not showing data?
- Check BigQuery data source connection
- Verify table exists: `elderly_census_tracts_one_to_one`
- Check filters aren't too restrictive
- Verify `tract_geom` is GEOGRAPHY type (not STRING)

### Maps not displaying?
- Ensure `tract_geom` field is GEOGRAPHY type
- Run the GEOGRAPHY conversion SQL if needed
- Check that geometries are valid
- Try refreshing the data source

### Performance issues?
- BigQuery should handle this dataset efficiently
- Consider adding filters to limit data
- Use calculated fields for aggregations

---

## Quick Reference: Data Source

**BigQuery Table:** `abcdc-project.abcdc_data.elderly_census_tracts_one_to_one`

**Fields:**
- `geo_id` (STRING) - Census tract ID
- `tract_name` (STRING) - Census tract name
- `median_income` (FLOAT) - Median income
- `tract_geom` (GEOGRAPHY) - Tract boundaries for map
- `elderly_count` (INTEGER) - Number of elderly per tract
- `avg_age` (FLOAT) - Average age of elderly

**Total Elderly:** 4,799 residents

---

**Last Updated:** November 2025

