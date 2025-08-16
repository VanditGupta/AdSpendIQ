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
        COALESCE(conversions, 0) as conversions
        
    FROM source
    WHERE date >= CURRENT_DATE - {{ var('retention_days', 90) }}
),

with_kpis AS (
    SELECT 
        *,
        -- Calculated KPIs
        CASE 
            WHEN impressions > 0 
            THEN ROUND(CAST(clicks AS FLOAT) / impressions, 4) 
            ELSE 0 
        END as ctr,
        
        CASE 
            WHEN clicks > 0 
            THEN ROUND(spend_usd / clicks, 2) 
            ELSE 0 
        END as cpc,
        
        CASE 
            WHEN clicks > 0 
            THEN ROUND(CAST(conversions AS FLOAT) / clicks, 4) 
            ELSE 0 
        END as cvr,
        
        CASE 
            WHEN spend_usd > 0 
            THEN ROUND(CAST(conversions AS FLOAT) / spend_usd, 4) 
            ELSE 0 
        END as roas
        
    FROM cleaned
),

final AS (
    SELECT 
        *,
        -- Data quality flags (now referencing calculated fields)
        CASE 
            WHEN impressions < clicks THEN 'impressions_less_than_clicks'
            WHEN ctr > 1 THEN 'ctr_greater_than_100'
            WHEN cpc < 0 THEN 'negative_cpc'
            ELSE 'valid'
        END as data_quality_flag,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'staging' as _model_type
        
    FROM with_kpis
)

SELECT * FROM final
WHERE data_quality_flag = 'valid'  -- Only include valid data
