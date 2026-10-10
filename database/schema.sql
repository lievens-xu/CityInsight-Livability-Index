-- PostgreSQL initialization for a fresh database. Do not drop existing user data.
-- Existing installations require an explicit migration before applying new constraints.
BEGIN;
CREATE TABLE IF NOT EXISTS city (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL UNIQUE,
    province VARCHAR(50),
    region VARCHAR(50),
    city_level VARCHAR(50)
);
CREATE TABLE IF NOT EXISTS city_indicator (
    id SERIAL PRIMARY KEY,
    city_id INT NOT NULL REFERENCES city(city_id),
    year INT NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    gdp_per_capita NUMERIC CHECK (gdp_per_capita > 0),
    avg_salary_non_private NUMERIC CHECK (avg_salary_non_private > 0),
    avg_salary_private NUMERIC CHECK (avg_salary_private > 0),
    tertiary_industry_ratio NUMERIC CHECK (tertiary_industry_ratio BETWEEN 0 AND 100),
    house_price NUMERIC CHECK (house_price > 0),
    rent_per_sqm NUMERIC CHECK (rent_per_sqm > 0),
    house_price_income_ratio_non_private NUMERIC CHECK (house_price_income_ratio_non_private >= 0),
    house_price_income_ratio_private NUMERIC CHECK (house_price_income_ratio_private >= 0),
    hospital_count INT CHECK (hospital_count >= 0),
    university_count INT CHECK (university_count >= 0),
    rail_station_count INT CHECK (rail_station_count >= 0),
    pm25 NUMERIC CHECK (pm25 >= 0),
    good_air_days_ratio NUMERIC CHECK (good_air_days_ratio BETWEEN 0 AND 100),
    park_count INT CHECK (park_count >= 0),
    UNIQUE (city_id, year)
);
CREATE TABLE IF NOT EXISTS livability_score (
    id SERIAL PRIMARY KEY,
    city_id INT NOT NULL REFERENCES city(city_id),
    year INT NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    economy_score NUMERIC CHECK (economy_score BETWEEN 0 AND 100),
    cost_score NUMERIC CHECK (cost_score BETWEEN 0 AND 100),
    service_score NUMERIC CHECK (service_score BETWEEN 0 AND 100),
    environment_score NUMERIC CHECK (environment_score BETWEEN 0 AND 100),
    total_score NUMERIC CHECK (total_score BETWEEN 0 AND 100),
    coverage NUMERIC NOT NULL CHECK (coverage BETWEEN 0 AND 1),
    rank INT CHECK (rank > 0),
    status TEXT NOT NULL CHECK (status IN ('provisional', 'insufficient_data')),
    model_version TEXT NOT NULL,
    UNIQUE (city_id, year, model_version),
    CHECK ((status = 'provisional' AND total_score IS NOT NULL AND rank IS NOT NULL)
        OR (status = 'insufficient_data' AND total_score IS NULL AND rank IS NULL))
);
CREATE TABLE IF NOT EXISTS indicator_source (
    city_id INT NOT NULL REFERENCES city(city_id),
    year INT NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    indicator TEXT NOT NULL,
    value NUMERIC,
    unit TEXT NOT NULL,
    source_name TEXT,
    source_url TEXT,
    source_type TEXT,
    notes TEXT,
    verification_status TEXT NOT NULL DEFAULT 'pending' CHECK (verification_status IN ('verified', 'pending')),
    verified_on DATE,
    PRIMARY KEY (city_id, year, indicator)
);
COMMIT;
