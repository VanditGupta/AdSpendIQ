{{ config(materialized='table') }}

WITH fact_data AS (
    SELECT * FROM {{ ref('fact_ad_performance') }}
),

platform_performance AS (
    SELECT 
        platform_id,
        geo_id,
        date_id,
        device_id,
        campaign_type_id,
        ad_format_id,
        
        -- Core metrics
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(spend_usd) as total_spend_usd,
        SUM(conversions) as total_conversions,
        
        -- Aggregated KPIs
        CASE 
            WHEN SUM(impressions) > 0 
            THEN ROUND(SUM(clicks) / SUM(impressions), 4) 
            ELSE 0 
        END as platform_ctr,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(clicks), 2) 
            ELSE 0 
        END as platform_cpc,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(conversions) / SUM(clicks), 4) 
            ELSE 0 
        END as platform_cvr,
        
        CASE 
            WHEN SUM(spend_usd) > 0 
            THEN ROUND(SUM(conversions) / SUM(spend_usd), 4) 
            ELSE 0 
        END as platform_roas,
        
        -- Additional metrics
        CASE 
            WHEN SUM(impressions) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(impressions) * 1000, 2) 
            ELSE 0 
        END as platform_cpm,
        
        -- Campaign count
        COUNT(DISTINCT campaign_id) as campaign_count,
        
        -- Date range
        COUNT(DISTINCT date_id) as active_days,
        
        -- Metadata
        MIN(date_id) as first_activity,
        MAX(date_id) as last_activity,
        CURRENT_TIMESTAMP as _loaded_at,
        'mart' as _model_type
        
    FROM fact_data
    GROUP BY 
        platform_id, geo_id, date_id, device_id, campaign_type_id, ad_format_id
),

final AS (
    SELECT 
        *,
        -- Platform performance tier
        CASE 
            WHEN platform_ctr >= 0.02 AND platform_cpc <= 2.00 AND platform_cvr >= 0.02 THEN 'Top Performer'
            WHEN platform_ctr >= 0.015 AND platform_cpc <= 3.00 AND platform_cvr >= 0.015 THEN 'High Performer'
            WHEN platform_ctr >= 0.01 AND platform_cpc <= 4.00 AND platform_cvr >= 0.01 THEN 'Medium Performer'
            WHEN platform_ctr >= 0.005 AND platform_cpc <= 5.00 AND platform_cvr >= 0.005 THEN 'Low Performer'
            ELSE 'Poor Performer'
        END as performance_tier,
        
        -- Cost efficiency rating
        CASE 
            WHEN platform_cpc <= 1.00 THEN 'Very Efficient'
            WHEN platform_cpc <= 2.00 THEN 'Efficient'
            WHEN platform_cpc <= 3.00 THEN 'Moderate'
            WHEN platform_cpc <= 4.00 THEN 'Expensive'
            ELSE 'Very Expensive'
        END as cost_efficiency,
        
        -- ROI rating
        CASE 
            WHEN platform_roas >= 0.05 THEN 'Excellent ROI'
            WHEN platform_roas >= 0.03 THEN 'Good ROI'
            WHEN platform_roas >= 0.02 THEN 'Moderate ROI'
            WHEN platform_roas >= 0.01 THEN 'Low ROI'
            ELSE 'Poor ROI'
        END as roi_rating,
        
        -- Volume tier
        CASE 
            WHEN total_impressions >= 100000 THEN 'High Volume'
            WHEN total_impressions >= 50000 THEN 'Medium Volume'
            WHEN total_impressions >= 10000 THEN 'Low Volume'
            ELSE 'Very Low Volume'
        END as volume_tier
        
    FROM platform_performance
)

SELECT * FROM final
ORDER BY platform_id, total_spend_usd DESC
