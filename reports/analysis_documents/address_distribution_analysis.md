# Allston-Brighton Address Distribution Analysis

## Overview
This analysis compares address distributions between property assessment data and voter registration data for the Allston-Brighton area.

## Key Findings

### Dataset Sizes
- **Property Addresses**: 5,985 total addresses (5,917 unique)
- **Voter Records**: 43,759 total records (25,773 unique addresses)
- **Address Overlap**: Only 60 addresses appear in both datasets

### Geographic Coverage Differences

#### ZIP Code Distribution

**Property Data ZIPs:**
- 2116: 2,992 properties (50%)
- 2215: 1,217 properties (20%)
- 2115: 1,019 properties (17%)
- 2108: 481 properties (8%)
- 2118: 258 properties (4%)
- 2111: 17 properties
- 2133: 1 property

**Voter Data ZIPs:**
- 2135: 29,463 voters (67%)
- 2134: 11,150 voters (25%)
- 2215: 2,584 voters (6%)
- 2163: 370 voters
- 2467: 161 voters
- 2445: 18 voters
- 2446: 13 voters

#### Street Coverage

**Property Data Streets (9 total):**
- BEACON ST: 3,001 properties
- COMMONWEALTH AV: 2,507 properties
- BROOKLINE AV: 158 properties
- W Brookline ST: 145 properties
- E BROOKLINE ST: 113 properties
- Harvard ST: 16 properties
- Beacon ST: 3 properties
- Brookline AVE: 1 property
- BEACON: 1 property

**Voter Data Streets (389 total):**
- COMMONWEALTH AVE: 4,937 voters
- WASHINGTON ST: 1,851 voters
- CHESTNUT HILL AVE: 854 voters
- WALLINGFORD RD: 705 voters
- BRAINERD RD: 694 voters
- STRATHMORE RD: 671 voters
- NORTH BEACON ST: 577 voters
- BEACON ST: 574 voters
- KELTON ST: 548 voters
- FANEUIL ST: 537 voters

## Analysis

### 1. **Geographic Focus Differences**
- **Property Data**: Concentrated on major commercial corridors (Beacon Street, Commonwealth Avenue)
- **Voter Data**: Covers broader residential areas with 389 different streets

### 2. **ZIP Code Mismatch**
- **Property Data**: Primarily 2116, 2215, 2115 (commercial/mixed-use areas)
- **Voter Data**: Primarily 2135, 2134 (residential areas)

### 3. **Data Source Characteristics**
- **Property Data**: Assessment records focus on taxable properties
- **Voter Data**: Residential voter registration covers all housing types

### 4. **Address Overlap**
- Only 60 addresses appear in both datasets
- Property-only addresses: 5,857
- Voter-only addresses: 25,713

## Implications

### For Analysis
1. **Property Data**: Best for commercial/mixed-use property analysis
2. **Voter Data**: Best for residential population analysis
3. **Combined**: Provides comprehensive coverage of Allston-Brighton

### For Mapping
1. **Property Points**: Show commercial/assessment properties
2. **Voter Addresses**: Show residential population distribution
3. **Building Points**: Show all structures regardless of use type

## Recommendations

1. **Use Property Data** for:
   - Commercial property analysis
   - Assessment value studies
   - Zoning analysis

2. **Use Voter Data** for:
   - Residential population analysis
   - Demographic studies
   - Community engagement

3. **Use Building Points** for:
   - Complete building inventory
   - Structural analysis
   - Comprehensive mapping

## Data Quality Notes

- Property data appears to be filtered for assessment purposes
- Voter data provides broader residential coverage
- Building footprint data offers complete structural inventory
- Address standardization needed for better matching

---
*Analysis completed: October 2025*
*Data sources: MassGIS property assessments, Boston voter registration*
