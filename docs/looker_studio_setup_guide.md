# Looker Studio Setup Guide for ABCDC Database

## Overview

This guide will help you connect your PostgreSQL database to Looker Studio (formerly Google Data Studio) and create interactive dashboards for the ABCDC Affordable Senior Housing Initiative.

## Your Current Setup

- **Database**: PostgreSQL with PostGIS
- **Database Name**: `abcdc_spatial`
- **Host**: localhost (port 5432)
- **Key Data**:
  - 43,759 voters with demographics
  - 10,272 buildings with property data
  - 22 census tracts with income data
  - 29 precincts
  - 27,769 voter-to-building mappings

---

## Option 1: Direct PostgreSQL Connection (Recommended if your database is accessible)

### Prerequisites

1. **Make your PostgreSQL database accessible**:
   - If hosting locally, you'll need to expose it to the internet OR
   - Use a cloud-hosted PostgreSQL instance (AWS RDS, Google Cloud SQL, etc.)
   - **Security Note**: Never expose your local database directly to the internet without proper security

### Steps

1. **Go to Looker Studio**:
   - Navigate to [lookerstudio.google.com](https://lookerstudio.google.com)
   - Sign in with your Google account

2. **Create a New Data Source**:
   - Click **Create** → **Data Source**
   - Search for **PostgreSQL** in the connector list
   - Click on the PostgreSQL connector

3. **Enter Connection Details**:
   ```
   Host Name: [Your PostgreSQL Host - if cloud hosted]
   Port: 5432
   Database: abcdc_spatial
   Username: Studies (or your DB username)
   Password: [Your password]
   ```

4. **Enable SSL** (if required by your hosting provider)

5. **Click Connect** and then **Authenticate**

6. **Select a Table**:
   - Choose one of your tables to start (e.g., `voters`, `buildings`, `census_tracts`)
   - You can create multiple data sources for different tables

---

## Option 2: CSV Export Method (Easiest for Local Development)

Since your database is running locally, the easiest approach is to export your data to CSV files and upload them to Looker Studio.

### Step 1: Export Data from PostgreSQL

Create a Python script to export your data:

```python
# export_for_looker.py
import psycopg2
import pandas as pd
import os

# Database connection
conn = psycopg2.connect(
    host='localhost',
    dbname='abcdc_spatial',
    user='Studies',
    password='',  # Add your password if needed
    port='5432'
)

# Output directory
output_dir = 'looker_exports'
os.makedirs(output_dir, exist_ok=True)

# Queries to export
queries = {
    'elderly_by_ward': """
        SELECT ward_id, ward_name, elderly_count, mean_age, median_age,
               age_62_69, age_70_79, age_80_89, age_90_plus
        FROM elderly_by_ward
    """,
    
    'elderly_by_precinct': """
        SELECT 
            p.ward_id,
            p.precinct_id,
            p.precinct_name,
            COUNT(v.res_id) as elderly_count,
            COUNT(CASE WHEN v.is_elderly THEN 1 END) as elderly_count_elderly,
            AVG(v.age) as mean_age,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.age) as median_age
        FROM precincts p
        LEFT JOIN voters v ON p.precinct_id = v.precinct_id
        GROUP BY p.ward_id, p.precinct_id, p.precinct_name
    """,
    
    'census_tracts_income': """
        SELECT tract_id, tract_name, median_income,
               state_code, county_code, tract_code
        FROM census_tracts
        ORDER BY median_income DESC
    """,
    
    'buildings_summary': """
        SELECT 
            b.struct_id,
            b.st_num,
            b.st_name,
            b.city,
            b.zip_code,
            b.owner,
            b.owner_occ,
            b.bldg_type,
            b.total_value,
            b.yr_built,
            b.res_units,
            b.com_units,
            b.living_area,
            b.gross_area,
            COUNT(DISTINCT vbm.res_id) as mapped_voters,
            COUNT(DISTINCT CASE WHEN v.is_elderly THEN vbm.res_id END) as elderly_voters
        FROM buildings b
        LEFT JOIN voters_buildings_map vbm ON b.struct_id = vbm.struct_id
        LEFT JOIN voters v ON vbm.res_id = v.res_id
        GROUP BY b.struct_id, b.st_num, b.st_name, b.city, b.zip_code,
                 b.owner, b.owner_occ, b.bldg_type, b.total_value, b.yr_built,
                 b.res_units, b.com_units, b.living_area, b.gross_area
    """,
    
    'voter_demographics': """
        SELECT 
            ward_id,
            precinct_id,
            is_elderly,
            age,
            COUNT(*) as voter_count
        FROM voters
        WHERE age IS NOT NULL
        GROUP BY ward_id, precinct_id, is_elderly, age
    """,
    
    'building_elderly_concentration': """
        SELECT 
            b.struct_id,
            b.st_num || ' ' || b.st_name as address,
            b.city,
            b.zip_code,
            b.total_value,
            b.yr_built,
            COUNT(DISTINCT v.res_id) as total_elderly,
            AVG(v.age) as avg_elderly_age
        FROM buildings b
        INNER JOIN voters_buildings_map vbm ON b.struct_id = vbm.struct_id
        INNER JOIN voters v ON vbm.res_id = v.res_id
        WHERE v.is_elderly = true
        GROUP BY b.struct_id, b.st_num, b.st_name, b.city, b.zip_code, 
                 b.total_value, b.yr_built
        HAVING COUNT(DISTINCT v.res_id) > 0
        ORDER BY total_elderly DESC
    """,
    
    'precinct_census_income': """
        SELECT 
            p.ward_id,
            p.precinct_id,
            p.precinct_name,
            ct.tract_id,
            ct.tract_name,
            ct.median_income,
            pctm.overlap_percentage,
            pctm.overlap_type
        FROM precincts p
        LEFT JOIN precinct_census_tract_mapping pctm 
            ON p.ward_id = pctm.ward_id AND p.precinct_id = pctm.precinct_id
        LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
        ORDER BY p.ward_id, p.precinct_id, pctm.overlap_percentage DESC
    """
}

# Export each query to CSV
for name, query in queries.items():
    print(f"Exporting {name}...")
    df = pd.read_sql(query, conn)
    output_path = os.path.join(output_dir, f'{name}.csv')
    df.to_csv(output_path, index=False)
    print(f"  ✓ Saved to {output_path} ({len(df)} rows)")

conn.close()
print("\nAll exports complete!")
print(f"Files are in the '{output_dir}' directory")
```

### Step 2: Run the Export Script

```bash
cd /Users/Studies/Projects/ds-abcdc-allston/fa25-team-a/web_app
python export_for_looker.py
```

### Step 3: Upload to Google Sheets (Easiest) or Looker Studio Directly

**Option A: Via Google Sheets (Recommended)**
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet for each CSV file
3. File → Import → Upload → Select your CSV file
4. In Looker Studio, connect to Google Sheets as your data source

**Option B: Direct CSV Upload to Looker Studio**
1. Go to Looker Studio
2. Create → Data Source → File Upload
3. Upload your CSV files
4. Note: File upload has a 100MB limit

---

## Option 3: Use Google Cloud SQL (Best for Production)

If you want a more robust solution:

1. **Set up Google Cloud SQL PostgreSQL**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a Cloud SQL PostgreSQL instance
   - Enable Cloud SQL Admin API

2. **Migrate your database**:
   ```bash
   # Export your local database
   pg_dump -h localhost -U Studies -d abcdc_spatial -f backup.sql
   
   # Import to Cloud SQL (use Cloud SQL Proxy or connection string)
   psql -h [CLOUD_SQL_IP] -U [USERNAME] -d abcdc_spatial -f backup.sql
   ```

3. **Connect Looker Studio to Cloud SQL**:
   - More secure and reliable
   - Direct connection without exports
   - Real-time data updates

---

## Recommended Dashboard Visualizations

Based on your data, here are the key visualizations to create:

### Dashboard 1: Elderly Population Overview

**Charts to Create**:
1. **Scorecard**: Total elderly count (7,396)
2. **Pie Chart**: Elderly vs Non-Elderly voters
3. **Bar Chart**: Elderly count by ward (Ward 21 vs Ward 22)
4. **Column Chart**: Elderly count by precinct
5. **Bar Chart**: Age distribution (62-69, 70-79, 80-89, 90+)
6. **Table**: Top 10 precincts by elderly count

**Data Source**: `elderly_by_ward.csv` and `elderly_by_precinct.csv`

### Dashboard 2: Census Tract Income Analysis

**Charts to Create**:
1. **Geo Chart** (if you have lat/long): Census tracts colored by median income
2. **Bar Chart**: Median income by census tract (sorted)
3. **Histogram**: Income distribution
4. **Scorecard**: Average median income across all tracts
5. **Scorecard**: Income range (min to max)

**Data Source**: `census_tracts_income.csv`

### Dashboard 3: Building & Property Analysis

**Charts to Create**:
1. **Scatter Plot**: Building value vs. number of elderly residents
2. **Bar Chart**: Top 20 buildings by elderly resident count
3. **Line Chart**: Building age distribution (year built)
4. **Table**: Buildings with highest elderly concentration
5. **Column Chart**: Total value by building type

**Data Source**: `buildings_summary.csv` and `building_elderly_concentration.csv`

### Dashboard 4: Precinct-Income Correlation

**Charts to Create**:
1. **Combo Chart**: Elderly count vs. median income by precinct
2. **Heatmap Table**: Precinct vs Census Tract overlap
3. **Scatter Plot**: Correlation between income and elderly population

**Data Source**: `precinct_census_income.csv`

---

## Step-by-Step: Creating Your First Dashboard

### 1. Create Data Sources

1. Go to [Looker Studio](https://lookerstudio.google.com)
2. Click **Create** → **Data Source**
3. Select your connection method (Google Sheets, PostgreSQL, or File Upload)
4. Create separate data sources for:
   - Elderly by ward
   - Elderly by precinct  
   - Census tracts with income
   - Buildings summary
   - Building elderly concentration

### 2. Create a New Report

1. Click **Create** → **Report**
2. Select your first data source (e.g., `elderly_by_ward`)
3. Looker Studio will create a blank canvas

### 3. Add Visualizations

**Add a Scorecard**:
1. Click **Add a chart** → **Scorecard**
2. Drag to position on canvas
3. In the **Data** panel:
   - Metric: Select `elderly_count`
   - Aggregation: SUM

**Add a Bar Chart**:
1. Click **Add a chart** → **Bar chart**
2. Drag to position
3. In the **Data** panel:
   - Dimension: `ward_name`
   - Metric: `elderly_count`
   - Sort: By `elderly_count`, Descending

**Add a Pie Chart**:
1. Click **Add a chart** → **Pie chart**
2. In the **Data** panel:
   - Dimension: Select age groups or elderly status
   - Metric: Count

### 4. Add Filters

1. Click **Add a control** → **Drop-down list**
2. Control field: `ward_id` or `precinct_id`
3. This allows users to filter the entire dashboard

### 5. Style Your Dashboard

1. Use **Theme and layout** to apply consistent colors
2. Add text boxes for titles and descriptions
3. Organize charts in a logical flow
4. Add borders and backgrounds for visual separation

---

## Sample Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  ABCDC Elderly Population Dashboard                     │
├─────────────────────────────────────────────────────────┤
│  [Filter: Ward ▼] [Filter: Precinct ▼]                 │
├──────────────┬──────────────┬──────────────┬───────────┤
│  Total       │  Ward 21     │  Ward 22     │  Avg Age  │
│  Elderly     │  Elderly     │  Elderly     │           │
│  7,396       │  4,199       │  3,197       │  40.5     │
├──────────────┴──────────────┴──────────────┴───────────┤
│                                                          │
│  [Elderly by Precinct - Bar Chart]                      │
│                                                          │
├──────────────┬──────────────────────────────────────────┤
│  Age         │  Top Buildings by Elderly Count          │
│  Distribution│  [Table showing building addresses]      │
│  [Pie Chart] │                                          │
└──────────────┴──────────────────────────────────────────┘
```

---

## Tips for Success

### Data Preparation
- ✅ Clean your data before exporting (remove nulls, fix data types)
- ✅ Add calculated fields in Looker Studio if needed
- ✅ Use consistent naming conventions
- ✅ Export data at the right granularity

### Visualization Best Practices
- 📊 Use appropriate chart types for your data
- 🎨 Keep color schemes consistent and accessible
- 📱 Make dashboards mobile-friendly
- ⚡ Limit data to improve performance (use filters)

### Performance
- ⚡ If using direct database connection, create database views for complex queries
- ⚡ Use data extracts instead of live queries for large datasets
- ⚡ Add indexes to frequently queried columns

### Sharing
- 👥 Share reports with view or edit access
- 🔒 Set up row-level security if needed
- 📧 Schedule email reports for stakeholders

---

## Troubleshooting

### "Can't connect to database"
- Check firewall settings
- Verify database credentials
- Ensure PostgreSQL accepts connections from external IPs

### "Data not refreshing"
- Check data source settings
- Manually refresh the data source
- For file uploads, re-upload the latest CSV

### "Charts showing wrong values"
- Check aggregation settings (SUM vs COUNT vs AVG)
- Verify data types in data source
- Check for null values

---

## Next Steps

1. ✅ **Export your data** using the provided script
2. ✅ **Upload to Google Sheets** or directly to Looker Studio
3. ✅ **Create your first dashboard** with elderly population data
4. ✅ **Add more visualizations** for buildings and income analysis
5. ✅ **Share with stakeholders** and gather feedback
6. ✅ **Iterate and improve** based on usage

---

## Resources

- [Looker Studio Help Center](https://support.google.com/looker-studio)
- [Looker Studio Community](https://support.google.com/looker-studio/community)
- [Google Sheets Integration](https://support.google.com/looker-studio/answer/6305875)
- [PostgreSQL Connector](https://support.google.com/looker-studio/answer/7288010)

---

## Questions?

If you need help with any of these steps, feel free to ask! The easiest starting point is:

1. Run the export script to create CSV files
2. Upload to Google Sheets
3. Connect Looker Studio to those sheets
4. Start building visualizations

This approach requires no database configuration changes and works immediately!

