-- =====================================================
-- AdSpendIQ - MySQL Star Schema ERD
-- =====================================================
-- This script creates the complete star schema for the AdSpendIQ project
-- Run this in MySQL Workbench to generate the ERD diagram
-- =====================================================

-- Create the database
CREATE DATABASE IF NOT EXISTS adspendiq;
USE adspendiq;

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- 1. dim_campaigns - Campaign dimension table
CREATE TABLE dim_campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_type VARCHAR(100) NOT NULL,
    campaign_records INT DEFAULT 0,
    first_seen_date DATE,
    last_seen_date DATE,
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    campaign_ctr DECIMAL(6,4) DEFAULT 0.0000,
    campaign_cpc DECIMAL(8,2) DEFAULT 0.00,
    campaign_roas DECIMAL(8,4) DEFAULT 0.0000,
    budget_tier ENUM('Low Budget', 'Medium Budget', 'High Budget') DEFAULT 'Low Budget',
    effectiveness_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_campaign_type (campaign_type),
    INDEX idx_budget_tier (budget_tier),
    INDEX idx_effectiveness_score (effectiveness_score)
);

-- 2. dim_platforms - Platform dimension table
CREATE TABLE dim_platforms (
    platform_id VARCHAR(50) PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL,
    platform_category ENUM('Major', 'Growing', 'Emerging') DEFAULT 'Emerging',
    platform_region ENUM('Global', 'Regional') DEFAULT 'Regional',
    platform_features TEXT,
    performance_tier ENUM('Tier 1', 'Tier 2', 'Tier 3') DEFAULT 'Tier 3',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _model_type VARCHAR(20) DEFAULT 'dimension',
    
    INDEX idx_platform_category (platform_category),
    INDEX idx_performance_tier (performance_tier),
    INDEX idx_platform_region (platform_region)
);

-- 3. dim_geography - Geography dimension table
CREATE TABLE dim_geography (
    geo_id VARCHAR(10) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    continent ENUM('North America', 'South America', 'Europe', 'Asia-Pacific', 'Asia', 'Other') DEFAULT 'Other',
    market_type ENUM('Developed', 'Emerging', 'Developing') DEFAULT 'Developing',
    region VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'USD',
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _model_type VARCHAR(20) DEFAULT 'dimension',
    
    INDEX idx_continent (continent),
    INDEX idx_market_type (market_type),
    INDEX idx_region (region),
    INDEX idx_currency (currency)
);

-- 4. dim_devices - Device dimension table
CREATE TABLE dim_devices (
    device_id VARCHAR(50) PRIMARY KEY,
    device_type VARCHAR(100) NOT NULL,
    device_family ENUM('Mobile', 'Desktop', 'Other') DEFAULT 'Other',
    is_mobile BOOLEAN DEFAULT FALSE,
    device_records INT DEFAULT 0,
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    first_seen_date DATE,
    last_seen_date DATE,
    device_ctr DECIMAL(6,4) DEFAULT 0.0000,
    device_cpc DECIMAL(8,2) DEFAULT 0.00,
    device_roas DECIMAL(8,4) DEFAULT 0.0000,
    performance_tier ENUM('Low Performance', 'Medium Performance', 'High Performance') DEFAULT 'Low Performance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_device_type (device_type),
    INDEX idx_device_family (device_family),
    INDEX idx_is_mobile (is_mobile),
    INDEX idx_performance_tier (performance_tier)
);

-- 5. dim_ad_formats - Ad format dimension table
CREATE TABLE dim_ad_formats (
    ad_format_id VARCHAR(50) PRIMARY KEY,
    ad_format_type VARCHAR(100) NOT NULL,
    format_category ENUM('Video', 'Static', 'Interactive', 'Other') DEFAULT 'Other',
    is_video BOOLEAN DEFAULT FALSE,
    is_interactive BOOLEAN DEFAULT FALSE,
    format_records INT DEFAULT 0,
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    first_seen_date DATE,
    last_seen_date DATE,
    format_ctr DECIMAL(6,4) DEFAULT 0.0000,
    format_cpc DECIMAL(8,2) DEFAULT 0.00,
    format_roas DECIMAL(8,4) DEFAULT 0.0000,
    performance_tier ENUM('Low Performance', 'Medium Performance', 'High Performance') DEFAULT 'Low Performance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ad_format_type (ad_format_type),
    INDEX idx_format_category (format_category),
    INDEX idx_is_video (is_video),
    INDEX idx_performance_tier (performance_tier)
);

