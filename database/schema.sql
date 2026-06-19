DROP TABLE IF EXISTS livability_score;
DROP TABLE IF EXISTS city_indicator;
DROP TABLE IF EXISTS city;

CREATE TABLE city (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(50) NOT NULL,
    province VARCHAR(50),
    region VARCHAR(50),
    city_level VARCHAR(50)
);

CREATE TABLE city_indicator (
    id SERIAL PRIMARY KEY,
    city_id INT REFERENCES city(city_id),
    year INT,

    -- 经济机会
    gdp_per_capita FLOAT,
    avg_salary_non_private FLOAT,
    avg_salary_private FLOAT,
    tertiary_industry_ratio FLOAT,
    new_company_count FLOAT,

    -- 生活成本
    house_price FLOAT,
    avg_rent FLOAT,
    house_price_income_ratio_non_private FLOAT,
    house_price_income_ratio_private FLOAT,
    cost_of_living_index FLOAT,

    -- 公共服务
    hospital_count FLOAT,
    university_count FLOAT,
    metro_station_count FLOAT,
    bus_station_count FLOAT,
    shopping_mall_count FLOAT,

    -- 环境质量
    aqi FLOAT,
    pm25 FLOAT,
    good_air_days_ratio FLOAT,
    park_count FLOAT,
    green_coverage_ratio FLOAT,

    -- 城市活力
    population_growth_rate FLOAT,
    young_population_ratio FLOAT,
    retail_sales_total FLOAT,

    -- 气候舒适度
    avg_temperature FLOAT,
    high_temp_days FLOAT,
    low_temp_days FLOAT,
    rainy_days FLOAT,
    humidity FLOAT
);

CREATE TABLE livability_score (
    id SERIAL PRIMARY KEY,
    city_id INT REFERENCES city(city_id),
    year INT,

    economy_score FLOAT,
    cost_score FLOAT,
    service_score FLOAT,
    environment_score FLOAT,
    vitality_score FLOAT,
    climate_score FLOAT,
    total_score FLOAT
);