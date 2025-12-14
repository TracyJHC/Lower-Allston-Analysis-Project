# Research Questions

## 1. Who are the elderly residents in Allston-Brighton, and where are they located?

### Overall Statistics
- **Total Elderly Residents (62+)**: 7,396 out of 43,759 total voters (16.9%)
- **Average Age**: 74.9 years
- **Median Age**: 74.0 years
- **Age Range**: 62-105+ years

### Geographic Distribution

#### Ward Level
- **Ward 21 (Allston)**: 4,199 elderly residents (17.7% of ward population, avg age 76.2)
- **Ward 22 (Brighton)**: 3,197 elderly residents (16.0% of ward population, avg age 73.1)
- Allston has a higher percentage and older average age of elderly residents

#### Top Precincts by Elderly Count
1. **Precinct 21-13**: 841 elderly (39.7% of precinct, avg age 79.5)
2. **Precinct 21-16**: 540 elderly (33.2% of precinct, avg age 77.7)
3. **Precinct 21-12**: 499 elderly (32.0% of precinct, avg age 78.2)
4. **Precinct 22-2**: 423 elderly (17.2% of precinct, avg age 73.3)
5. **Precinct 21-10**: 413 elderly (26.3% of precinct, avg age 75.9)

#### Top Streets by Elderly Count
1. **Commonwealth Ave**: 650 elderly (13.8% of street, avg age 73.9)
2. **Wallingford Rd**: 548 elderly (77.7% of street, avg age 83.0) - highest concentration
3. **Washington St**: 513 elderly (41.2% of street, avg age 78.7)
4. **Chestnut Hill Ave**: 279 elderly (44.6% of street, avg age 77.0)
5. **Fidelis Way**: 134 elderly (41.2% of street, avg age 74.9)

### Mapping and Geocoding Status
- **Mapped to Buildings**: 5,391 elderly (72.9% of total elderly)
- **Geocoded (has lat/long)**: 7,371 elderly (99.7% of total elderly)
- **Mapped AND Geocoded**: 5,388 elderly (72.9% of total elderly)
- High geocoding success rate indicates most elderly have valid addresses

### Census Tract Analysis
- **21 census tracts** contain mapped elderly residents
- **5,042 elderly residents** mapped across these tracts (68.2% of total elderly)
- **Median income range**: $33,229 to $151,466 across tracts
- **Top tract (5.05)**: 965 elderly residents with median income $80,556
- Spatial distribution shows elderly concentrated in specific areas, with varying income levels

### Key Insights
1. **Concentration**: Elderly residents are highly concentrated in certain precincts (up to 39.7% in Precinct 21-13) and streets (up to 77.7% on Wallingford Rd)
2. **Age Distribution**: Average age ranges from 70.5 to 83.7 years, with some areas having significantly older populations
3. **Geographic Clustering**: Strong clustering in Allston (Ward 21), particularly in precincts 13, 16, and 12
4. **Income Diversity**: Elderly live across a wide range of income levels, from lower-income ($33K) to higher-income ($151K) census tracts
5. **Mapping Coverage**: 72.9% mapping rate allows for detailed building-level analysis

### Detailed Analysis

For complete methodology, detailed statistics, and visualizations, see:
- **[Full Question 1 Analysis](./question1.md)** - Comprehensive location and demographic analysis with all findings

### Interactive Map

The interactive map shows census tracts color-coded by median income (red = low income, green = high income) with labels showing the elderly count in each tract.

**Map Features:**
- Census tracts color-coded by median income (red = low, green = high)
- Labels showing elderly count in each tract
- Click on any tract to see: Tract ID, name, elderly count, and median income
- Color legend showing income range ($33,229 to $151,466)

**To view the full interactive map:**
- [Open elderly_census_tract_map.html](../reports/figures/elderly_census_tract_map.html) in your web browser
- Full path: `fa25-team-a/reports/figures/elderly_census_tract_map.html`

---

## 2. How many qualify for new affordable senior housing opportunities?

### Overall Statistics
- **Total Elderly Analyzed** (after excluding income-restricted housing): 6,958
- **High Priority Candidates**: 30 residents (0.4%)
- **Medium Priority Candidates**: 1,050 residents (15.1%)
- **Total Qualifying (Medium + High)**: 1,080 residents (15.5%)

