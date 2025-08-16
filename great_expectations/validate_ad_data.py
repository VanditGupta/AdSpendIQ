#!/usr/bin/env python3
"""
Great Expectations Data Validation Script
Validates ad campaign data quality using Great Expectations
Saves results to timestamped text files for record keeping
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import io

# Load environment variables
load_dotenv('../.env')

class ValidationLogger:
    """Custom logger that captures output to both console and file"""
    
    def __init__(self):
        self.output_buffer = io.StringIO()
        self.console_output = []
        
    def log(self, message):
        """Log message to both console and buffer"""
        # Print to console
        print(message)
        
        # Store in buffer for file output
        self.output_buffer.write(message + '\n')
        self.console_output.append(message)
    
    def get_output(self):
        """Get all captured output"""
        return self.output_buffer.getvalue()
    
    def close(self):
        """Close the buffer"""
        self.output_buffer.close()

def save_validation_report(logger, success, validation_results):
    """Save validation results to a timestamped file"""
    try:
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), 'validation_reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data_quality_validation_{timestamp}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        # Create comprehensive report
        report_content = f"""Ad Campaign Data Quality Validation Report
{'=' * 60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'✅ PASSED' if success else '❌ FAILED'}

{logger.get_output()}

{'=' * 60}
Report saved to: {filepath}
"""
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.log(f"\n📁 Validation report saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.log(f"⚠️ Warning: Could not save report to file: {e}")
        return None

def validate_data_quality(df, logger):
    """Validate data quality using basic checks"""
    logger.log("\n🔍 Validating Data Quality...")
    logger.log("=" * 50)
    
    # Convert column names to lowercase for consistency
    df.columns = df.columns.str.lower()
    
    # Debug: Show actual columns
    logger.log(f"📋 Actual columns in data: {list(df.columns)}")
    logger.log(f"📊 Data shape: {df.shape}")
    logger.log(f"📋 First few rows:")
    logger.log(str(df.head()))
    
    validation_results = []
    
    # 1. Schema validation
    logger.log("\n📋 Schema Validation:")
    required_columns = [
        'campaign_id', 'platform', 'date', 'geo', 'device',
        'campaign_type', 'ad_format', 'impressions', 'clicks',
        'spend_usd', 'conversions'
    ]
    
    for col in required_columns:
        if col in df.columns:
            logger.log(f"   ✅ {col}: Present")
            validation_results.append(True)
        else:
            logger.log(f"   ❌ {col}: Missing")
            validation_results.append(False)
    
    # 2. Data type validation
    logger.log("\n🔧 Data Type Validation:")
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
                    logger.log(f"   ✅ {col}: Correct type ({df[col].dtype})")
                    validation_results.append(True)
                else:
                    logger.log(f"   ❌ {col}: Wrong type ({df[col].dtype}, expected {expected_type})")
                    validation_results.append(False)
            else:
                if df[col].dtype == expected_type:
                    logger.log(f"   ✅ {col}: Correct type ({df[col].dtype})")
                    validation_results.append(True)
                else:
                    logger.log(f"   ❌ {col}: Wrong type ({df[col].dtype}, expected {expected_type})")
                    validation_results.append(False)
    
    # 3. Value validation
    logger.log("\n📊 Value Validation:")
    
    # Platform values
    if 'platform' in df.columns:
        valid_platforms = ['Google', 'Facebook', 'LinkedIn', 'TikTok', 'Twitter']
        platform_check = all(platform in valid_platforms for platform in df['platform'].unique())
        logger.log(f"   {'✅' if platform_check else '❌'} Platforms: Valid values")
        validation_results.append(platform_check)
    else:
        logger.log("   ⚠️ Platform column not available")
        validation_results.append(False)
    
    # Geo values
    if 'geo' in df.columns:
        valid_geos = ['US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP', 'IN', 'BR', 'MX', 'NL', 'IT', 'ES', 'SE']
        geo_check = all(geo in valid_geos for geo in df['geo'].unique())
        logger.log(f"   {'✅' if geo_check else '❌'} Geography: Valid values")
        validation_results.append(geo_check)
    else:
        logger.log("   ⚠️ Geo column not available")
        validation_results.append(False)
    
    # Device values
    if 'device' in df.columns:
        valid_devices = ['mobile', 'desktop', 'tablet']
        device_check = all(device in valid_devices for device in df['device'].unique())
        logger.log(f"   {'✅' if device_check else '❌'} Devices: Valid values")
        validation_results.append(device_check)
    else:
        logger.log("   ⚠️ Device column not available")
        validation_results.append(False)
    
    # 4. Business logic validation
    logger.log("\n💼 Business Logic Validation:")
    
    # Non-negative values
    if all(col in df.columns for col in ['impressions', 'clicks', 'spend_usd', 'conversions']):
        non_negative_check = all(df['impressions'] >= 0) and all(df['clicks'] >= 0) and all(df['spend_usd'] >= 0) and all(df['conversions'] >= 0)
        logger.log(f"   {'✅' if non_negative_check else '❌'} Non-negative values")
        validation_results.append(non_negative_check)
        
        # Business rules
        business_rule_check = all(df['impressions'] >= df['clicks']) and all(df['clicks'] >= df['conversions'])
        logger.log(f"   {'✅' if business_rule_check else '❌'} Business rules (impressions ≥ clicks ≥ conversions)")
        validation_results.append(business_rule_check)
    else:
        logger.log("   ⚠️ Required numeric columns not available for business logic validation")
        validation_results.extend([False, False])
    
    # 5. Data volume validation
    logger.log("\n📈 Data Volume Validation:")
    
    volume_check = 1000 <= len(df) <= 10000000
    logger.log(f"   {'✅' if volume_check else '❌'} Record count: {len(df):,} (should be 1K-10M)")
    validation_results.append(volume_check)
    
    # 6. Summary
    logger.log("\n📋 Validation Summary:")
    logger.log("=" * 50)
    
    passed = sum(validation_results)
    total = len(validation_results)
    
    logger.log(f"✅ Passed: {passed}/{total}")
    logger.log(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        logger.log("\n🎉 All validations passed! Data quality is excellent!")
        return True, validation_results
    else:
        logger.log(f"\n⚠️ {total - passed} validations failed. Review the results above.")
        return False, validation_results

def main():
    """Main validation function"""
    # Initialize logger
    logger = ValidationLogger()
    
    logger.log("🚀 Great Expectations Data Validation")
    logger.log("=" * 40)
    
    try:
        # Get data from Snowflake for validation
        from snowflake.connector import connect
        
        logger.log("🔌 Connecting to Snowflake...")
        conn = connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT').split('.')[0],
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
        )
        
        # Query sample data for validation
        logger.log("📊 Querying sample data...")
        query = "SELECT * FROM RAW.ad_data LIMIT 1000"
        df = pd.read_sql(query, conn)
        conn.close()
        
        logger.log(f"📊 Loaded {len(df)} records for validation")
        
        # Run validation
        success, validation_results = validate_data_quality(df, logger)
        
        logger.log("\n📚 Next steps:")
        logger.log("1. Review validation results")
        logger.log("2. Fix any data quality issues")
        logger.log("3. Re-run validation")
        logger.log("4. Set up automated validation in your pipeline")
        
        # Save validation report to file
        report_file = save_validation_report(logger, success, validation_results)
        
        # Clean up logger
        logger.close()
        
        return 0 if success else 1
        
    except Exception as e:
        logger.log(f"❌ Validation process failed: {e}")
        logger.close()
        return 1

if __name__ == "__main__":
    sys.exit(main())