-- 6. dim_dates - Date dimension table
CREATE TABLE dim_dates (
    date_id DATE PRIMARY KEY,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL,
    day_of_year INT NOT NULL,
    quarter INT NOT NULL,
    quarter_name VARCHAR(10) NOT NULL,
    year_quarter VARCHAR(10) NOT NULL,
    week_of_year INT NOT NULL,
    year_week VARCHAR(10) NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_weekday BOOLEAN NOT NULL,
    season ENUM('Winter', 'Spring', 'Summer', 'Fall') NOT NULL,
    business_period VARCHAR(20) NOT NULL,
    campaign_season VARCHAR(30) NOT NULL,
    _loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    _model_type VARCHAR(20) DEFAULT 'dimension',
    
    INDEX idx_year (year),
    INDEX idx_month (month),
    INDEX idx_quarter (quarter),
    INDEX idx_season (season),
    INDEX idx_campaign_season (campaign_season),
    INDEX idx_is_weekend (is_weekend)
);

-- =====================================================
-- FACT TABLE
-- =====================================================

-- fact_ad_performance - Central fact table
CREATE TABLE fact_ad_performance (
    fact_id VARCHAR(64) PRIMARY KEY,
    platform_id VARCHAR(50) NOT NULL,
    geo_id VARCHAR(10) NOT NULL,
    date_id DATE NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(50) NOT NULL,
    ad_format_id VARCHAR(50) NOT NULL,
    
    -- Core metrics (facts) - ONLY NUMERIC VALUES
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    spend_usd DECIMAL(15,2) DEFAULT 0.00,
    conversions INT DEFAULT 0,
    
    -- Calculated KPIs (numeric)
    ctr DECIMAL(6,4) DEFAULT 0.0000,
    cpc DECIMAL(8,2) DEFAULT 0.00,
    cvr DECIMAL(6,4) DEFAULT 0.0000,
    roas DECIMAL(8,4) DEFAULT 0.0000,
    
    -- Additional business metrics (numeric)
    cpm DECIMAL(8,2) DEFAULT 0.00,  -- Cost per thousand impressions
    conversion_rate_per_dollar DECIMAL(8,4) DEFAULT 0.0000,
    effectiveness_score INT DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Key Constraints
    FOREIGN KEY (platform_id) REFERENCES dim_platforms(platform_id) ON DELETE RESTRICT,
    FOREIGN KEY (geo_id) REFERENCES dim_geography(geo_id) ON DELETE RESTRICT,
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id) ON DELETE RESTRICT,
    FOREIGN KEY (device_id) REFERENCES dim_devices(device_id) ON DELETE RESTRICT,
    FOREIGN KEY (campaign_id) REFERENCES dim_campaigns(campaign_id) ON DELETE RESTRICT,
    FOREIGN KEY (ad_format_id) REFERENCES dim_ad_formats(ad_format_id) ON DELETE RESTRICT,
    
    -- Indexes for performance
    INDEX idx_platform_id (platform_id),
    INDEX idx_geo_id (geo_id),
    INDEX idx_date_id (date_id),
    INDEX idx_device_id (device_id),
    INDEX idx_campaign_id (campaign_id),
    INDEX idx_ad_format_id (ad_format_id),
    INDEX idx_impressions (impressions),
    INDEX idx_spend_usd (spend_usd),
    INDEX idx_effectiveness_score (effectiveness_score)
);

-- =====================================================
-- MART TABLES (Business Intelligence Views)
-- =====================================================

