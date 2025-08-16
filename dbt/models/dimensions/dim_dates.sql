{{ config(materialized='table') }}

WITH date_range AS (
    SELECT DISTINCT date
    FROM {{ ref('stg_ad_data') }}
    WHERE date IS NOT NULL
),

enriched AS (
    SELECT 
        date,
        date as date_id,  -- Using date as ID for simplicity
        
        -- Basic date parts
        EXTRACT(YEAR FROM date) as year,
        EXTRACT(MONTH FROM date) as month,
        EXTRACT(DAY FROM date) as day,
        EXTRACT(DAYOFWEEK FROM date) as day_of_week,
        EXTRACT(DAYOFYEAR FROM date) as day_of_year,
        
        -- Quarter
        EXTRACT(QUARTER FROM date) as quarter,
        CONCAT('Q', EXTRACT(QUARTER FROM date)) as quarter_name,
        CONCAT(EXTRACT(YEAR FROM date), '-Q', EXTRACT(QUARTER FROM date)) as year_quarter,
        
        -- Week
        EXTRACT(WEEK FROM date) as week_of_year,
        CONCAT(EXTRACT(YEAR FROM date), '-W', LPAD(EXTRACT(WEEK FROM date)::STRING, 2, '0')) as year_week,
        
        -- Month names
        CASE EXTRACT(MONTH FROM date)
            WHEN 1 THEN 'January'
            WHEN 2 THEN 'February'
            WHEN 3 THEN 'March'
            WHEN 4 THEN 'April'
            WHEN 5 THEN 'May'
            WHEN 6 THEN 'June'
            WHEN 7 THEN 'July'
            WHEN 8 THEN 'August'
            WHEN 9 THEN 'September'
            WHEN 10 THEN 'October'
            WHEN 11 THEN 'November'
            WHEN 12 THEN 'December'
        END as month_name,
        
        -- Day names
        CASE EXTRACT(DAYOFWEEK FROM date)
            WHEN 1 THEN 'Sunday'
            WHEN 2 THEN 'Monday'
            WHEN 3 THEN 'Tuesday'
            WHEN 4 THEN 'Wednesday'
            WHEN 5 THEN 'Thursday'
            WHEN 6 THEN 'Friday'
            WHEN 7 THEN 'Saturday'
        END as day_name,
        
        -- Business logic
        CASE 
            WHEN EXTRACT(DAYOFWEEK FROM date) IN (1, 7) THEN true
            ELSE false
        END as is_weekend,
        
        CASE 
            WHEN EXTRACT(DAYOFWEEK FROM date) IN (2, 3, 4, 5, 6) THEN true
            ELSE false
        END as is_weekday,
        
        -- Seasons
        CASE 
            WHEN EXTRACT(MONTH FROM date) IN (12, 1, 2) THEN 'Winter'
            WHEN EXTRACT(MONTH FROM date) IN (3, 4, 5) THEN 'Spring'
            WHEN EXTRACT(MONTH FROM date) IN (6, 7, 8) THEN 'Summer'
            WHEN EXTRACT(MONTH FROM date) IN (9, 10, 11) THEN 'Fall'
        END as season,
        
        -- Business periods
        CASE 
            WHEN EXTRACT(MONTH FROM date) IN (1, 2) THEN 'Q1 Start'
            WHEN EXTRACT(MONTH FROM date) IN (3) THEN 'Q1 End'
            WHEN EXTRACT(MONTH FROM date) IN (4, 5) THEN 'Q2'
            WHEN EXTRACT(MONTH FROM date) IN (6) THEN 'Q2 End'
            WHEN EXTRACT(MONTH FROM date) IN (7, 8) THEN 'Q3'
            WHEN EXTRACT(MONTH FROM date) IN (9) THEN 'Q3 End'
            WHEN EXTRACT(MONTH FROM date) IN (10, 11) THEN 'Q4'
            WHEN EXTRACT(MONTH FROM date) IN (12) THEN 'Q4 End'
        END as business_period,
        
        -- Holiday seasons (for ad campaign planning)
        CASE 
            WHEN EXTRACT(MONTH FROM date) = 12 THEN 'Holiday Season'
            WHEN EXTRACT(MONTH FROM date) = 11 AND EXTRACT(DAY FROM date) >= 20 THEN 'Holiday Season'
            WHEN EXTRACT(MONTH FROM date) = 1 AND EXTRACT(DAY FROM date) <= 5 THEN 'Holiday Season'
            WHEN EXTRACT(MONTH FROM date) = 7 THEN 'Summer Campaigns'
            WHEN EXTRACT(MONTH FROM date) = 9 THEN 'Back to School'
            WHEN EXTRACT(MONTH FROM date) = 10 THEN 'Fall Campaigns'
            ELSE 'Regular Period'
        END as campaign_season,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'dimension' as _model_type
        
    FROM date_range
)

SELECT * FROM enriched
ORDER BY date
