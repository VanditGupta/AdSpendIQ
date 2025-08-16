-- =====================================================
-- PORTFOLIO SHOWCASE QUERIES
-- Ad Campaign Analytics Star Schema
-- =====================================================

-- =====================================================
-- 1. EXECUTIVE SUMMARY - Top Level KPIs
-- =====================================================
SELECT 
    'Overall Performance' as metric_category,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(spend_usd) as total_spend_usd,
    SUM(conversions) as total_conversions,
    ROUND(SUM(clicks) / SUM(impressions), 4) as overall_ctr,
    ROUND(SUM(spend_usd) / SUM(clicks), 2) as overall_cpc,
    ROUND(SUM(conversions) / SUM(clicks), 4) as overall_cvr,
    ROUND(SUM(conversions) / SUM(spend_usd), 4) as overall_roas
FROM RAW.fact_ad_performance;

-- =====================================================
-- 2. PLATFORM PERFORMANCE ANALYSIS
-- =====================================================
SELECT 
    p.platform_name,
    p.platform_category,
    p.performance_tier,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    SUM(f.impressions) as total_impressions,
    SUM(f.spend_usd) as total_spend_usd,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as platform_ctr,
    ROUND(SUM(f.spend_usd) / SUM(f.clicks), 2) as platform_cpc,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as platform_roas
FROM RAW.fact_ad_performance f
JOIN RAW.dim_platforms p ON f.platform_id = p.platform_id
GROUP BY p.platform_name, p.platform_category, p.performance_tier
ORDER BY total_spend_usd DESC;

-- =====================================================
-- 3. GEOGRAPHIC PERFORMANCE INSIGHTS
-- =====================================================
SELECT 
    g.country_name,
    g.continent,
    g.market_type,
    g.currency,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    SUM(f.impressions) as total_impressions,
    SUM(f.spend_usd) as total_spend_usd,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as geo_ctr,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as geo_roas
FROM RAW.fact_ad_performance f
JOIN RAW.dim_geography g ON f.geo_id = g.geo_id
GROUP BY g.country_name, g.continent, g.market_type, g.currency
ORDER BY total_spend_usd DESC;

-- =====================================================
-- 4. TIME-BASED TREND ANALYSIS
-- =====================================================
SELECT 
    d.year,
    d.quarter,
    d.month_name,
    d.campaign_season,
    COUNT(DISTINCT f.campaign_id) as active_campaigns,
    SUM(f.impressions) as monthly_impressions,
    SUM(f.spend_usd) as monthly_spend,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as monthly_ctr,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as monthly_roas
FROM RAW.fact_ad_performance f
JOIN RAW.dim_dates d ON f.date_id = d.date_id
GROUP BY d.year, d.quarter, d.month_name, d.campaign_season
ORDER BY d.year DESC, d.quarter DESC, d.month DESC;

-- =====================================================
-- 5. CAMPAIGN TYPE EFFECTIVENESS
-- =====================================================
SELECT 
    f.campaign_type_id,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    SUM(f.impressions) as total_impressions,
    SUM(f.spend_usd) as total_spend_usd,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as type_ctr,
    ROUND(SUM(f.conversions) / SUM(f.clicks), 4) as type_cvr,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as type_roas,
    AVG(f.effectiveness_score) as avg_effectiveness
FROM RAW.fact_ad_performance f
GROUP BY f.campaign_type_id
ORDER BY avg_effectiveness DESC;

-- =====================================================
-- 6. DEVICE PERFORMANCE COMPARISON
-- =====================================================
SELECT 
    f.device_id,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    SUM(f.impressions) as total_impressions,
    SUM(f.spend_usd) as total_spend_usd,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as device_ctr,
    ROUND(SUM(f.conversions) / SUM(f.clicks), 4) as device_cvr,
    ROUND(SUM(f.spend_usd) / SUM(f.impressions) * 1000, 2) as device_cpm
FROM RAW.fact_ad_performance f
GROUP BY f.device_id
ORDER BY total_spend_usd DESC;

