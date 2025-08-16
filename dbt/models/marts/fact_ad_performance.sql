{{ config(materialized='table') }}

WITH staging_data AS (
    SELECT * FROM {{ ref('stg_ad_data') }}
),

fact_data AS (
    SELECT 
        -- Primary key (composite key for uniqueness)
        MD5(campaign_id || date || platform || geo || device || campaign_type || ad_format) as fact_id,
        
        -- Foreign keys to dimensions
        platform as platform_id,
        geo as geo_id,
        date as date_id,
        device as device_id,
        campaign_type as campaign_type_id,
        ad_format as ad_format_id,
        
        -- Business identifiers
        campaign_id,
        
        -- Core metrics (facts)
        impressions,
        clicks,
        spend_usd,
        conversions,
        
        -- Calculated KPIs
        ctr,
        cpc,
        cvr,
        roas,
        
        -- Additional business metrics
        CASE 
            WHEN impressions > 0 THEN ROUND(spend_usd / impressions * 1000, 2)
            ELSE 0 
        END as cpm,  -- Cost per thousand impressions
        
        CASE 
            WHEN spend_usd > 0 THEN ROUND(conversions / spend_usd, 4)
            ELSE 0 
        END as conversion_rate_per_dollar,
        
        -- Performance indicators
        CASE 
            WHEN ctr >= 0.02 THEN 'High CTR'
            WHEN ctr >= 0.01 THEN 'Medium CTR'
            ELSE 'Low CTR'
        END as ctr_performance,
        
        CASE 
            WHEN cpc <= 1.00 THEN 'Low Cost'
            WHEN cpc <= 3.00 THEN 'Medium Cost'
            ELSE 'High Cost'
        END as cpc_performance,
        
        CASE 
            WHEN cvr >= 0.03 THEN 'High Conversion'
            WHEN cvr >= 0.01 THEN 'Medium Conversion'
            ELSE 'Low Conversion'
        END as cvr_performance,
        
        -- ROI indicators
        CASE 
            WHEN roas >= 0.05 THEN 'High ROAS'
            WHEN roas >= 0.02 THEN 'Medium ROAS'
            ELSE 'Low ROAS'
        END as roas_performance,
        
        -- Campaign effectiveness score (0-100)
        CASE 
            WHEN impressions > 0 AND clicks > 0 AND conversions > 0 THEN
                ROUND(
                    (ctr * 25) + 
                    (CASE WHEN cpc <= 2.00 THEN 25 ELSE 25 - (cpc - 2.00) * 5 END) +
                    (cvr * 200) + 
                    (CASE WHEN roas >= 0.02 THEN 25 ELSE roas * 1250 END)
                , 0)
            ELSE 0
        END as effectiveness_score,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'fact' as _model_type
        
    FROM staging_data
)

SELECT * FROM fact_data
ORDER BY date_id, platform_id, geo_id
