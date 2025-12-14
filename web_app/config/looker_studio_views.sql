-- SQL Views for Looker Studio Visualizations
-- Run these in your Cloud SQL database to create views for easy Looker Studio connections

-- ==============================================
-- VIEW 1: Elderly Resident Concentration
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_resident_map AS
SELECT 
    v.res_id,
    v.first_name,
    v.last_name,
    v.age,
    CASE 
        WHEN v.age BETWEEN 62 AND 69 THEN '62-69'
        WHEN v.age BETWEEN 70 AND 79 THEN '70-79'
        WHEN v.age BETWEEN 80 AND 89 THEN '80-89'
        ELSE '90+'
    END as age_group,
    v.latitude,
    v.longitude,
    v.ward_id,
    v.precinct_id,
    v.street_number || ' ' || v.street_name as address,
    v.apartment,
    p.precinct_name
FROM voters v
LEFT JOIN precincts p ON v.precinct_id = p.precinct_id
WHERE v.is_elderly = true
AND v.latitude IS NOT NULL
AND v.longitude IS NOT NULL;

-- ==============================================
-- VIEW 2: Housing Eligibility and Barriers
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_eligibility AS
SELECT 
    v.res_id,
    v.first_name,
    v.last_name,
    v.age,
    v.ward_id,
    v.precinct_id,
    COALESCE(ct.median_income, 0) as median_income,
    CASE 
        WHEN COALESCE(ct.median_income, 0) < 50000 THEN 'Low Income'
        WHEN COALESCE(ct.median_income, 0) < 75000 THEN 'Moderate Income'
        ELSE 'Higher Income'
    END as income_category,
    CASE 
        WHEN COALESCE(ct.median_income, 0) < 50000 THEN 'Eligible'
        WHEN COALESCE(ct.median_income, 0) < 75000 THEN 'Potentially Eligible'
        ELSE 'Not Eligible'
    END as eligibility_status,
    ehc.interior_condition,
    ehc.exterior_condition,
    ehc.grade,
    CASE 
        WHEN ehc.interior_condition IN ('Poor', 'Fair') OR 
             ehc.exterior_condition IN ('Poor', 'Fair') OR
             ehc.grade IN ('Poor', 'Fair') THEN true
        ELSE false
    END as has_poor_conditions,
    COALESCE(evs.open_violations, 0) as open_violations,
    CASE 
        WHEN COALESCE(evs.open_violations, 0) > 0 THEN true
        ELSE false
    END as has_violations,
    CASE 
        WHEN COALESCE(ct.median_income, 0) < 50000 OR
             (ehc.interior_condition IN ('Poor', 'Fair') OR 
              ehc.exterior_condition IN ('Poor', 'Fair')) OR
             COALESCE(evs.open_violations, 0) > 0 THEN true
        ELSE false
    END as has_barriers
FROM voters v
LEFT JOIN elderly_housing_conditions ehc ON v.res_id = ehc.res_id
LEFT JOIN elderly_violations_one_to_one_summary evs ON v.res_id = evs.res_id
LEFT JOIN precinct_census_tract_mapping pctm ON v.precinct_id = pctm.precinct_id
LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
WHERE v.is_elderly = true
GROUP BY v.res_id, v.first_name, v.last_name, v.age, v.ward_id, v.precinct_id,
         ct.median_income, ehc.interior_condition, ehc.exterior_condition, 
         ehc.grade, evs.open_violations;

-- ==============================================
-- VIEW 3: Residential Tenure and Ownership
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_tenure AS
SELECT 
    v.res_id,
    v.first_name,
    v.last_name,
    v.age,
    v.ward_id,
    v.precinct_id,
    p.precinct_name,
    b.owner,
    b.owner_occ,
    CASE 
        WHEN b.owner_occ = 'Y' THEN 'Homeowner'
        WHEN b.owner IS NOT NULL AND b.owner_occ != 'Y' THEN 'Owner (Not Occupied)'
        ELSE 'Renter'
    END as tenure_status,
    b.total_value as property_value,
    CASE 
        WHEN b.total_value < 500000 THEN 'Low Value'
        WHEN b.total_value < 1000000 THEN 'Moderate Value'
        ELSE 'High Value'
    END as value_category
FROM voters v
LEFT JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
LEFT JOIN buildings b ON vbm.struct_id = b.struct_id
LEFT JOIN precincts p ON v.precinct_id = p.precinct_id
WHERE v.is_elderly = true
GROUP BY v.res_id, v.first_name, v.last_name, v.age, v.ward_id, v.precinct_id,
         p.precinct_name, b.owner, b.owner_occ, b.total_value;

