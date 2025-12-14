# Question 4: How long have they lived in their current residences? Are they homeowners or renters?

## Executive Summary

This analysis examines residential tenure (homeowner vs renter status) and length of residency for elderly residents (62+) in Allston-Brighton. The analysis covers **5,391 elderly residents** mapped to buildings, allowing for tenure determination, and **6,958 elderly residents** for residency length analysis.

**Key Finding**: **5,391 elderly residents (72.9% of total)** are mapped to buildings, allowing for tenure analysis. Of these mapped residents, **2,492 (46.2%) are renters** and **1,898 (35.2%) are homeowners**, with 1,001 (18.6%) having unknown tenure status. 

**Important Note on Residency Length**: The 5-year minimum residency is an **inference from data matching**, not verified residency. The building match indicates that these residents' addresses could be matched to building records between 2020 (voter data) and 2025 (property data), but this does NOT verify that residents have lived at the same address continuously for 5+ years. The matching process is spatial (address matching), not temporal (residency verification). The actual length of residency cannot be definitively determined from the current data matching process.

---

## Methodology

### Analysis Population

- **Total elderly**: 7,396
- **Mapped to buildings**: 5,391 (72.9% of total elderly)
- **With tenure data**: 5,391 (100% of mapped elderly, though 1,001 have unknown tenure status)
- **With residency length data**: 7,396 (all elderly analyzed)

### Data Sources

1. **Homeowner/Renter Status**: 
   - `owner_occ` field in buildings table
   - 'Y' = Owner-occupied (Homeowner)
   - Other = Renter or Owner (Not Occupied)

2. **Length of Residency**:
   - **Current Analysis**: Building match indicates address could be matched to building records
   - **Limitation**: The `voters_buildings_map` table matches addresses spatially, not temporally
   - **Note**: While voter data is from 2020 and property data is from 2025, the matching process doesn't verify that residents have been at the same address for 5+ years
   - Cannot determine exact move-in date or verify continuous residency

### Limitations

1. **Residency Length**:
   - **Critical Limitation**: The 5-year minimum residency is an **inference from data matching**, NOT verified residency
   - The current analysis does NOT actually verify 5+ years of residency
   - Building match only indicates that an address could be matched to a building record
   - The matching process is spatial (address matching), not temporal (residency verification)
   - Cannot determine actual length of residency from current data
   - Cannot detect moves between 2020-2025
   - The "5+ years" claim is an inference/assumption based on data sources being 5 years apart, but is NOT verified by the matching algorithm
   - A resident could have moved in 2024 and still appear in both datasets, or could have moved away and returned

2. **Tenure Status**:
   - Only available for mapped elderly (72.9% of total)
   - Some properties may have missing `owner_occ` data
   - 1,001 residents (18.6% of mapped) have unknown tenure status

---

## 1. Homeowner vs Renter Status

### Overall Tenure Distribution

**Analysis**: Based on `owner_occ` field from buildings table for 5,391 mapped elderly residents.

**Findings**:
- **Homeowners** (owner_occ = 'Y'): Owner-occupied properties
- **Renters** (owner_occ ≠ 'Y'): Non-owner-occupied properties
- **Unknown** (owner_occ IS NULL): Missing tenure data

**Tenure Status Distribution**:
- **Renter**: 2,492 residents (46.2%)
- **Homeowner**: 1,898 residents (35.2%)
- **Unknown**: 1,001 residents (18.6%)

**Key Insight**: Renters outnumber homeowners among elderly residents (46.2% vs 35.2%), indicating that a significant portion of the elderly population may face housing insecurity or rent increases. This is particularly important for affordable senior housing planning.

### Property Value by Tenure Status

**Analysis**: Property values for homeowners vs renters.

**Findings**:
- **Homeowner property values**: [Statistics to be filled]
- **Renter property values**: [Statistics to be filled]
- **Value categories**: Low (<$500k), Moderate ($500k-$1M), High ($1M+)

**Key Insight**: [To be filled with insights about property values and tenure]

---

## 2. Length of Residency

### Residency Duration Analysis

**Important Note**: The 5-year minimum residency mentioned below is an **inference from data matching**, not verified residency. While voter data is from 2020 and property data is from 2025, the matching process does not verify that residents have been at the same address continuously for 5+ years. The matching is spatial (address matching), not temporal (residency verification).

**Analysis**: Minimum 5-year residency inferred from matching 2020 voter data to 2025 property assessment data. This inference is based on the assumption that if a resident's address appears in both datasets, they may have been there for at least 5 years, but this is not verified.

