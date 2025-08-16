{{ config(materialized='table') }}

WITH fact_data AS (
    SELECT * FROM {{ ref('fact_ad_performance') }}
),

campaign_summary AS (
    SELECT 
        -- Campaign level aggregations
        campaign_id,
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
        END as overall_ctr,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(clicks), 2) 
            ELSE 0 
        END as overall_cpc,
        
        CASE 
            WHEN SUM(clicks) > 0 
            THEN ROUND(SUM(conversions) / SUM(clicks), 4) 
            ELSE 0 
        END as overall_cvr,
        
        CASE 
            WHEN SUM(spend_usd) > 0 
            THEN ROUND(SUM(conversions) / SUM(spend_usd), 4) 
            ELSE 0 
        END as overall_roas,
        
        -- Additional metrics
        CASE 
            WHEN SUM(impressions) > 0 
            THEN ROUND(SUM(spend_usd) / SUM(impressions) * 1000, 2) 
            ELSE 0 
        END as overall_cpm,
        
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
        END as overall_effectiveness_score,
        
        -- Campaign duration
        COUNT(DISTINCT date_id) as campaign_duration_days,
        
        -- Metadata
        MIN(date_id) as campaign_start_date,
        MAX(date_id) as campaign_end_date,
        CURRENT_TIMESTAMP as _loaded_at,
        'mart' as _model_type
        
    FROM fact_data
    GROUP BY 
        campaign_id, platform_id, geo_id, date_id, device_id, campaign_type_id, ad_format_id
),

final AS (
    SELECT 
        *,
        -- Campaign performance tier
        CASE 
            WHEN overall_effectiveness_score >= 80 THEN 'Top Performer'
            WHEN overall_effectiveness_score >= 60 THEN 'High Performer'
            WHEN overall_effectiveness_score >= 40 THEN 'Medium Performer'
            WHEN overall_effectiveness_score >= 20 THEN 'Low Performer'
            ELSE 'Poor Performer'
        END as performance_tier,
        
        -- ROI category
        CASE 
            WHEN overall_roas >= 0.05 THEN 'High ROI'
            WHEN overall_roas >= 0.02 THEN 'Medium ROI'
            WHEN overall_roas >= 0.01 THEN 'Low ROI'
            ELSE 'Negative ROI'
        END as roi_category,
        
        -- Cost efficiency
        CASE 
            WHEN overall_cpc <= 1.00 THEN 'Very Efficient'
            WHEN overall_cpc <= 2.00 THEN 'Efficient'
            WHEN overall_cpc <= 3.00 THEN 'Moderate'
            ELSE 'Expensive'
        END as cost_efficiency
        
    FROM campaign_summary
)

SELECT * FROM final
ORDER BY overall_effectiveness_score DESC, total_spend_usd DESC
