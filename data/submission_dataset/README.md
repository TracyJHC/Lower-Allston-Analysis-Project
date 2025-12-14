# Elderly Housing Analysis - Submission Dataset

This folder contains the key datasets from the comprehensive elderly housing analysis for Allston-Brighton, organized by analysis category for easy submission and review.

## Dataset Overview

This submission includes processed datasets from a comprehensive analysis of 7,396 elderly residents (age 62+) in Allston-Brighton, examining their demographics, geographic distribution, housing needs, eligibility for affordable senior housing, barriers to housing access, tenure status, and the potential market impact of housing transitions.

## Folder Structure

### 01_demographics_location/
**Purpose**: Demographic characteristics and geographic distribution of elderly residents

**Files**:
- `census_tract_elderly_distribution.csv` - Distribution of elderly residents across census tracts with median income data

**Key Variables**:
- Census tract identifiers
- Elderly population counts
- Median income by tract
- Average age by tract

### 02_eligibility/
**Purpose**: Eligibility analysis for affordable senior housing opportunities

**Files**:
- `comprehensive_eligibility_analysis.csv` - **MAIN DATASET**: Complete eligibility analysis with all features and scores for 6,958 elderly residents
- `age_eligibility.csv` - Age-based eligibility (all 62+)
- `income_eligibility.csv` - Income-based eligibility by census tract
- `housing_conditions_eligibility.csv` - Housing condition-based eligibility
- `violations_eligibility.csv` - Property violation-based eligibility
- `store_accessibility.csv` - Store proximity analysis
- `park_accessibility.csv` - Park proximity analysis
- `residency_stability.csv` - Residency stability indicators

**Key Variables in comprehensive_eligibility_analysis.csv**:
- `res_id` - Unique resident identifier
- `age`, `age_group` - Age information
- `ward_id`, `precinct_id` - Geographic identifiers
- `tract_id`, `tract_name`, `median_income` - Census tract data
- `income_category` - Low/Moderate/Higher Income classification
- `has_poor_conditions` - Housing condition flag
- `has_violations` - Property violation flag
- `store_accessibility`, `park_accessibility` - Amenity access levels
- `eligibility_score` - Total eligibility score (0-100)
- `priority_level` - High/Medium/Low priority classification

**Summary Statistics**:
- Total analyzed: 6,958 elderly residents
- High Priority: 30 residents (0.4%)
- Medium Priority: 1,050 residents (15.1%)
- Total Qualifying: 1,080 residents (15.5%)

### 03_barriers/
**Purpose**: Barriers to housing access and quality of life

**Files**:
- `barriers_comprehensive.csv` - **MAIN DATASET**: Complete barrier profile for each resident
- `barriers_financial.csv` - Financial barriers (income-based)
- `barriers_conditions.csv` - Building condition barriers
- `barriers_violations.csv` - Property violation barriers
- `barriers_by_ward.csv` - Barrier analysis aggregated by ward
- `barriers_by_precinct.csv` - Barrier analysis aggregated by precinct

**Key Variables in barriers_comprehensive.csv**:
- `res_id` - Unique resident identifier
- `has_financial_barrier` - Financial barrier flag
- `has_condition_barrier` - Housing condition barrier flag
- `has_violation_barrier` - Property violation barrier flag
- `has_accessibility_barrier` - Accessibility barrier flag
- `total_barriers` - Count of barriers per resident

**Summary Statistics**:
- Elderly with any barrier: 1,037 residents (14.9%)
- Elderly with multiple barriers (2+): ~168 residents (2.4%)
- Elderly with high barriers (3+): ~35 residents (0.5%)

### 04_tenure_residency/
**Purpose**: Homeowner/renter status and residency information

**Files**:
- `tenure_comprehensive.csv` - **MAIN DATASET**: Complete tenure and residency profile
- `tenure_homeowner_renter.csv` - Homeowner vs renter status
- `tenure_residency_length.csv` - Residency length indicators
- `tenure_by_ward.csv` - Tenure analysis by ward
- `tenure_by_precinct.csv` - Tenure analysis by precinct
- `tenure_by_age_group.csv` - Tenure analysis by age group
- `tenure_by_income.csv` - Tenure analysis by income category

**Key Variables in tenure_comprehensive.csv**:
- `res_id` - Unique resident identifier
- `tenure_status` - Homeowner/Renter/Unknown
- `property_value` - Property value (for homeowners)
- `residency_status` - Mapped/Not Mapped indicator
- `ward_id`, `precinct_id` - Geographic identifiers

