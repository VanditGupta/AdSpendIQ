#!/usr/bin/env python3
"""
Portfolio Showcase Queries Runner
Connects to Snowflake and executes the portfolio showcase queries
"""

import os
import sys
import pandas as pd
from snowflake.connector import connect
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

def get_snowflake_connection():
    """Create Snowflake connection"""
    try:
        conn = connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT').split('.')[0],
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW'),
            role='ACCOUNTADMIN'
        )
        print("✅ Connected to Snowflake successfully!")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Snowflake: {e}")
        return None

def run_query(conn, query_name, sql):
    """Execute a query and display results"""
    try:
        print(f"\n{'='*60}")
        print(f"🔍 {query_name}")
        print(f"{'='*60}")
        
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Get data
        data = cursor.fetchall()
        
        if data:
            # Create DataFrame for better display
            df = pd.DataFrame(data, columns=columns)
            print(f"📊 Results: {len(data)} rows")
            print("\n" + df.to_string(index=False))
        else:
            print("📊 No results returned")
            
        cursor.close()
        
    except Exception as e:
        print(f"❌ Query failed: {e}")

def main():
    """Main function to run portfolio queries"""
    print("🚀 Portfolio Showcase Queries Runner")
    print("=" * 50)
    
    # Connect to Snowflake
    conn = get_snowflake_connection()
    if not conn:
        return
    
    # Portfolio Showcase Queries
    queries = {
        "1. Executive Summary - Top Level KPIs": """
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
            FROM RAW.fact_ad_performance
        """,
        
        "2. Platform Performance Analysis": """
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
            ORDER BY total_spend_usd DESC
        """,
        
        "3. Geographic Performance Insights": """
            SELECT 
                g.country_name,
                g.continent,
                g.market_type,
                COUNT(DISTINCT f.campaign_id) as campaign_count,
                SUM(f.impressions) as total_impressions,
                SUM(f.spend_usd) as total_spend_usd,
                ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as geo_ctr,
                ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as geo_roas
            FROM RAW.fact_ad_performance f
            JOIN RAW.dim_geography g ON f.geo_id = g.geo_id
            GROUP BY g.country_name, g.continent, g.market_type
            ORDER BY total_spend_usd DESC
            LIMIT 10
        """,
        
        "4. Time-Based Trend Analysis": """
            SELECT 
                d.year,
                d.quarter,
                d.month_name,
                COUNT(DISTINCT f.campaign_id) as active_campaigns,
                SUM(f.impressions) as monthly_impressions,
                SUM(f.spend_usd) as monthly_spend,
                ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as monthly_ctr,
                ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as monthly_roas
            FROM RAW.fact_ad_performance f
            JOIN RAW.dim_dates d ON f.date_id = d.date_id
            GROUP BY d.year, d.quarter, d.month_name
            ORDER BY d.year DESC, d.quarter DESC, d.month DESC
            LIMIT 12
        """,
        
        "5. Top Performing Campaigns": """
            SELECT 
                f.campaign_id,
                p.platform_name,
                g.country_name,
                SUM(f.impressions) as campaign_impressions,
                SUM(f.spend_usd) as campaign_spend,
                ROUND(SUM(f.clicks) / SUM(f.impressions), 4) as campaign_ctr,
                ROUND(SUM(f.conversions) / SUM(f.spend_usd), 4) as campaign_roas,
                AVG(f.effectiveness_score) as campaign_effectiveness
            FROM RAW.fact_ad_performance f
            JOIN RAW.dim_platforms p ON f.platform_id = p.platform_id
            JOIN RAW.dim_geography g ON f.geo_id = g.geo_id
            GROUP BY f.campaign_id, p.platform_name, g.country_name
            HAVING SUM(f.impressions) > 1000
            ORDER BY campaign_effectiveness DESC, campaign_spend DESC
            LIMIT 10
        """
    }
    
    # Run each query
    for query_name, sql in queries.items():
        run_query(conn, query_name, sql)
    
    print(f"\n{'='*60}")
    print("🎉 Portfolio Showcase Complete!")
    print("=" * 60)
    
    # Close connection
    conn.close()
    print("✅ Snowflake connection closed")

if __name__ == "__main__":
    main()
