{{ config(materialized='table') }}

WITH fact_data AS (
    SELECT * FROM {{ ref('fact_ad_performance') }}
),

daily_summary AS (
    SELECT 
        date_id,
        platform_id,
        geo_id,
        device_id,
        campaign_id,
        ad_format_id,
        
        -- Core metrics
        SUM(impressions) as daily_impressions,
        SUM(clicks) as daily_clicks,
        SUM(spend_usd) as daily_spend_usd,
        SUM(conversions) as daily_conversions,
        
        -- Daily KPIs
        CASE 
            WHEN SUM(impressions) > 0 
            THEN ROUND(SUM(clicks) / SUM(impressions), 4) 
            ELSE 0 
        END as daily_ctr,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(clicks), 2) 
            ELSE 0 
        END as daily_cpc,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(conversions) / SUM(clicks), 4) 
            ELSE 0 
        END as daily_cvr,
        
        CASE 
            WHEN SUM(spend_usd) > 0 
            THEN ROUND(SUM(conversions) / SUM(spend_usd), 4) 
            ELSE 0 
        END as daily_roas,
        
        -- Additional metrics
        CASE 
            WHEN SUM(impressions) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(impressions) * 1000, 2) 
            ELSE 0 
        END as daily_cpm,
        
        -- Campaign metrics
        COUNT(DISTINCT campaign_id) as active_campaigns,
        
        -- Performance indicators
        CASE 
            WHEN SUM(impressions) > 0 AND SUM(clicks) > 0 AND SUM(conversions) > 0 THEN
                ROUND(
                    (CASE WHEN SUM(clicks) / SUM(impressions) >= 0.02 THEN 25 ELSE (SUM(clicks) / SUM(impressions)) * 1250 END) + 
                    (CASE WHEN SUM(spend_usd) / SUM(clicks) <= 2.00 THEN 25 ELSE 25 - (SUM(spend_usd) / SUM(clicks) - 2.00) * 5 END) +
                    (CASE WHEN SUM(conversions) / SUM(clicks) >= 0.03 THEN 25 ELSE (SUM(conversions) / SUM(clicks)) * 833 END) + 
                    (CASE WHEN SUM(conversions) / SUM(spend_usd) >= 0.02 THEN 25 ELSE (SUM(conversions) / SUM(spend_usd)) * 1250 END)
                , 0)
            ELSE 0
        END as daily_effectiveness_score,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'dashboard_mart' as _model_type
        
    FROM fact_data
    GROUP BY 
        date_id, platform_id, geo_id, device_id, campaign_id, ad_format_id
),

final AS (
    SELECT 
        *,
        -- Daily performance tier
        CASE 
            WHEN daily_effectiveness_score >= 80 THEN 'Excellent'
            WHEN daily_effectiveness_score >= 60 THEN 'Good'
            WHEN daily_effectiveness_score >= 40 THEN 'Fair'
            WHEN daily_effectiveness_score >= 20 THEN 'Poor'
            ELSE 'Very Poor'
        END as daily_performance_tier,
        
        -- Spend efficiency
        CASE 
            WHEN daily_cpc <= 1.00 THEN 'Very Efficient'
            WHEN daily_cpc <= 2.00 THEN 'Efficient'
            WHEN daily_cpc <= 3.00 THEN 'Moderate'
            WHEN daily_cpc <= 4.00 THEN 'Expensive'
            ELSE 'Very Expensive'
        END as daily_cost_efficiency,
        
        -- ROI performance
        CASE 
            WHEN daily_roas >= 0.05 THEN 'High ROI'
            WHEN daily_roas >= 0.02 THEN 'Medium ROI'
            WHEN daily_roas >= 0.01 THEN 'Low ROI'
            ELSE 'Poor ROI'
        END as daily_roi_performance,
        
        -- Volume indicator
        CASE 
            WHEN daily_impressions >= 10000 THEN 'High Volume'
            WHEN daily_impressions >= 5000 THEN 'Medium Volume'
            WHEN daily_impressions >= 1000 THEN 'Low Volume'
            ELSE 'Very Low Volume'
        END as daily_volume_indicator
        
    FROM daily_summary
)

SELECT * FROM final
ORDER BY date_id DESC, daily_spend_usd DESC