**Summary Statistics**:
- Total mapped: 5,391 residents (72.9% of total elderly)
- Renters: 2,492 (46.2% of mapped)
- Homeowners: 1,898 (35.2% of mapped)
- Unknown: 1,001 (18.6% of mapped)

**Important Note**: Building matching is spatial (address matching), not temporal (residency verification). The residency length indicators show address matching capability, not verified continuous residency.

### 05_market_impact/
**Purpose**: Housing market impact analysis for proposed 50-60 unit senior housing project

**Files**:
- `outreach_pool_expanded_300.csv` - **MAIN DATASET**: Expanded outreach pool of 300 priority candidates
- `project_candidates_top60.csv` - Top 60 priority candidates for the project
- `project_homeowner_candidates.csv` - Homeowner candidates and their properties
- `outreach_pool_homeowners.csv` - Homeowner candidates from expanded pool
- `neighborhood_market_impact.csv` - Neighborhood-level impact analysis
- `alternative_strategy_renters.csv` - Alternative selection: Renter-priority strategy
- `alternative_strategy_conditions.csv` - Alternative selection: Condition-priority strategy

**Key Variables in outreach_pool_expanded_300.csv**:
- `res_id` - Unique resident identifier
- `age`, `age_group` - Age information
- `eligibility_score` - Eligibility score (0-100)
- `priority_level` - High/Medium priority
- `tenure_status` - Homeowner/Renter/Unknown
- `property_value` - Property value (for homeowners)
- `ward_id`, `precinct_id`, `tract_id` - Geographic identifiers
- `income_category` - Income classification
- `has_poor_conditions`, `has_violations` - Housing quality indicators

**Summary Statistics**:
- Total outreach pool: 300 candidates
- Homeowners: 150 (50.0%)
- Renters: 90 (30.0%)
- Unknown tenure: 60 (20.0%)
- Total homeowner property value: $163.3 million
- Estimated impact (20-30% acceptance): $31.5-$47.8 million

**Top 60 Candidates**:
- Homeowners: 26 (43.3%)
- Total property value: $26.6 million
- Average property value: $1.02 million

### 06_outreach_targeting/
**Purpose**: Geographic targeting data for outreach program

**Files**:
- `outreach_targeting_tracts.csv` - Census tract level targeting data
- `outreach_targeting_areas.csv` - Precinct/ward level targeting data

**Key Variables**:
- Geographic identifiers (ward, precinct, census tract)
- Candidate counts by area
- Average eligibility scores
- Homeowner counts
- Property value totals

**Top Target Areas**:
- Census Tract 7.03: 33 candidates
- Census Tract 101.03: 14 candidates
- Census Tract 6.03: 10 candidates

## Data Quality Notes

1. **Exclusions**: Residents already in income-restricted or senior housing projects (458 residents, 6.2% of total) were excluded from eligibility analysis.

2. **Mapping Coverage**: 72.9% of elderly residents (5,391) are mapped to buildings, enabling property-level analysis.

3. **Tenure Data**: 18.6-20% of residents have unknown tenure status, limiting full market impact assessment.

4. **Residency Length**: Building matching indicates address-level matching capability, but does NOT verify actual residency length or continuity. The matching is spatial, not temporal.

5. **Property Values**: Assessed values from FY2025 property assessments may differ from market values.

## Methodology

All datasets are derived from:
- Voter registration data (2020): 43,759 registered voters in Wards 21 and 22
- Property assessment data (2025): Building characteristics, property values, housing conditions
- Census tract data: Median income, demographic characteristics
- Property violations: Open and closed violations
- Amenity data: Store and park locations

Eligibility scoring system (0-100 points):
- Need Factors (60 points max): Income, housing conditions, violations, residency
- Amenity Access (10 points max): Store and park proximity

Priority levels:
- High (40-59 points): 30 residents
- Medium (20-39 points): 1,050 residents
- Low (0-19 points): 5,878 residents

## Usage

These datasets can be used for:
- Housing policy development
- Resource allocation planning
- Outreach program targeting
- Market impact assessment
- Research and analysis

## Contact

For questions about these datasets, please refer to the comprehensive analysis report:
- `fa25-team-a/reports/latex/Elderly_Housing_Analysis_Report.pdf`

## Version

Dataset Version: 1.0
Date: 2025-01-XX
Analysis Period: 2020-2025

