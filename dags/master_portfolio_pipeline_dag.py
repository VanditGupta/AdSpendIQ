"""
Ad Campaign Analytics - Master Portfolio Pipeline DAG

This master DAG orchestrates the entire portfolio pipeline workflow.
Shows the complete end-to-end data engineering process.

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.smtp.operators.smtp import EmailOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration - read from environment variables
EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', 'admin@example.com').split(',')

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'catchup': False,
}

def initialize_portfolio_pipeline(**context):
    """
    Initialize the portfolio pipeline and log start.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Initialization message
    """
    
    print("🚀 Initializing Ad Campaign Analytics Portfolio Pipeline...")
    
    # Get execution date
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    initialization_message = f"""
    🎯 PORTFOLIO PIPELINE INITIALIZATION - {target_date}
    ================================================
    
    📅 Date: {target_date}
    🕐 Start time: {execution_date}
    
    🏗️ Pipeline Architecture:
    • Phase 1: Data Generation & Loading (9:00 AM)
    • Phase 2: Data Quality Validation (9:30 AM)
    • Phase 3: dbt Transformation (10:00 AM)
    • Phase 4: Analytics & Testing (11:00 AM)
    • Phase 5: Monitoring & Alerting (12:00 PM)
    
    🎯 Portfolio Objectives:
    • Demonstrate end-to-end data engineering skills
    • Showcase modern data stack proficiency
    • Implement production-ready data pipeline
    • Build comprehensive testing & validation
    • Create business intelligence solutions
    
    🚀 Starting portfolio pipeline...
    ================================================
    """
    
    print(initialization_message)
    
    # Store initialization in XCom
    context['task_instance'].xcom_push(key='pipeline_start_time', value=str(execution_date))
    context['task_instance'].xcom_push(key='target_date', value=str(target_date))
    
    return "Portfolio pipeline initialized successfully"

def log_phase_completion(phase_name, **context):
    """
    Log completion of a pipeline phase.
    
    Args:
        phase_name (str): Name of the completed phase
        **context: Airflow context
    
    Returns:
        str: Completion message
    """
    
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    completion_message = f"""
    ✅ PHASE COMPLETED: {phase_name}
    =============================================
    
    📅 Date: {target_date}
    🕐 Completion time: {execution_date}
    🎯 Phase: {phase_name}
    
    🚀 Proceeding to next phase...
    =============================================
    """
    
    print(completion_message)
    
    # Store phase completion in XCom
    context['task_instance'].xcom_push(key=f'{phase_name.lower().replace(" ", "_")}_completion_time', value=str(execution_date))
    
    return f"{phase_name} completed successfully"

def log_portfolio_completion(**context):
    """
    Log portfolio pipeline completion and success.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Completion message
    """
    
    # Get execution date
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    completion_message = f"""
    🎉 PORTFOLIO PIPELINE COMPLETED SUCCESSFULLY!
    =============================================
    
    📅 Date: {target_date}
    🕐 Completion time: {execution_date}
    
    ✅ ALL PHASES COMPLETED:
    
    1. 📊 Data Generation & Loading (9:00 AM)
       • 261,224 historical ad campaign records
       • Snowflake integration with duplicate prevention
       • Data retention management (90-day policy)
    
    2. 🔍 Data Quality Validation (9:30 AM)
       • Great Expectations validation suite
       • Comprehensive data quality checks
       • Schema, business logic, and value validation
    
    3. 🏗️ dbt Transformation (10:00 AM)
       • Kimball star schema implementation
       • 6 dimension tables + 1 fact table + 4 mart tables
       • Automated testing and documentation
    
    4. 📈 Analytics & Testing (11:00 AM)
       • Portfolio showcase queries
       • Comprehensive testing suite
       • Data quality monitoring
    
    5. 🔍 Monitoring & Alerting (12:00 PM)
       • Pipeline health checks
       • Portfolio summary generation
       • Success notifications
    
    🚀 PORTFOLIO STATUS: READY FOR DEMONSTRATION!
    
    🎯 Technical Skills Demonstrated:
    • End-to-end data pipeline development
    • Cloud data warehouse integration
    • Data transformation & modeling
    • Data quality assurance
    • Automated testing & monitoring
    • Professional documentation
    
    🔄 Complete Daily Workflow:
    • 9:00 AM → 9:30 AM → 10:00 AM → 11:00 AM → 12:00 PM
    • Data → Quality → Transform → Analytics → Monitor
    
    🎊 Congratulations! Your portfolio is complete and operational!
    
    =============================================
    """
    
    print(completion_message)
    
    # Store completion in XCom
    context['task_instance'].xcom_push(key='pipeline_completion_time', value=str(execution_date))
    context['task_instance'].xcom_push(key='portfolio_status', value='COMPLETED')
    
    return "Portfolio pipeline completed successfully - ready for demonstration!"

def send_pipeline_start_alert(**context):
    """
    Send email alert when pipeline starts.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    subject = f"🚀 Portfolio Pipeline Started - {target_date}"
    
    html_content = f"""
    <html>
    <body>
        <h2>🎯 Ad Campaign Analytics Portfolio Pipeline Started</h2>
        <p><strong>Date:</strong> {target_date}</p>
        <p><strong>Start Time:</strong> {execution_date}</p>
        
        <h3>📋 Pipeline Overview</h3>
        <ul>
            <li><strong>Phase 1:</strong> Data Generation & Loading (9:00 AM)</li>
            <li><strong>Phase 2:</strong> Data Quality Validation (9:30 AM)</li>
            <li><strong>Phase 3:</strong> dbt Transformation (10:00 AM)</li>
            <li><strong>Phase 4:</strong> Analytics & Testing (11:00 AM)</li>
            <li><strong>Phase 5:</strong> Monitoring & Alerting (12:00 PM)</li>
        </ul>
        
        <h3>🎯 Portfolio Objectives</h3>
        <ul>
            <li>Demonstrate end-to-end data engineering skills</li>
            <li>Showcase modern data stack proficiency</li>
            <li>Implement production-ready data pipeline</li>
            <li>Build comprehensive testing & validation</li>
            <li>Create business intelligence solutions</li>
        </ul>
        
        <p><em>Pipeline is now running. You will receive completion notification.</em></p>
        
        <hr>
        <p><small>Generated by Ad Campaign Analytics Portfolio Pipeline</small></p>
    </body>
    </html>
    """
    
    # Store email content in XCom for the EmailOperator
    context['task_instance'].xcom_push(key='start_alert_subject', value=subject)
    context['task_instance'].xcom_push(key='start_alert_html', value=html_content)
    
    return "Pipeline start alert prepared"

