"""
Ad Campaign Spend Tracker - Comprehensive Airflow DAG

This DAG handles both data generation and Snowflake loading with intelligent 15-day refresh cycles.
Runs every day at 9:00 AM to generate data and load it to Snowflake.

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
import sys
import os
from pathlib import Path

# Import our custom functions
sys.path.append(str(Path(__file__).parent.parent))
from scripts.generate_fake_ads import generate_fake_ad_data, save_daily_data
from scripts.load_daily_snowflake import load_daily_to_snowflake

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False,
}

def generate_daily_ad_data(**context):
    """
    Generate daily ad campaign data and save to CSV.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with file path
    """
    
    # Get execution date from Airflow context (Airflow 3.0 compatible)
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    print(f"🚀 Starting daily ad data generation for {target_date}")
    
    try:
        # Generate fake ad data for the target date
        df = generate_fake_ad_data(num_rows=5000, target_date=target_date)
        
        # Save to CSV
        filepath = save_daily_data(df, target_date=target_date)
        
        # Store file path in XCom for next task
        context['task_instance'].xcom_push(key='daily_file_path', value=str(filepath))
        
        # Log success
        print(f"✅ Successfully generated {len(df)} rows of ad data")
        print(f"📁 File saved to: {filepath}")
        
        # Return success message
        return f"Successfully generated ad data for {target_date}. File: {filepath}"
        
    except Exception as e:
        print(f"❌ Error generating ad data: {str(e)}")
        raise e

def load_daily_to_snowflake_task(**context):
    """
    Load daily generated ad data to Snowflake.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Summary of action taken
    """
    
    try:
        print("🚀 Starting daily Snowflake data loader")
        
        # Get the daily file path from previous task
        task_instance = context['task_instance']
        daily_file_path = task_instance.xcom_pull(key='daily_file_path')
        
        print(f"🔍 XCom pull result: daily_file_path = {daily_file_path}")
        
        # For testing purposes, if no XCom data, try to find the file manually
        if not daily_file_path:
            print("⚠️ No XCom data found, trying to find daily file manually...")
            # For testing, look for the same date that was generated (execution date)
            execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
            target_date = execution_date.date()
            daily_file_path = f"data/raw/daily/{target_date.strftime('%Y/%m')}/ads_{target_date.strftime('%Y-%m-%d')}.csv"
            print(f"🔍 Trying manual path: {daily_file_path}")
            
            if not Path(daily_file_path).exists():
                raise ValueError(f"No daily file found at {daily_file_path}")
        
        print(f"📁 Loading daily file: {daily_file_path}")
        
        # Load the daily data to Snowflake using our dedicated script
        rows_loaded = load_daily_to_snowflake(daily_file_path)
        
        print(f"✅ Successfully loaded {rows_loaded:,} rows to Snowflake")
        
        # Store results in XCom for summary task
        context['task_instance'].xcom_push(key='action_taken', value='daily_incremental')
        context['task_instance'].xcom_push(key='rows_loaded', value=rows_loaded)
        
        return f"Daily data loaded successfully: {rows_loaded:,} rows added to Snowflake"
        
    except Exception as e:
        print(f"❌ Daily Snowflake loader failed: {e}")
        raise e

def log_pipeline_summary(**context):
    """
    Log a comprehensive summary of the entire pipeline execution.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Summary message
    """
    
    # Get execution date from Airflow context (Airflow 3.0 compatible)
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    # Get XCom data with safe defaults
    task_instance = context['task_instance']
    daily_file_path = task_instance.xcom_pull(key='daily_file_path', default='unknown')
    action_taken = task_instance.xcom_pull(key='action_taken', default='unknown')
    rows_loaded = task_instance.xcom_pull(key='rows_loaded', default=0)
    
    # Ensure we have safe values for formatting
    if daily_file_path is None:
        daily_file_path = 'unknown'
    if action_taken is None:
        action_taken = 'unknown'
    if rows_loaded is None:
        rows_loaded = 0
    
    summary = f"""
    📊 Comprehensive Ad Campaign Pipeline Summary - {target_date}
    ================================================================
    
    ✅ Pipeline completed successfully
    📅 Date: {target_date}
    🕐 Execution time: {execution_date}
    
    📁 Data Generation:
    • File: {daily_file_path}
    • 5,000 rows of realistic ad campaign data
    
    🗄️ Snowflake Loading:
    • Action: {action_taken}
    • Rows processed: {rows_loaded:,}
    
    📈 Raw Ad Platform Data:
    • 5 platforms: Google, Facebook, LinkedIn, TikTok, Twitter
    • 7 campaign types: brand_awareness, conversions, traffic, app_installs, lead_generation, retargeting, video_views
    • 6 ad formats: search, display, video, social, shopping, remarketing
    • Raw metrics: impressions, clicks, spend, conversions
    • Geographic & device-specific performance
    
    🔄 Data Management:
    • Daily incremental loading to Snowflake
    • Clean separation of concerns with dedicated scripts
    • Efficient data pipeline for portfolio demonstration
    
    Next steps:
    1. Data is loaded and ready in Snowflake
    2. Run dbt models to transform the data
    3. Update dashboards with new data
    
    ================================================================
    """
    
    print(summary)
    return summary

# Create the DAG
dag = DAG(
    'ad_data_generator_dag',
    default_args=default_args,
    description='Daily ad campaign data generation and Snowflake loading pipeline',
    schedule='0 9 * * *',  # Daily at 9:00 AM
    max_active_runs=1,
    tags=['ad_campaigns', 'data_generation', 'snowflake', 'portfolio'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

generate_data_task = PythonOperator(
    task_id='generate_daily_ad_data',
    python_callable=generate_daily_ad_data,
    dag=dag,
)

snowflake_loader_task = PythonOperator(
    task_id='load_daily_to_snowflake',
    python_callable=load_daily_to_snowflake_task,
    dag=dag,
)

log_summary_task = PythonOperator(
    task_id='log_pipeline_summary',
    python_callable=log_pipeline_summary,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies - Sequential execution
start_task >> generate_data_task >> snowflake_loader_task >> log_summary_task >> end_task

# Task documentation
start_task.doc = "Start the comprehensive ad campaign pipeline"
generate_data_task.doc = """
Generates 5,000 rows of realistic fake ad campaign data for the current execution date.
Data includes campaign metrics across Google, Facebook, LinkedIn, TikTok, and Twitter platforms.
Features: campaign types, ad formats, device targeting, geographic performance, and raw metrics.
Raw data format matches exactly what ad platforms like Google Ads and Facebook Ads send.
"""

snowflake_loader_task.doc = """
Loads daily generated ad campaign data to Snowflake.
Uses the dedicated load_daily_snowflake.py script for clean separation of concerns.
Appends new data to the existing raw.ad_data table efficiently.
"""

log_summary_task.doc = """
Logs a comprehensive summary of the entire pipeline execution including data generation,
Snowflake loading actions, and next steps for the data engineering workflow.
"""

end_task.doc = "End the comprehensive ad campaign pipeline"
