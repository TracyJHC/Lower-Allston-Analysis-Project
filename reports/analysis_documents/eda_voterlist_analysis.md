# Exploratory Data Analysis (EDA) - Cleaned Voter List
## ABCDC Affordable Senior Housing Initiative

**Project:** Allston Brighton Community Development Corporation (ABCDC) Affordable Senior Housing Initiative  
**Dataset:** Cleaned Voter List - Ward 21 and 22  
**Analysis Date:** October 2025

---

## Executive Summary

This exploratory data analysis examines the cleaned voter registration data from Wards 21 and 22 in the Allston-Brighton neighborhood to identify elderly residents (aged 62 and older) who may be eligible for new affordable senior housing developments. The analysis provides a data-driven foundation for equitable outreach, housing readiness assessment, and neighborhood impact forecasting.

### Key Findings
- **Total Population:** 43,759 registered voters
- **Elderly Population (62+):** 7,384 residents (16.9% of total population)
- **Geographic Coverage:** Ward 21 (4,192 elderly) and Ward 22 (3,192 elderly), Allston-Brighton
- **Primary Objective:** Identify elderly residents for affordable senior housing outreach

---

## 1. Dataset Overview

### 1.1 Data Source
- **Original Dataset:** Voter List - Ward 21 and 22.xls
- **Cleaned Dataset:** voter_list_cleaned.csv
- **Processing:** Data cleaning and standardization applied
- **Geographic Scope:** Allston-Brighton neighborhood, Boston

### 1.2 Dataset Structure
The cleaned dataset contains the following columns:

| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| Res ID | String | Unique resident identifier |
| Street . | Integer | Street number |
| Sffx | String | Street suffix (optional) |
| Street Name | String | Name of the street |
| Apt . | String | Apartment number (if applicable) |
| Zip | Integer | ZIP code |
| Ward | Integer | Ward number (21 or 22) |
| Precinct | Integer | Precinct number |
| DOB | Date | Date of birth |
| Occupation | String | Occupation or "UNKNOWN" |

### 1.3 Data Quality Assessment
- **Total Records:** 43,759
- **Missing Values:** Minimal missing data in optional fields
- **Data Completeness:** High quality with complete age and address information
- **Geographic Coverage:** Comprehensive coverage of Wards 21 and 22

---

## 2. Elderly Population Analysis

### 2.1 Age Demographics
The analysis focuses on residents aged 62 and older, as this is the typical threshold for senior housing eligibility.

#### Age Distribution
- **Age Range:** 62-106 years
- **Mean Age:** 74.9 years
- **Median Age:** 74.0 years

#### Age Group Breakdown
| Age Group | Count | Percentage |
|-----------|-------|------------|
| 62-69 | 2,531 | 34.3% |
| 70-79 | 2,720 | 36.8% |
| 80-89 | 1,538 | 20.8% |
| 90+ | 595 | 8.1% |

### 2.2 Elderly Population Statistics
- **Total Elderly Residents (62+):** 7,384
- **Percentage of Total Population:** 16.9%
- **Geographic Distribution:** 4,192 in Ward 21, 3,192 in Ward 22

**Elderly Distribution Visualization:**
![Elderly Distribution](figures/elderly_dist_voterlist.png)

---

## 3. Geographic Analysis

### 3.1 Ward-Level Distribution
Analysis of elderly population distribution across the two wards:

| Ward | Elderly Count | Percentage of Ward Population |
|------|---------------|-------------------------------|
| Ward 21 | 4,192 | 17.6% |
| Ward 22 | 3,192 | 16.0% |

### 3.2 Precinct-Level Analysis
Identification of precincts with highest elderly populations for targeted outreach:

**Top 3 Precincts by Elderly Population:**
1. W21-P13: 840 elderly residents (highest concentration, mean age 79.5)
2. W21-P16: 540 elderly residents (mean age 77.7)
3. W21-P12: 498 elderly residents (mean age 78.1)

*Complete precinct analysis data available in: `fa25-team-a/data/processed/precinct_elderly_analysis.csv`*

### 3.3 Street-Level Analysis
Identification of streets with high concentrations of elderly residents:

**Top 3 Streets by Elderly Population:**
1. COMMONWEALTH AVE (Ward 21): 649 elderly residents (top street for outreach, mean age 73.9)
2. WALLINGFORD RD (Ward 21): 547 elderly residents (mean age 83.0)
3. WASHINGTON ST (Ward 21): 513 elderly residents (mean age 78.7)

*Complete street analysis data available in: `fa25-team-a/data/processed/street_elderly_analysis.csv`*

### 3.4 Elderly Density Analysis
Precincts ranked by elderly density (percentage of total residents who are elderly):

