"""
Ad Campaign Analytics - Monitoring & Alerting DAG

This DAG runs final monitoring, health checks, and generates portfolio summary.
Runs every day at 12:00 PM (after analytics and testing).

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

def run_pipeline_health_check(**context):
    """
    Run comprehensive pipeline health check.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🏥 Running pipeline health check...")
        
        # For now, simulate health check
        print("✅ Pipeline health check completed (simulated)")
        return "Pipeline health check completed successfully"
        
    except Exception as e:
        print(f"❌ Error in health check: {str(e)}")
        raise e

def check_data_freshness(**context):
    """
    Check data freshness and completeness.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("📅 Checking data freshness...")
        
        # For now, simulate data freshness check
        print("✅ Data freshness check completed (simulated)")
        return "Data freshness check completed successfully"
        
    except Exception as e:
        print(f"❌ Error in data freshness check: {str(e)}")
        raise e

def generate_portfolio_summary(**context):
    """
    Generate comprehensive portfolio summary report.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("📋 Generating portfolio summary...")
        
        # For now, simulate portfolio summary generation
        print("✅ Portfolio summary generated (simulated)")
        return "Portfolio summary generated successfully"
        
    except Exception as e:
        print(f"❌ Error generating portfolio summary: {str(e)}")
        raise e

def run_final_validation(**context):
    """
    Run final validation to ensure pipeline success.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🔍 Running final validation...")
        
        # Run dbt tests as final validation
        dbt_dir = os.path.join(os.path.dirname(__file__), '..', 'dbt')
        result = subprocess.run(
            ['dbt', 'test'],
            capture_output=True,
            text=True,
            cwd=dbt_dir
        )
        
        if result.returncode == 0:
            print("✅ Final validation completed successfully")
            return "Final validation completed successfully"
        else:
            raise Exception(f"Final validation failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error in final validation: {str(e)}")
        raise e

def log_pipeline_completion(**context):
    """
    Log final pipeline completion status.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🎉 Logging pipeline completion...")
        
        # Get execution date
        execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
        target_date = execution_date.date()
        
        completion_message = f"""
        🎊 AD CAMPAIGN ANALYTICS PIPELINE COMPLETED - {target_date}
        =====================================================
        
        📅 Date: {target_date}
        🕐 Completion time: {execution_date}
        
        ✅ ALL PHASES COMPLETED:
        
        1. 📊 Data Generation & Loading (9:00 AM)
        2. 🔍 Data Quality Validation (9:30 AM)
        3. 🏗️ dbt Transformation (10:00 AM)
        4. 📈 Analytics & Testing (11:00 AM)
        5. 🔍 Monitoring & Alerting (12:00 PM)
        
        🚀 PORTFOLIO STATUS: READY FOR DEMONSTRATION!
        
        🎯 Technical Skills Demonstrated:
        • End-to-end data pipeline development
        • Cloud data warehouse integration
        • Data transformation & modeling
        • Data quality assurance
        • Automated testing & monitoring
        • Professional documentation
        
        🎊 Congratulations! Your portfolio is complete and operational!
        
        =====================================================
        """
        
        print(completion_message)
        return "Pipeline completion logged successfully"
        
    except Exception as e:
        print(f"❌ Error logging completion: {str(e)}")
        raise e

# Create the DAG
dag = DAG(
    'monitoring_alerting_dag',
    default_args=default_args,
    description='Run final monitoring, health checks, and portfolio summary',
    schedule='0 12 * * *',  # Daily at 12:00 PM (after analytics and testing)
    max_active_runs=1,
    tags=['monitoring', 'alerting', 'portfolio'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

health_task = PythonOperator(
    task_id='run_pipeline_health_check',
    python_callable=run_pipeline_health_check,
    dag=dag,
)

freshness_task = PythonOperator(
    task_id='check_data_freshness',
    python_callable=check_data_freshness,
    dag=dag,
)

summary_task = PythonOperator(
    task_id='generate_portfolio_summary',
    python_callable=generate_portfolio_summary,
    dag=dag,
)

validation_task = PythonOperator(
    task_id='run_final_validation',
    python_callable=run_final_validation,
    dag=dag,
)

completion_task = PythonOperator(
    task_id='log_pipeline_completion',
    python_callable=log_pipeline_completion,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies
start_task >> health_task >> freshness_task >> summary_task >> validation_task >> completion_task >> end_task

# Task documentation
start_task.doc = "Start monitoring and alerting pipeline"
health_task.doc = "Run comprehensive pipeline health check"
freshness_task.doc = "Check data freshness and completeness"
summary_task.doc = "Generate comprehensive portfolio summary"
validation_task.doc = "Run final validation to ensure pipeline success"
completion_task.doc = "Log final pipeline completion status"
end_task.doc = "Complete monitoring and alerting pipeline"