### Key Eligibility Factors

#### Income Eligibility
- **Low Income** (<$50k census tract): 562 residents (11.8% of those with income data)
- **Moderate Income** ($50k-$75k): 475 residents (10.0%)
- **Total Income-Eligible**: 1,037 residents (21.8% of those with income data)

#### Housing Quality Barriers
- **Poor/Fair Housing Conditions**: 133 residents (2.7% of those with condition data)
- **Open Property Violations**: 35 residents (0.5%)

#### Residency Stability
- **5+ Years at Current Address**: 4,933 residents (71.1%)

#### Amenity Access
- **Excellent Park Access** (≤300m): 6,326 residents (91.5%)
- **Excellent Store Access** (≤500m): 3,391 residents (48.9%)

### Eligibility Scoring System

A comprehensive scoring system (0-100 points) was developed based on:
- **Need Factors** (60 points max): Income, housing conditions, violations, residency
- **Amenity Access** (10 points max): Store and park proximity

**Priority Levels:**
- Very High (60-100 points): 0 residents
- High (40-59 points): 30 residents
- Medium (20-39 points): 1,050 residents
- Low (0-19 points): 5,878 residents

### Key Insights

1. **Significant Demand**: 1,080 elderly residents (15.5%) qualify as Medium to High priority for affordable senior housing
2. **Income-Based Need**: 1,037 residents live in low or moderate-income census tracts
3. **Housing Quality Issues**: 133 residents face Poor/Fair housing conditions, 35 have open violations
4. **Geographic Distribution**: Eligible residents distributed across 21 census tracts
5. **Strong Community Ties**: 71.1% have lived at current address 5+ years

### Detailed Analysis

For complete methodology, detailed statistics, and recommendations, see:
- **[Full Question 2 Analysis](./question2.md)** - Comprehensive eligibility analysis with all findings

### Data Files

All eligibility analysis results are available in `/data/processed/elderly_analysis/`:
- `comprehensive_eligibility_analysis.csv` - Complete dataset with all features and scores
- Individual feature tables (income, conditions, violations, accessibility, etc.)

## 3. What barriers exist in their current living situations (financial, building condition, etc)?

### Overall Statistics
- **Total Elderly Analyzed** (after excluding income-restricted housing): 6,958
- **Elderly with Any Barrier**: 1,037 residents (14.9%)
- **Elderly with Multiple Barriers (2+)**: ~168 residents (2.4%)
- **Elderly with High Barriers (3+)**: ~35 residents (0.5%)

### Barrier Types

#### Financial Barriers
- **Low Income** (<$50k census tract): 562 residents (8.1% of analyzed, 11.8% of those with income data)
- **Moderate Income** ($50k-$75k): 475 residents (6.8% of analyzed, 10.0% of those with income data)
- **Total Financial Barriers**: 1,037 residents (14.9%)

#### Building Condition Barriers
- **Poor/Fair Housing Conditions**: 133 residents (2.7% of those with condition data)
- **Interior barriers**: 78 residents
- **Exterior barriers**: 71 residents
- **Grade barriers**: 3 residents

#### Property Violations
- **Open Violations**: 35 residents (0.5%)
- **Violation Categories**: Safety issues, maintenance, permit/code issues

#### Accessibility Barriers
- **Limited Store Access** (>1000m): 4 residents (0.1%)
- **Limited Park Access** (>600m): 4 residents (0.1%)
- Most elderly have excellent access to stores and parks

### Key Insights

1. **Financial Barriers Most Common**: 14.9% face income-based barriers
2. **Housing Quality Issues**: 2.7% face poor/fair housing conditions
3. **Active Violations**: 0.5% have open property violations requiring attention
4. **Accessibility Generally Good**: Less than 0.1% face access barriers
5. **Multiple Barriers**: 0.5% face 3+ compounding barriers

### Detailed Analysis

For complete methodology, detailed statistics, and recommendations, see:
- **[Full Question 3 Analysis](./question3.md)** - Comprehensive barrier analysis with all findings

### Data Files

