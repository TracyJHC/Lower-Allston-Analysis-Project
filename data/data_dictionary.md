# Data Dictionary
## ABCDC Affordable Senior Housing Initiative

**Project:** Allston Brighton Community Development Corporation (ABCDC) Affordable Senior Housing Initiative  
**Last Updated:** November 23, 2025  
**Dataset Version:** Comprehensive Elderly Housing Analysis v1.0

---

## Overview

This data dictionary documents the structure and content of datasets used in the ABCDC Affordable Senior Housing Initiative analysis. The primary dataset consists of cleaned voter registration data from Wards 21 and 22 in the Allston-Brighton neighborhood, with comprehensive derived analysis files focusing on elderly population demographics, geographic distribution, housing eligibility, barriers to housing access, tenure status, and market impact assessment.

**Project Timeline:**
- **Project Start:** September 17, 2025
- **Analysis Period:** September - November 2025
- **Last Updated:** November 23, 2025

---

## Primary Dataset: `voter_list_cleaned.csv`

**Source:** Raw voter registration data from "Voter List - Ward 21 and 22.xls"  
**Processing:** Data cleaning and column selection applied via `clean_voterList.py`  
**Records:** 43,759 registered voters  
**Geographic Scope:** Allston-Brighton neighborhood, Boston (Wards 21 and 22)

### Field Descriptions

| Field Name | Data Type | Description | Example Values | Notes |
|------------|-----------|-------------|----------------|-------|
| **Res ID** | String | Unique resident identifier | "02ZJA0439000", "07MKN2399001" | Primary key for each voter record |
| **Street .** | Integer | Street number | 142, 144, 1999 | Numeric portion of street address |
| **Sffx** | String | Street suffix (optional) | "", "A", "B" | Additional address identifier, often empty |
| **Street Name** | String | Name of the street | "KENRICK ST", "COMMONWEALTH AVE" | Full street name |
| **Apt .** | String | Apartment number (if applicable) | "11", "2A", "" | Unit identifier for multi-unit buildings |
| **Zip** | Integer | ZIP code | 2135 | 5-digit postal code |
| **Ward** | Integer | Ward number | 21, 22 | Political subdivision of Boston |
| **Precinct** | Integer | Precinct number | 8, 9, 13, 16 | Subdivision within ward for voting |
| **DOB** | Date | Date of birth | "1939-02-04", "1999-07-23" | Used to calculate age for elderly analysis |
| **Occupation** | String | Occupation or "UNKNOWN" | "UNKNOWN", "RESEARCHER", "SECURITY" | Employment status, many marked as "UNKNOWN" |

### Data Quality Notes
- **Completeness:** High data quality with minimal missing values
- **Age Calculation:** Ages calculated from DOB field for elderly analysis (62+ years)
- **Geographic Coverage:** Comprehensive coverage of Wards 21 and 22
- **Address Standardization:** Street addresses cleaned and standardized

---

## Derived Analysis Datasets

### 1. `ward_elderly_analysis.csv`
**Purpose:** Ward-level summary statistics for elderly population (62+ years)

| Field Name | Data Type | Description | Example Values |
|------------|-----------|-------------|----------------|
| **Ward** | Integer | Ward number | 21, 22 |
| **Elderly_Count** | Integer | Number of elderly residents (62+) | 4192, 3192 |
| **Mean_Age** | Float | Average age of elderly residents | 76.2, 73.1 |
| **Median_Age** | Float | Median age of elderly residents | 75.0, 72.0 |
| **Min_Age** | Integer | Minimum age in ward | 62 |
| **Max_Age** | Integer | Maximum age in ward | 106, 103 |

### 2. `precinct_elderly_analysis.csv`
**Purpose:** Precinct-level analysis for targeted outreach planning

| Field Name | Data Type | Description | Example Values |
|------------|-----------|-------------|----------------|
| **Ward** | Integer | Ward number | 21, 22 |
| **Precinct** | Integer | Precinct number | 2, 8, 9, 10, 12, 13, 16 |
| **Elderly_Count** | Integer | Number of elderly residents (62+) | 840, 540, 498 |
| **Mean_Age** | Float | Average age of elderly residents | 79.5, 77.7, 78.1 |

**Key Insights:**
- Top precincts by elderly population: W21-P13 (840), W21-P16 (540), W21-P12 (498)
- 31 total precincts analyzed across both wards

### 3. `street_elderly_analysis.csv`
**Purpose:** Street-level analysis for neighborhood-specific outreach

| Field Name | Data Type | Description | Example Values |
|------------|-----------|-------------|----------------|
| **Street Name** | String | Name of the street | "COMMONWEALTH AVE", "WALLINGFORD RD" |
| **Ward** | Integer | Ward number | 21, 22 |
| **Elderly_Count** | Integer | Number of elderly residents (62+) | 649, 547, 513 |
| **Mean_Age** | Float | Average age of elderly residents | 73.9, 83.0, 78.7 |

**Key Insights:**
- Top streets by elderly population: COMMONWEALTH AVE (649), WALLINGFORD RD (547), WASHINGTON ST (513)
- 362 unique streets analyzed



