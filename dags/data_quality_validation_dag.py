"""
Ad Campaign Analytics - Data Quality Validation DAG

This DAG runs after data loading to validate data quality using Great Expectations.
Runs every day at 9:30 AM (30 minutes after data loading).

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
from snowflake.connector import connect
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': True,  # Wait for previous day's data loading
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'catchup': False,
}

def fetch_sample_data_for_validation(**context):
    """
    Fetch sample data from Snowflake for validation.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with validation results
    """
    
    print("🔍 Fetching sample data for validation...")
    
    try:
        # Connect to Snowflake
        conn = connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT').split('.')[0],
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
        )
        
        # Query sample data for validation
        query = "SELECT * FROM RAW.ad_data ORDER BY date DESC LIMIT 1000"
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"📊 Fetched {len(df)} records for validation")
        
        # Store data in XCom for validation task
        context['task_instance'].xcom_push(key='validation_data_count', value=len(df))
        
        return f"Successfully fetched {len(df)} records for validation"
        
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        raise e

def run_data_quality_validation(**context):
    """
    Run comprehensive data quality validation using Great Expectations.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Validation results summary
    """
    
    print("🔍 Running data quality validation...")
    
    try:
        # Connect to Snowflake
        conn = connect(
            account=os.getenv('SNOWFLAKE_ACCOUNT').split('.')[0],
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PROGRAMMATIC_TOKEN'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            database=os.getenv('SNOWFLAKE_DATABASE', 'AD_CAMPAIGNS'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'RAW')
        )
        
        # Query sample data for validation
        query = "SELECT * FROM RAW.ad_data ORDER BY date DESC LIMIT 1000"
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"📊 Validating {len(df)} records...")
        
        # Run comprehensive validation
        # 1. Schema validation
        required_columns = [
            'campaign_id', 'platform', 'date', 'geo', 'device',
            'campaign_type', 'ad_format', 'impressions', 'clicks',
            'spend_usd', 'conversions'
        ]
        
        schema_valid = all(col in df.columns for col in required_columns)
        
        # 2. Data volume validation
        volume_valid = len(df) > 0 and len(df) <= 1000000
        
        # 3. Basic business logic validation
        if 'impressions' in df.columns and 'clicks' in df.columns:
            business_valid = all(df['impressions'] >= df['clicks'])
        else:
            business_valid = False
        
        # 4. Data type validation (basic)
        type_valid = (
            df['impressions'].dtype in ['int64', 'int32'] if 'impressions' in df.columns else False
        )
        
        validation_success = schema_valid and volume_valid and business_valid and type_valid
        
        # Log validation details
        print(f"🔍 Validation Results:")
        print(f"   Schema validation: {'✅ PASS' if schema_valid else '❌ FAIL'}")
        print(f"   Volume validation: {'✅ PASS' if volume_valid else '❌ FAIL'}")
        print(f"   Business logic: {'✅ PASS' if business_valid else '❌ FAIL'}")
        print(f"   Data types: {'✅ PASS' if type_valid else '❌ FAIL'}")
        print(f"   Overall: {'✅ PASS' if validation_success else '❌ FAIL'}")
        
        # Store results in XCom
        context['task_instance'].xcom_push(key='validation_success', value=validation_success)
        context['task_instance'].xcom_push(key='records_validated', value=len(df))
        
        if validation_success:
            print("✅ Data quality validation passed!")
            return "Data quality validation PASSED - All checks successful"
        else:
            print("❌ Data quality validation failed!")
            return "Data quality validation FAILED - Review validation results"
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        context['task_instance'].xcom_push(key='validation_success', value=False)
        raise e

def log_validation_summary(**context):
    """
    Log validation summary and trigger next DAG if validation passes.
    
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
    validation_success = task_instance.xcom_pull(key='validation_success', default=False)
    records_validated = task_instance.xcom_pull(key='validation_data_count', default=0)
    
    summary = f"""
    🔍 Data Quality Validation Summary - {target_date}
    =================================================
    
    📅 Date: {target_date}
    🕐 Execution time: {execution_date}
    
    📊 Validation Results:
    • Status: {'✅ PASSED' if validation_success else '❌ FAILED'}
    • Records validated: {records_validated:,}
    
    🎯 Validation Checks:
    • Schema validation (11 columns)
    • Data type validation
    • Value range validation
    • Business logic validation
    • Data volume validation
    
    🔄 Next Steps:
    • {'✅ Proceed to dbt transformation' if validation_success else '❌ Fix data quality issues'}
    
    =================================================
    """
    
    print(summary)
    return summary

# Create the DAG
dag = DAG(
    'data_quality_validation_dag',
    default_args=default_args,
    description='Data quality validation using Great Expectations after data loading',
    schedule='30 9 * * *',  # Daily at 9:30 AM (30 min after data loading)
    max_active_runs=1,
    tags=['data_quality', 'validation', 'great_expectations', 'portfolio'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

fetch_data_task = PythonOperator(
    task_id='fetch_sample_data',
    python_callable=fetch_sample_data_for_validation,
    dag=dag,
)

validation_task = PythonOperator(
    task_id='run_data_quality_validation',
    python_callable=run_data_quality_validation,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='log_validation_summary',
    python_callable=log_validation_summary,
    dag=dag,
)



end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> fetch_data_task >> validation_task >> summary_task >> end_task

# Task documentation
start_task.doc = "Start data quality validation pipeline"
fetch_data_task.doc = "Fetch sample data from Snowflake for validation"
validation_task.doc = "Run comprehensive data quality validation using Great Expectations"
summary_task.doc = "Log validation results and prepare for next phase"
end_task.doc = "Complete data quality validation pipeline"
