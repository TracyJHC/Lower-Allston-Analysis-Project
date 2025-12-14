# Project Questions Assessment
## Can You Answer These Questions with Current Data?

---

## ✅ QUESTION 1: Who are the elderly residents in Allston-Brighton, and where are they located?

**Data Available:**
- 7,396 elderly residents identified (age 62+)
- 5,391 mapped to buildings (72.9% coverage)
- 5,713 with coordinates (75.9% geocoding coverage)
- Geographic distribution by:
  - Ward (21 & 22)
  - Precinct (29 precincts)
  - Street (362 streets)
  - Census tract (22 tracts)

**Analysis Completed:**
- Age distribution (62-69, 70-79, 80-89, 90+)
- Mean/median age by geographic area
- Interactive map visualization
- Database views: `elderly_by_ward`, `precinct_elderly_analysis`, `street_elderly_analysis`

**Deliverables Ready:**
- Maps of elderly resident concentrations ✅
- Geographic distribution analysis ✅
- Demographic profiles ✅

---

## ✅ QUESTION 2: How many qualify for new affordable senior housing opportunities?

### **YES - ANSWERABLE** (Create Eligibility Criteria from Available Data)

**Given Criteria:**
- **Age cutoff: 62+** (already applied - all 7,396 elderly meet this)

**Data Available to Create Eligibility Criteria:**
- Income data via census tracts (median income by tract)
- Housing conditions data (interior/exterior condition, grade)
- Property violations data (open/closed violations)
- Property values (assessments)
- Residency stability (minimum 5 years from 2020-2025 analysis)

**Current Analysis:**
- `vw_elderly_eligibility` view already created with income-based eligibility:
  - Low Income (<$50k): "Eligible"
  - Moderate Income ($50k-$75k): "Potentially Eligible"
  - Higher Income (>$75k): "Not Eligible"
- Housing condition barriers identified
- Property violation barriers identified

**Recommended Eligibility Criteria to Create:**

1. **Primary Eligibility (Must Meet):**
   - Age: 62+ ✅ (already have - all 7,396 meet this)

2. **Secondary Eligibility Factors (Create thresholds):**

   **A. Financial & Housing Need Factors:**
   - **Income-based:** Use standard affordable housing thresholds
     - Low-income: Census tract median income < $50k
     - Moderate-income: Census tract median income $50k-$75k
   - **Housing condition barriers:**
     - Poor/Fair interior or exterior condition
     - Poor/Fair property grade
   - **Property violations:**
     - Open violations (indicates housing quality issues)
   - **Residency stability:**
     - Minimum 5-year residency (from 2020-2025 match)

   **B. Amenity & Quality of Life Factors:**
   - **Store/Retail Proximity:**
     - Distance to nearest store (55 stores available)
     - 3,641 elderly already mapped to stores (average 707 meters)
     - Threshold: Within 500m = excellent, 500-1000m = good, >1000m = limited access
   - **Parks/Open Space Proximity:**
     - Distance to nearest park (1,099 parks/open spaces available)
     - Threshold: Within 300m = excellent, 300-600m = good, >600m = limited access
   - **Accessibility:**
     - Proximity to major roads (141 road segments available)
     - Transit accessibility (if data available)

   **C. Other Influencing Factors:**
   - **Building age:** Older buildings may indicate maintenance needs
   - **Property type:** Multi-family vs single-family considerations
   - **Geographic concentration:** Areas with high elderly density may need more housing

**Comprehensive Eligibility Scoring System:**

**Priority Score Calculation (0-100 scale):**

1. **Need Factors (60 points):**
   - Low income (<$50k): +25 points
   - Moderate income ($50k-$75k): +15 points
   - Poor housing conditions: +20 points
   - Fair housing conditions: +10 points
   - Open violations: +15 points
   - 5+ year residency: +10 points

2. **Amenity Factors (30 points):**
   - Store within 500m: +15 points
   - Store within 1000m: +10 points
   - Park within 300m: +10 points
   - Park within 600m: +5 points
   - Limited store access (>1000m): -5 points
   - Limited park access (>600m): -5 points

3. **Geographic Factors (10 points):**
   - High elderly density area: +5 points
   - Precinct with high need: +5 points

**Eligibility Tiers:**
- **Highly Eligible (80-100 points):** Multiple need factors + good amenities
- **Moderately Eligible (60-79 points):** Some need factors + adequate amenities
- **Potentially Eligible (40-59 points):** Limited need factors
- **Lower Priority (<40 points):** Few need factors or good current situation

