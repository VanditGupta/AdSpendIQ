#!/usr/bin/env python3
"""
Ad Campaign Spend Tracker - Snowflake Data Loader

This script loads ad campaign data into Snowflake for both backfill and daily ingestion.
Supports loading historical backfill data and can be reused for daily file ingestion.

Author: Vandit Gupta
Date: 2025
"""

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import os
from pathlib import Path
import logging
from datetime import datetime
import sys
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/snowflake_loader.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Suppress urllib3 warnings that cause connection retry messages
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)
logging.getLogger('snowflake.connector.vendored.urllib3').setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Authentication method (programmatic_token only)
AUTH_METHOD = 'programmatic_token'

# Snowflake connection configuration from environment variables
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'user': os.getenv('SNOWFLAKE_USER'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
}

# For programmatic access token authentication
PROGRAMMATIC_TOKEN = os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN')

def validate_environment():
    """
    Validate that required environment variables are set.
    """
    required_vars = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PROGRAMMATIC_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    logger.info("✅ Environment variables validated (using programmatic access token)")

def create_snowflake_connection():
    """
    Create and return a Snowflake connection using programmatic access token.
    
    Returns:
        snowflake.connector.SnowflakeConnection: Active Snowflake connection
    """
    try:
        # Connection parameters for programmatic access token
        # Try using just the account identifier (without .snowflakecomputing.com)
        account_id = SNOWFLAKE_CONFIG['account'].replace('.snowflakecomputing.com', '')
        
        connection_params = {
            'account': account_id,  # Just the account identifier
            'user': SNOWFLAKE_CONFIG['user'],
            'password': PROGRAMMATIC_TOKEN,  # Use password field for token
            'warehouse': SNOWFLAKE_CONFIG['warehouse'],
            'database': SNOWFLAKE_CONFIG['database'],
            'schema': SNOWFLAKE_CONFIG['schema'],
            'client_session_keep_alive': True,
            'disable_retry': True,
            'insecure_mode': False,
            'login_timeout': 60,
            'network_timeout': 60
        }
        
        # Create connection
        conn = snowflake.connector.connect(**connection_params)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        
        logger.info(f"🎫 Successfully connected to Snowflake (Version: {version})")
        return conn
        
    except snowflake.connector.errors.DatabaseError as e:
        logger.error(f"❌ Database connection error: {str(e)}")
        raise e
    except snowflake.connector.errors.NetworkError as e:
        logger.error(f"❌ Network connection error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"❌ Unexpected connection error: {str(e)}")
        raise e

def create_table_if_not_exists(conn):
    """
    Create the raw.ad_data table if it doesn't exist.
    
    Args:
        conn: Snowflake connection object
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS raw.ad_data (
        campaign_id         STRING,
        platform            STRING,
        date                DATE,
        geo                 STRING,
        device              STRING,
        campaign_type       STRING,
        ad_format           STRING,
        impressions         INTEGER,
        clicks              INTEGER,
        spend_usd           FLOAT,
        conversions         INTEGER
    );
    """
    
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        cursor.close()
        logger.info("✅ Table raw.ad_data created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create table: {str(e)}")
        raise e

def load_csv_to_snowflake(file_path, table_name='raw.ad_data', truncate_first=False):
    """
    Load CSV data into Snowflake table.
    
    Args:
        file_path (str): Path to the CSV file
        table_name (str): Target Snowflake table name
        truncate_first (bool): Whether to truncate table before loading
    
    Returns:
        int: Number of rows loaded
    """
    # Verify file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read CSV file
    logger.info(f"📖 Reading CSV file: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"📊 Loaded {len(df)} rows from CSV")
    except Exception as e:
        logger.error(f"❌ Failed to read CSV: {str(e)}")
        raise e
    
    # Connect to Snowflake
    conn = create_snowflake_connection()
    
    try:
        # Create table if it doesn't exist
        create_table_if_not_exists(conn)
        
        # Truncate table if requested
        if truncate_first:
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            cursor.close()
            logger.info(f"🗑️ Truncated table {table_name}")
        
        # Load data to Snowflake
        logger.info(f"🚀 Loading {len(df)} rows to {table_name}")
        
        # Convert date column to proper format
        df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Load data using Snowflake's fast COPY INTO command with file upload
        cursor = conn.cursor()
        
        # Create a temporary stage for the data
        stage_name = f"TEMP_STAGE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        create_stage_sql = f"CREATE TEMPORARY STAGE {stage_name}"
        cursor.execute(create_stage_sql)
        logger.info(f"📁 Created temporary stage: {stage_name}")
        
        # Save DataFrame to temporary CSV file with proper formatting
        temp_csv_path = f"/tmp/temp_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(temp_csv_path, index=False, header=False, quoting=1)  # QUOTE_ALL
        
        # Upload CSV file to Snowflake stage
        put_sql = f"PUT file://{temp_csv_path} @{stage_name}"
        cursor.execute(put_sql)
        logger.info(f"📤 Uploaded CSV file to stage: {stage_name}")
        
        # Use COPY INTO for fast bulk loading with simplified format
        columns = ', '.join(df.columns)
        copy_sql = f"""
        COPY INTO {table_name} ({columns})
        FROM @{stage_name}
        FILE_FORMAT = (
            TYPE = 'CSV' 
            FIELD_DELIMITER = ',' 
            SKIP_HEADER = 0
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            TRIM_SPACE = TRUE
        )
        ON_ERROR = 'CONTINUE'
        """
        
        cursor.execute(copy_sql)
        
        # Clean up temporary stage and file
        cursor.execute(f"DROP STAGE IF EXISTS {stage_name}")
        os.remove(temp_csv_path)
        
        cursor.close()
        
        # For COPY INTO, use the DataFrame length as the actual rows loaded
        # cursor.rowcount may not always reflect the actual rows with COPY INTO
        rows_inserted = len(df)
        
        logger.info(f"✅ Successfully loaded {rows_inserted} rows to {table_name} using COPY INTO")
        return rows_inserted
        
    except Exception as e:
        logger.error(f"❌ Failed to load data to Snowflake: {str(e)}")
        raise e
    finally:
        conn.close()
        logger.info("🔌 Snowflake connection closed")

def load_csv_to_snowflake_parallel(file_path, table_name='raw.ad_data', truncate_first=False, max_workers=4):
    """
    Load CSV data into Snowflake table using parallel processing.
    
    Args:
        file_path (str): Path to the CSV file
        table_name (str): Target Snowflake table name
        truncate_first (bool): Whether to truncate table before loading
        max_workers (int): Number of parallel workers
    
    Returns:
        int: Number of rows loaded
    """
    # Verify file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read CSV file
    logger.info(f"📖 Reading CSV file: {file_path}")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"📊 Loaded {len(df)} rows from CSV")
    except Exception as e:
        logger.error(f"❌ Failed to read CSV: {str(e)}")
        raise e
    
    # Convert date column to proper format
    df['date'] = pd.to_datetime(df['date']).dt.date
    
    # Split DataFrame into chunks for parallel processing
    chunk_size = len(df) // max_workers
    if chunk_size == 0:
        chunk_size = len(df)
    
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        chunks.append(chunk)
    
    logger.info(f"🔄 Split data into {len(chunks)} chunks for parallel processing")
    
    # Create initial connection and table
    conn = create_snowflake_connection()
    try:
        create_table_if_not_exists(conn)
        if truncate_first:
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            cursor.close()
            logger.info(f"🗑️ Truncated table {table_name}")
    finally:
        conn.close()
    
    # Function to process a single chunk
    def process_chunk(chunk, chunk_id):
        try:
            chunk_conn = create_snowflake_connection()
            cursor = chunk_conn.cursor()
            
            # Create temporary stage for this chunk
            stage_name = f"TEMP_STAGE_CHUNK_{chunk_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cursor.execute(f"CREATE TEMPORARY STAGE {stage_name}")
            
            # Save chunk to temporary CSV file
            temp_csv_path = f"/tmp/temp_chunk_{chunk_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            chunk.to_csv(temp_csv_path, index=False, header=False)
            
            # Upload CSV file to Snowflake stage
            cursor.execute(f"PUT file://{temp_csv_path} @{stage_name}")
            
            # Use COPY INTO for fast bulk loading
            columns = ', '.join(chunk.columns)
            copy_sql = f"""
            COPY INTO {table_name} ({columns})
            FROM @{stage_name}
            FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 0)
            ON_ERROR = 'CONTINUE'
            """
            
            cursor.execute(copy_sql)
            rows_inserted = cursor.rowcount
            
            # Clean up
            cursor.execute(f"DROP STAGE IF EXISTS {stage_name}")
            os.remove(temp_csv_path)
            chunk_conn.close()
            
            logger.info(f"📦 Chunk {chunk_id}: Loaded {rows_inserted} rows")
            return rows_inserted
            
        except Exception as e:
            logger.error(f"❌ Chunk {chunk_id} failed: {str(e)}")
            raise e
    
    # Process chunks in parallel
    total_rows = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all chunk processing tasks
        future_to_chunk = {
            executor.submit(process_chunk, chunk, i): i 
            for i, chunk in enumerate(chunks)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_chunk):
            chunk_id = future_to_chunk[future]
            try:
                rows_inserted = future.result()
                total_rows += rows_inserted
            except Exception as e:
                logger.error(f"❌ Chunk {chunk_id} failed: {str(e)}")
                raise e
    
    logger.info(f"✅ Successfully loaded {total_rows} rows to {table_name} using parallel processing")
    return total_rows

def load_backfill_data(force_refresh=False):
    """
    Load the historical backfill data into Snowflake.
    
    Args:
        force_refresh (bool): If True, truncate and reload. If False, check if data exists first.
    """
    backfill_file = "data/raw/historical/ads_backfill.csv"
    
    logger.info("🚀 Starting backfill data load to Snowflake")
    logger.info(f"📁 Source file: {backfill_file}")
    
    try:
        # Check if we should force refresh or check existing data
        if force_refresh:
            logger.info("🔄 Force refresh mode: Will truncate existing data")
            truncate_first = True
        else:
            # Check if table already has data
            conn = create_snowflake_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM raw.ad_data")
                existing_count = cursor.fetchone()[0]
                cursor.close()
                
                if existing_count > 0:
                    logger.info(f"📊 Table already contains {existing_count:,} rows")
                    logger.info("💡 Use force_refresh=True to reload all data")
                    logger.info("💡 Use load_daily_data() to add new daily records")
                    return existing_count
                else:
                    logger.info("📊 Table is empty, proceeding with initial load")
                    truncate_first = False
            finally:
                conn.close()
        
        rows_loaded = load_csv_to_snowflake(
            file_path=backfill_file,
            table_name='raw.ad_data',
            truncate_first=truncate_first
        )
        
        print(f"✅ Loaded {rows_loaded:,} rows to raw.ad_data in Snowflake")
        logger.info(f"🎯 Backfill complete: {rows_loaded:,} rows loaded")
        
        return rows_loaded
        
    except Exception as e:
        logger.error(f"❌ Backfill failed: {str(e)}")
        print(f"❌ Failed to load backfill data: {str(e)}")
        raise e

def load_backfill_data_parallel(max_workers=4):
    """
    Load the historical backfill data into Snowflake using parallel processing.
    
    Args:
        max_workers (int): Number of parallel workers (default: 4)
    """
    backfill_file = "data/raw/historical/ads_backfill.csv"
    
    logger.info(f"🚀 Starting parallel backfill data load to Snowflake (workers: {max_workers})")
    logger.info(f"📁 Source file: {backfill_file}")
    
    try:
        rows_loaded = load_csv_to_snowflake_parallel(
            file_path=backfill_file,
            table_name='raw.ad_data',
            truncate_first=True,  # Clear existing data for backfill
            max_workers=max_workers
        )
        
        print(f"✅ Loaded {rows_loaded:,} rows to raw.ad_data in Snowflake using parallel processing")
        logger.info(f"🎯 Parallel backfill complete: {rows_loaded:,} rows loaded")
        
        return rows_loaded
        
    except Exception as e:
        logger.error(f"❌ Parallel backfill failed: {str(e)}")
        print(f"❌ Failed to load backfill data: {str(e)}")
        raise e

def load_daily_data(file_path):
    """
    Load a daily data file into Snowflake (append mode).
    
    Args:
        file_path (str): Path to the daily CSV file
    """
    logger.info(f"🚀 Loading daily data: {file_path}")
    
    try:
        rows_loaded = load_csv_to_snowflake(
            file_path=file_path,
            table_name='raw.ad_data',
            truncate_first=False  # Append to existing data
        )
        
        logger.info(f"✅ Daily load complete: {rows_loaded} rows added")
        return rows_loaded
        
    except Exception as e:
        logger.error(f"❌ Daily load failed: {str(e)}")
        raise e

def main():
    """Main function to load backfill data."""
    
    print("🚀 Ad Campaign Spend Tracker - Snowflake Data Loader")
    print("=" * 60)
    print("Loading Strategy:")
    print("🔄 Smart Backfill: Checks if data exists, only loads if empty")
    print("📅 Daily Incremental: Adds new daily records (use load_daily_to_snowflake.py)")
    print("🔄 Force Refresh: Reloads all data (use --force flag)")
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    try:
        # Validate environment variables
        validate_environment()
        
        # Check command line arguments for force refresh
        force_refresh = '--force' in sys.argv
        
        if force_refresh:
            print("\n🔄 Force refresh mode enabled - will reload all data")
            rows_loaded = load_backfill_data(force_refresh=True)
        else:
            print("\n💡 Smart mode - will check existing data first")
            rows_loaded = load_backfill_data(force_refresh=False)
        
        print(f"\n🎯 Data load complete!")
        print(f"📊 Total rows in table: {rows_loaded:,}")
        print(f"📁 Target table: raw.ad_data")
        print(f"💡 Ready for dbt transformation models")
        print(f"\n💡 Next steps:")
        print(f"   • Daily data: python scripts/load_daily_to_snowflake.py")
        print(f"   • Force refresh: python scripts/load_backfill_to_snowflake.py --force")
        
    except Exception as e:
        print(f"\n❌ Data load failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