All barrier analysis results are available in `/data/processed/elderly_analysis/`:
- `barriers_comprehensive.csv` - Complete barrier profile for each resident
- `barriers_financial.csv` - Financial barrier analysis
- `barriers_conditions.csv` - Building condition barriers
- `barriers_violations.csv` - Property violations analysis
- `barriers_by_ward.csv` - Geographic analysis by ward
- `barriers_by_precinct.csv` - Geographic analysis by precinct

## 4. How long have they lived in their current residences? Are they homeowners or renters?

### Overall Statistics
- **Total Elderly Analyzed** (for residency length): 6,958
- **Elderly with 5+ Years Residency**: 4,933 residents (71.1%)
- **Elderly with Tenure Data** (homeowner/renter): 5,391 residents (72.9% of total elderly)

### Homeowner vs Renter Status
- **Renters**: 2,492 residents (46.2%)
- **Homeowners**: 1,898 residents (35.2%)
- **Unknown**: 1,001 residents (18.6%)
- Available for 5,391 mapped elderly residents (72.9% of total)

### Length of Residency
- **Mapped to Buildings**: 5,391 residents (72.9% of total elderly)
- **Not Mapped**: 2,005 residents (27.1%)
- **Method**: Address matching between voter data (2020) and building assessment data (2025)
- **Critical Important Note**: The 5-year minimum residency is an **inference from data matching, NOT verified residency**. Building match indicates address-level matching capability, but does NOT verify actual residency length or continuity. The matching is spatial (address matching), not temporal (residency verification). A resident could have moved in 2024 and still appear in both datasets.

### Key Insights

1. **Address Matching Success**: 72.9% of elderly could be matched to building records
2. **Tenure Distribution**: 46.2% renters, 35.2% homeowners (18.6% unknown)
3. **Geographic Variation**: Ward 22 (Brighton) has 65.4% homeowners vs Ward 21 (Allston) at 12.8%
4. **Age Pattern**: Homeownership decreases with age (39.3% at 62-69 to 25.4% at 90+)
5. **Data Limitation**: Building matching is spatial (address matching), not temporal - does not verify actual residency length

### Detailed Analysis

For complete methodology, detailed statistics, and recommendations, see:
- **[Full Question 4 Analysis](./question4.md)** - Comprehensive tenure and residency analysis with all findings

### Data Files

All tenure analysis results are available in `/data/processed/elderly_analysis/`:
- `tenure_comprehensive.csv` - Complete tenure profile for each resident
- `tenure_homeowner_renter.csv` - Homeowner/renter status
- `tenure_residency_length.csv` - Residency length analysis
- `tenure_by_ward.csv` - Geographic analysis by ward
- `tenure_by_precinct.csv` - Geographic analysis by precinct
- `tenure_by_age_group.csv` - Analysis by age group
- `tenure_by_income.csv` - Analysis by income category

### Limitations

1. **Residency Length**: Only provides minimum 5-year duration, not exact length
2. **Temporal Coverage**: Cannot detect moves between 2020-2025
3. **Tenure Coverage**: Only available for mapped elderly (72.9% of total)

## 5. What would be the impact on the housing market if they transitioned to senior housing?

### Project Context
- **New Housing Project**: 50-60 units
- **Outreach Pool Needed**: 200-300 candidates (assuming 20-30% response rate)
- **Expanded Outreach Pool**: Top 300 priority candidates identified
- **Top Candidates Selected**: 60 priority candidates (30 High + 30 Medium priority)
- **Average Eligibility Score**: 42.7 (range: 40-50)

### Expanded Outreach Pool

**Outreach Strategy**: To fill 50-60 units, outreach to 200-300 candidates is needed (assuming 20-30% response rate).

**Expanded Pool Characteristics**:
- **Total Pool**: Top 300 priority candidates (all 30 High + top 270 Medium priority)
- **Average Eligibility Score**: 37.1 (range: 35-50)
- **Tenure Distribution**: 150 Homeowners (50.0%), 90 Renters (30.0%), 60 Unknown (20.0%)
- **Geographic Distribution**: Ward 22 (199 candidates, 66.3%), Ward 21 (101 candidates, 33.7%)
- **Top Census Tracts**: Tract 101.03 (115 candidates), Tract 7.03 (95 candidates), Tract 6.03 (75 candidates)
- **Homeowner Property Value**: $163.3M total, avg $1,088,799
- **Estimated Property Value if 20-30% Accept**: $31.5M-$47.8M (30-45 homeowners)

