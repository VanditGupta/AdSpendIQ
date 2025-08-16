{{ config(materialized='view') }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'ad_data') }}
),

cleaned AS (
    SELECT 
        -- Primary identifiers
        campaign_id,
        date,
        
        -- Dimensions
        platform,
        geo,
        device,
        campaign_type,
        ad_format,
        
        -- Metrics (ensure they're numeric and positive)
        COALESCE(impressions, 0) as impressions,
        COALESCE(clicks, 0) as clicks,
        COALESCE(spend_usd, 0) as spend_usd,
        COALESCE(conversions, 0) as conversions,
        
        -- Calculated KPIs
        CASE 
            WHEN COALESCE(impressions, 0) > 0 
            THEN ROUND(COALESCE(clicks, 0)::FLOAT / impressions, 4) 
            ELSE 0 
        END as ctr,
        
        CASE 
            WHEN COALESCE(clicks, 0) > 0 
            THEN ROUND(COALESCE(spend_usd, 0) / clicks, 2) 
            ELSE 0 
        END as cpc,
        
        CASE 
            WHEN COALESCE(clicks, 0) > 0 
            THEN ROUND(COALESCE(conversions, 0)::FLOAT / clicks, 4) 
            ELSE 0 
        END as cvr,
        
        CASE 
            WHEN COALESCE(spend_usd, 0) > 0 
            THEN ROUND(COALESCE(conversions, 0)::FLOAT / spend_usd, 4) 
            ELSE 0 
        END as roas,
        
        -- Data quality flags
        CASE 
            WHEN impressions < clicks THEN 'impressions_less_than_clicks'
            WHEN ctr > 1 THEN 'ctr_greater_than_100'
            WHEN cpc < 0 THEN 'negative_cpc'
            ELSE 'valid'
        END as data_quality_flag,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'staging' as _model_type
        
    FROM source
    WHERE date >= CURRENT_DATE - {{ var('retention_days', 90) }}
)

SELECT * FROM cleaned
WHERE data_quality_flag = 'valid'  -- Only include valid data
