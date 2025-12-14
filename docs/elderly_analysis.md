# Elderly Analysis Data Files

This folder contains analysis results for mapped elderly residents with one-to-one parcel mapping.

## Files

### 1. `elderly_housing_conditions.csv`
- **Description**: Housing conditions for all mapped elderly residents
- **Rows**: 12,470 (includes multiple mappings per person)
- **Unique elderly**: 5,391
- **Contains**: Elderly demographics, building info, parcel conditions (interior/exterior condition, grade, property type, etc.)

### 2. `elderly_permits_one_to_one.csv`
- **Description**: Detailed building permits data for elderly with exactly 1 parcel_id
- **Rows**: 76,290 permit records
- **Unique elderly**: 5,121 (one-to-one parcel mapping)
- **Contains**: Full permit details (permit number, work type, description, dates, fees, etc.) matched to elderly residents

### 3. `elderly_permits_one_to_one_summary.csv`
- **Description**: Summary of permits per elderly person
- **Rows**: 5,121 (one per elderly person)
- **Contains**: res_id, name, age, ward, precinct, parcel_id, has_permits (boolean), permit_count

### 4. `elderly_violations_one_to_one.csv`
- **Description**: Detailed property violations data for elderly with exactly 1 parcel_id
- **Rows**: 779 violation records
- **Unique elderly**: 564 matched
- **Contains**: Full violation details (case number, description, status, dates, etc.) matched to elderly residents

### 5. `elderly_violations_one_to_one_summary.csv`
- **Description**: Summary of violations per elderly person
- **Rows**: 5,121 (one per elderly person)
- **Contains**: res_id, name, age, ward, precinct, parcel_id, address, has_violations (boolean), total_violations, open_violations, closed_violations

## Statistics

- **Total elderly with one-to-one mapping**: 5,121
- **Elderly with permits**: 4,318 (84.3%)
- **Elderly with violations**: 564 (11.0%)
- **Total permits matched**: 76,290
- **Total violations matched**: 779

## Notes

- All files use one-to-one parcel mapping (elderly with exactly 1 parcel_id)
- Permits and violations are building/parcel-level, not resident-specific
- Address matching used normalization (AV vs AVE, ST vs STREET, etc.)

