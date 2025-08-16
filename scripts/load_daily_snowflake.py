#!/usr/bin/env python3
"""
Daily Ad Data Loader for Snowflake

This script loads daily generated ad campaign data into Snowflake.
It's designed to be called from the Airflow DAG after data generation.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.load_backfill_to_snowflake import create_snowflake_connection, load_daily_data
import pandas as pd

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_daily_to_snowflake(daily_file_path: str) -> int:
    """
    Load daily ad data file to Snowflake with duplicate prevention.
    
    Args:
        daily_file_path (str): Path to the daily CSV file
        
    Returns:
        int: Number of rows loaded (excluding duplicates)
        
    Raises:
        FileNotFoundError: If the daily file doesn't exist
        Exception: For Snowflake connection or loading errors
    """
    try:
        # Validate file exists
        if not Path(daily_file_path).exists():
            raise FileNotFoundError(f"Daily file not found: {daily_file_path}")
        
        logger.info(f"📁 Loading daily file: {daily_file_path}")
        
        # Load the daily data to Snowflake with duplicate prevention
        rows_loaded = load_daily_data_with_dedup(daily_file_path)
        
        logger.info(f"✅ Successfully loaded {rows_loaded:,} rows to Snowflake (duplicates prevented)")
        return rows_loaded
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load daily data to Snowflake: {e}")
        raise

def load_daily_data_with_dedup(daily_file_path: str) -> int:
    """
    Load daily data to Snowflake with duplicate prevention.
    
    Args:
        daily_file_path (str): Path to the daily CSV file
        
    Returns:
        int: Number of rows actually loaded (excluding duplicates)
    """
    try:
        # Read the daily data
        df = pd.read_csv(daily_file_path)
        logger.info(f"📖 Read {len(df)} rows from {daily_file_path}")
        
        # Connect to Snowflake
        conn = create_snowflake_connection()
        cursor = conn.cursor()
        
        try:
            # Check for existing data with the same date and campaign_id
            # This prevents duplicates if the script is run multiple times
            date_from_file = df['date'].iloc[0]  # All rows have same date
            
            # Get existing campaign_ids for this date
            cursor.execute("""
                SELECT DISTINCT campaign_id 
                FROM raw.ad_data 
                WHERE date = %s
            """, (date_from_file,))
            
            existing_campaign_ids = {row[0] for row in cursor.fetchall()}
            logger.info(f"📊 Found {len(existing_campaign_ids)} existing campaign IDs for {date_from_file}")
            
            # Filter out rows that would create duplicates
            df_filtered = df[~df['campaign_id'].isin(existing_campaign_ids)]
            
            if len(df_filtered) == 0:
                logger.info("✅ No new data to load - all rows already exist")
                return 0
            
            if len(df_filtered) < len(df):
                logger.info(f"🔄 Filtered out {len(df) - len(df_filtered)} duplicate rows")
            
            # Load the filtered data
            rows_loaded = load_daily_data_from_dataframe(df_filtered, conn)
            
            return rows_loaded
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Error in duplicate prevention: {e}")
        raise

def load_daily_data_from_dataframe(df: pd.DataFrame, conn) -> int:
    """
    Load data from DataFrame to Snowflake using COPY INTO.
    
    Args:
        df (pd.DataFrame): Data to load
        conn: Snowflake connection
        
    Returns:
        int: Number of rows loaded
    """
    try:
        if len(df) == 0:
            return 0
            
        cursor = conn.cursor()
        
        # Create a temporary stage name
        stage_name = f"TEMP_STAGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create temporary stage
            cursor.execute(f"CREATE TEMPORARY STAGE {stage_name}")
            logger.info(f"📁 Created temporary stage: {stage_name}")
            
            # Save DataFrame to temporary CSV
            temp_csv_path = f"/tmp/temp_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(temp_csv_path, index=False)
            
            # Upload to stage
            cursor.execute(f"PUT file://{temp_csv_path} @{stage_name}")
            logger.info(f"📤 Uploaded CSV file to stage: {stage_name}")
            
            # Load data using COPY INTO
            copy_sql = f"""
            COPY INTO raw.ad_data
            FROM @{stage_name}
            FILE_FORMAT = (TYPE = 'CSV', FIELD_DELIMITER = ',', SKIP_HEADER = 1)
            """
            
            cursor.execute(copy_sql)
            
            # Clean up temporary file
            import os
            os.remove(temp_csv_path)
            
            logger.info(f"✅ Successfully loaded {len(df)} rows using COPY INTO")
            return len(df)
            
        finally:
            # Clean up temporary stage
            cursor.execute(f"DROP STAGE IF EXISTS {stage_name}")
            logger.info(f"🧹 Cleaned up temporary stage: {stage_name}")
            
    except Exception as e:
        logger.error(f"❌ Error loading DataFrame to Snowflake: {e}")
        raise

def cleanup_duplicates_in_snowflake():
    """
    Clean up existing duplicates in the Snowflake table.
    This function can be run manually to fix existing duplicate data.
    """
    try:
        logger.info("🧹 Starting duplicate cleanup in Snowflake...")
        
        conn = create_snowflake_connection()
        cursor = conn.cursor()
        
        try:
            # Create a temporary table with deduplicated data
            cursor.execute("""
                CREATE OR REPLACE TEMPORARY TABLE temp_dedup AS
                SELECT * FROM (
                    SELECT *,
                           ROW_NUMBER() OVER (
                               PARTITION BY campaign_id, date, platform, geo, device, campaign_type, ad_format
                               ORDER BY created_at DESC
                           ) as rn
                    FROM raw.ad_data
                ) ranked
                WHERE rn = 1
            """)
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM raw.ad_data")
            original_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM temp_dedup")
            deduped_count = cursor.fetchone()[0]
            
            duplicates_removed = original_count - deduped_count
            
            if duplicates_removed > 0:
                # Replace the original table with deduplicated data
                cursor.execute("TRUNCATE TABLE raw.ad_data")
                cursor.execute("INSERT INTO raw.ad_data SELECT * FROM temp_dedup")
                
                logger.info(f"✅ Cleaned up {duplicates_removed} duplicate rows")
                logger.info(f"📊 Original: {original_count} rows, After cleanup: {deduped_count} rows")
            else:
                logger.info("✅ No duplicates found - table is clean")
                
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Error cleaning up duplicates: {e}")
        raise

def main():
    """Main function for standalone execution."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python load_daily_snowflake.py <daily_file_path>")
        print("  python load_daily_snowflake.py --cleanup")
        print("\nExamples:")
        print("  python load_daily_snowflake.py data/raw/daily/2025/08/ads_2025-08-15.csv")
        print("  python load_daily_snowflake.py --cleanup")
        sys.exit(1)
    
    if sys.argv[1] == "--cleanup":
        try:
            cleanup_duplicates_in_snowflake()
            print("✅ Duplicate cleanup completed successfully!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            sys.exit(1)
    
    daily_file_path = sys.argv[1]
    
    try:
        rows_loaded = load_daily_to_snowflake(daily_file_path)
        print(f"✅ Success! Loaded {rows_loaded:,} rows to Snowflake")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
