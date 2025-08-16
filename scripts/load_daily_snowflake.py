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
    Load daily ad data file to Snowflake.
    
    Args:
        daily_file_path (str): Path to the daily CSV file
        
    Returns:
        int: Number of rows loaded
        
    Raises:
        FileNotFoundError: If the daily file doesn't exist
        Exception: For Snowflake connection or loading errors
    """
    try:
        # Validate file exists
        if not Path(daily_file_path).exists():
            raise FileNotFoundError(f"Daily file not found: {daily_file_path}")
        
        logger.info(f"📁 Loading daily file: {daily_file_path}")
        
        # Load the daily data to Snowflake
        rows_loaded = load_daily_data(daily_file_path)
        
        logger.info(f"✅ Successfully loaded {rows_loaded:,} rows to Snowflake")
        return rows_loaded
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load daily data to Snowflake: {e}")
        raise

def main():
    """Main function for standalone execution."""
    if len(sys.argv) != 2:
        print("Usage: python load_daily_snowflake.py <daily_file_path>")
        print("Example: python load_daily_snowflake.py data/raw/daily/2025/08/ads_2025-08-15.csv")
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
