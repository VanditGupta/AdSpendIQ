"""
Ultra-Simple Test DAG for macOS Debugging
Just prints messages without any external calls
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'catchup': False,
}

def simple_print_task(**context):
    """Just print a message - no external calls"""
    print("🎯 Simple test task executed successfully!")
    print("✅ No subprocess calls, no imports, just basic Python")
    return "Success"

def another_simple_task(**context):
    """Another simple task"""
    print("🎉 Another simple task executed!")
    print("✅ Still working fine")
    return "Success"

# Create the DAG
dag = DAG(
    'simple_test_dag',
    default_args=default_args,
    description='Ultra-simple test DAG for debugging',
    schedule=None,  # Manual trigger only
    max_active_runs=1,
    tags=['test', 'debug', 'simple'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

test_task1 = PythonOperator(
    task_id='simple_print_task',
    python_callable=simple_print_task,
    dag=dag,
)

test_task2 = PythonOperator(
    task_id='another_simple_task',
    python_callable=another_simple_task,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> test_task1 >> test_task2 >> end_task
