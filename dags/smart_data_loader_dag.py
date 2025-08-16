"""
Ad Campaign Spend Tracker - Smart Data Loader DAG

Simplified DAG that focuses on core data loading with 15-day refresh cycles.
This DAG runs daily and automatically decides whether to refresh all data or load incrementally.

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
    'smart_data_loader',
    default_args=default_args,
    description='Smart data loader with 15-day refresh cycles',
    schedule='0 6 * * *',  # Daily at 6 AM (schedule_interval deprecated in Airflow 3.0)
    max_active_runs=1,
    tags=['ad_campaigns', 'data_loader', 'snowflake']
)

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
    
    logger.info("✅ Smart data loader cycle completed")

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
start_task.doc = "Start the smart data loader workflow"
smart_loader_task.doc = "Intelligently manage data loading (15-day refresh or daily incremental)"
completion_task.doc = "Log completion status and metrics"
end_task.doc = "End the workflow"
