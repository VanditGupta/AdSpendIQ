"""
Ad Campaign Analytics - dbt Transformation DAG

This DAG runs dbt models to transform raw data into a complete star schema.
Creates dimension tables, fact tables, and mart tables for analytics.

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
    'retry_delay': timedelta(minutes=10),
    'catchup': False,
}

def run_dbt_debug(**context):
    """
    Run dbt debug to check configuration.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🔧 Running dbt debug...")
        
        # Navigate to dbt directory and run debug
        dbt_dir = os.path.join(os.path.dirname(__file__), '..', 'dbt')
        result = subprocess.run(
            ['dbt', 'debug'],
            capture_output=True,
            text=True,
            cwd=dbt_dir
        )
        
        if result.returncode == 0:
            print("✅ dbt debug successful")
            return "dbt configuration is valid"
        else:
            raise Exception(f"dbt debug failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running dbt debug: {str(e)}")
        raise e

def run_dbt_models(**context):
    """
    Run all dbt models to create the star schema.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🏗️ Running dbt models to create star schema...")
        
        # Navigate to dbt directory and run all models
        dbt_dir = os.path.join(os.path.dirname(__file__), '..', 'dbt')
        result = subprocess.run(
            ['dbt', 'run'],
            capture_output=True,
            text=True,
            cwd=dbt_dir
        )
        
        if result.returncode == 0:
            print("✅ dbt models created successfully")
            return "Star schema created successfully with all dimension, fact, and mart tables"
        else:
            raise Exception(f"dbt run failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running dbt models: {str(e)}")
        raise e

def run_dbt_tests(**context):
    """
    Run dbt tests to validate data quality.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🧪 Running dbt tests...")
        
        # Navigate to dbt directory and run tests
        dbt_dir = os.path.join(os.path.dirname(__file__), '..', 'dbt')
        result = subprocess.run(
            ['dbt', 'test'],
            capture_output=True,
            text=True,
            cwd=dbt_dir
        )
        
        if result.returncode == 0:
            print("✅ dbt tests passed")
            return "All dbt tests passed successfully"
        else:
            raise Exception(f"dbt tests failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running dbt tests: {str(e)}")
        raise e

def generate_dbt_docs(**context):
    """
    Generate dbt documentation.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("📚 Generating dbt documentation...")
        
        # Navigate to dbt directory and generate docs
        dbt_dir = os.path.join(os.path.dirname(__file__), '..', 'dbt')
        result = subprocess.run(
            ['dbt', 'docs', 'generate'],
            capture_output=True,
            text=True,
            cwd=dbt_dir
        )
        
        if result.returncode == 0:
            print("✅ dbt documentation generated")
            return "dbt documentation generated successfully"
        else:
            raise Exception(f"dbt docs generation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error generating dbt docs: {str(e)}")
        raise e

# Create the DAG
dag = DAG(
    'dbt_transformation_dag',
    default_args=default_args,
    description='Run dbt models to create complete star schema',
    schedule='0 10 * * *',  # Daily at 10:00 AM (after data loading)
    max_active_runs=1,
    tags=['dbt', 'transformation', 'star-schema'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

debug_task = PythonOperator(
    task_id='run_dbt_debug',
    python_callable=run_dbt_debug,
    dag=dag,
)

models_task = PythonOperator(
    task_id='run_dbt_models',
    python_callable=run_dbt_models,
    dag=dag,
)

tests_task = PythonOperator(
    task_id='run_dbt_tests',
    python_callable=run_dbt_tests,
    dag=dag,
)

docs_task = PythonOperator(
    task_id='generate_dbt_docs',
    python_callable=generate_dbt_docs,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> debug_task >> models_task >> tests_task >> docs_task >> end_task

# Task documentation
start_task.doc = "Start dbt transformation pipeline"
debug_task.doc = "Run dbt debug to validate configuration"
models_task.doc = "Run all dbt models to create star schema"
tests_task.doc = "Run dbt tests to validate data quality"
docs_task.doc = "Generate dbt documentation"
end_task.doc = "Complete dbt transformation pipeline"
