"""
Ad Campaign Analytics - dbt Transformation DAG

This DAG runs dbt transformations to build the Kimball star schema.
Runs every day at 10:00 AM (after data quality validation).

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

import sys
import os
import subprocess
from pathlib import Path

# Import our custom functions
sys.path.append(str(Path(__file__).parent.parent))

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': True,  # Wait for previous day's validation
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
    'catchup': False,
}

def run_dbt_dependencies(**context):
    """
    Install dbt dependencies.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("📦 Installing dbt dependencies...")
    
    try:
        # Change to dbt directory
        dbt_dir = Path(__file__).parent.parent / 'dbt'
        
        # Run dbt deps
        result = subprocess.run(
            ['dbt', 'deps'],
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            env=dict(os.environ, **{
                'SNOWFLAKE_ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
                'SNOWFLAKE_USER': os.getenv('SNOWFLAKE_USER'),
                'SNOWFLAKE_PROGRAMMATIC_TOKEN': os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
                'SNOWFLAKE_DATABASE': os.getenv('SNOWFLAKE_DATABASE'),
                'SNOWFLAKE_SCHEMA': os.getenv('SNOWFLAKE_SCHEMA'),
                'SNOWFLAKE_WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE'),
            })
        )
        
        if result.returncode == 0:
            print("✅ dbt dependencies installed successfully")
            return "dbt dependencies installed successfully"
        else:
            print(f"❌ dbt deps failed: {result.stderr}")
            raise Exception(f"dbt deps failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error installing dbt dependencies: {str(e)}")
        raise e

def run_dbt_models(**context):
    """
    Run dbt models to build the Kimball star schema.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with model count
    """
    
    print("🏗️ Running dbt models...")
    
    try:
        # Change to dbt directory
        dbt_dir = Path(__file__).parent.parent / 'dbt'
        
        # Run dbt run
        result = subprocess.run(
            ['dbt', 'run'],
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            env=dict(os.environ, **{
                'SNOWFLAKE_ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
                'SNOWFLAKE_USER': os.getenv('SNOWFLAKE_USER'),
                'SNOWFLAKE_PROGRAMMATIC_TOKEN': os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
                'SNOWFLAKE_DATABASE': os.getenv('SNOWFLAKE_DATABASE'),
                'SNOWFLAKE_SCHEMA': os.getenv('SNOWFLAKE_SCHEMA'),
                'SNOWFLAKE_WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE'),
            })
        )
        
        if result.returncode == 0:
            # Parse output to count models
            output_lines = result.stdout.split('\n')
            model_count = len([line for line in output_lines if 'PASS' in line])
            
            print(f"✅ dbt models completed successfully: {model_count} models")
            
            # Store results in XCom
            context['task_instance'].xcom_push(key='models_built', value=model_count)
            
            return f"dbt models completed successfully: {model_count} models built"
        else:
            print(f"❌ dbt run failed: {result.stderr}")
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
        str: Success message with test results
    """
    
    print("🧪 Running dbt tests...")
    
    try:
        # Change to dbt directory
        dbt_dir = Path(__file__).parent.parent / 'dbt'
        
        # Run dbt test
        result = subprocess.run(
            ['dbt', 'test'],
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            env=dict(os.environ, **{
                'SNOWFLAKE_ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
                'SNOWFLAKE_USER': os.getenv('SNOWFLAKE_USER'),
                'SNOWFLAKE_PROGRAMMATIC_TOKEN': os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
                'SNOWFLAKE_DATABASE': os.getenv('SNOWFLAKE_DATABASE'),
                'SNOWFLAKE_SCHEMA': os.getenv('SNOWFLAKE_SCHEMA'),
                'SNOWFLAKE_WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE'),
            })
        )
        
        if result.returncode == 0:
            # Parse output to count tests
            output_lines = result.stdout.split('\n')
            test_count = len([line for line in output_lines if 'PASS' in line])
            
            print(f"✅ dbt tests completed successfully: {test_count} tests passed")
            
            # Store results in XCom
            context['task_instance'].xcom_push(key='tests_passed', value=test_count)
            
            return f"dbt tests completed successfully: {test_count} tests passed"
        else:
            print(f"❌ dbt test failed: {result.stderr}")
            raise Exception(f"dbt test failed: {result.stderr}")
            
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
    
    print("📚 Generating dbt documentation...")
    
    try:
        # Change to dbt directory
        dbt_dir = Path(__file__).parent.parent / 'dbt'
        
        # Run dbt docs generate
        result = subprocess.run(
            ['dbt', 'docs', 'generate'],
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            env=dict(os.environ, **{
                'SNOWFLAKE_ACCOUNT': os.getenv('SNOWFLAKE_ACCOUNT'),
                'SNOWFLAKE_USER': os.getenv('SNOWFLAKE_USER'),
                'SNOWFLAKE_PROGRAMMATIC_TOKEN': os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
                'SNOWFLAKE_DATABASE': os.getenv('SNOWFLAKE_DATABASE'),
                'SNOWFLAKE_SCHEMA': os.getenv('SNOWFLAKE_SCHEMA'),
                'SNOWFLAKE_WAREHOUSE': os.getenv('SNOWFLAKE_WAREHOUSE'),
            })
        )
        
        if result.returncode == 0:
            print("✅ dbt documentation generated successfully")
            return "dbt documentation generated successfully"
        else:
            print(f"❌ dbt docs generate failed: {result.stderr}")
            raise Exception(f"dbt docs generate failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error generating dbt docs: {str(e)}")
        raise e

def log_dbt_summary(**context):
    """
    Log dbt transformation summary and trigger next DAG.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Summary message
    """
    
    # Get execution date
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    # Get XCom data
    task_instance = context['task_instance']
    models_built = task_instance.xcom_pull(key='models_built', default=0)
    tests_passed = task_instance.xcom_pull(key='tests_passed', default=0)
    
    summary = f"""
    🏗️ dbt Transformation Summary - {target_date}
    =============================================
    
    📅 Date: {target_date}
    🕐 Execution time: {execution_date}
    
    📊 Transformation Results:
    • Models built: {models_built}
    • Tests passed: {tests_passed}
    
    🎯 Kimball Star Schema:
    • Staging models (data cleaning)
    • Dimension tables (platforms, geography, dates)
    • Fact tables (ad performance metrics)
    • Mart models (business intelligence)
    
    🔄 Next Steps:
    • ✅ Proceed to analytics and testing
    • 📚 Documentation available at dbt docs
    
    =============================================
    """
    
    print(summary)
    return summary

# Create the DAG
dag = DAG(
    'dbt_transformation_dag',
    default_args=default_args,
    description='dbt transformation pipeline to build Kimball star schema',
    schedule='0 10 * * *',  # Daily at 10:00 AM (after validation)
    max_active_runs=1,
    tags=['dbt', 'transformation', 'kimball', 'star_schema', 'portfolio'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

deps_task = PythonOperator(
    task_id='install_dbt_dependencies',
    python_callable=run_dbt_dependencies,
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

summary_task = PythonOperator(
    task_id='log_dbt_summary',
    python_callable=log_dbt_summary,
    dag=dag,
)



end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> deps_task >> models_task >> tests_task >> docs_task >> summary_task >> end_task

# Task documentation
start_task.doc = "Start dbt transformation pipeline"
deps_task.doc = "Install dbt package dependencies"
models_task.doc = "Run dbt models to build Kimball star schema"
tests_task.doc = "Run dbt tests to validate data quality"
docs_task.doc = "Generate dbt documentation"
summary_task.doc = "Log transformation results and prepare for analytics"
end_task.doc = "Complete dbt transformation pipeline"
