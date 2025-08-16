#!/usr/bin/env python3
"""
PyTest tests for data generation functionality
Tests data quality, business logic, and generation functions
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, date, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_fake_ads import generate_fake_ad_data
from scripts.generate_backfill_ads import generate_historical_ad_data

class TestDataGeneration:
    """Test class for data generation functionality"""
    
    def test_generate_fake_ad_data_structure(self):
        """Test that fake ad data has correct structure"""
        df = generate_fake_ad_data()
        
        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check required columns
        required_columns = [
            'campaign_id', 'platform', 'date', 'geo', 'device',
            'campaign_type', 'ad_format', 'impressions', 'clicks',
            'spend_usd', 'conversions'
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_generate_fake_ad_data_types(self):
        """Test that fake ad data has correct data types"""
        df = generate_fake_ad_data()
        
        # Check data types
        assert df['campaign_id'].dtype == 'object'  # String
        assert df['platform'].dtype == 'object'     # String
        assert df['date'].dtype == 'object'         # String or datetime
        assert df['geo'].dtype == 'object'          # String
        assert df['device'].dtype == 'object'       # String
        assert df['campaign_type'].dtype == 'object' # String
        assert df['ad_format'].dtype == 'object'    # String
        assert df['impressions'].dtype in ['int64', 'int32']  # Integer
        assert df['clicks'].dtype in ['int64', 'int32']      # Integer
        assert df['spend_usd'].dtype in ['float64', 'float32'] # Float
        assert df['conversions'].dtype in ['int64', 'int32']   # Integer
    
    def test_generate_fake_ad_data_values(self):
        """Test that fake ad data has valid values"""
        df = generate_fake_ad_data()
        
        # Check platform values
        valid_platforms = ['Google', 'Facebook', 'LinkedIn', 'TikTok', 'Twitter']
        assert all(platform in valid_platforms for platform in df['platform'].unique())
        
        # Check geo values
        valid_geos = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'BR', 'MX', 'NL', 'IT', 'ES', 'SE']
        assert all(geo in valid_geos for geo in df['geo'].unique())
        
        # Check device values
        valid_devices = ['mobile', 'desktop', 'tablet']
        assert all(device in valid_devices for device in df['device'].unique())
        
        # Check campaign type values
        valid_campaign_types = [
            'brand_awareness', 'conversions', 'traffic', 'app_installs',
            'lead_generation', 'retargeting', 'video_views'
        ]
        assert all(ct in valid_campaign_types for ct in df['campaign_type'].unique())
        
        # Check ad format values
        valid_ad_formats = ['search', 'display', 'video', 'social', 'shopping', 'remarketing']
        assert all(af in valid_ad_formats for af in df['ad_format'].unique())
    
    def test_generate_fake_ad_data_ranges(self):
        """Test that fake ad data has reasonable value ranges"""
        df = generate_fake_ad_data()
        
        # Check numeric ranges
        assert all(df['impressions'] >= 0), "Impressions should be non-negative"
        assert all(df['clicks'] >= 0), "Clicks should be non-negative"
        assert all(df['spend_usd'] >= 0), "Spend should be non-negative"
        assert all(df['conversions'] >= 0), "Conversions should be non-negative"
        
        # Check business logic
        assert all(df['impressions'] >= df['clicks']), "Impressions should >= clicks"
        assert all(df['clicks'] >= df['conversions']), "Clicks should >= conversions"
        
        # Check reasonable upper bounds
        assert all(df['impressions'] <= 1000000), "Impressions should be reasonable"
        assert all(df['clicks'] <= 100000), "Clicks should be reasonable"
        assert all(df['spend_usd'] <= 100000), "Spend should be reasonable"
        assert all(df['conversions'] <= 10000), "Conversions should be reasonable"
    
    def test_generate_fake_ad_data_campaign_distribution(self):
        """Test that fake ad data has reasonable campaign distribution"""
        df = generate_fake_ad_data()
        
        # Check that we have multiple campaigns (realistic scenario)
        unique_campaigns = df['campaign_id'].nunique()
        assert unique_campaigns > 1, "Should have multiple campaigns"
        assert unique_campaigns <= 500, "Should not have too many campaigns"
        
        # Check campaign ID format (should contain campaign prefixes)
        campaign_id_prefixes = ['Q1_', 'Q2_', 'Q3_', 'Q4_', 'Holiday_', 'Summer_', 'Winter_', 'Spring_', 'BackToSchool_', 'BlackFriday_']
        for campaign_id in df['campaign_id']:
            assert any(prefix in campaign_id for prefix in campaign_id_prefixes), \
                f"Campaign ID {campaign_id} should contain campaign prefix"
    
    def test_generate_fake_ad_data_date(self):
        """Test that fake ad data has correct date format"""
        df = generate_fake_ad_data()
        
        # Check date format - handle both string and datetime.date types
        for date_val in df['date']:
            if isinstance(date_val, str):
                try:
                    datetime.strptime(date_val, '%Y-%m-%d')
                except ValueError:
                    pytest.fail(f"Invalid date string format: {date_val}")
            elif isinstance(date_val, date):
                # This is fine - datetime.date objects are valid
                pass
            else:
                pytest.fail(f"Unexpected date type: {type(date_val)} for value: {date_val}")
        
        # Check that all dates are the same (daily data)
        unique_dates = df['date'].unique()
        assert len(unique_dates) == 1, "Daily data should have only one date"
        
        # Check that date is today or recent
        today = datetime.now().date()
        if isinstance(unique_dates[0], str):
            data_date = datetime.strptime(unique_dates[0], '%Y-%m-%d').date()
        else:
            data_date = unique_dates[0]
        assert (today - data_date).days <= 1, "Data should be from today or yesterday"
    
    def test_generate_historical_ad_data_structure(self):
        """Test that historical ad data has correct structure"""
        df = generate_historical_ad_data()
        
        # Check basic structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        
        # Check required columns
        required_columns = [
            'campaign_id', 'platform', 'date', 'geo', 'device',
            'campaign_type', 'ad_format', 'impressions', 'clicks',
            'spend_usd', 'conversions'
        ]
        
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"
    
    def test_generate_historical_ad_data_date_range(self):
        """Test that historical ad data has correct date range"""
        df = generate_historical_ad_data()
        
        # Check date range
        dates = pd.to_datetime(df['date'])
        min_date = dates.min()
        max_date = dates.max()
        
        # Should cover multiple days
        assert (max_date - min_date).days > 0, "Historical data should cover multiple days"
        
        # Should be within reasonable range (not too old)
        today = datetime.now().date()
        assert (today - max_date.date()).days <= 120, "Historical data should not be too old"
    
    def test_data_quality_business_rules(self):
        """Test business logic and data quality rules"""
        df = generate_fake_ad_data()
        
        # Business rule: CTR should be reasonable (0-100%)
        df['ctr'] = df['clicks'] / df['impressions'].replace(0, 1)
        assert all(df['ctr'] <= 1.0), "CTR should not exceed 100%"
        assert all(df['ctr'] >= 0.0), "CTR should be non-negative"
        
        # Business rule: CPC should be reasonable (adjusted for realistic values)
        df['cpc'] = df['spend_usd'] / df['clicks'].replace(0, 1)
        assert all(df['cpc'] >= 0.0), "CPC should be non-negative"
        assert all(df['cpc'] <= 1000.0), "CPC should be reasonable (allowing for high-value campaigns)"
        
        # Business rule: CVR should be reasonable (0-100%)
        df['cvr'] = df['conversions'] / df['clicks'].replace(0, 1)
        assert all(df['cvr'] <= 1.0), "CVR should not exceed 100%"
        assert all(df['cvr'] >= 0.0), "CVR should be non-negative"
    
    def test_data_volume_consistency(self):
        """Test that data volume is consistent and reasonable"""
        df = generate_fake_ad_data()
        
        # Should generate reasonable number of records
        assert 1000 <= len(df) <= 10000, "Daily data should have reasonable volume"
        
        # Should have good distribution across dimensions
        assert len(df['platform'].unique()) >= 4, "Should cover most platforms"
        assert len(df['geo'].unique()) >= 10, "Should cover most geographies"
        assert len(df['device'].unique()) == 3, "Should cover all device types"
        assert len(df['campaign_type'].unique()) >= 5, "Should cover most campaign types"
        assert len(df['ad_format'].unique()) >= 4, "Should cover most ad formats"

if __name__ == "__main__":
    pytest.main([__file__])