-- mart_campaign_performance_summary
CREATE TABLE mart_campaign_performance_summary (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id VARCHAR(50) NOT NULL,
    campaign_type VARCHAR(100) NOT NULL,
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    avg_ctr DECIMAL(6,4) DEFAULT 0.0000,
    avg_cpc DECIMAL(8,2) DEFAULT 0.00,
    avg_cvr DECIMAL(6,4) DEFAULT 0.0000,
    avg_roas DECIMAL(8,4) DEFAULT 0.0000,
    effectiveness_score INT DEFAULT 0,
    budget_tier ENUM('Low Budget', 'Medium Budget', 'High Budget') DEFAULT 'Low Budget',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (campaign_id) REFERENCES dim_campaigns(campaign_id) ON DELETE CASCADE,
    INDEX idx_campaign_type (campaign_type),
    INDEX idx_budget_tier (budget_tier),
    INDEX idx_effectiveness_score (effectiveness_score)
);

-- mart_platform_performance
CREATE TABLE mart_platform_performance (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_id VARCHAR(50) NOT NULL,
    platform_name VARCHAR(100) NOT NULL,
    platform_category ENUM('Major', 'Growing', 'Emerging') DEFAULT 'Emerging',
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    avg_ctr DECIMAL(6,4) DEFAULT 0.0000,
    avg_cpc DECIMAL(8,2) DEFAULT 0.00,
    avg_cvr DECIMAL(6,4) DEFAULT 0.0000,
    avg_roas DECIMAL(8,4) DEFAULT 0.0000,
    performance_tier ENUM('Tier 1', 'Tier 2', 'Tier 3') DEFAULT 'Tier 3',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (platform_id) REFERENCES dim_platforms(platform_id) ON DELETE CASCADE,
    INDEX idx_platform_category (platform_category),
    INDEX idx_performance_tier (performance_tier)
);

-- mart_daily_performance_dashboard
CREATE TABLE mart_daily_performance_dashboard (
    summary_id INT AUTO_INCREMENT PRIMARY KEY,
    date_id DATE NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    quarter INT NOT NULL,
    season ENUM('Winter', 'Spring', 'Summer', 'Fall') NOT NULL,
    campaign_season VARCHAR(30) NOT NULL,
    total_impressions BIGINT DEFAULT 0,
    total_clicks BIGINT DEFAULT 0,
    total_spend DECIMAL(15,2) DEFAULT 0.00,
    total_conversions INT DEFAULT 0,
    avg_ctr DECIMAL(6,4) DEFAULT 0.0000,
    avg_cpc DECIMAL(8,2) DEFAULT 0.00,
    avg_cvr DECIMAL(6,4) DEFAULT 0.0000,
    avg_roas DECIMAL(8,4) DEFAULT 0.0000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id) ON DELETE CASCADE,
    INDEX idx_date_id (date_id),
    INDEX idx_year (year),
    INDEX idx_month (month),
    INDEX idx_quarter (quarter),
    INDEX idx_season (season),
    INDEX idx_campaign_season (campaign_season)
);

-- =====================================================
-- SAMPLE DATA INSERTION (for ERD visualization)
-- =====================================================

-- Insert sample data into dimension tables for ERD visualization

-- Sample campaigns
INSERT INTO dim_campaigns (campaign_id, campaign_type, budget_tier) VALUES
('CAMP001', 'Brand Awareness', 'High Budget'),
('CAMP002', 'Conversions', 'Medium Budget'),
('CAMP003', 'Traffic', 'Low Budget');

-- Sample platforms
INSERT INTO dim_platforms (platform_id, platform_name, platform_category, performance_tier) VALUES
('Google', 'Google', 'Major', 'Tier 1'),
('Facebook', 'Facebook', 'Major', 'Tier 1'),
('LinkedIn', 'LinkedIn', 'Growing', 'Tier 2');

-- Sample geography
INSERT INTO dim_geography (geo_id, country_code, country_name, continent, market_type) VALUES
('US', 'US', 'United States', 'North America', 'Developed'),
('CA', 'CA', 'Canada', 'North America', 'Developed'),
('GB', 'GB', 'United Kingdom', 'Europe', 'Developed');

-- Sample devices
INSERT INTO dim_devices (device_id, device_type, device_family, is_mobile) VALUES
('mobile', 'mobile', 'Mobile', TRUE),
('desktop', 'desktop', 'Desktop', FALSE),
('tablet', 'tablet', 'Mobile', TRUE);