**Top 3 Precincts by Elderly Density:**
1. W21-P13: 39.7% elderly (840 out of 2,116 residents, highest density)
2. W21-P16: 33.2% elderly (540 out of 1,625 residents)
3. W21-P12: 31.9% elderly (498 out of 1,561 residents)


### 3.5 Geographic Visualizations
Supporting visualizations for the geographic analysis:

**Geographic Distribution Map:**
![Geographic Distribution](figures/geographic_dist_voterlist.png)

These figures provide visual representations of the elderly population distribution across Wards 21 and 22, supporting the quantitative analysis presented above.

---

## 4. Occupation Analysis

### 4.1 Occupation Distribution
Analysis of occupation patterns among elderly residents:

| Occupation Category | Count | Percentage | Description |
|-------------------|-------|------------|-------------|
| Other | 4,466 | 60.5% | Various other occupations |
| Unknown | 2,359 | 31.9% | Unknown occupation status |
| Professional/Stable | 233 | 3.2% | Teachers, engineers, doctors, managers |
| Service Sector | 143 | 1.9% | Retail, sales, service workers |
| Healthcare | 122 | 1.7% | Healthcare workers, medical professionals |
| Construction/Trades | 31 | 0.4% | Construction, contractors, tradespeople |
| Government/Public | 30 | 0.4% | Government, public sector workers |

### 4.2 Occupation Insights
- **Professional/Stable Occupations:** 233 elderly residents
- **Healthcare Workers:** 122 elderly residents (potential service providers)
- **Unknown Occupation Status:** 2,359 elderly residents
- **Service Sector:** 143 elderly residents

---

## 5. Summary Insights

### 5.1 Key Findings
- **Total Elderly Population:** 7,384 residents aged 62+
- **Geographic Distribution:** 4,192 in Ward 21, 3,192 in Ward 22
- **Average Age:** 74.9 years
- **Occupation Diversity:** 7 categories with 60.5% in "Other" category and 31.9% unknown status

### 5.2 Geographic Targeting
- **Highest Elderly Density Precinct:** W21-P13 with 39.7% elderly
- **Top Streets for Outreach:** COMMONWEALTH AVE with 649 elderly residents
- **Ward Distribution:** Ward 21 (4,192 elderly), Ward 22 (3,192 elderly)

---

## 6. Data Limitations and Considerations

### 6.1 Data Limitations
- **Income Data:** Not available (used occupation as proxy)
- **Housing Costs:** Not included in voter data
- **Health Status:** Not available in voter data
- **Family Members/Status:** Not available in voter data

### 6.2 Recommendations for Additional Data
- Housing cost data for affordability assessment
- Health and mobility data for service planning
- Income verification for eligibility assessment
- Community engagement history for outreach effectiveness

---

## 7. Next Steps

### 7.1 Immediate Actions
1. **Run Complete Analysis:** Execute all EDA notebook cells to generate final statistics
2. **Validate Results:** Review and validate all calculated metrics
3. **Update Documentation:** Fill in calculated values in this document
4. **Create Outreach Lists:** Generate resident lists for ABCDC

### 7.2 Follow-up Analysis
1. **Integration with Other Datasets:** Combine with POI and housing price data
2. **GIS Mapping:** Create geographic visualizations
3. **Impact Modeling:** Develop neighborhood impact forecasts
4. **Outreach Effectiveness:** Track and measure outreach success

### 7.3 Reporting
1. **Executive Summary:** Create high-level summary for ABCDC leadership
2. **Detailed Analysis:** Provide comprehensive findings for planning teams
3. **Actionable Recommendations:** Deliver outreach strategies
4. **Monitoring Framework:** Establish metrics for ongoing assessment

---

## 8. Technical Appendix

### 8.1 Analysis Tools Used
- **Python Libraries:** pandas, numpy, matplotlib, seaborn
- **Data Processing:** Data cleaning, age calculation, categorization
- **Visualization:** Charts, graphs, dashboards
- **Statistical Analysis:** Descriptive statistics, distribution analysis

### 8.2 Code Repository
- **Notebook:** `notebooks/eda_voterlist.ipynb`
- **Data Source:** `data/processed/voter_list_cleaned.csv`
- **Documentation:** `reports/eda_voterList_analysis.md`

### 8.3 Data Privacy and Ethics
- All analysis uses publicly available voter registration data
- No personal identifying information is exposed in analysis
- Recommendations focus on community-level insights
- Respect for resident privacy maintained throughout

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Next Review:** [To be scheduled]  

---

*This document provides the foundation for ABCDC's data-driven approach to affordable senior housing planning in the Allston-Brighton neighborhood. The analysis enables equitable outreach, informed decision-making, and community-centered housing development.*