-- ==============================================
-- VIEW 4: Housing Conditions Summary
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_housing_conditions_summary AS
SELECT 
    res_id,
    first_name,
    last_name,
    age,
    ward_id,
    precinct_id,
    parcel_id,
    property_type,
    year_built,
    property_age,
    interior_condition,
    exterior_condition,
    grade,
    interior_finish,
    exterior_finish,
    foundation,
    roof_cover,
    roof_structure,
    ac_type,
    heat_type,
    living_area_sqft,
    lot_size_sqft,
    fy2025_total_assessed_value_numeric as property_value,
    CASE 
        WHEN interior_condition IN ('Poor', 'Fair') OR 
             exterior_condition IN ('Poor', 'Fair') OR
             grade IN ('Poor', 'Fair') THEN 'Poor Condition'
        WHEN interior_condition = 'Good' AND 
             exterior_condition = 'Good' AND
             grade = 'Good' THEN 'Good Condition'
        ELSE 'Average Condition'
    END as overall_condition
FROM elderly_housing_conditions
WHERE res_id IN (
    SELECT DISTINCT res_id 
    FROM elderly_housing_conditions 
    WHERE res_id IS NOT NULL
    GROUP BY res_id 
    HAVING COUNT(*) = 1
);

-- ==============================================
-- VIEW 5: Building Permits Summary
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_permits_summary AS
SELECT 
    res_id,
    first_name,
    last_name,
    age,
    ward_id,
    precinct_id,
    parcel_id,
    permitnumber,
    worktype,
    permittypedescr,
    description,
    applicant,
    declared_valuation,
    total_fees,
    issued_date,
    expiration_date,
    status,
    CASE 
        WHEN issued_date >= '2020-01-01' THEN true
        ELSE false
    END as is_recent,
    EXTRACT(YEAR FROM issued_date) as permit_year
FROM elderly_permits_one_to_one
WHERE permitnumber IS NOT NULL;

-- ==============================================
-- VIEW 6: Property Violations Summary
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_violations_summary AS
SELECT 
    res_id,
    first_name,
    last_name,
    age,
    ward_id,
    precinct_id,
    parcel_id,
    case_no,
    status,
    description,
    violation_stno,
    violation_street,
    violation_city,
    violation_zip,
    status_dttm,
    CASE 
        WHEN status = 'Open' THEN true
        ELSE false
    END as is_open,
    CASE 
        WHEN description ILIKE '%unsafe%' OR description ILIKE '%dangerous%' THEN 'Safety Issue'
        WHEN description ILIKE '%maintenance%' THEN 'Maintenance'
        WHEN description ILIKE '%permit%' THEN 'Permit Issue'
        ELSE 'Other'
    END as violation_category
FROM elderly_violations_one_to_one
WHERE case_no IS NOT NULL;

-- ==============================================
-- VIEW 7: Income Analysis by Precinct
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_income_by_precinct AS
SELECT 
    p.precinct_id,
    p.precinct_name,
    p.ward_id,
    COUNT(DISTINCT v.res_id) as elderly_count,
    AVG(v.age) as avg_age,
    AVG(ct.median_income) as avg_median_income,
    MIN(ct.median_income) as min_median_income,
    MAX(ct.median_income) as max_median_income,
    CASE 
        WHEN AVG(ct.median_income) < 50000 THEN 'Low Income'
        WHEN AVG(ct.median_income) < 75000 THEN 'Moderate Income'
        ELSE 'Higher Income'
    END as income_category,
    COUNT(DISTINCT CASE WHEN ct.median_income < 50000 THEN v.res_id END) as low_income_elderly,
    COUNT(DISTINCT CASE WHEN ct.median_income >= 50000 AND ct.median_income < 75000 THEN v.res_id END) as moderate_income_elderly,
    COUNT(DISTINCT CASE WHEN ct.median_income >= 75000 THEN v.res_id END) as higher_income_elderly
FROM precincts p
LEFT JOIN voters v ON p.precinct_id = v.precinct_id AND v.is_elderly = true
LEFT JOIN precinct_census_tract_mapping pctm ON p.precinct_id = pctm.precinct_id
LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
GROUP BY p.precinct_id, p.precinct_name, p.ward_id;