**Findings**:
- **Total analyzed**: 7,396 elderly residents
- **Mapped to buildings**: 5,391 residents (72.9%)
- **Not mapped**: 2,005 residents (27.1%)

**Mapping Status Distribution**:
- Mapped (address matched to building): 5,391 (72.9%)
- Not Mapped: 2,005 (27.1%)

**Key Insight**: 72.9% of elderly residents could be matched to building records, allowing for tenure analysis. However, this mapping does not verify actual length of residency. The mapping indicates that these residents' addresses exist in both the voter database and building assessment database, but does not confirm they have lived there continuously for 5+ years.

---

## 3. Combined Tenure and Residency Analysis

### Tenure Status by Residency Duration

**Analysis**: Cross-tabulation of homeowner/renter status with residency length.

**Findings**:
- **Homeowners mapped to buildings**: 1,898 (100% of mapped homeowners)
- **Renters mapped to buildings**: 2,492 (100% of mapped renters)
- **Unknown tenure mapped to buildings**: 1,001
- **Homeowners not mapped**: 0 (by definition - only mapped residents are in this analysis)
- **Renters not mapped**: 0 (by definition - only mapped residents are in this analysis)

**Key Insight**: All elderly residents with tenure data (homeowners and renters) have been successfully matched to building records. This allows for property-level analysis. However, this does not verify actual residency length - it only confirms that their addresses could be matched to building records. The 1,001 residents with unknown tenure status are also mapped to buildings, but their `owner_occ` status could not be determined.

---

## 4. Geographic Distribution

### Tenure Status by Ward

**Analysis**: Homeowner/renter breakdown by ward.

**Ward 21 (Allston)**:
- Total elderly: 3,094
- Homeowners: 395 (12.8%)
- Renters: 1,820 (58.8%)
- Unknown: 879 (28.4%)
- Homeowner percentage: 12.8%

**Ward 22 (Brighton)**:
- Total elderly: 2,297
- Homeowners: 1,503 (65.4%)
- Renters: 672 (29.3%)
- Unknown: 122 (5.3%)
- Homeowner percentage: 65.4%

**Key Insight**: There is a stark contrast between the two wards. Ward 22 (Brighton) has a much higher homeowner rate (65.4%) compared to Ward 21 (Allston) at only 12.8%. Ward 21 is predominantly renter-occupied (58.8%), which may indicate different housing needs and priorities between the two areas.

### Tenure Status by Precinct

**Top Precincts** (by elderly count):
- **Precinct 13**: 967 total (164 homeowners/17.0%, 628 renters/64.9%, 175 unknown)
- **Precinct 16**: [Additional precincts available in data files]

**Key Insight**: Precinct-level analysis shows variation in tenure patterns, with some precincts having higher renter concentrations than others.

---

## 5. Demographic Analysis

### Tenure Status by Age Group

**Analysis**: Homeowner/renter status across age groups.

**Findings**:
- **62-69 years**: 1,838 total (722 homeowners/39.3%, 712 renters/38.7%, 404 unknown)
- **70-79 years**: 1,963 total (725 homeowners/36.9%, 833 renters/42.4%, 405 unknown)
- **80-89 years**: 1,122 total (332 homeowners/29.6%, 638 renters/56.9%, 152 unknown)
- **90+ years**: 468 total (119 homeowners/25.4%, 309 renters/66.0%, 40 unknown)

**Key Insight**: Homeownership rates decrease with age, while renter rates increase. Younger elderly (62-69) have nearly equal homeowner and renter rates (~39% each), but by age 90+, renters make up 66% of the population. This suggests that older elderly may be more likely to transition from homeownership to renting, or that long-term renters are more likely to reach advanced ages.

### Tenure Status by Income Category

**Analysis**: Homeowner/renter status by census tract median income.

**Findings**:
- **Higher Income** ($75k+): 3,997 total (1,415 homeowners/35.4%, 1,916 renters/47.9%, 666 unknown)
- **Low Income** (<$50k): 916 total (324 homeowners/35.4%, 341 renters/37.2%, 251 unknown)
- **Moderate Income** ($50k-$75k): 475 total (159 homeowners/33.5%, 235 renters/49.5%, 81 unknown)

**Key Insight**: Homeownership rates are relatively consistent across income categories (33-35%), but renter rates vary more significantly. Higher income areas have the highest absolute number of both homeowners and renters, while moderate income areas have the highest renter percentage (49.5%). This suggests that income level alone doesn't strongly predict tenure status among elderly residents.