## Key Statistics Summary

### Population Overview
- **Total Registered Voters:** 43,759
- **Elderly Population (62+):** 7,396 (16.9% of total)
- **Age Range:** 62-105+ years
- **Mean Age (Elderly):** 74.9 years
- **Median Age (Elderly):** 74.0 years

### Geographic Distribution
- **Ward 21 (Allston):** 4,199 elderly residents (17.7% of ward population, avg age 76.2)
- **Ward 22 (Brighton):** 3,197 elderly residents (16.0% of ward population, avg age 73.1)
- **Total Precincts:** 31 across both wards
- **Unique Streets:** 362 with elderly residents
- **Census Tracts:** 21 tracts with mapped elderly residents

### Age Group Distribution (Elderly Population)
- **62-69 years:** 2,430 (32.9%)
- **70-79 years:** 2,546 (34.4%)
- **80-89 years:** 1,425 (19.3%)
- **90+ years:** 537 (7.3%)

### Eligibility for Affordable Senior Housing
- **Total Analyzed:** 6,958 elderly residents (after excluding income-restricted housing)
- **High Priority:** 30 residents (0.4%)
- **Medium Priority:** 1,050 residents (15.1%)
- **Total Qualifying:** 1,080 residents (15.5%)
- **Low Priority:** 5,878 residents (84.5%)

### Barriers to Housing Access
- **Elderly with Any Barrier:** 1,037 residents (14.9%)
- **Financial Barriers:** 1,037 residents (14.9%)
- **Housing Condition Barriers:** 133 residents (2.7%)
- **Property Violations:** 35 residents (0.5%)
- **Accessibility Barriers:** 4 residents (0.1%)

### Tenure Status
- **Mapped to Buildings:** 5,391 residents (72.9% of total elderly)
- **Renters:** 2,492 (46.2% of mapped)
- **Homeowners:** 1,898 (35.2% of mapped)
- **Unknown Tenure:** 1,001 (18.6% of mapped)

### Market Impact (50-60 Unit Project)
- **Expanded Outreach Pool:** 300 candidates
- **Homeowners in Pool:** 150 (50.0%)
- **Total Property Value:** $163.3 million
- **Estimated Impact (20-30% acceptance):** $31.5-$47.8 million
- **Top 60 Candidates:** 26 homeowners, $26.6 million property value

---

## Usage Notes

### For Outreach Planning
- Use precinct-level data for targeted geographic outreach
- Use street-level data for neighborhood-specific campaigns
- Consider age distribution for appropriate messaging and services

### For Housing Development
- Ward-level statistics inform overall housing demand
- Precinct-level data helps with site selection
- Street-level analysis supports neighborhood impact assessment

### Data Limitations
- Occupation data has high "UNKNOWN" values
- Data represents registered voters only (not total population)
- Analysis limited to Wards 21 and 22 (Allston-Brighton)

---

## Comprehensive Analysis Datasets

### Submission Dataset Folder

All key analysis datasets are organized in `data/processed/submission_dataset/` for easy submission and review. See `data/processed/submission_dataset/README.md` for complete documentation.

**Main Datasets:**
- `02_eligibility/comprehensive_eligibility_analysis.csv` - Complete eligibility analysis with scores (6,958 residents)
- `03_barriers/barriers_comprehensive.csv` - Complete barrier profiles
- `04_tenure_residency/tenure_comprehensive.csv` - Homeowner/renter status and residency
- `05_market_impact/outreach_pool_expanded_300.csv` - Expanded outreach pool for 50-60 unit project
- `05_market_impact/project_candidates_top60.csv` - Top 60 priority candidates

### Eligibility Analysis Datasets

Located in `data/processed/elderly_analysis/`:

**comprehensive_eligibility_analysis.csv** - Main eligibility dataset
- **Records:** 6,958 elderly residents (after excluding income-restricted housing)
- **Key Fields:**
  - `res_id` - Unique resident identifier
  - `age`, `age_group` - Age information
  - `ward_id`, `precinct_id`, `tract_id` - Geographic identifiers
  - `median_income` - Census tract median income
  - `income_category` - Low/Moderate/Higher Income classification
  - `has_poor_conditions` - Housing condition flag (boolean)
  - `has_violations` - Property violation flag (boolean)
  - `store_accessibility` - Store proximity category (Excellent/Good/Limited)
  - `park_accessibility` - Park proximity category (Excellent/Good/Limited)
  - `eligibility_score` - Total score (0-100 points)
  - `priority_level` - High/Medium/Low priority classification

**Individual Eligibility Components:**
- `age_eligibility.csv` - Age-based eligibility (all 62+)
- `income_eligibility.csv` - Income-based eligibility by census tract
- `housing_conditions_eligibility.csv` - Housing condition-based eligibility
- `violations_eligibility.csv` - Property violation-based eligibility
- `store_accessibility.csv` - Store proximity analysis
- `park_accessibility.csv` - Park proximity analysis
- `residency_stability.csv` - Residency stability indicators

### Barriers Analysis Datasets