-- ==============================================
-- VIEW 8: Outreach Priority Areas
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_outreach_priority AS
SELECT 
    p.precinct_id,
    p.precinct_name,
    p.ward_id,
    COUNT(DISTINCT v.res_id) as elderly_count,
    AVG(ct.median_income) as avg_median_income,
    COUNT(DISTINCT CASE WHEN evs.open_violations > 0 THEN v.res_id END) as elderly_with_violations,
    COUNT(DISTINCT CASE WHEN ehc.interior_condition IN ('Poor', 'Fair') OR 
                           ehc.exterior_condition IN ('Poor', 'Fair') THEN v.res_id END) as elderly_poor_conditions,
    COUNT(DISTINCT CASE WHEN ct.median_income < 50000 THEN v.res_id END) as low_income_elderly,
    -- Priority Score Calculation
    (COUNT(DISTINCT v.res_id) * 0.4) + 
    (CASE WHEN AVG(ct.median_income) < 50000 THEN 30 ELSE 0 END) +
    (COUNT(DISTINCT CASE WHEN evs.open_violations > 0 THEN v.res_id END) * 0.2) +
    (COUNT(DISTINCT CASE WHEN ehc.interior_condition IN ('Poor', 'Fair') OR 
                                ehc.exterior_condition IN ('Poor', 'Fair') THEN v.res_id END) * 0.1) as priority_score
FROM precincts p
LEFT JOIN voters v ON p.precinct_id = v.precinct_id AND v.is_elderly = true
LEFT JOIN elderly_violations_one_to_one_summary evs ON v.res_id = evs.res_id
LEFT JOIN elderly_housing_conditions ehc ON v.res_id = ehc.res_id
LEFT JOIN precinct_census_tract_mapping pctm ON p.precinct_id = pctm.precinct_id
LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
GROUP BY p.precinct_id, p.precinct_name, p.ward_id
HAVING COUNT(DISTINCT v.res_id) > 0
ORDER BY priority_score DESC;

-- ==============================================
-- VIEW 9: Combined Elderly Profile
-- ==============================================
CREATE OR REPLACE VIEW vw_elderly_complete_profile AS
SELECT 
    v.res_id,
    v.first_name,
    v.last_name,
    v.age,
    CASE 
        WHEN v.age BETWEEN 62 AND 69 THEN '62-69'
        WHEN v.age BETWEEN 70 AND 79 THEN '70-79'
        WHEN v.age BETWEEN 80 AND 89 THEN '80-89'
        ELSE '90+'
    END as age_group,
    v.ward_id,
    v.precinct_id,
    v.latitude,
    v.longitude,
    v.street_number || ' ' || v.street_name as address,
    COALESCE(eps.has_permits, false) as has_permits,
    COALESCE(eps.permit_count, 0) as permit_count,
    COALESCE(evs.has_violations, false) as has_violations,
    COALESCE(evs.total_violations, 0) as total_violations,
    COALESCE(evs.open_violations, 0) as open_violations,
    ehc.property_type,
    ehc.interior_condition,
    ehc.exterior_condition,
    ehc.grade,
    ehc.property_age,
    ehc.fy2025_total_assessed_value_numeric as property_value,
    COALESCE(ct.median_income, 0) as median_income,
    CASE 
        WHEN COALESCE(ct.median_income, 0) < 50000 THEN 'Low Income'
        WHEN COALESCE(ct.median_income, 0) < 75000 THEN 'Moderate Income'
        ELSE 'Higher Income'
    END as income_category,
    b.owner_occ,
    CASE 
        WHEN b.owner_occ = 'Y' THEN 'Homeowner'
        ELSE 'Renter'
    END as tenure_status
FROM voters v
LEFT JOIN elderly_permits_one_to_one_summary eps ON v.res_id = eps.res_id
LEFT JOIN elderly_violations_one_to_one_summary evs ON v.res_id = evs.res_id
LEFT JOIN elderly_housing_conditions ehc ON v.res_id = ehc.res_id
LEFT JOIN voters_buildings_map vbm ON v.res_id = vbm.res_id
LEFT JOIN buildings b ON vbm.struct_id = b.struct_id
LEFT JOIN precinct_census_tract_mapping pctm ON v.precinct_id = pctm.precinct_id
LEFT JOIN census_tracts ct ON pctm.tract_id = ct.tract_id
WHERE v.is_elderly = true
GROUP BY v.res_id, v.first_name, v.last_name, v.age, v.ward_id, v.precinct_id,
         v.latitude, v.longitude, v.street_number, v.street_name,
         eps.has_permits, eps.permit_count, evs.has_violations, evs.total_violations,
         evs.open_violations, ehc.property_type, ehc.interior_condition,
         ehc.exterior_condition, ehc.grade, ehc.property_age,
         ehc.fy2025_total_assessed_value_numeric, ct.median_income, b.owner_occ;