-- Sample ad formats
INSERT INTO dim_ad_formats (ad_format_id, ad_format_type, format_category, is_video) VALUES
('video', 'video', 'Video', TRUE),
('image', 'image', 'Static', FALSE),
('display', 'display', 'Static', FALSE);

-- Sample dates
INSERT INTO dim_dates (date_id, year, month, day, day_of_week, day_of_year, quarter, quarter_name, year_quarter, week_of_year, year_week, month_name, day_name, is_weekend, is_weekday, season, business_period, campaign_season) VALUES
('2025-01-15', 2025, 1, 15, 4, 15, 1, 'Q1', '2025-Q1', 3, '2025-W03', 'January', 'Wednesday', FALSE, TRUE, 'Winter', 'Q1 Start', 'Regular Period'),
('2025-01-16', 2025, 1, 16, 5, 16, 1, 'Q1', '2025-Q1', 3, '2025-W03', 'January', 'Thursday', FALSE, TRUE, 'Winter', 'Q1 Start', 'Regular Period');

-- Sample fact records
INSERT INTO fact_ad_performance (fact_id, platform_id, geo_id, date_id, device_id, campaign_id, ad_format_id, impressions, clicks, spend_usd, conversions, ctr, cpc, cvr, roas, cpm, conversion_rate_per_dollar, effectiveness_score) VALUES
('sample_fact_1', 'Google', 'US', '2025-01-15', 'mobile', 'CAMP001', 'video', 10000, 150, 500.00, 15, 0.0150, 3.33, 0.1000, 0.0300, 50.00, 0.0300, 75),
('sample_fact_2', 'Facebook', 'CA', '2025-01-16', 'desktop', 'CAMP002', 'image', 8000, 120, 400.00, 12, 0.0150, 3.33, 0.1000, 0.0300, 50.00, 0.0300, 75);

-- =====================================================
-- ERD RELATIONSHIP NOTES
-- =====================================================
/*
ERD RELATIONSHIPS:

1. fact_ad_performance (FACT TABLE) - Central hub
   ├── dim_platforms (1:Many) - One platform can have many ad performances
   ├── dim_geography (1:Many) - One country can have many ad performances  
   ├── dim_dates (1:Many) - One date can have many ad performances
   ├── dim_devices (1:Many) - One device can have many ad performances
   ├── dim_campaigns (1:Many) - One campaign can have many ad performances
   └── dim_ad_formats (1:Many) - One ad format can have many ad performances

2. MART TABLES (Business Intelligence Views)
   ├── mart_campaign_performance_summary - Aggregated campaign metrics
   ├── mart_platform_performance - Aggregated platform metrics
   └── mart_daily_performance_dashboard - Aggregated daily metrics

3. STAR SCHEMA CHARACTERISTICS:
   - One central fact table (fact_ad_performance)
   - Multiple dimension tables surrounding the fact table
   - Denormalized structure for query performance
   - Business-focused design for marketing analytics
   - Proper indexing on foreign keys and frequently queried columns

4. KEY FEATURES:
   - Composite primary key in fact table for uniqueness
   - Proper foreign key constraints for referential integrity
   - Comprehensive indexing for query performance
   - Business logic embedded in dimension tables
   - Calculated metrics stored in fact table for performance
*/

-- =====================================================
-- ERD GENERATION INSTRUCTIONS
-- =====================================================
/*
TO GENERATE ERD IN MYSQL WORKBENCH:

1. Run this entire script in MySQL Workbench
2. Go to Database → Reverse Engineer
3. Select the 'adspendiq' database
4. Choose all tables to include in the ERD
5. MySQL Workbench will automatically generate the ERD diagram
6. The diagram will show:
   - All 6 dimension tables
   - 1 central fact table
   - 3 mart tables
   - Proper foreign key relationships
   - Star schema structure

ERD FEATURES:
- Clear star schema visualization
- Proper relationship lines showing cardinality
- Table structures with field types
- Foreign key constraints
- Professional database design presentation
*/