**barriers_comprehensive.csv** - Complete barrier profiles
- **Records:** 6,958 elderly residents
- **Key Fields:**
  - `res_id` - Unique resident identifier
  - `has_financial_barrier` - Financial barrier flag (boolean)
  - `has_condition_barrier` - Housing condition barrier flag (boolean)
  - `has_violation_barrier` - Property violation barrier flag (boolean)
  - `has_accessibility_barrier` - Accessibility barrier flag (boolean)
  - `total_barriers` - Count of barriers per resident (integer)

**Aggregated Barrier Analysis:**
- `barriers_financial.csv` - Financial barriers (income-based)
- `barriers_conditions.csv` - Building condition barriers
- `barriers_violations.csv` - Property violation barriers
- `barriers_by_ward.csv` - Barrier analysis aggregated by ward
- `barriers_by_precinct.csv` - Barrier analysis aggregated by precinct

### Tenure and Residency Datasets

**tenure_comprehensive.csv** - Complete tenure and residency profile
- **Records:** 5,391 mapped elderly residents (72.9% of total)
- **Key Fields:**
  - `res_id` - Unique resident identifier
  - `tenure_status` - Homeowner/Renter/Unknown
  - `property_value` - Property value (for homeowners, float)
  - `residential_units` - Number of residential units (integer)
  - `building_type` - Building type code (string)
  - `residency_status` - Mapped/Not Mapped indicator
  - `ward_id`, `precinct_id` - Geographic identifiers

**Aggregated Tenure Analysis:**
- `tenure_homeowner_renter.csv` - Homeowner vs renter status
- `tenure_residency_length.csv` - Residency length indicators
- `tenure_by_ward.csv` - Tenure analysis by ward
- `tenure_by_precinct.csv` - Tenure analysis by precinct
- `tenure_by_age_group.csv` - Tenure analysis by age group
- `tenure_by_income.csv` - Tenure analysis by income category

**Important Note:** Building matching is spatial (address matching), not temporal (residency verification). The residency length indicators show address matching capability, not verified continuous residency.

### Market Impact Datasets

**outreach_pool_expanded_300.csv** - Expanded outreach pool for 50-60 unit project
- **Records:** 300 priority candidates
- **Key Fields:**
  - `res_id` - Unique resident identifier
  - `age`, `age_group` - Age information
  - `eligibility_score` - Eligibility score (0-100)
  - `priority_level` - High/Medium priority
  - `tenure_status` - Homeowner/Renter/Unknown
  - `property_value` - Property value (for homeowners)
  - `ward_id`, `precinct_id`, `tract_id` - Geographic identifiers
  - `income_category` - Income classification
  - `has_poor_conditions`, `has_violations` - Housing quality indicators

**project_candidates_top60.csv** - Top 60 priority candidates
- **Records:** 60 candidates (30 High + 30 Medium priority)
- **Key Fields:** Same as outreach_pool_expanded_300.csv

**project_homeowner_candidates.csv** - Homeowner candidates and properties
- **Records:** 26 homeowners from top 60 candidates
- **Key Fields:** Includes property value, building type, residential units

**neighborhood_market_impact.csv** - Neighborhood-level impact analysis
- **Records:** 5 census tracts
- **Key Fields:**
  - `tract_id`, `tract_name` - Census tract identifiers
  - `median_income` - Census tract median income
  - `candidates` - Number of candidates in tract
  - `homeowners` - Number of homeowner candidates
  - `total_property_value` - Total property value in tract

**Outreach Targeting:**
- `outreach_targeting_tracts.csv` - Census tract level targeting data
- `outreach_targeting_areas.csv` - Precinct/ward level targeting data

## File Locations

```
fa25-team-a/data/
├── raw/
│   ├── Voter List - Ward 21 and 22.xls          # Original dataset
│   ├── fy2025-property-assessment-data_12_30_2024.csv  # Property assessments
│   └── property_violation.csv                  # Property violations
├── processed/
│   ├── voter_data/
│   │   ├── voter_list_cleaned.csv              # Primary cleaned dataset
│   │   ├── ward_elderly_analysis.csv           # Ward-level analysis
│   │   ├── precinct_elderly_analysis.csv       # Precinct-level analysis
│   │   └── street_elderly_analysis.csv         # Street-level analysis
│   ├── elderly_analysis/                       # Comprehensive analysis datasets
│   │   ├── comprehensive_eligibility_analysis.csv  # Main eligibility dataset
│   │   ├── barriers_comprehensive.csv          # Barrier profiles
│   │   ├── tenure_comprehensive.csv           # Tenure and residency
│   │   ├── outreach_pool_expanded_300.csv     # Outreach pool
│   │   └── [46 total CSV files]
│   └── submission_dataset/                     # Submission-ready organized datasets
│       ├── 01_demographics_location/
│       ├── 02_eligibility/
│       ├── 03_barriers/
│       ├── 04_tenure_residency/
│       ├── 05_market_impact/
│       └── 06_outreach_targeting/
└── data_dictionary.md                          # This file
```

---

## Contact Information

For questions about this data dictionary or the analysis, please refer to the project documentation in the `fa25-team-a/docs/` directory or the EDA report in `fa25-team-a/reports/EDA_VoterList_Analysis.md`.
