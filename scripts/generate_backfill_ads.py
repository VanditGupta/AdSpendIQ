#!/usr/bin/env python3
"""
Ad Campaign Spend Tracker - Historical Data Backfill Generator

This script generates 300,000 rows of historical ad campaign data for portfolio demonstration.
Data is spread across the date range: 2024-08-01 to 2025-08-15.

Author: Data Engineer Portfolio
Date: 2025
"""

import pandas as pd
import random
from datetime import datetime, date, timedelta
from faker import Faker
import uuid
import os
from pathlib import Path

# Initialize Faker with consistent seed for reproducible results
fake = Faker()
Faker.seed(42)

def generate_historical_ad_data(start_date=None, end_date=None, total_rows=300000):
    """
    Generate historical fake ad campaign data across a date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format (defaults to 120 days ago)
        end_date (str): End date in YYYY-MM-DD format (defaults to today)
        total_rows (int): Total number of rows to generate
    
    Returns:
        pd.DataFrame: DataFrame containing historical fake ad campaign data
    """
    
    # Set default dates if not provided
    if end_date is None:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    if start_date is None:
        start_date = end_date - timedelta(days=120)  # Default to 120 days ago
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    # Calculate date range
    date_range = (end_date - start_date).days + 1
    
    # Calculate rows per day (with some variation)
    base_rows_per_day = total_rows // date_range
    remaining_rows = total_rows % date_range
    
    print(f"📅 Date range: {start_date} to {end_date} ({date_range} days)")
    print(f"📊 Base rows per day: {base_rows_per_day}")
    print(f"🔢 Remaining rows to distribute: {remaining_rows}")
    
    # Platform options with realistic distribution and performance characteristics
    platforms = ['Google', 'Facebook', 'LinkedIn', 'TikTok', 'Twitter']
    platform_weights = [0.45, 0.25, 0.15, 0.10, 0.05]  # More realistic distribution
    
    # Geographic options (major markets) with realistic performance
    countries = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'BR', 'MX', 'NL', 'IT', 'ES', 'SE']
    country_weights = [0.35, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04, 0.08, 0.06, 0.05, 0.03, 0.03, 0.03, 0.03]
    
    # Device options with platform-specific preferences
    devices = ['mobile', 'desktop', 'tablet']
    
    # Campaign types with realistic objectives
    campaign_types = ['brand_awareness', 'conversions', 'traffic', 'app_installs', 'lead_generation', 'retargeting', 'video_views']
    
    # Ad formats for more granular data
    ad_formats = ['search', 'display', 'video', 'social', 'shopping', 'remarketing']
    
    # Generate a smaller set of campaign IDs with realistic naming
    num_campaigns = min(2000, total_rows // 150)  # 2000 campaigns for backfill, ~150 rows per campaign
    campaign_ids = []
    
    # Create realistic campaign names
    campaign_prefixes = ['Q1_', 'Q2_', 'Q3_', 'Q4_', 'Holiday_', 'Summer_', 'Winter_', 'Spring_', 'BackToSchool_', 'BlackFriday_', 'CyberMonday_', 'Valentines_', 'Easter_', 'Memorial_', 'Independence_', 'Labor_', 'Thanksgiving_', 'Christmas_']
    campaign_suffixes = ['_Brand', '_Conversion', '_Traffic', '_App', '_Lead', '_Retarget', '_Video', '_Shopping', '_Awareness']
    
    for i in range(num_campaigns):
        prefix = random.choice(campaign_prefixes)
        suffix = random.choice(campaign_suffixes)
        campaign_id = f"{prefix}{fake.word().title()}{suffix}_{str(i+1).zfill(4)}"
        campaign_ids.append(campaign_id)
    
    # Seasonal factors (higher spend during holidays, lower during summer)
    def get_seasonal_multiplier(target_date):
        month = target_date.month
        if month in [11, 12]:  # Holiday season
            return 1.3
        elif month in [6, 7, 8]:  # Summer months
            return 0.8
        elif month in [1, 2]:  # Post-holiday
            return 0.9
        else:
            return 1.0
    
    all_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Calculate rows for this date (with some randomness)
        seasonal_mult = get_seasonal_multiplier(current_date)
        rows_today = int(base_rows_per_day * seasonal_mult * random.uniform(0.8, 1.2))
        
        # Add remaining rows to first few dates
        if remaining_rows > 0:
            rows_today += 1
            remaining_rows -= 1
        
        print(f"📅 {current_date}: Generating {rows_today} rows")
        
        for _ in range(rows_today):
            # Select campaign ID from the pool
            campaign_id = random.choice(campaign_ids)
            
            # Select platform with weighted distribution
            platform = random.choices(platforms, weights=platform_weights)[0]
            
            # Select country with weighted distribution
            geo = random.choices(countries, weights=country_weights)[0]
            
            # Select device with platform-specific preferences
            if platform == 'TikTok':
                device_weights = [0.85, 0.10, 0.05]  # TikTok is very mobile-heavy
            elif platform == 'LinkedIn':
                device_weights = [0.45, 0.50, 0.05]  # LinkedIn has more desktop usage
            else:
                device_weights = [0.65, 0.30, 0.05]  # General mobile-first
            
            device = random.choices(devices, weights=device_weights)[0]
            
            # Select campaign type and ad format
            campaign_type = random.choice(campaign_types)
            ad_format = random.choice(ad_formats)
            
            # Generate realistic impressions based on platform, geo, and campaign type
            base_impressions = {
                'Google': (8000, 60000),
                'Facebook': (5000, 45000),
                'LinkedIn': (2000, 30000),
                'TikTok': (3000, 40000),
                'Twitter': (2000, 25000)
            }
            
            min_imp, max_imp = base_impressions[platform]
            
            # Adjust for country (US gets higher volume)
            if geo == 'US':
                min_imp = int(min_imp * 1.2)
                max_imp = int(max_imp * 1.3)
            elif geo in ['IN', 'BR', 'MX']:  # Emerging markets
                min_imp = int(min_imp * 0.7)
                max_imp = int(max_imp * 0.8)
            
            # Adjust for campaign type
            if campaign_type == 'brand_awareness':
                min_imp = int(min_imp * 1.3)  # Brand campaigns get more impressions
                max_imp = int(max_imp * 1.4)
            elif campaign_type == 'conversions':
                min_imp = int(min_imp * 0.8)  # Conversion campaigns are more targeted
                max_imp = int(max_imp * 0.9)
            
            # Apply seasonal multiplier
            seasonal_mult = get_seasonal_multiplier(current_date)
            min_imp = int(min_imp * seasonal_mult)
            max_imp = int(max_imp * seasonal_mult)
            
            impressions = random.randint(min_imp, max_imp)
            
            # Generate realistic CTR based on platform, format, and device
            base_ctr = {
                'Google': {'search': 0.025, 'display': 0.008, 'video': 0.015, 'shopping': 0.020, 'remarketing': 0.018, 'social': 0.012},
                'Facebook': {'social': 0.012, 'video': 0.018, 'display': 0.008, 'search': 0.015, 'shopping': 0.016, 'remarketing': 0.014},
                'LinkedIn': {'social': 0.008, 'video': 0.012, 'display': 0.006, 'search': 0.010, 'remarketing': 0.009},
                'TikTok': {'video': 0.020, 'social': 0.015, 'display': 0.010, 'shopping': 0.018},
                'Twitter': {'social': 0.010, 'video': 0.015, 'display': 0.008, 'search': 0.012}
            }
            
            # Ensure ad_format exists for the platform, otherwise use a default
            if platform in base_ctr and ad_format in base_ctr[platform]:
                ctr_rate = base_ctr[platform][ad_format]
            else:
                # Map missing formats to closest available
                format_mapping = {
                    'search': 'search' if 'search' in base_ctr.get(platform, {}) else 'social',
                    'display': 'display',
                    'video': 'video',
                    'social': 'social',
                    'shopping': 'shopping' if 'shopping' in base_ctr.get(platform, {}) else 'display',
                    'remarketing': 'remarketing' if 'remarketing' in base_ctr.get(platform, {}) else 'display'
                }
                mapped_format = format_mapping[ad_format]
                ctr_rate = base_ctr[platform].get(mapped_format, 0.010)
            
            # Adjust CTR for device (mobile typically has lower CTR)
            if device == 'mobile':
                ctr_rate *= 0.8
            elif device == 'desktop':
                ctr_rate *= 1.2
            
            # Add some randomness to CTR
            ctr_rate *= random.uniform(0.7, 1.3)
            ctr_rate = max(0.001, min(0.05, ctr_rate))  # Keep within realistic bounds
            
            clicks = max(0, int(impressions * ctr_rate))
            
            # Generate realistic spend based on platform, geo, and performance
            base_cpc = {
                'Google': 1.50, 'Facebook': 1.20, 'LinkedIn': 5.80, 'TikTok': 1.00, 'Twitter': 1.40
            }
            
            cpc = base_cpc[platform]
            
            # Adjust CPC for country
            if geo == 'US':
                cpc *= 1.5
            elif geo in ['IN', 'BR', 'MX']:
                cpc *= 0.6
            
            # Adjust CPC for campaign type
            if campaign_type == 'conversions':
                cpc *= 1.3  # Conversion campaigns cost more
            elif campaign_type == 'brand_awareness':
                cpc *= 0.8  # Brand campaigns are cheaper
            
            # Calculate spend based on clicks and CPC
            spend_usd = clicks * cpc * random.uniform(0.8, 1.2)  # Add some variance
            
            # Generate conversions with realistic CVR
            base_cvr = {
                'Google': 0.025, 'Facebook': 0.020, 'LinkedIn': 0.035, 'TikTok': 0.015, 'Twitter': 0.018
            }
            
            cvr_rate = base_cvr[platform]
            
            # Adjust CVR for campaign type
            if campaign_type == 'conversions':
                cvr_rate *= 1.4  # Conversion campaigns have higher CVR
            elif campaign_type == 'brand_awareness':
                cvr_rate *= 1.3  # Brand campaigns have lower CVR
            
            # Adjust CVR for device
            if device == 'desktop':
                cvr_rate *= 1.2  # Desktop typically has higher conversion rates
            
            # Add randomness and ensure realistic bounds
            cvr_rate *= random.uniform(0.6, 1.4)
            cvr_rate = max(0.001, min(0.15, cvr_rate))
            
            conversions = max(0, int(clicks * cvr_rate))
            
            # Add realistic data quality issues
            if random.random() < 0.05:  # 5% chance of zero impressions (tracking issues)
                impressions = 0
                clicks = 0
                conversions = 0
                spend_usd = 0
            
            if random.random() < 0.08:  # 8% chance of zero clicks (poor performance)
                clicks = 0
                conversions = 0
                spend_usd = spend_usd * 0.1  # Minimal spend for poor performance
            
            # Create row data with raw metrics only (as sent by ad platforms)
            row = {
                'campaign_id': campaign_id,
                'platform': platform,
                'date': current_date,
                'geo': geo,
                'device': device,
                'campaign_type': campaign_type,
                'ad_format': ad_format,
                'impressions': impressions,
                'clicks': clicks,
                'spend_usd': round(max(0, spend_usd), 2),
                'conversions': conversions
            }
            
            all_data.append(row)
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(all_data)

def save_backfill_data(df, filename='ads_backfill.csv'):
    """
    Save the generated historical data to CSV file in the data/raw directory.
    
    Args:
        df (pd.DataFrame): DataFrame to save
        filename (str): Output filename
    
    Returns:
        str: Path to the saved file
    """
    
    # Create data directory if it doesn't exist
    data_dir = Path('data/raw/historical')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filepath
    filepath = data_dir / filename
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Generated {len(df):,} rows of historical ad data")
    print(f"📁 Saved to: {filepath}")
    print(f"📊 Data summary:")
    print(f"   - Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   - Platforms: {df['platform'].value_counts().to_dict()}")
    print(f"   - Countries: {df['geo'].value_counts().head(5).to_dict()}")
    print(f"   - Devices: {df['device'].value_counts().to_dict()}")
    print(f"   - Campaign types: {df['campaign_type'].value_counts().to_dict()}")
    print(f"   - Ad formats: {df['ad_format'].value_counts().to_dict()}")
    print(f"   - Total spend: ${df['spend_usd'].sum():,.2f}")
    print(f"   - Total impressions: {df['impressions'].sum():,}")
    print(f"   - Total clicks: {df['clicks'].sum():,}")
    print(f"   - Total conversions: {df['conversions'].sum():,}")
    
    return str(filepath)

def main():
    """Main function to generate and save historical ad data."""
    
    print("🚀 Ad Campaign Spend Tracker - Historical Data Backfill Generator")
    print("=" * 70)
    
    # Generate historical data - starting from 120 days ago to ensure we get enough data
    # while staying within reasonable retention limits
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=120)  # 120 days ago
    
    print(f"📅 Generating data from {start_date} to {end_date}")
    print(f"📊 Target: 300,000 rows across {end_date - start_date} days")
    
    df = generate_historical_ad_data(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        total_rows=300000
    )
    
    # Save to CSV
    filepath = save_backfill_data(df)
    
    print("\n🎯 Historical data generation complete!")
    print(f"📈 Ready for processing in your data pipeline")
    print(f"💡 This file can be used as initial seed data for Snowflake/dbt")

if __name__ == "__main__":
    main()
