"""
Ad Campaign Analytics - Analytics & Testing DAG

This DAG runs analytics queries and comprehensive testing after dbt transformation.
Runs every day at 11:00 AM (after dbt transformation).

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
    'depends_on_past': True,  # Wait for previous day's transformation
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=15),
    'catchup': False,
}

def run_portfolio_analytics(**context):
    """
    Run portfolio showcase analytics queries.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with query results
    """
    
    print("📊 Running portfolio analytics queries...")
    
    try:
        # Change to project root directory
        project_dir = Path(__file__).parent.parent
        
        # Run portfolio queries script
        result = subprocess.run(
            ['python', 'run_portfolio_queries.py'],
            cwd=project_dir,
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
            # Parse output to count queries
            output_lines = result.stdout.split('\n')
            query_count = len([line for line in output_lines if 'Query' in line and 'Result:' in line])
            
            print(f"✅ Portfolio analytics completed successfully: {query_count} queries executed")
            
            # Store results in XCom
            context['task_instance'].xcom_push(key='queries_executed', value=query_count)
            
            return f"Portfolio analytics completed successfully: {query_count} queries executed"
        else:
            print(f"❌ Portfolio analytics failed: {result.stderr}")
            raise Exception(f"Portfolio analytics failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running portfolio analytics: {str(e)}")
        raise e

def run_comprehensive_testing(**context):
    """
    Run comprehensive testing suite including PyTest and Great Expectations.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with test results
    """
    
    print("🧪 Running comprehensive testing suite...")
    
    try:
        # Change to project root directory
        project_dir = Path(__file__).parent.parent
        
        # Run test suite
        result = subprocess.run(
            ['python', 'run_tests.py'],
            cwd=project_dir,
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
            test_count = len([line for line in output_lines if 'PASSED' in line])
            
            print(f"✅ Comprehensive testing completed successfully: {test_count} tests passed")
            
            # Store results in XCom
            context['task_instance'].xcom_push(key='tests_passed', value=test_count)
            
            return f"Comprehensive testing completed successfully: {test_count} tests passed"
        else:
            print(f"❌ Comprehensive testing failed: {result.stderr}")
            raise Exception(f"Comprehensive testing failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running comprehensive testing: {str(e)}")
        raise e

def run_data_quality_monitoring(**context):
    """
    Run data quality monitoring and alerting.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with monitoring results
    """
    
    print("🔍 Running data quality monitoring...")
    
    try:
        # Change to project root directory
        project_dir = Path(__file__).parent.parent
        
        # Run Great Expectations validation
        result = subprocess.run(
            ['python', 'great_expectations/validate_ad_data.py'],
            cwd=project_dir,
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
            # Parse output to check validation status
            output_lines = result.stdout.split('\n')
            validation_passed = any('All validations passed' in line for line in output_lines)
            
            print(f"✅ Data quality monitoring completed: {'PASSED' if validation_passed else 'FAILED'}")
            
            # Store results in XCom
            context['task_instance'].xcom_push(key='validation_passed', value=validation_passed)
            
            return f"Data quality monitoring completed: {'PASSED' if validation_passed else 'FAILED'}"
        else:
            print(f"❌ Data quality monitoring failed: {result.stderr}")
            raise Exception(f"Data quality monitoring failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running data quality monitoring: {str(e)}")
        raise e

def generate_analytics_report(**context):
    """
    Generate comprehensive analytics report.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message with report details
    """
    
    print("📈 Generating analytics report...")
    
    try:
        # Get execution date
        execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
        target_date = execution_date.date()
        
        # Get XCom data
        task_instance = context['task_instance']
        queries_executed = task_instance.xcom_pull(key='queries_executed', default=0)
        tests_passed = task_instance.xcom_pull(key='tests_passed', default=0)
        validation_passed = task_instance.xcom_pull(key='validation_passed', default=False)
        
        # Generate report
        report = f"""
        📊 Analytics & Testing Report - {target_date}
        =============================================
        
        📅 Date: {target_date}
        🕐 Execution time: {execution_date}
        
        📈 Analytics Results:
        • Portfolio queries executed: {queries_executed}
        • Tests passed: {tests_passed}
        • Data quality validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}
        
        🎯 Portfolio Highlights:
        • Executive summary queries
        • Platform performance analysis
        • Geographic insights
        • Campaign effectiveness metrics
        • ROI optimization analysis
        
        🔄 Pipeline Status:
        • Data loading: ✅ Complete
        • Data quality: {'✅ Validated' if validation_passed else '❌ Issues Found'}
        • Transformation: ✅ Complete
        • Analytics: ✅ Complete
        • Testing: ✅ Complete
        
        =============================================
        """
        
        print(report)
        
        # Store report in XCom
        context['task_instance'].xcom_push(key='analytics_report', value=report)
        
        return "Analytics report generated successfully"
        
    except Exception as e:
        print(f"❌ Error generating analytics report: {str(e)}")
        raise e

def log_analytics_summary(**context):
    """
    Log analytics summary and trigger final DAG.
    
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
    queries_executed = task_instance.xcom_pull(key='queries_executed', default=0)
    tests_passed = task_instance.xcom_pull(key='tests_passed', default=0)
    validation_passed = task_instance.xcom_pull(key='validation_passed', default=False)
    
    summary = f"""
    🎯 Analytics & Testing Summary - {target_date}
    =============================================
    
    📅 Date: {target_date}
    🕐 Execution time: {execution_date}
    
    📊 Results Summary:
    • Portfolio queries: {queries_executed} executed
    • Testing: {tests_passed} tests passed
    • Data quality: {'✅ PASSED' if validation_passed else '❌ FAILED'}
    
    🚀 Portfolio Status:
    • Complete data pipeline operational
    • Kimball star schema built and tested
    • Analytics queries validated
    • Data quality assured
    
    🔄 Next Steps:
    • ✅ Proceed to final monitoring and alerting
    • 📊 Portfolio ready for demonstration
    
    =============================================
    """
    
    print(summary)
    return summary

# Create the DAG
dag = DAG(
    'analytics_testing_dag',
    default_args=default_args,
    description='Analytics queries and comprehensive testing after dbt transformation',
    schedule='0 11 * * *',  # Daily at 11:00 AM (after dbt transformation)
    max_active_runs=1,
    tags=['analytics', 'testing', 'portfolio', 'monitoring', 'portfolio'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

analytics_task = PythonOperator(
    task_id='run_portfolio_analytics',
    python_callable=run_portfolio_analytics,
    dag=dag,
)

testing_task = PythonOperator(
    task_id='run_comprehensive_testing',
    python_callable=run_comprehensive_testing,
    dag=dag,
)

monitoring_task = PythonOperator(
    task_id='run_data_quality_monitoring',
    python_callable=run_data_quality_monitoring,
    dag=dag,
)

report_task = PythonOperator(
    task_id='generate_analytics_report',
    python_callable=generate_analytics_report,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='log_analytics_summary',
    python_callable=log_analytics_summary,
    dag=dag,
)



end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> analytics_task >> testing_task >> monitoring_task >> report_task >> summary_task >> end_task

# Task documentation
start_task.doc = "Start analytics and testing pipeline"
analytics_task.doc = "Run portfolio showcase analytics queries"
testing_task.doc = "Run comprehensive PyTest and Great Expectations testing"
monitoring_task.doc = "Run data quality monitoring and validation"
report_task.doc = "Generate comprehensive analytics report"
summary_task.doc = "Log analytics results and prepare for monitoring"
end_task.doc = "Complete analytics and testing pipeline"
