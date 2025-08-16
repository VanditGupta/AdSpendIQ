"""
Ad Campaign Spend Tracker - Smart Data Management DAG

This DAG automatically manages data loading with intelligent refresh cycles:
- Daily: Checks if data refresh is needed (15-day threshold)
- Every 15 days: Full data refresh to prevent infinite growth
- Daily incremental: Adds new daily records
- Uses sensors and branching for smart decision making

Author: Vandit Gupta
Date: 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
import logging

# Import our custom functions
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.load_backfill_to_snowflake import (
    load_backfill_data, 
    load_daily_data, 
    validate_environment,
    create_snowflake_connection
)
from scripts.generate_fake_ads import generate_fake_ad_data

# Configure logging
logger = logging.getLogger(__name__)

# Default arguments
default_args = {
    'owner': 'vandit_gupta',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

# DAG definition
dag = DAG(
    'smart_data_management',
    default_args=default_args,
    description='Smart data management with 15-day refresh cycles',
    schedule='0 6 * * *',  # Daily at 6 AM (schedule_interval deprecated in Airflow 3.0)
    max_active_runs=1,
    tags=['ad_campaigns', 'data_management', 'snowflake']
)

def check_data_refresh_needed(**context):
    """
    Check if we need to refresh all data based on 15-day threshold.
    Returns 'full_refresh' or 'daily_incremental' for branching.
    """
    try:
        # Validate environment
        validate_environment()
        
        # Connect to Snowflake to check current state
        conn = create_snowflake_connection()
        
        try:
            # Check if we need to refresh all data
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(date) FROM raw.ad_data")
            result = cursor.fetchone()
            cursor.close()
            
            if not result or not result[0]:
                logger.info("📊 Table is empty - full refresh needed")
                return 'full_refresh'
            
            last_refresh_date = result[0]
            days_since_refresh = (datetime.now().date() - last_refresh_date).days
            
            logger.info(f"📅 Days since last refresh: {days_since_refresh}")
            
            if days_since_refresh >= 15:
                logger.info(f"🔄 15 days threshold reached - full refresh needed")
                return 'full_refresh'
            else:
                logger.info(f"✅ Data is fresh ({15 - days_since_refresh} days until refresh)")
                return 'daily_incremental'
                
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error checking refresh status: {e}")
        # Default to daily incremental on error
        return 'daily_incremental'

def generate_daily_data_task(**context):
    """Generate daily ad campaign data."""
    try:
        logger.info("🚀 Generating daily ad campaign data")
        
        # Generate data for yesterday (since we run at 6 AM)
        yesterday = datetime.now().date() - timedelta(days=1)
        target_date = yesterday
        
        # Generate the data
        df = generate_fake_ad_data(num_rows=5000, target_date=target_date)
        
        logger.info(f"✅ Generated {len(df)} daily records for {target_date}")
        return len(df)
        
    except Exception as e:
        logger.error(f"❌ Failed to generate daily data: {e}")
        raise e

def full_data_refresh_task(**context):
    """Perform full data refresh (every 15 days)."""
    try:
        logger.info("🔄 Starting full data refresh")
        
        # Load fresh historical data
        total_rows = load_backfill_data(force_refresh=True)
        
        logger.info(f"✅ Full refresh complete: {total_rows:,} rows loaded")
        return total_rows
        
    except Exception as e:
        logger.error(f"❌ Full refresh failed: {e}")
        raise e

def daily_incremental_task(**context):
    """Load daily data incrementally."""
    try:
        logger.info("📅 Loading daily data incrementally")
        
        # Get yesterday's date
        yesterday = datetime.now().date() - timedelta(days=1)
        daily_file = f"data/raw/daily/{yesterday.strftime('%Y/%m')}/ads_{yesterday.strftime('%Y-%m-%d')}.csv"
        
        # Check if file exists
        if Path(daily_file).exists():
            rows_loaded = load_daily_data(daily_file)
            logger.info(f"✅ Daily data loaded: {rows_loaded:,} rows")
            return rows_loaded
        else:
            logger.warning(f"⚠️ Daily file not found: {daily_file}")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Daily incremental load failed: {e}")
        raise e

def smart_data_loader(**context):
    """
    Main function that intelligently manages data loading.
    Automatically decides between full refresh and daily incremental loading.
    """
    try:
        logger.info("🚀 Starting smart data loader")
        
        # Validate environment
        validate_environment()
        
        # Connect to Snowflake to check current state
        conn = create_snowflake_connection()
        
        try:
            # Check if we need to refresh all data
            cursor = conn.cursor()
            cursor.execute("SELECT MIN(date) FROM raw.ad_data")
            result = cursor.fetchone()
            cursor.close()
            
            if not result or not result[0]:
                logger.info("📊 Table is empty - performing full refresh")
                
                # Close connection before refresh
                conn.close()
                
                # Perform full refresh
                total_rows = load_backfill_data(force_refresh=True)
                logger.info(f"✅ Full refresh complete: {total_rows:,} rows loaded")
                
                context['task_instance'].xcom_push(key='action_taken', value='full_refresh')
                context['task_instance'].xcom_push(key='rows_loaded', value=total_rows)
                
                return f"Full refresh completed: {total_rows:,} rows"
            
            last_refresh_date = result[0]
            days_since_refresh = (datetime.now().date() - last_refresh_date).days
            
            logger.info(f"📅 Days since last refresh: {days_since_refresh}")
            
            if days_since_refresh >= 15:
                logger.info(f"🔄 15 days threshold reached - performing full refresh")
                
                # Close connection before refresh
                conn.close()
                
                # Perform full refresh
                total_rows = load_backfill_data(force_refresh=True)
                logger.info(f"✅ Full refresh complete: {total_rows:,} rows loaded")
                
                context['task_instance'].xcom_push(key='action_taken', value='full_refresh')
                context['task_instance'].xcom_push(key='rows_loaded', value=total_rows)
                
                return f"Full refresh completed: {total_rows:,} rows"
                
            else:
                logger.info(f"✅ Data is fresh ({15 - days_since_refresh} days until refresh)")
                logger.info("💡 Proceeding with daily incremental loading...")
                
                # Close connection
                conn.close()
                
                # Try to load daily data
                yesterday = datetime.now().date() - timedelta(days=1)
                daily_file = f"data/raw/daily/{yesterday.strftime('%Y/%m')}/ads_{yesterday.strftime('%Y-%m-%d')}.csv"
                
                if Path(daily_file).exists():
                    logger.info(f"📁 Found daily file: {daily_file}")
                    daily_rows = load_daily_data(daily_file)
                    logger.info(f"✅ Daily data loaded: {daily_rows:,} rows")
                    
                    context['task_instance'].xcom_push(key='action_taken', value='daily_incremental')
                    context['task_instance'].xcom_push(key='rows_loaded', value=daily_rows)
                    
                    return f"Daily incremental completed: {daily_rows:,} rows added"
                else:
                    logger.info(f"📁 No daily file found: {daily_file}")
                    logger.info("💡 Make sure to run the data generator first")
                    
                    context['task_instance'].xcom_push(key='action_taken', value='no_action')
                    context['task_instance'].xcom_push(key='rows_loaded', value=0)
                    
                    return "No daily data to load"
                    
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"❌ Smart data loader failed: {e}")
        raise e

def log_completion(**context):
    """Log completion status and metrics."""
    task_instance = context['task_instance']
    
    # Safely pull XCom data with defaults
    action_taken = task_instance.xcom_pull(key='action_taken', default='unknown')
    rows_loaded = task_instance.xcom_pull(key='rows_loaded', default=0)
    
    logger.info(f"🎯 Action taken: {action_taken}")
    logger.info(f"📊 Rows processed: {rows_loaded:,}")
    
    if action_taken == 'full_refresh':
        logger.info("🔄 15-day refresh cycle completed")
    elif action_taken == 'daily_incremental':
        logger.info("📅 Daily incremental loading completed")
    elif action_taken == 'unknown':
        logger.warning("⚠️ Previous task may have failed - no action data available")
    else:
        logger.info("💡 No action taken in this run")
    
    logger.info("✅ Smart data management cycle completed")

# Task definitions
start_task = EmptyOperator(
    task_id='start',
    dag=dag
)

smart_loader_task = PythonOperator(
    task_id='smart_data_loader',
    python_callable=smart_data_loader,
    dag=dag
)

completion_task = PythonOperator(
    task_id='log_completion',
    python_callable=log_completion,
    dag=dag
)

end_task = EmptyOperator(
    task_id='end',
    dag=dag
)

# Task dependencies
start_task >> smart_loader_task >> completion_task >> end_task

# Task documentation
start_task.doc = "Start the smart data management workflow"
smart_loader_task.doc = "Intelligently manage data loading (15-day refresh or daily incremental)"
completion_task.doc = "Log completion status and metrics"
end_task.doc = "End the workflow"