### Market Impact

#### Properties That Would Become Available (Top 60 Candidates)
- **Homeowner Candidates**: 26 (43.3% of top 60)
- **Total Property Value**: $26,582,000
- **Average Property Value**: $1,022,385
- **Median Property Value**: $1,003,000
- **Property Value Range**: $592,100 - $1,376,700

#### Tenure Breakdown of Top 60 Candidates
- **Homeowners**: 26 (43.3%) - Properties would become available
- **Renters**: 6 (10.0%) - Rental units would become available
- **Unknown Tenure**: 28 (46.7%) - Need additional data

**Note**: The expanded pool of 200-300 candidates includes significantly more homeowners, with higher total property value potential if 20-30% accept.

### Candidate Profile

**Demographics**:
- **Average Age**: 76.2 years (range: 62-97)
- **Age Distribution**: 70-79 (33.3%), 80-89 (30.0%), 62-69 (28.3%), 90+ (8.3%)

**Income & Conditions**:
- **95% Low Income** (57 candidates), 5% Moderate Income (3 candidates)
- **46.7% with Poor/Fair Housing Conditions** (28 candidates)
- **6.7% with Open Violations** (4 candidates)

**Geographic Distribution**:
- **Ward 21 (Allston)**: 34 candidates (56.7%)
- **Ward 22 (Brighton)**: 26 candidates (43.3%)
- **Top Census Tract**: Tract 7.03 with 33 candidates (55.0%)

### Key Insights

1. **Concentrated Market Impact**: 26 properties worth $26.6M would enter the market, concentrated in 3 low-income census tracts
2. **Property Values**: Average $1.02M suggests established homeowners with equity (range: $592k-$1.38M)
3. **Geographic Concentration**: 95% of candidates in 3 census tracts (7.03, 101.03, 6.03) enables efficient outreach
4. **Rental Market**: 6+ rental units would also become available from renter candidates
5. **Neighborhood Impact**: 5 census tracts affected, all with homeowner candidates ($32.6M total property value)
6. **Data Gap**: 46.7% unknown tenure limits full impact assessment

### Outreach Strategy

**Top Target Areas**:
1. **Ward 21, Precinct 7** (Census Tract 7.03): 24 candidates - highest concentration
2. **Ward 22, Precincts 1, 5, 2** (Census Tracts 101.03, 6.03): 22 candidates combined

**Priority Factors**: 
- High candidate density (33 candidates in Tract 7.03 alone)
- High eligibility scores (all 40+ points, avg 42.7)
- Low income areas (95% Low Income candidates)
- Housing quality issues (46.7% with poor conditions)

**Alternative Strategies Available**:
- Renter-priority: 60 candidates (avg score 36.2)
- Condition-priority: 60 candidates with housing issues (avg score 39.2)

### Detailed Analysis

For complete methodology, candidate profiles, outreach targeting, and alternative strategies, see:
- **[Full Question 5 Analysis](./question5.md)** - Comprehensive market impact and outreach analysis

### Data Files

All market impact analysis results are available in `/data/processed/elderly_analysis/`:
- `outreach_pool_expanded_300.csv` - **Expanded outreach pool of 300 candidates**
- `outreach_pool_homeowners.csv` - Homeowner candidates from expanded pool
- `project_candidates_top60.csv` - Top 60 candidates for the project
- `project_homeowner_candidates.csv` - Homeowner candidates and properties
- `outreach_targeting_areas.csv` - Geographic targeting for outreach
- `outreach_targeting_tracts.csv` - Census tract level targeting
- `neighborhood_market_impact.csv` - Neighborhood impact analysis
- Alternative strategy files (renters, income, conditions)

### Limitations

1. **Tenure Data**: 46.7% of candidates have unknown tenure status
2. **Property Values**: Assessed values may differ from market values
3. **Transition Assumption**: Analysis assumes all candidates transition simultaneously
4. **Market Dynamics**: Cannot predict actual market response

