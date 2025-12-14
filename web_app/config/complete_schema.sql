-- Complete Allston-Brighton ABCDC Database Schema
-- This version includes spatial components using PostGIS

-- Enable PostGIS extension (run as superuser if needed)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ==============================================
-- GEOGRAPHIC BOUNDARIES AND ADMINISTRATIVE UNITS
-- ==============================================

-- Wards table (Ward 21 and 22 for Allston-Brighton)
CREATE TABLE wards (
    ward_id INTEGER PRIMARY KEY,
    ward_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Precincts within wards
CREATE TABLE precincts (
    precinct_id INTEGER PRIMARY KEY,
    ward_id INTEGER NOT NULL,
    precinct_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);

-- Census tracts for income analysis with PostGIS geometry
CREATE TABLE census_tracts (
    tract_id VARCHAR(20) PRIMARY KEY,
    tract_name VARCHAR(200),
    state_code VARCHAR(2),
    county_code VARCHAR(3),
    tract_code VARCHAR(6),
    median_income DECIMAL(12,2),
    geometry GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- PROPERTY AND ASSESSMENT DATA
-- ==============================================

-- Property parcels
CREATE TABLE parcels (
    parcel_id VARCHAR(50) PRIMARY KEY,
    prop_id VARCHAR(50) UNIQUE,
    loc_id VARCHAR(50),
    site_address VARCHAR(200),
    addr_num INTEGER,
    full_street VARCHAR(100),
    location VARCHAR(100),
    city VARCHAR(50),
    zip_code VARCHAR(10),
    zoning VARCHAR(20),
    year_built INTEGER,
    building_area DECIMAL(10,2),
    lot_size DECIMAL(10,2),
    units INTEGER,
    residential_area DECIMAL(10,2),
    style VARCHAR(50),
    num_rooms DECIMAL(5,1),
    lot_units VARCHAR(10),
    stories_num INTEGER,
    stories VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property assessments (multiple assessments per property over time)
CREATE TABLE property_assessments (
    assessment_id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    building_value DECIMAL(12,2),
    land_value DECIMAL(12,2),
    other_value DECIMAL(12,2),
    total_value DECIMAL(12,2),
    last_sale_date DATE,
    last_sale_price DECIMAL(12,2),
    use_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);

-- Property ownership
CREATE TABLE property_ownership (
    ownership_id SERIAL PRIMARY KEY,
    parcel_id VARCHAR(50) NOT NULL,
    owner_name VARCHAR(200),
    owner_address VARCHAR(200),
    owner_city VARCHAR(50),
    owner_state VARCHAR(10),
    owner_zip VARCHAR(10),
    owner_country VARCHAR(50),
    last_sale_book VARCHAR(20),
    last_sale_page VARCHAR(20),
    registration_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);

-- ==============================================
-- BUILDING DATA
-- ==============================================

-- Buildings table for detailed building information
CREATE TABLE buildings (
    struct_id VARCHAR(50) PRIMARY KEY,
    parcel_id VARCHAR(50),
    suffix VARCHAR(10),
    pid VARCHAR(50),
    st_num VARCHAR(20),
    st_num2 VARCHAR(20),
    st_name VARCHAR(100),
    unit_num VARCHAR(20),
    city VARCHAR(50),
    zip_code VARCHAR(10),
    owner_occ VARCHAR(10),
    owner VARCHAR(200),
    mail_addressee VARCHAR(200),
    mail_street_address VARCHAR(200),
    mail_city VARCHAR(50),
    mail_state VARCHAR(10),
    mail_zip_code VARCHAR(10),
    bldg_type VARCHAR(50),
    total_value DECIMAL(12,2),
    gross_tax DECIMAL(12,2),
    yr_built INTEGER,
    yr_remodel INTEGER,
    structure_class VARCHAR(50),
    bed_rms DECIMAL(5,1),
    full_bth DECIMAL(5,1),
    hlf_bth DECIMAL(5,1),
    kitchens DECIMAL(5,1),
    tt_rms DECIMAL(5,1),
    res_units INTEGER,
    com_units INTEGER,
    rc_units INTEGER,
    land_sf DECIMAL(12,2),
    gross_area DECIMAL(12,2),
    living_area DECIMAL(12,2),
    land_value DECIMAL(12,2),
    bldg_value DECIMAL(12,2),
    sfyi_value DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parcel_id) REFERENCES parcels(parcel_id)
);

-- ==============================================
-- VOTER AND RESIDENT DATA
-- ==============================================

-- Registered voters
CREATE TABLE voters (
    res_id VARCHAR(50) PRIMARY KEY,
    last_name VARCHAR(100),
    first_name VARCHAR(100),
    date_of_birth DATE,
    occupation VARCHAR(100),
    street_number INTEGER,
    street_suffix VARCHAR(10),
    street_name VARCHAR(100),
    apartment VARCHAR(20),
    zip_code VARCHAR(10),
    ward_id INTEGER,
    precinct_id INTEGER,
    full_address VARCHAR(200),
    normalized_address VARCHAR(200),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_elderly BOOLEAN,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id),
    FOREIGN KEY (precinct_id) REFERENCES precincts(precinct_id)
);

-- ==============================================
-- INFRASTRUCTURE AND AMENITIES
-- ==============================================

-- Major roads
CREATE TABLE roads (
    road_id SERIAL PRIMARY KEY,
    road_name VARCHAR(100),
    road_type VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parks and open space
CREATE TABLE parks_openspace (
    park_id SERIAL PRIMARY KEY,
    park_name VARCHAR(200),
    park_type VARCHAR(100),
    area_sqft DECIMAL(15,2),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Retail stores and grocery locations
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    record_id VARCHAR(50) UNIQUE,
    store_name VARCHAR(200),
    store_type VARCHAR(100),
    street_number VARCHAR(20),
    street_name VARCHAR(100),
    additional_address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(10),
    zip_code VARCHAR(10),
    zip4 VARCHAR(10),
    county VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    authorization_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Voter to nearby stores mapping
CREATE TABLE voter_store_nearby (
    mapping_id SERIAL PRIMARY KEY,
    res_id VARCHAR(50) NOT NULL,
    store_id INTEGER NOT NULL,
    distance_meters DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (res_id) REFERENCES voters(res_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    UNIQUE(res_id, store_id)
);

-- ==============================================
-- ANALYSIS AND SUMMARY TABLES
-- ==============================================

-- Ward-level elderly analysis
CREATE TABLE ward_elderly_analysis (
    analysis_id SERIAL PRIMARY KEY,
    ward_id INTEGER NOT NULL,
    elderly_count INTEGER,
    mean_age DECIMAL(5,2),
    median_age DECIMAL(5,2),
    min_age INTEGER,
    max_age INTEGER,
    analysis_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);

-- Precinct-level elderly analysis
CREATE TABLE precinct_elderly_analysis (
    analysis_id SERIAL PRIMARY KEY,
    ward_id INTEGER NOT NULL,
    precinct_id INTEGER NOT NULL,
    elderly_count INTEGER,
    mean_age DECIMAL(5,2),
    analysis_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id),
    FOREIGN KEY (precinct_id) REFERENCES precincts(precinct_id)
);

-- Street-level elderly analysis
CREATE TABLE street_elderly_analysis (
    analysis_id SERIAL PRIMARY KEY,
    street_name VARCHAR(100),
    ward_id INTEGER,
    elderly_count INTEGER,
    mean_age DECIMAL(5,2),
    analysis_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

-- Common query indexes
CREATE INDEX idx_voters_elderly ON voters (is_elderly) WHERE is_elderly = true;
CREATE INDEX idx_voters_ward_precinct ON voters (ward_id, precinct_id);
CREATE INDEX idx_voters_street ON voters (street_name);
CREATE INDEX idx_voters_coords ON voters (latitude, longitude);
CREATE INDEX idx_assessments_parcel_year ON property_assessments (parcel_id, fiscal_year);
CREATE INDEX idx_parcels_zip ON parcels (zip_code);
CREATE INDEX idx_parcels_coords ON parcels (latitude, longitude);
CREATE INDEX idx_parcels_owner ON property_ownership (owner_name);
CREATE INDEX idx_buildings_parcel ON buildings (parcel_id);
CREATE INDEX idx_buildings_owner ON buildings (owner);
CREATE INDEX idx_buildings_address ON buildings (st_name, st_num);
CREATE INDEX idx_stores_coords ON stores (latitude, longitude);
CREATE INDEX idx_stores_type ON stores (store_type);
CREATE INDEX idx_voter_store_nearby_voter ON voter_store_nearby (res_id);
CREATE INDEX idx_voter_store_nearby_store ON voter_store_nearby (store_id);
CREATE INDEX idx_voter_store_nearby_distance ON voter_store_nearby (distance_meters);

-- Census tracts indexes
CREATE INDEX idx_census_tracts_geoid ON census_tracts(tract_id);
CREATE INDEX idx_census_tracts_geometry ON census_tracts USING GIST(geometry);
CREATE INDEX idx_census_tracts_income ON census_tracts(median_income);
CREATE INDEX idx_census_tracts_state_county ON census_tracts(state_code, county_code);

-- ==============================================
-- VIEWS FOR COMMON QUERIES
-- ==============================================

-- Elderly population by ward with demographics
CREATE VIEW elderly_by_ward AS
SELECT 
    w.ward_id,
    w.ward_name,
    COUNT(v.res_id) as elderly_count,
    AVG(v.age) as mean_age,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY v.age) as median_age,
    MIN(v.age) as min_age,
    MAX(v.age) as max_age,
    COUNT(CASE WHEN v.age BETWEEN 62 AND 69 THEN 1 END) as age_62_69,
    COUNT(CASE WHEN v.age BETWEEN 70 AND 79 THEN 1 END) as age_70_79,
    COUNT(CASE WHEN v.age BETWEEN 80 AND 89 THEN 1 END) as age_80_89,
    COUNT(CASE WHEN v.age >= 90 THEN 1 END) as age_90_plus
FROM wards w
LEFT JOIN voters v ON w.ward_id = v.ward_id AND v.is_elderly = true
GROUP BY w.ward_id, w.ward_name;

-- Property values by ward
CREATE VIEW property_values_by_ward AS
SELECT 
    w.ward_id,
    w.ward_name,
    COUNT(p.parcel_id) as total_properties,
    AVG(pa.total_value) as avg_property_value,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pa.total_value) as median_property_value,
    MIN(pa.total_value) as min_property_value,
    MAX(pa.total_value) as max_property_value,
    COUNT(CASE WHEN pa.total_value > 1000000 THEN 1 END) as high_value_properties
FROM wards w
LEFT JOIN parcels p ON w.ward_id = 21 OR w.ward_id = 22  -- Simplified for now
LEFT JOIN property_assessments pa ON p.parcel_id = pa.parcel_id 
    AND pa.fiscal_year = (SELECT MAX(fiscal_year) FROM property_assessments)
GROUP BY w.ward_id, w.ward_name;

-- Elderly density by precinct
CREATE VIEW elderly_density_by_precinct AS
SELECT 
    p.precinct_id,
    p.ward_id,
    COUNT(v.res_id) as elderly_count,
    COUNT(v.res_id) as total_voters,
    ROUND(COUNT(v.res_id) * 100.0 / NULLIF(COUNT(v.res_id), 0), 2) as elderly_percentage
FROM precincts p
LEFT JOIN voters v ON p.precinct_id = v.precinct_id
GROUP BY p.precinct_id, p.ward_id;

-- ==============================================
-- FUNCTIONS FOR ANALYSIS
-- ==============================================

-- Function to calculate elderly population within a buffer of a point
CREATE OR REPLACE FUNCTION elderly_within_buffer(
    center_lat DECIMAL(10,8),
    center_lon DECIMAL(11,8),
    buffer_meters INTEGER
)
RETURNS TABLE (
    res_id VARCHAR(50),
    distance_meters DECIMAL(10,2),
    age INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.res_id,
        -- Simple distance calculation (not perfect but works for small areas)
        SQRT(POWER(69.1 * (v.latitude - center_lat), 2) + 
             POWER(69.1 * (center_lon - v.longitude) * COS(v.latitude / 57.3), 2)) * 1609.34 as distance_meters,
        v.age
    FROM voters v
    WHERE v.is_elderly = true
    AND v.latitude IS NOT NULL 
    AND v.longitude IS NOT NULL
    AND SQRT(POWER(69.1 * (v.latitude - center_lat), 2) + 
             POWER(69.1 * (center_lon - v.longitude) * COS(v.latitude / 57.3), 2)) * 1609.34 <= buffer_meters
    ORDER BY distance_meters;
END;
$$ LANGUAGE plpgsql;

-- Function to find properties near elderly residents
CREATE OR REPLACE FUNCTION properties_near_elderly(
    elderly_threshold INTEGER DEFAULT 10,
    max_distance_meters INTEGER DEFAULT 500
)
RETURNS TABLE (
    parcel_id VARCHAR(50),
    property_address VARCHAR(200),
    nearby_elderly_count BIGINT,
    avg_elderly_age DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.parcel_id,
        p.site_address,
        COUNT(v.res_id) as nearby_elderly_count,
        AVG(v.age) as avg_elderly_age
    FROM parcels p
    JOIN voters v ON p.latitude IS NOT NULL 
        AND v.latitude IS NOT NULL
        AND SQRT(POWER(69.1 * (p.latitude - v.latitude), 2) + 
                 POWER(69.1 * (v.longitude - p.longitude) * COS(p.latitude / 57.3), 2)) * 1609.34 <= max_distance_meters
    WHERE v.is_elderly = true
    GROUP BY p.parcel_id, p.site_address
    HAVING COUNT(v.res_id) >= elderly_threshold
    ORDER BY nearby_elderly_count DESC;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- SAMPLE DATA
-- ==============================================

-- Insert sample wards
INSERT INTO wards (ward_id, ward_name) VALUES 
(21, 'Allston'),
(22, 'Brighton');

-- Insert sample precincts
INSERT INTO precincts (precinct_id, ward_id, precinct_name) VALUES 
(1, 21, 'Precinct 1'),
(2, 21, 'Precinct 2'),
(3, 22, 'Precinct 3'),
(4, 22, 'Precinct 4');

-- Insert sample voters with coordinates
INSERT INTO voters (res_id, last_name, first_name, date_of_birth, occupation, street_number, street_name, zip_code, ward_id, precinct_id, latitude, longitude, is_elderly, age) VALUES 
('TEST001', 'Smith', 'John', '1950-01-01', 'Retired', 123, 'Main St', '02134', 21, 1, 42.3500, -71.1400, true, 74),
('TEST002', 'Johnson', 'Mary', '1960-05-15', 'Teacher', 456, 'Oak Ave', '02134', 21, 1, 42.3510, -71.1410, true, 64),
('TEST003', 'Williams', 'Robert', '1945-12-10', 'Engineer', 789, 'Pine St', '02135', 22, 3, 42.3520, -71.1420, true, 79),
('TEST004', 'Brown', 'Sarah', '1980-03-20', 'Doctor', 321, 'Elm St', '02135', 22, 3, 42.3530, -71.1430, false, 44);

-- Insert sample properties with coordinates
INSERT INTO parcels (parcel_id, site_address, city, zip_code, year_built, building_area, latitude, longitude) VALUES 
('PARCEL001', '123 Main St', 'Boston', '02134', 1950, 1500.0, 42.3501, -71.1401),
('PARCEL002', '456 Oak Ave', 'Boston', '02134', 1960, 2000.0, 42.3511, -71.1411),
('PARCEL003', '789 Pine St', 'Boston', '02135', 1970, 1800.0, 42.3521, -71.1421);

-- Insert sample property assessments
INSERT INTO property_assessments (parcel_id, fiscal_year, total_value, building_value, land_value) VALUES 
('PARCEL001', 2023, 500000.0, 400000.0, 100000.0),
('PARCEL002', 2023, 750000.0, 600000.0, 150000.0),
('PARCEL003', 2023, 650000.0, 500000.0, 150000.0);

-- Insert sample property ownership
INSERT INTO property_ownership (parcel_id, owner_name, owner_city, owner_state) VALUES 
('PARCEL001', 'John Smith', 'Boston', 'MA'),
('PARCEL002', 'Mary Johnson', 'Boston', 'MA'),
('PARCEL003', 'Robert Williams', 'Boston', 'MA');

-- Insert sample roads
INSERT INTO roads (road_name, road_type, latitude, longitude) VALUES 
('Commonwealth Avenue', 'Major Road', 42.3500, -71.1400),
('Beacon Street', 'Major Road', 42.3510, -71.1410),
('Brighton Avenue', 'Major Road', 42.3520, -71.1420);

-- Insert sample parks
INSERT INTO parks_openspace (park_name, park_type, area_sqft, latitude, longitude) VALUES 
('Allston Community Park', 'Community Park', 50000.0, 42.3505, -71.1405),
('Brighton Recreation Area', 'Recreation', 75000.0, 42.3515, -71.1415);