**What You Can Provide:**
- Count of elderly by eligibility tier with comprehensive scoring
- Count with specific barriers (income, conditions, violations, amenity access)
- Geographic distribution of eligible residents
- Priority ranking based on multi-factor scoring
- Amenity accessibility analysis (stores, parks)
- Areas of opportunity for ABCDC outreach (high need + good amenities)

**Action Needed:**
- **Create comprehensive eligibility scoring system** using all available data
- **Add amenity proximity analysis:**
  - Calculate distance to nearest park for each elderly resident
  - Enhance store proximity analysis (already have 3,641 mapped)
  - Create combined amenity accessibility score
- Apply multi-factor criteria (age + income + conditions + violations + amenities)
- Generate final eligibility counts and rankings
- Document methodology and assumptions

---

## ✅ QUESTION 3: What barriers exist in their current living situations (financial, building condition, etc)?

### **YES - FULLY ANSWERABLE**

**Data Available:**
- **Financial Barriers:**
  - Census tract median income (22 tracts)
  - Property values (from assessments)
  
- **Building Condition Barriers:**
  - Interior condition (Poor/Fair/Good/Excellent)
  - Exterior condition (Poor/Fair/Good/Excellent)
  - Property grade
  - Property age
  - 5,391 elderly with housing condition data

- **Property Violations:**
  - 564 elderly with violations (11.0% of mapped)
  - 779 total violation records
  - Open vs closed violations tracked

- **Building Improvements:**
  - 4,318 elderly with permits (84.3% of mapped)
  - 76,290 permit records
  - Permit types and dates

**Analysis Completed:**
- `vw_elderly_housing_conditions_summary` view
- `vw_elderly_eligibility` view with barrier flags
- `elderly_housing_conditions.csv` with full details
- `elderly_violations_one_to_one_summary.csv`

**Deliverables Ready:**
- Analysis of residential tenure, income, ownership status ✅
- Housing condition analysis ✅
- Patterns in building improvements and liens ✅

---

## ⚠️ QUESTION 4: How long have they lived in their current residences? Are they homeowners or renters?

### **PARTIALLY ANSWERABLE**

**Homeowner vs Renter: YES ✅**
- `owner_occ` field in buildings table
- `vw_elderly_tenure` view created
- Analysis shows homeowner vs renter breakdown
- Available for mapped elderly (5,391 residents)

**Length of Residency: ⚠️ PARTIALLY ANSWERABLE**
- **Temporal Analysis Available:**
  - Voter dataset: 2020
  - Property assessment data: 2025
  - **5-year minimum residency** can be inferred for matched residents
  - If elderly person appears in 2020 voter list at address X, and address X exists in 2025 property data, they've been there at least 5 years

**What You Can Provide:**
- **Minimum residency duration:** At least 5 years for residents matched between 2020 voter data and 2025 property data
- **Stability indicator:** Residents who appear in both datasets at same address
- Homeowner vs renter breakdown by:
  - Ward
  - Precinct
  - Age group
  - Income category
- Property ownership information
- Owner-occupied vs non-owner-occupied properties

**Limitations:**
- Cannot determine exact move-in date (could have moved in before 2020)
- Cannot detect moves between 2020-2025 (if they moved and came back, or moved within neighborhood)
- Only provides minimum duration, not exact length
- Does not account for residents who moved away between 2020-2025

**Analysis Approach:**
- Match 2020 voter addresses to 2025 property assessments
- Identify residents with same address in both datasets = minimum 5-year residency
- Combine with building age data for additional context
- Could cross-reference with Registry of Deeds for more precise dates (if available)

---

## ⚠️ QUESTION 5: What would be the impact on the housing market if they transitioned to senior housing?

### **PARTIALLY ANSWERABLE** (Needs Additional Analysis)

**Data Available:**
- Property values (assessments)
- Property types
- Building characteristics
- Elderly homeowner locations
- Property ownership information

**Current Analysis:**
- Can identify properties owned/occupied by elderly
- Can calculate property values
- Can map geographic distribution

**Missing Analysis:**
- **Market impact modeling** (not yet done):
  - Units that would become available
  - Property value impacts
  - Neighborhood-level effects
  - Supply/demand analysis

