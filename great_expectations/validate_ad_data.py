#!/usr/bin/env python3
"""
Great Expectations Data Validation Script
Validates ad campaign data quality using Great Expectations
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

def validate_data_quality(df):
    """Validate data quality using basic checks"""
    print("\n🔍 Validating Data Quality...")
    print("=" * 50)
    
    # Convert column names to lowercase for consistency
    df.columns = df.columns.str.lower()
    
    # Debug: Show actual columns
    print(f"📋 Actual columns in data: {list(df.columns)}")
    print(f"📊 Data shape: {df.shape}")
    print(f"📋 First few rows:")
    print(df.head())
    
    validation_results = []
    
    # 1. Schema validation
    print("\n📋 Schema Validation:")
    required_columns = [
        'campaign_id', 'platform', 'date', 'geo', 'device',
        'campaign_type', 'ad_format', 'impressions', 'clicks',
        'spend_usd', 'conversions'
    ]
    
    for col in required_columns:
        if col in df.columns:
            print(f"   ✅ {col}: Present")
            validation_results.append(True)
        else:
            print(f"   ❌ {col}: Missing")
            validation_results.append(False)
    
    # 2. Data type validation
    print("\n🔧 Data Type Validation:")
    expected_types = {
        'campaign_id': 'object',
        'platform': 'object',
        'date': 'object',
        'geo': 'object',
        'device': 'object',
        'campaign_type': 'object',
        'ad_format': 'object',
        'impressions': ['int64', 'int32'],
        'clicks': ['int64', 'int32'],
        'spend_usd': ['float64', 'float32'],
        'conversions': ['int64', 'int32']
    }
    
    for col, expected_type in expected_types.items():
        if col in df.columns:
            if isinstance(expected_type, list):
                if df[col].dtype in expected_type:
                    print(f"   ✅ {col}: Correct type ({df[col].dtype})")
                    validation_results.append(True)
                else:
                    print(f"   ❌ {col}: Wrong type ({df[col].dtype}, expected {expected_type})")
                    validation_results.append(False)
            else:
                if df[col].dtype == expected_type:
                    print(f"   ✅ {col}: Correct type ({df[col].dtype})")
                    validation_results.append(True)
                else:
                    print(f"   ❌ {col}: Wrong type ({df[col].dtype}, expected {expected_type})")
                    validation_results.append(False)
    
    # 3. Value validation
    print("\n📊 Value Validation:")
    
    # Platform values
    if 'platform' in df.columns:
        valid_platforms = ['Google', 'Facebook', 'LinkedIn', 'TikTok', 'Twitter']
        platform_check = all(platform in valid_platforms for platform in df['platform'].unique())
        print(f"   {'✅' if platform_check else '❌'} Platforms: Valid values")
        validation_results.append(platform_check)
    else:
        print("   ⚠️ Platform column not available")
        validation_results.append(False)
    
    # Geo values
    if 'geo' in df.columns:
        valid_geos = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'BR', 'MX', 'NL', 'IT', 'ES', 'SE']
        geo_check = all(geo in valid_geos for geo in df['geo'].unique())
        print(f"   {'✅' if geo_check else '❌'} Geography: Valid values")
        validation_results.append(geo_check)
    else:
        print("   ⚠️ Geo column not available")
        validation_results.append(False)
    
    # Device values
    if 'device' in df.columns:
        valid_devices = ['mobile', 'desktop', 'tablet']
        device_check = all(device in valid_devices for device in df['device'].unique())
        print(f"   {'✅' if device_check else '❌'} Devices: Valid values")
        validation_results.append(device_check)
    else:
        print("   ⚠️ Device column not available")
        validation_results.append(False)
    
    # 4. Business logic validation
    print("\n💼 Business Logic Validation:")
    
    # Non-negative values
    if all(col in df.columns for col in ['impressions', 'clicks', 'spend_usd', 'conversions']):
        non_negative_check = all(df['impressions'] >= 0) and all(df['clicks'] >= 0) and all(df['spend_usd'] >= 0) and all(df['conversions'] >= 0)
        print(f"   {'✅' if non_negative_check else '❌'} Non-negative values")
        validation_results.append(non_negative_check)
        
        # Business rules
        business_rule_check = all(df['impressions'] >= df['clicks']) and all(df['clicks'] >= df['conversions'])
        print(f"   {'✅' if business_rule_check else '❌'} Business rules (impressions ≥ clicks ≥ conversions)")
        validation_results.append(business_rule_check)
    else:
        print("   ⚠️ Required numeric columns not available for business logic validation")
        validation_results.extend([False, False])
    
    # 5. Data volume validation
    print("\n📈 Data Volume Validation:")
    
    volume_check = 1000 <= len(df) <= 10000000
    print(f"   {'✅' if volume_check else '❌'} Record count: {len(df):,} (should be 1K-10M)")
    validation_results.append(volume_check)
    
    # 6. Summary
    print("\n📋 Validation Summary:")
    print("=" * 50)
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All validations passed! Data quality is excellent!")
        return True
    else:
        print(f"\n⚠️ {total - passed} validations failed. Review the results above.")
        return False

def main():
    """Main validation function"""
    print("🚀 Great Expectations Data Validation")
    print("=" * 40)
    
    try:
        # Get data from Snowflake for validation
        from snowflake.connector import connect
        
        print("🔌 Connecting to Snowflake...")
        conn = connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT').split('.')[0],
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
        )
        
        # Query sample data for validation
        print("📊 Querying sample data...")
        query = "SELECT * FROM RAW.ad_data LIMIT 1000"
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"📊 Loaded {len(df)} records for validation")
        
        # Run validation
        success = validate_data_quality(df)
        
        print("\n📚 Next steps:")
        print("1. Review validation results")
        print("2. Fix any data quality issues")
        print("3. Re-run validation")
        print("4. Set up automated validation in your pipeline")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Validation process failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
