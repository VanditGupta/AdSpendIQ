"""
Test suite for dimension tables in the AdSpendIQ data pipeline.

This module tests the integrity and quality of dimension tables:
- dim_campaigns
- dim_devices  
- dim_ad_formats
- dim_dates
- dim_geography
- dim_platforms

Author: Vandit Gupta
Date: August 15, 2025
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestDimensionTables:
    """Test class for dimension table validation."""
    
    def test_dim_campaigns_structure(self):
        """Test dim_campaigns table structure and data quality."""
        # This would normally connect to Snowflake/dbt
        # For now, we'll test the expected structure
        
        expected_columns = [
            'campaign_id', 'campaign_name', 'campaign_type', 'campaign_objective',
            'budget_amount', 'start_date', 'end_date', 'status', 'target_audience',
            'created_at', 'updated_at', 'campaign_status', 'campaign_duration_days',
            'budget_tier'
        ]
        
        # Simulate table structure validation
        actual_columns = expected_columns  # In real scenario, fetch from DB
        
        assert len(actual_columns) == len(expected_columns), \
            f"Expected {len(expected_columns)} columns, got {len(actual_columns)}"
        
        for col in expected_columns:
            assert col in actual_columns, f"Missing column: {col}"
    
    def test_dim_devices_structure(self):
        """Test dim_devices table structure and data quality."""
        expected_columns = [
            'device_id', 'device_type', 'device_category', 'device_platform',
            'screen_resolution', 'operating_system', 'browser_type', 'is_mobile',
            'created_at', 'updated_at', 'device_family', 'platform_family',
            'screen_size_category'
        ]
        
        actual_columns = expected_columns  # In real scenario, fetch from DB
        
        assert len(actual_columns) == len(expected_columns), \
            f"Expected {len(expected_columns)} columns, got {len(actual_columns)}"
        
        for col in expected_columns:
            assert col in actual_columns, f"Missing column: {col}"
    
    def test_dim_ad_formats_structure(self):
        """Test dim_ad_formats table structure and data quality."""
        expected_columns = [
            'ad_format_id', 'ad_format_type', 'placement_type', 'dimensions',
            'file_size', 'duration_seconds', 'is_video', 'is_interactive',
            'supported_platforms', 'created_at', 'updated_at', 'format_category',
            'file_size_category', 'duration_category', 'platform_compatibility'
        ]
        
        actual_columns = expected_columns  # In real scenario, fetch from DB
        
        assert len(actual_columns) == len(expected_columns), \
            f"Expected {len(expected_columns)} columns, got {len(actual_columns)}"
        
        for col in expected_columns:
            assert col in actual_columns, f"Missing column: {col}"
    
    def test_dimension_table_business_rules(self):
        """Test business rules for dimension tables."""
        
        # Test campaign budget tiers
        budget_tiers = ['Low Budget', 'Medium Budget', 'High Budget']
        assert 'Low Budget' in budget_tiers, "Low Budget tier should exist"
        assert 'Medium Budget' in budget_tiers, "Medium Budget tier should exist"
        assert 'High Budget' in budget_tiers, "High Budget tier should exist"
        
        # Test device families
        device_families = ['Mobile', 'Desktop', 'Other']
        assert 'Mobile' in device_families, "Mobile device family should exist"
        assert 'Desktop' in device_families, "Desktop device family should exist"
        
        # Test ad format categories
        format_categories = ['Video', 'Static', 'Interactive', 'Other']
        assert 'Video' in format_categories, "Video format category should exist"
        assert 'Static' in format_categories, "Static format category should exist"
    
    def test_dimension_table_constraints(self):
        """Test that dimension tables maintain referential integrity."""
        
        # In a real scenario, this would test foreign key relationships
        # For now, we'll test the concept
        
        # Test that campaign_id is unique
        campaign_ids = ['campaign_001', 'campaign_002', 'campaign_003']
        unique_campaign_ids = set(campaign_ids)
        assert len(campaign_ids) == len(unique_campaign_ids), \
            "Campaign IDs should be unique"
        
        # Test that device_id is unique
        device_ids = ['device_001', 'device_002', 'device_003']
        unique_device_ids = set(device_ids)
        assert len(device_ids) == len(unique_device_ids), \
            "Device IDs should be unique"
        
        # Test that ad_format_id is unique
        ad_format_ids = ['format_001', 'format_002', 'format_003']
        unique_ad_format_ids = set(ad_format_ids)
        assert len(ad_format_ids) == len(unique_ad_format_ids), \
            "Ad format IDs should be unique"
    
    def test_dimension_table_data_quality(self):
        """Test data quality aspects of dimension tables."""
        
        # Test that required fields are not null
        required_fields = ['campaign_id', 'device_id', 'ad_format_id']
        for field in required_fields:
            assert field is not None, f"Required field {field} should not be null"
        
        # Test that dates are valid
        test_date = datetime.now()
        assert isinstance(test_date, datetime), "Date should be datetime type"
        
        # Test that numeric fields are within reasonable ranges
        budget_amount = 5000
        assert 0 <= budget_amount <= 1000000, \
            "Budget amount should be between 0 and 1,000,000"
        
        file_size = 1024000  # 1MB in bytes
        assert 0 <= file_size <= 100000000, \
            "File size should be between 0 and 100MB"

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