**What You Can Provide:**
- List of properties that could become available (elderly homeowners)
- Property value distribution
- Geographic concentration of potential transitions
- Building characteristics of affected properties

**What Needs to Be Done:**
- Create analysis of housing market impact
- Model potential unit availability
- Analyze neighborhood-level effects
- Create visualizations for impact assessment

---

## SUMMARY: Questions Answerability

| Question | Status | Completeness |
|----------|--------|--------------|
| 1. Who are elderly and where? | ✅ YES | 100% - Fully answerable |
| 2. How many qualify? | ✅ YES | 90% - Create eligibility criteria from available data |
| 3. What barriers exist? | ✅ YES | 100% - Fully answerable |
| 4. Homeowner/renter? | ✅ YES | 100% - Fully answerable |
| 4. Length of residency? | ⚠️ PARTIAL | 60% - Can infer minimum 5 years (2020-2025) |
| 5. Housing market impact? | ⚠️ PARTIAL | 40% - Need analysis/modeling |

---

## DELIVERABLES STATUS

### ✅ Ready to Deliver:
1. **Elderly resident profiles** - Complete
2. **Maps of elderly concentrations** - Complete
3. **Analysis of residential tenure** - Complete (homeowner/renter)
4. **Income analysis** - Complete
5. **Ownership status** - Complete
6. **Housing condition analysis** - Complete
7. **Building improvements patterns** - Complete (permits)
8. **Property violations/liens** - Complete

### ⚠️ Needs Additional Work:
1. **Affordable housing eligibility** - Create eligibility criteria/scoring system from available data
2. **Length of residency analysis** - Create temporal matching analysis (2020→2025)
3. **Housing market impact modeling** - Need to create analysis
4. **Narrative report** - Need to write based on findings

### 📊 Looker Studio Visualizations:
- **Ready:** 5-7 visualizations can be created with current data
- **Data exported:** 9 key datasets available
- **Views created:** Multiple SQL views ready for Looker Studio

---

## RECOMMENDATIONS

### Immediate Actions:
1. **Create comprehensive eligibility scoring system** for Question 2:
   - Include age + income + conditions + violations (already have)
   - **Add amenity factors:** Store proximity (3,641 already mapped) + Park proximity (need to calculate)
   - Create multi-factor scoring algorithm (0-100 scale)
   - Generate eligibility tiers and priority rankings
2. **Create park proximity analysis:**
   - Calculate distance from each elderly resident to nearest park (1,099 parks available)
   - Similar to existing store proximity analysis
3. **Create temporal residency analysis** (match 2020 voter data to 2025 property data)
4. **Create housing market impact analysis** for Question 5
5. **Write narrative report** summarizing findings
6. **Build Looker Studio dashboards** with available data

### Data Gaps to Address:
1. **Length of residency:** 
   - ✅ Can infer minimum 5-year residency (2020 voter data → 2025 property data)
   - ⚠️ Need to create analysis matching addresses across time periods
   - Could enhance with Registry of Deeds data for exact move-in dates (if available)
   - Building age can provide additional context
   
2. **Affordable housing inventory:**
   - Load ABCDC Affordable Housing Portfolio data (mentioned in project details)
   - Match eligibility criteria to resident data

### What You Have Strong Coverage On:
- ✅ Geographic distribution (excellent)
- ✅ Demographics (excellent)
- ✅ Housing conditions (good - 5,391 mapped)
- ✅ Property violations (good - 564 with violations)
- ✅ Building permits (excellent - 4,318 with permits)
- ✅ Income analysis (good - via census tracts)
- ✅ Homeowner/renter status (good - for mapped residents)
- ✅ Store proximity (good - 3,641 elderly mapped to 55 stores)
- ⚠️ Park proximity (data available - 1,099 parks, but need to calculate distances)
- ✅ Roads/accessibility (141 road segments available)

---

## CONCLUSION

**You can answer all 5 main questions** with current data, with some limitations:

1. ✅ **Fully answerable:** Who/where, barriers, homeowner/renter, eligibility (create criteria)
2. ⚠️ **Partially answerable:** 
   - Market impact (need analysis/modeling)
   - Length of residency (can infer minimum 5 years from 2020-2025 temporal analysis)

**Overall Readiness: ~85%** - Strong foundation, need to:
- Get client eligibility criteria
- Complete market impact analysis
- Write narrative report
- Build Looker Studio dashboards

