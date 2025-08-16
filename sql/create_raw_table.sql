-- Create raw.ad_data table for ad campaign data
-- Run this in Snowflake before loading data

USE DATABASE AD_CAMPAIGNS;
USE SCHEMA RAW;
USE WAREHOUSE COMPUTE_WH;

CREATE TABLE IF NOT EXISTS raw.ad_data (
    campaign_id         STRING,
    platform            STRING,
    date                DATE,
    geo                 STRING,
    device              STRING,
    campaign_type       STRING,
    ad_format           STRING,
    impressions         INTEGER,
    clicks              INTEGER,
    spend_usd           FLOAT,
    conversions         INTEGER
);

-- Add table description
COMMENT ON TABLE raw.ad_data IS 'Raw ad campaign performance data from multiple platforms (Google, Facebook, LinkedIn, TikTok, Twitter)';

-- Add column descriptions
COMMENT ON COLUMN raw.ad_data.campaign_id IS 'Unique campaign identifier with descriptive naming';
COMMENT ON COLUMN raw.ad_data.platform IS 'Ad platform: Google, Facebook, LinkedIn, TikTok, Twitter';
COMMENT ON COLUMN raw.ad_data.date IS 'Campaign date in YYYY-MM-DD format';
COMMENT ON COLUMN raw.ad_data.geo IS 'Geographic location (country code)';
COMMENT ON COLUMN raw.ad_data.device IS 'Device type: mobile, desktop, tablet';
COMMENT ON COLUMN raw.ad_data.campaign_type IS 'Campaign objective: brand_awareness, conversions, traffic, etc.';
COMMENT ON COLUMN raw.ad_data.ad_format IS 'Ad format: search, display, video, social, shopping, remarketing';
COMMENT ON COLUMN raw.ad_data.impressions IS 'Number of ad impressions served';
COMMENT ON COLUMN raw.ad_data.clicks IS 'Number of clicks received';
COMMENT ON COLUMN raw.ad_data.spend_usd IS 'Total spend in USD';
COMMENT ON COLUMN raw.ad_data.conversions IS 'Number of conversions achieved';

-- Verify table creation
DESCRIBE TABLE raw.ad_data;