---

## Key Findings

### Summary Statistics

1. **Address Matching**: 72.9% of elderly could be matched to building records
2. **Homeowner/Renter Distribution**: 46.2% renters, 35.2% homeowners, 18.6% unknown
3. **Geographic Patterns**: Ward 22 (Brighton) has 65.4% homeowners vs Ward 21 (Allston) at 12.8%
4. **Age Patterns**: Homeownership decreases with age (39.3% at 62-69 to 25.4% at 90+)
5. **Income Patterns**: Homeownership rates consistent across income levels (~33-35%)

**Note**: The building matching indicates address-level matching capability, but does not verify actual residency length or continuity.

### Priority Populations

**Mapped Homeowners**: 1,898 residents
- Successfully matched to building records
- May have equity in property
- Potential candidates for downsizing or senior housing transition
- Concentrated in Ward 22 (Brighton)

**Mapped Renters**: 2,492 residents
- Successfully matched to building records
- May face rent increases or housing insecurity
- Potential candidates for affordable senior housing
- Concentrated in Ward 21 (Allston)
- Higher proportion in older age groups (66% at age 90+)

**Unknown Tenure (Mapped)**: 1,001 residents
- Matched to building records but tenure status could not be determined
- May include both homeowners and renters
- Need additional data collection for `owner_occ` field

---

## Recommendations

### Immediate Actions

1. **Support Long-term Homeowners**: Develop programs to help long-term homeowners age in place or transition to appropriate senior housing
2. **Protect Long-term Renters**: Identify long-term renters who may face displacement and prioritize them for affordable senior housing
3. **Geographic Targeting**: Focus outreach on areas with high concentrations of long-term residents

### Long-Term Strategies

1. **Housing Stability Programs**: Support programs to help elderly maintain stable housing
2. **Transition Support**: Services to help elderly transition from homeownership to senior housing when appropriate
3. **Renter Protection**: Policies to protect long-term elderly renters from displacement

### Data Gaps

1. **Exact Residency Length**: Current analysis only provides minimum 5-year residency
2. **Move History**: Cannot track moves between 2020-2025
3. **Tenure Coverage**: Only 72.9% of elderly have tenure data (mapped to buildings)

---

## Data Files

All tenure analysis data is available in:
- `tenure_homeowner_renter.csv` - Homeowner/renter status for each resident
- `tenure_residency_length.csv` - Residency length analysis
- `tenure_combined.csv` - Combined tenure and residency data
- `tenure_comprehensive.csv` - Complete tenure profile with demographics
- `tenure_by_ward.csv` - Geographic analysis by ward
- `tenure_by_precinct.csv` - Geographic analysis by precinct
- `tenure_by_age_group.csv` - Analysis by age group
- `tenure_by_income.csv` - Analysis by income category

---

## Methodology Notes

### Tenure Status Definitions

**Homeowner**: Property where `owner_occ = 'Y'` (owner-occupied)
**Renter**: Property where `owner_occ ≠ 'Y'` (non-owner-occupied, person living there is a renter)
**Unknown**: Property where `owner_occ IS NULL` (missing data)

### Residency Length Definitions

**Mapped to Building**: Resident's address successfully matched to a building record in `voters_buildings_map`
**Not Mapped**: Resident's address could not be matched to a building record

**Critical Important Note**: The building matching process is spatial (address matching), not temporal. While the data sources are from 2020 (voters) and 2025 (property assessments), the matching process does not verify that residents have been at the same address continuously for 5+ years. **The 5-year minimum residency is an inference from data matching, not verified residency.** The "5+ years" claim is an inference/assumption based on the data source dates, but is NOT verified by the matching algorithm. A resident could have moved in 2024 and still appear in both datasets, or could have moved away and returned between 2020-2025.

### Data Sources

- Voter demographics: 2020 voter list
- Property assessments: FY2025 property assessment data
- Building data: Buildings table with `owner_occ` field
- Census tract income: American Community Survey data

### Limitations

1. **Residency Length**: Only provides minimum duration, not exact length
2. **Temporal Coverage**: Cannot detect moves between 2020-2025
3. **Tenure Coverage**: Only available for mapped elderly (72.9%)
4. **Move History**: Cannot determine if resident moved and returned

---

## Visualizations

Available visualizations:
- Tenure status distribution charts
- Residency length distribution
- Geographic tenure maps by ward/precinct
- Age group tenure analysis
- Income category tenure analysis

See `elderly_tenure_analysis.ipynb` notebook for detailed visualizations and interactive analysis.

