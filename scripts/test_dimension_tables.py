#!/usr/bin/env python3
"""
Test script for the new dimension tables in AdSpendIQ.

This script tests the newly created dimension tables:
- dim_campaigns
- dim_devices
- dim_ad_formats

Author: Vandit Gupta
Date: August 15, 2025
"""

import os
import sys
import subprocess
from pathlib import Path

def test_dbt_models():
    """Test that the new dimension tables can be built with dbt."""
    print("🏗️ Testing dbt model building for new dimension tables...")
    
    try:
        # Change to dbt directory
        dbt_dir = Path(__file__).parent.parent / 'dbt'
        
        # Test dbt parse to ensure models are valid
        print("📋 Parsing dbt models...")
        result = subprocess.run(
            ['dbt', 'parse'],
            cwd=dbt_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ dbt parse successful - all models are valid")
        else:
            print(f"❌ dbt parse failed: {result.stderr}")
            return False
        
        # Test dbt compile to ensure models can be compiled
        print("🔧 Compiling dbt models...")
        result = subprocess.run(
            ['dbt', 'compile'],
            cwd=dbt_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ dbt compile successful - all models can be compiled")
        else:
            print(f"❌ dbt compile failed: {result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing dbt models: {str(e)}")
        return False

def test_dimension_table_structure():
    """Test the structure of the new dimension tables."""
    print("\n📊 Testing dimension table structure...")
    
    # Test dim_campaigns
    print("🎯 Testing dim_campaigns structure...")
    campaigns_file = Path(__file__).parent.parent / 'dbt' / 'models' / 'dimensions' / 'dim_campaigns.sql'
    if campaigns_file.exists():
        print("✅ dim_campaigns.sql exists")
        
        # Check for key columns
        content = campaigns_file.read_text()
        required_columns = ['campaign_id', 'campaign_name', 'campaign_type', 'budget_amount']
        for col in required_columns:
            if col in content:
                print(f"   ✅ Contains {col}")
            else:
                print(f"   ❌ Missing {col}")
    else:
        print("❌ dim_campaigns.sql not found")
    
    # Test dim_devices
    print("📱 Testing dim_devices structure...")
    devices_file = Path(__file__).parent.parent / 'dbt' / 'models' / 'dimensions' / 'dim_devices.sql'
    if devices_file.exists():
        print("✅ dim_devices.sql exists")
        
        # Check for key columns
        content = devices_file.read_text()
        required_columns = ['device_id', 'device_type', 'is_mobile', 'device_family']
        for col in required_columns:
            if col in content:
                print(f"   ✅ Contains {col}")
            else:
                print(f"   ❌ Missing {col}")
    else:
        print("❌ dim_devices.sql not found")
    
    # Test dim_ad_formats
    print("🎨 Testing dim_ad_formats structure...")
    formats_file = Path(__file__).parent.parent / 'dbt' / 'models' / 'dimensions' / 'dim_ad_formats.sql'
    if formats_file.exists():
        print("✅ dim_ad_formats.sql exists")
        
        # Check for key columns
        content = formats_file.read_text()
        required_columns = ['ad_format_id', 'ad_format_type', 'is_video', 'format_category']
        for col in required_columns:
            if col in content:
                print(f"   ✅ Contains {col}")
            else:
                print(f"   ❌ Missing {col}")
    else:
        print("❌ dim_ad_formats.sql not found")

def test_schema_validation():
    """Test the schema.yml file for the new dimension tables."""
    print("\n📋 Testing schema validation...")
    
    schema_file = Path(__file__).parent.parent / 'dbt' / 'models' / 'dimensions' / 'schema.yml'
    if schema_file.exists():
        print("✅ schema.yml exists")
        
        # Check for dimension table definitions
        content = schema_file.read_text()
        required_tables = ['dim_campaigns', 'dim_devices', 'dim_ad_formats']
        for table in required_tables:
            if table in content:
                print(f"   ✅ Contains {table}")
            else:
                print(f"   ❌ Missing {table}")
    else:
        print("❌ schema.yml not found")

def main():
    """Main test function."""
    print("🧪 Testing New Dimension Tables in AdSpendIQ")
    print("=" * 60)
    
    # Test dbt models
    dbt_success = test_dbt_models()
    
    # Test table structure
    test_dimension_table_structure()
    
    # Test schema validation
    test_schema_validation()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    if dbt_success:
        print("✅ New dimension tables are ready for dbt!")
        print("🚀 You can now run: cd dbt && dbt run")
        print("🎯 Your star schema is now complete with 6 dimension tables!")
    else:
        print("❌ Some issues found with the new dimension tables")
        print("🔧 Please check the errors above")
    
    return 0 if dbt_success else 1

if __name__ == "__main__":
    sys.exit(main())
