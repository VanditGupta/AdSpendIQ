{{ config(materialized='table') }}

WITH platform_data AS (
    SELECT DISTINCT
        platform as platform_name,
        platform as platform_id  -- Using platform name as ID for simplicity
    FROM {{ ref('stg_ad_data') }}
    WHERE platform IS NOT NULL
),

enriched AS (
    SELECT 
        platform_id,
        platform_name,
        
        -- Platform categorization
        CASE 
            WHEN platform_name IN ('Google', 'Facebook') THEN 'Major'
            WHEN platform_name IN ('LinkedIn', 'TikTok') THEN 'Growing'
            ELSE 'Emerging'
        END as platform_category,
        
        -- Platform region
        CASE 
            WHEN platform_name IN ('Google', 'Facebook') THEN 'Global'
            ELSE 'Regional'
        END as platform_region,
        
        -- Platform features
        CASE 
            WHEN platform_name = 'Google' THEN 'Search, Display, Video, Shopping'
            WHEN platform_name = 'Facebook' THEN 'Social, Video, Display, Stories'
            WHEN platform_name = 'LinkedIn' THEN 'Professional, B2B, Thought Leadership'
            WHEN platform_name = 'TikTok' THEN 'Short-form Video, Gen Z, Entertainment'
            WHEN platform_name = 'Twitter' THEN 'Real-time, News, Conversations'
        END as platform_features,
        
        -- Performance tier
        CASE 
            WHEN platform_name IN ('Google', 'Facebook') THEN 'Tier 1'
            WHEN platform_name IN ('LinkedIn', 'TikTok') THEN 'Tier 2'
            ELSE 'Tier 3'
        END as performance_tier,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'dimension' as _model_type
        
    FROM platform_data
)

SELECT * FROM enriched
ORDER BY performance_tier, platform_name