-- =====================================================
-- 7. TOP PERFORMING CAMPAIGNS
-- =====================================================
SELECT 
    f.campaign_id,
    p.platform_name,
    g.country_name,
    f.device_id,
    f.campaign_type_id,
    f.ad_format_id,
    SUM(f.impressions) as campaign_impressions,
    SUM(f.clicks) as campaign_clicks,
    SUM(f.spend_usd) as campaign_spend,
    SUM(f.conversions) as campaign_conversions,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as campaign_ctr,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as campaign_roas,
    AVG(f.effectiveness_score) as campaign_effectiveness
FROM RAW.fact_ad_performance f
JOIN RAW.dim_platforms p ON f.platform_id = p.platform_id
JOIN RAW.dim_geography g ON f.geo_id = g.geo_id
GROUP BY f.campaign_id, p.platform_name, g.country_name, f.device_id, f.campaign_type_id, f.ad_format_id
HAVING SUM(f.impressions) > 1000  -- Only campaigns with significant volume
ORDER BY campaign_effectiveness DESC, campaign_spend DESC
LIMIT 20;

-- =====================================================
-- 8. COST EFFICIENCY ANALYSIS
-- =====================================================
SELECT 
    CASE 
        WHEN f.cpc <= 1.00 THEN 'Very Efficient ($0-$1)'
        WHEN f.cpc <= 2.00 THEN 'Efficient ($1-$2)'
        WHEN f.cpc <= 3.00 THEN 'Moderate ($2-$3)'
        WHEN f.cpc <= 4.00 THEN 'Expensive ($3-$4)'
        ELSE 'Very Expensive ($4+)'
    END as cost_efficiency_bucket,
    COUNT(*) as record_count,
    ROUND(AVG(f.ctr), 4) as avg_ctr,
    ROUND(AVG(f.cvr), 4) as avg_cvr,
    ROUND(AVG(f.roas), 4) as avg_roas,
    ROUND(AVG(f.effectiveness_score), 0) as avg_effectiveness
FROM RAW.fact_ad_performance f
WHERE f.cpc > 0  -- Exclude records with zero clicks
GROUP BY cost_efficiency_bucket
ORDER BY 
    CASE cost_efficiency_bucket
        WHEN 'Very Efficient ($0-$1)' THEN 1
        WHEN 'Efficient ($1-$2)' THEN 2
        WHEN 'Moderate ($2-$3)' THEN 3
        WHEN 'Expensive ($3-$4)' THEN 4
        ELSE 5
    END;

-- =====================================================
-- 9. SEASONAL PERFORMANCE PATTERNS
-- =====================================================
SELECT 
    d.season,
    d.campaign_season,
    COUNT(DISTINCT f.campaign_id) as active_campaigns,
    SUM(f.impressions) as seasonal_impressions,
    SUM(f.spend_usd) as seasonal_spend,
    ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as seasonal_ctr,
    ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as seasonal_roas,
    ROUND(AVG(f.effectiveness_score), 0) as avg_seasonal_effectiveness
FROM RAW.fact_ad_performance f
JOIN RAW.dim_dates d ON f.date_id = d.date_id
GROUP BY d.season, d.campaign_season
ORDER BY seasonal_spend DESC;

-- =====================================================
-- 10. ROI OPTIMIZATION OPPORTUNITIES
-- =====================================================
SELECT 
    'High ROI Campaigns' as category,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    ROUND(AVG(f.roas), 4) as avg_roas,
    ROUND(AVG(f.effectiveness_score), 0) as avg_effectiveness
FROM RAW.fact_ad_performance f
WHERE f.roas >= 0.05

UNION ALL

SELECT 
    'Medium ROI Campaigns' as category,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    ROUND(AVG(f.roas), 4) as avg_roas,
    ROUND(AVG(f.effectiveness_score), 0) as avg_effectiveness
FROM RAW.fact_ad_performance f
WHERE f.roas >= 0.02 AND f.roas < 0.05

UNION ALL

SELECT 
    'Low ROI Campaigns' as category,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    ROUND(AVG(f.roas), 4) as avg_roas,
    ROUND(AVG(f.effectiveness_score), 0) as avg_effectiveness
FROM RAW.fact_ad_performance f
WHERE f.roas < 0.02

ORDER BY avg_roas DESC;
