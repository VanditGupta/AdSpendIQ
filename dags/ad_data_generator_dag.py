"""
Ad Campaign Spend Tracker - Simplified Airflow DAG

This DAG handles data generation and Snowflake loading with intelligent 15-day refresh cycles.
Runs every day at 9:00 AM to generate data and load it to Snowflake.

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
import subprocess
import os

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
    Generate daily ad campaign data using the script.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    print(f"🚀 Starting daily ad data generation for {target_date}")
    
    try:
        # Run the data generation script
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'generate_fake_ads.py')
        python_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'bin', 'python')
        
        print(f"🔍 Debug info:")
        print(f"  Script path: {script_path}")
        print(f"  Python path: {python_path}")
        print(f"  Working directory: {os.path.dirname(script_path)}")
        print(f"  Script exists: {os.path.exists(script_path)}")
        print(f"  Python exists: {os.path.exists(python_path)}")
        
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
        if not os.path.exists(python_path):
            raise Exception(f"Python interpreter not found: {python_path}")
        
        result = subprocess.run(
            [python_path, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path)
        )
        
        print(f"📊 Subprocess result:")
        print(f"  Return code: {result.returncode}")
        print(f"  Stdout: {result.stdout}")
        print(f"  Stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Successfully generated daily ad data")
            return f"Successfully generated ad data for {target_date}"
        else:
            raise Exception(f"Script failed with return code {result.returncode}: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error generating ad data: {str(e)}")
        raise e

def load_daily_to_snowflake_task(**context):
    """
    Load daily generated ad data to Snowflake.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🚀 Starting daily Snowflake data loader")
        
        # Run the Snowflake loader script
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'load_daily_snowflake.py')
        
        # Find today's daily file
        execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
        target_date = execution_date.date()
        daily_file = f"data/raw/daily/{target_date.year}/{target_date.month:02d}/ads_{target_date}.csv"
        
        # Use full virtual environment Python path
        python_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'bin', 'python')
        result = subprocess.run(
            [python_path, script_path, daily_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            print("✅ Successfully loaded daily data to Snowflake")
            return f"Successfully loaded data for {target_date} to Snowflake"
        else:
            raise Exception(f"Script failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error loading data to Snowflake: {str(e)}")
        raise e

def run_data_retention(**context):
    """
    Run data retention management.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🧹 Starting data retention management")
        
        # Run the retention manager script
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'data_retention_manager.py')
        python_path = os.path.join(os.path.dirname(__file__), '..', 'venv', 'bin', 'python')
        result = subprocess.run(
            [python_path, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            print("✅ Successfully ran data retention management")
            return "Data retention management completed successfully"
        else:
            raise Exception(f"Script failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running data retention: {str(e)}")
        raise e

# Create the DAG
dag = DAG(
    'ad_data_generator_dag',
    default_args=default_args,
    description='Generate daily ad campaign data and load to Snowflake',
    schedule='0 9 * * *',  # Daily at 9:00 AM
    max_active_runs=1,
    tags=['data-generation', 'snowflake', 'daily'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

generate_data_task = PythonOperator(
    task_id='generate_daily_ad_data',
    python_callable=generate_daily_ad_data,
    dag=dag,
)

load_snowflake_task = PythonOperator(
    task_id='load_daily_to_snowflake',
    python_callable=load_daily_to_snowflake_task,
    dag=dag,
)

retention_task = PythonOperator(
    task_id='run_data_retention',
    python_callable=run_data_retention,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> generate_data_task >> load_snowflake_task >> retention_task >> end_task

# Task documentation
start_task.doc = "Start daily ad data generation pipeline"
generate_data_task.doc = "Generate 5000 rows of daily ad campaign data"
load_snowflake_task.doc = "Load daily data to Snowflake with duplicate prevention"
retention_task.doc = "Run data retention management (90-day policy)"
end_task.doc = "Complete daily ad data generation pipeline"
