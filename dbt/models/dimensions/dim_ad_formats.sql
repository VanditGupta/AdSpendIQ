{{
  config(
    materialized='table',
    unique_key='ad_format',
    indexes=[
      {'columns': ['ad_format'], 'type': 'btree'},
      {'columns': ['format_category'], 'type': 'btree'}
    ]
  )
}}

WITH ad_format_data AS (
  SELECT DISTINCT
    ad_format,
    COUNT(*) as format_records,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend_usd) as total_spend,
    SUM(conversions) as total_conversions,
    MIN(date) as first_seen_date,
    MAX(date) as last_seen_date
  FROM {{ source('raw', 'ad_data') }}
  WHERE ad_format IS NOT NULL
  GROUP BY ad_format
),

enriched_ad_formats AS (
  SELECT
    ad_format as ad_format_id,
    ad_format as ad_format_type,
    CASE 
      WHEN ad_format IN ('video') THEN 'Video'
      WHEN ad_format IN ('image', 'display', 'social') THEN 'Static'
      WHEN ad_format IN ('interactive', 'remarketing') THEN 'Interactive'
      ELSE 'Other'
    END as format_category,
    CASE 
      WHEN ad_format = 'video' THEN TRUE
      ELSE FALSE
    END as is_video,
    CASE 
      WHEN ad_format IN ('remarketing', 'interactive') THEN TRUE
      ELSE FALSE
    END as is_interactive,
    format_records,
    total_impressions,
    total_clicks,
    total_spend,
    total_conversions,
    first_seen_date,
    last_seen_date,
    -- Format performance metrics
    CASE 
      WHEN total_impressions > 0 THEN ROUND(CAST(total_clicks AS FLOAT) / total_impressions, 4)
      ELSE 0 
    END as format_ctr,
    CASE 
      WHEN total_clicks > 0 THEN ROUND(total_spend / total_clicks, 2)
      ELSE 0 
    END as format_cpc,
    CASE 
      WHEN total_spend > 0 THEN ROUND(CAST(total_conversions AS FLOAT) / total_spend, 4)
      ELSE 0 
    END as format_roas,
    -- Format performance tier
    CASE 
      WHEN total_spend > 50000 THEN 'High Performance'
      WHEN total_spend > 10000 THEN 'Medium Performance'
      ELSE 'Low Performance'
    END as performance_tier,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
  FROM ad_format_data
)

SELECT * FROM enriched_ad_formats
