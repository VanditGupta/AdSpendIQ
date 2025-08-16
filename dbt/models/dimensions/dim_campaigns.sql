{{
  config(
    materialized='table',
    unique_key='campaign_id',
    indexes=[
      {'columns': ['campaign_id'], 'type': 'btree'},
      {'columns': ['campaign_type'], 'type': 'btree'}
    ]
  )
}}

WITH campaign_data AS (
  SELECT DISTINCT
    campaign_id,
    campaign_type,
    COUNT(*) as campaign_records,
    MIN(date) as first_seen_date,
    MAX(date) as last_seen_date,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend_usd) as total_spend,
    SUM(conversions) as total_conversions
  FROM {{ source('raw', 'ad_data') }}
  WHERE campaign_id IS NOT NULL
  GROUP BY campaign_id, campaign_type
),

enriched_campaigns AS (
  SELECT
    campaign_id,
    COALESCE(campaign_type, 'Unknown') as campaign_type,
    campaign_records,
    first_seen_date,
    last_seen_date,
    total_impressions,
    total_clicks,
    total_spend,
    total_conversions,
    -- Business logic fields
    CASE 
      WHEN total_impressions > 0 THEN ROUND(CAST(total_clicks AS FLOAT) / total_impressions, 4)
      ELSE 0 
    END as campaign_ctr,
    CASE 
      WHEN total_clicks > 0 THEN ROUND(total_spend / total_clicks, 2)
      ELSE 0 
    END as campaign_cpc,
    CASE 
      WHEN total_spend > 0 THEN ROUND(CAST(total_conversions AS FLOAT) / total_spend, 4)
      ELSE 0 
    END as campaign_roas,
    -- Campaign performance tier
    CASE 
      WHEN total_spend > 10000 THEN 'High Budget'
      WHEN total_spend > 1000 THEN 'Medium Budget'
      ELSE 'Low Budget'
    END as budget_tier,
    -- Campaign effectiveness score (simplified)
    CASE 
      WHEN total_impressions > 0 AND total_clicks > 0 AND total_conversions > 0 THEN
        ROUND(
          (CASE WHEN total_impressions > 0 THEN ROUND(CAST(total_clicks AS FLOAT) / total_impressions, 4) ELSE 0 END * 25) + 
          (CASE WHEN total_clicks > 0 AND ROUND(total_spend / total_clicks, 2) <= 2.00 THEN 25 ELSE 25 - (ROUND(total_spend / total_clicks, 2) - 2.00) * 5 END) +
          (CASE WHEN total_clicks > 0 THEN ROUND(CAST(total_conversions AS FLOAT) / total_clicks, 4) ELSE 0 END * 200) + 
          (CASE WHEN total_spend > 0 AND ROUND(CAST(total_conversions AS FLOAT) / total_spend, 4) >= 0.02 THEN 25 ELSE ROUND(CAST(total_conversions AS FLOAT) / total_spend, 4) * 1250 END)
        , 0)
      ELSE 0
    END as effectiveness_score,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
  FROM campaign_data
)

SELECT * FROM enriched_campaigns
