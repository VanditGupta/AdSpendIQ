"""
Ad Campaign Spend Tracker - Airflow DAG

This DAG automates the daily generation of fake ad campaign data.
Runs every day at 9:00 AM to generate 5000 rows of ad data.

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
import sys
import os
from pathlib import Path

# Import the data generation function
from scripts.generate_fake_ads import generate_fake_ad_data, save_daily_data

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
    
    # Get execution date from Airflow context
    execution_date = context['execution_date']
    target_date = execution_date.date()
    
    print(f"🚀 Starting daily ad data generation for {target_date}")
    
    try:
        # Generate fake ad data for the target date
        df = generate_fake_ad_data(num_rows=5000, target_date=target_date)
        
        # Save to CSV
        filepath = save_daily_data(df, target_date=target_date)
        
        # Log success
        print(f"✅ Successfully generated {len(df)} rows of ad data")
        print(f"📁 File saved to: {filepath}")
        
        # Return success message
        return f"Successfully generated ad data for {target_date}. File: {filepath}"
        
    except Exception as e:
        print(f"❌ Error generating ad data: {str(e)}")
        raise e

def log_generation_summary(**context):
    """
    Log a summary of the data generation process.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Summary message
    """
    
    execution_date = context['execution_date']
    target_date = execution_date.date()
    
    summary = f"""
    📊 Daily Ad Data Generation Summary - {target_date}
    ================================================
    
    ✅ Task completed successfully
    📅 Date: {target_date}
    🕐 Execution time: {execution_date}
    📁 Output: data/raw/daily/{target_date.strftime('%Y/%m')}/ads_{target_date.strftime('%Y-%m-%d')}.csv
    
    📈 Raw Ad Platform Data:
    • 5 platforms: Google, Facebook, LinkedIn, TikTok, Twitter
    • 7 campaign types: brand_awareness, conversions, traffic, app_installs, lead_generation, retargeting, video_views
    • 6 ad formats: search, display, video, social, shopping, remarketing
    • Raw metrics: impressions, clicks, spend, conversions
    • Geographic & device-specific performance
    
    Next steps:
    1. Data is ready for Snowflake ingestion
    2. Run dbt models to transform the data
    3. Update dashboards with new data
    
    ================================================
    """
    
    print(summary)
    return summary

# Create the DAG
dag = DAG(
    'ad_data_generator_dag',
    default_args=default_args,
    description='Daily generation of fake ad campaign data',
    schedule_interval='0 9 * * *',  # Daily at 9:00 AM
    max_active_runs=1,
    tags=['ad_campaigns', 'data_generation', 'portfolio'],
)

# Define tasks
generate_data_task = PythonOperator(
    task_id='generate_daily_ad_data',
    python_callable=generate_daily_ad_data,
    provide_context=True,
    dag=dag,
)

log_summary_task = PythonOperator(
    task_id='log_generation_summary',
    python_callable=log_generation_summary,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
generate_data_task >> log_summary_task

# Task documentation
generate_data_task.doc = """
Generates 5000 rows of realistic fake ad campaign data for the current execution date.
Data includes campaign metrics across Google, Facebook, LinkedIn, TikTok, and Twitter platforms.
Features: campaign types, ad formats, device targeting, geographic performance, and raw metrics (impressions, clicks, spend, conversions).
Raw data format matches exactly what ad platforms like Google Ads and Facebook Ads send.
"""

log_summary_task.doc = """
Logs a summary of the data generation process and next steps.
Useful for monitoring and debugging the pipeline.
"""