def send_pipeline_completion_alert(**context):
    """
    Send email alert when pipeline completes successfully.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
    target_date = execution_date.date()
    
    subject = f"🎉 Portfolio Pipeline Completed Successfully - {target_date}"
    
    html_content = f"""
    <html>
    <body>
        <h2>🎊 Ad Campaign Analytics Portfolio Pipeline Completed!</h2>
        <p><strong>Date:</strong> {target_date}</p>
        <p><strong>Completion Time:</strong> {execution_date}</p>
        
        <h3>✅ All Phases Completed Successfully</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 8px;">Phase</th>
                <th style="padding: 8px;">Time</th>
                <th style="padding: 8px;">Status</th>
            </tr>
            <tr>
                <td style="padding: 8px;">📊 Data Generation & Loading</td>
                <td style="padding: 8px;">9:00 AM</td>
                <td style="padding: 8px; color: green;">✅ COMPLETED</td>
            </tr>
            <tr>
                <td style="padding: 8px;">🔍 Data Quality Validation</td>
                <td style="padding: 8px;">9:30 AM</td>
                <td style="padding: 8px; color: green;">✅ COMPLETED</td>
            </tr>
            <tr>
                <td style="padding: 8px;">🏗️ dbt Transformation</td>
                <td style="padding: 8px;">10:00 AM</td>
                <td style="padding: 8px; color: green;">✅ COMPLETED</td>
            </tr>
            <tr>
                <td style="padding: 8px;">📈 Analytics & Testing</td>
                <td style="padding: 8px;">11:00 AM</td>
                <td style="padding: 8px; color: green;">✅ COMPLETED</td>
            </tr>
            <tr>
                <td style="padding: 8px;">🔍 Monitoring & Alerting</td>
                <td style="padding: 8px;">12:00 PM</td>
                <td style="padding: 8px; color: green;">✅ COMPLETED</td>
            </tr>
        </table>
        
        <h3>🚀 Portfolio Status: READY FOR DEMONSTRATION!</h3>
        
        <h3>🎯 Technical Skills Demonstrated</h3>
        <ul>
            <li>End-to-end data pipeline development</li>
            <li>Cloud data warehouse integration</li>
            <li>Data transformation & modeling</li>
            <li>Data quality assurance</li>
            <li>Automated testing & monitoring</li>
            <li>Professional documentation</li>
        </ul>
        
        <h3>🔄 Complete Daily Workflow</h3>
        <p><strong>9:00 AM → 9:30 AM → 10:00 AM → 11:00 AM → 12:00 PM</strong></p>
        <p><strong>Data → Quality → Transform → Analytics → Monitor</strong></p>
        
        <p style="color: green; font-weight: bold;">🎊 Congratulations! Your portfolio is complete and operational!</p>
        
        <hr>
        <p><small>Generated by Ad Campaign Analytics Portfolio Pipeline</small></p>
    </body>
    </html>
    """
    
    # Store email content in XCom for the EmailOperator
    context['task_instance'].xcom_push(key='completion_alert_subject', value=subject)
    context['task_instance'].xcom_push(key='completion_alert_html', value=html_content)
    
    return "Pipeline completion alert prepared"

# Create the DAG
dag = DAG(
    'master_portfolio_pipeline_dag',
    default_args=default_args,
    description='Master DAG orchestrating the complete Ad Campaign Analytics portfolio pipeline',
    schedule='0 8 * * *',  # Daily at 8:00 AM (before other DAGs)
    max_active_runs=1,
    tags=['master', 'orchestration', 'portfolio', 'pipeline'],
)

# Define tasks
start_task = EmptyOperator(task_id='start', dag=dag)

init_task = PythonOperator(
    task_id='initialize_portfolio_pipeline',
    python_callable=initialize_portfolio_pipeline,
    dag=dag,
)

# Email alert for pipeline start
start_alert_task = PythonOperator(
    task_id='send_pipeline_start_alert',
    python_callable=send_pipeline_start_alert,
    dag=dag,
)

start_email_task = EmailOperator(
    task_id='send_start_email',
    to=EMAIL_RECIPIENTS,
    subject="{{ task_instance.xcom_pull(task_ids='send_pipeline_start_alert', key='start_alert_subject') }}",
    html_content="{{ task_instance.xcom_pull(task_ids='send_pipeline_start_alert', key='start_alert_html') }}",
    dag=dag,
)

# Phase 1: Data Generation & Loading
trigger_data_task = TriggerDagRunOperator(
    task_id='trigger_data_generation_loading',
    trigger_dag_id='data_generation_loading_dag',
    dag=dag,
)

wait_data_task = ExternalTaskSensor(
    task_id='wait_for_data_generation_loading',
    external_dag_id='data_generation_loading_dag',
    external_task_id='end',
    timeout=3600,  # 1 hour timeout
    mode='reschedule',
    dag=dag,
)

data_complete_task = PythonOperator(
    task_id='log_data_phase_completion',
    python_callable=log_phase_completion,
    op_kwargs={'phase_name': 'Data Generation & Loading'},
    dag=dag,
)

# Phase 2: Data Quality Validation
trigger_validation_task = TriggerDagRunOperator(
    task_id='trigger_data_quality_validation',
    trigger_dag_id='data_quality_validation_dag',
    dag=dag,
)

wait_validation_task = ExternalTaskSensor(
    task_id='wait_for_data_quality_validation',
    external_dag_id='data_quality_validation_dag',
    external_task_id='end',
    timeout=1800,  # 30 minutes timeout
    mode='reschedule',
    dag=dag,
)

validation_complete_task = PythonOperator(
    task_id='log_validation_phase_completion',
    python_callable=log_phase_completion,
    op_kwargs={'phase_name': 'Data Quality Validation'},
    dag=dag,
)

# Phase 3: dbt Transformation
trigger_transformation_task = TriggerDagRunOperator(
    task_id='trigger_dbt_transformation',
    trigger_dag_id='dbt_transformation_dag',
    dag=dag,
)

wait_transformation_task = ExternalTaskSensor(
    task_id='wait_for_dbt_transformation',
    external_dag_id='dbt_transformation_dag',
    external_task_id='end',
    timeout=3600,  # 1 hour timeout
    mode='reschedule',
    dag=dag,
)

transformation_complete_task = PythonOperator(
    task_id='log_transformation_phase_completion',
    python_callable=log_phase_completion,
    op_kwargs={'phase_name': 'dbt Transformation'},
    dag=dag,
)

# Phase 4: Analytics & Testing
trigger_analytics_task = TriggerDagRunOperator(
    task_id='trigger_analytics_testing',
    trigger_dag_id='analytics_testing_dag',
    dag=dag,
)

wait_analytics_task = ExternalTaskSensor(
    task_id='wait_for_analytics_testing',
    external_dag_id='analytics_testing_dag',
    external_task_id='end',
    timeout=1800,  # 30 minutes timeout
    mode='reschedule',
    dag=dag,
)

analytics_complete_task = PythonOperator(
    task_id='log_analytics_phase_completion',
    python_callable=log_phase_completion,
    op_kwargs={'phase_name': 'Analytics & Testing'},
    dag=dag,
)

# Phase 5: Monitoring & Alerting
trigger_monitoring_task = TriggerDagRunOperator(
    task_id='trigger_monitoring_alerting',
    trigger_dag_id='monitoring_alerting_dag',
    dag=dag,
)

wait_monitoring_task = ExternalTaskSensor(
    task_id='wait_for_monitoring_alerting',
    external_dag_id='monitoring_alerting_dag',
    external_task_id='end',
    timeout=1800,  # 30 minutes timeout
    mode='reschedule',
    dag=dag,
)

monitoring_complete_task = PythonOperator(
    task_id='log_monitoring_phase_completion',
    python_callable=log_phase_completion,
    op_kwargs={'phase_name': 'Monitoring & Alerting'},
    dag=dag,
)

# Final completion logging
completion_task = PythonOperator(
    task_id='log_portfolio_completion',
    python_callable=log_portfolio_completion,
    dag=dag,
)

# Email alert for pipeline completion
completion_alert_task = PythonOperator(
    task_id='send_pipeline_completion_alert',
    python_callable=send_pipeline_completion_alert,
    dag=dag,
)

completion_email_task = EmailOperator(
    task_id='send_completion_email',
    to=EMAIL_RECIPIENTS,
    subject="{{ task_instance.xcom_pull(task_ids='send_pipeline_completion_alert', key='completion_alert_subject') }}",
    html_content="{{ task_instance.xcom_pull(task_ids='send_pipeline_completion_alert', key='completion_alert_html') }}",
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies - Sequential workflow with proper DAG triggering
start_task >> init_task >> start_alert_task >> start_email_task >> trigger_data_task >> wait_data_task >> data_complete_task >> trigger_validation_task >> wait_validation_task >> validation_complete_task >> trigger_transformation_task >> wait_transformation_task >> transformation_complete_task >> trigger_analytics_task >> wait_analytics_task >> analytics_complete_task >> trigger_monitoring_task >> wait_monitoring_task >> monitoring_complete_task >> completion_task >> completion_alert_task >> completion_email_task >> end_task

# Task documentation
start_task.doc = "Start master portfolio pipeline orchestration"
init_task.doc = "Initialize portfolio pipeline and log start"
start_alert_task.doc = "Prepare pipeline start email alert content"
start_email_task.doc = "Send pipeline start notification email"
trigger_data_task.doc = "Trigger data generation and loading DAG"
wait_data_task.doc = "Wait for data generation and loading DAG to complete"
data_complete_task.doc = "Log completion of data generation and loading phase"
trigger_validation_task.doc = "Trigger data quality validation DAG"
wait_validation_task.doc = "Wait for data quality validation DAG to complete"
validation_complete_task.doc = "Log completion of data quality validation phase"
trigger_transformation_task.doc = "Trigger dbt transformation DAG"
wait_transformation_task.doc = "Wait for dbt transformation DAG to complete"
transformation_complete_task.doc = "Log completion of dbt transformation phase"
trigger_analytics_task.doc = "Trigger analytics and testing DAG"
wait_analytics_task.doc = "Wait for analytics and testing DAG to complete"
analytics_complete_task.doc = "Log completion of analytics and testing phase"
trigger_monitoring_task.doc = "Trigger monitoring and alerting DAG"
wait_monitoring_task.doc = "Wait for monitoring and alerting DAG to complete"
monitoring_complete_task.doc = "Log completion of monitoring and alerting phase"
completion_task.doc = "Log portfolio pipeline completion and success"
completion_alert_task.doc = "Prepare pipeline completion email alert content"
completion_email_task.doc = "Send pipeline completion notification email"
end_task.doc = "Complete master portfolio pipeline orchestration"
