{{
  config(
    materialized='table',
    unique_key='device',
    indexes=[
      {'columns': ['device'], 'type': 'btree'},
      {'columns': ['device_type'], 'type': 'btree'}
    ]
  )
}}

WITH device_data AS (
  SELECT DISTINCT
    device,
    COUNT(*) as device_records,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend_usd) as total_spend,
    SUM(conversions) as total_conversions,
    MIN(date) as first_seen_date,
    MAX(date) as last_seen_date
  FROM {{ source('raw', 'ad_data') }}
  WHERE device IS NOT NULL
  GROUP BY device
),

enriched_devices AS (
  SELECT
    device as device_id,
    device as device_type,
    CASE 
      WHEN device IN ('mobile', 'tablet') THEN 'Mobile'
      WHEN device = 'desktop' THEN 'Desktop'
      ELSE 'Other'
    END as device_family,
    CASE 
      WHEN device IN ('mobile', 'tablet') THEN TRUE
      ELSE FALSE
    END as is_mobile,
    device_records,
    total_impressions,
    total_clicks,
    total_spend,
    total_conversions,
    first_seen_date,
    last_seen_date,
    -- Device performance metrics
    CASE 
      WHEN total_impressions > 0 THEN ROUND(CAST(total_clicks AS FLOAT) / total_impressions, 4)
      ELSE 0 
    END as device_ctr,
    CASE 
      WHEN total_clicks > 0 THEN ROUND(total_spend / total_clicks, 2)
      ELSE 0 
    END as device_cpc,
    CASE 
      WHEN total_spend > 0 THEN ROUND(CAST(total_conversions AS FLOAT) / total_spend, 4)
      ELSE 0 
    END as device_roas,
    -- Device performance tier
    CASE 
      WHEN total_spend > 50000 THEN 'High Performance'
      WHEN total_spend > 10000 THEN 'Medium Performance'
      ELSE 'Low Performance'
    END as performance_tier,
    CURRENT_TIMESTAMP as created_at,
    CURRENT_TIMESTAMP as updated_at
  FROM device_data
)

SELECT * FROM enriched_devices
