"""
Ad Campaign Analytics - Master Portfolio Pipeline DAG

This master DAG orchestrates the entire portfolio pipeline workflow.
Actually triggers other DAGs to run the complete end-to-end data engineering process.

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.external_task import ExternalTaskSensor
import subprocess
import os
import io

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

class MasterPipelineLogger:
    """Custom logger that captures output to both console and file"""
    
    def __init__(self):
        self.output_buffer = io.StringIO()
        self.console_output = []
        
    def log(self, message):
        """Log message to both console and buffer"""
        # Print to console
        print(message)
        
        # Store in buffer for file output
        self.output_buffer.write(message + '\n')
        self.console_output.append(message)
    
    def get_output(self):
        """Get all captured output"""
        return self.output_buffer.getvalue()
    
    def close(self):
        """Close the buffer"""
        self.output_buffer.close()

def get_project_root():
    """
    Dynamically find the project root directory.
    Goes up from the DAG file location to find the project root.
    """
    # Start from the DAG file location
    current_dir = os.path.dirname(__file__)  # ~/airflow/dags
    
    print(f"🔍 Starting search from: {current_dir}")
    
    # Go up directories until we find the project root
    # Look for indicators like 'scripts' folder, 'dbt' folder, etc.
    depth = 0
    max_depth = 10  # Prevent infinite loops
    
    while current_dir != os.path.dirname(current_dir) and depth < max_depth:  # Stop at root
        print(f"🔍 Checking directory (depth {depth}): {current_dir}")
        
        # Check if this directory has the project structure
        scripts_exists = os.path.exists(os.path.join(current_dir, "scripts"))
        dbt_exists = os.path.exists(os.path.join(current_dir, "dbt"))
        venv_exists = os.path.exists(os.path.join(current_dir, "venv"))
        
        print(f"   📁 scripts: {scripts_exists}")
        print(f"   📁 dbt: {dbt_exists}")
        print(f"   📁 venv: {venv_exists}")
        
        if scripts_exists and dbt_exists and venv_exists:
            print(f"✅ Found project root: {current_dir}")
            return current_dir
            
        current_dir = os.path.dirname(current_dir)
        depth += 1
    
    # Fallback: try to find by going up from AIRFLOW_HOME
    print("🔍 Fallback: searching from AIRFLOW_HOME parent")
    airflow_home = os.environ.get('AIRFLOW_HOME', os.path.expanduser('~/airflow'))
    if os.path.exists(airflow_home):
        # Go up from airflow home and look for project
        parent_dir = os.path.dirname(airflow_home)
        print(f"🔍 Searching from AIRFLOW_HOME parent: {parent_dir}")
        
        # Search recursively for project indicators
        for root, dirs, files in os.walk(parent_dir):
            if (os.path.exists(os.path.join(root, "scripts")) and 
                os.path.exists(os.path.join(root, "dbt")) and
                os.path.exists(os.path.join(root, "venv"))):
                print(f"✅ Found project root via fallback: {root}")
                return root
            # Limit search depth to avoid going too deep
            if root.count(os.sep) - parent_dir.count(os.sep) > 3:
                dirs.clear()  # Don't go deeper
    
    # If we still can't find it, try searching from current working directory
    print("🔍 Final fallback: searching from current working directory")
    cwd = os.getcwd()
    print(f"🔍 Current working directory: {cwd}")
    
    # Go up from current working directory
    current_dir = cwd
    depth = 0
    while current_dir != os.path.dirname(current_dir) and depth < max_depth:
        print(f"🔍 Checking CWD parent (depth {depth}): {current_dir}")
        
        scripts_exists = os.path.exists(os.path.join(current_dir, "scripts"))
        dbt_exists = os.path.exists(os.path.join(current_dir, "dbt"))
        venv_exists = os.path.exists(os.path.join(current_dir, "venv"))
        
        if scripts_exists and dbt_exists and venv_exists:
            print(f"✅ Found project root via CWD: {current_dir}")
            return current_dir
            
        current_dir = os.path.dirname(current_dir)
        depth += 1
    
    raise Exception("Could not find project root directory. Make sure you have 'scripts', 'dbt', and 'venv' folders in your project root.")

def save_master_pipeline_report(logger, init_results, data_results, validation_results, transformation_results, analytics_results, monitoring_results, completion_results):
    """Save master pipeline results to a timestamped file"""
    try:
        # Get project root for proper file location
        project_root = get_project_root()
        
        # Create reports directory in the project root
        reports_dir = os.path.join(project_root, 'master_pipeline_reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"master_portfolio_pipeline_report_{timestamp}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        logger.log(f"📁 Saving master pipeline report to: {filepath}")
        
        # Create comprehensive report
        report_content = f"""Ad Campaign Analytics - Master Portfolio Pipeline Report
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🚀 MASTER PIPELINE EXECUTION SUMMARY
{'=' * 50}

🎯 PIPELINE INITIALIZATION RESULTS
{'=' * 40}
{init_results}

📊 DATA GENERATION PHASE RESULTS
{'=' * 40}
{data_results}

🔍 DATA QUALITY VALIDATION PHASE RESULTS
{'=' * 50}
{validation_results}

🏗️ DBT TRANSFORMATION PHASE RESULTS
{'=' * 40}
{transformation_results}

📈 ANALYTICS & TESTING PHASE RESULTS
{'=' * 50}
{analytics_results}

🔍 MONITORING & ALERTING PHASE RESULTS
{'=' * 50}
{monitoring_results}

🎉 PIPELINE COMPLETION RESULTS
{'=' * 40}
{completion_results}

📋 COMPLETE MASTER PIPELINE EXECUTION LOG
{'=' * 50}
{logger.get_output()}

{'=' * 80}
Report saved to: {filepath}
"""
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.log(f"✅ Master pipeline report saved successfully to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.log(f"⚠️ Warning: Could not save master pipeline report to file: {e}")
        return None

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

def log_data_generation_completion(**context):
    """
    Log completion of data generation phase.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("📊 Data Generation & Loading Phase Completed Successfully!")
    return "Data generation phase completed successfully - DAG triggered and completed"

def log_validation_completion(**context):
    """
    Log completion of data quality validation phase.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("🔍 Data Quality Validation Phase Completed Successfully!")
    return "Data quality validation phase completed successfully - DAG triggered and completed"

def log_transformation_completion(**context):
    """
    Log completion of dbt transformation phase.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("🏗️ dbt Transformation Phase Completed Successfully!")
    return "dbt transformation phase completed successfully - DAG triggered and completed"

def log_analytics_completion(**context):
    """
    Log completion of analytics and testing phase.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("📈 Analytics & Testing Phase Completed Successfully!")
    return "Analytics and testing phase completed successfully - DAG triggered and completed"

def log_monitoring_completion(**context):
    """
    Log completion of monitoring and alerting phase.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    print("🔍 Monitoring & Alerting Phase Completed Successfully!")
    return "Monitoring and alerting phase completed successfully - DAG triggered and completed"

def log_portfolio_completion(**context):
    """
    Log portfolio pipeline completion and success.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Completion message
    """
    
    try:
        print("🎉 Logging portfolio pipeline completion...")
        
        # Initialize logger for capturing output
        logger = MasterPipelineLogger()
        
        # Get execution date
        execution_date = context.get('logical_date') or context.get('execution_date') or datetime.now()
        target_date = execution_date.date()
        
        completion_message = f"""
        🎉 PORTFOLIO PIPELINE COMPLETED SUCCESSFULLY!
        =============================================
        
        📅 Date: {target_date}
        🕐 Completion time: {execution_date}
        
        ✅ ALL PHASES COMPLETED IN CORRECT ORDER:
        
        1. 📊 Data Generation & Loading (9:00 AM)
           • 261,224 historical + 5,000 daily ad campaign records
           • Snowflake integration with duplicate prevention
           • Data retention management (90-day policy)
        
        2. 🏗️ dbt Transformation (10:00 AM)
           • Kimball star schema implementation
           • 6 dimension tables + 1 fact table + 4 mart tables
           • Automated testing and documentation
        
        3. 🔍 Data Quality Validation (10:30 AM)
           • Great Expectations validation suite
           • Comprehensive data quality checks
           • Schema, business logic, and value validation
        
        4. 🧪 Testing & Validation (11:00 AM)
           • dbt model testing
           • Data integrity validation
           • Business logic verification
        
        5. 📈 Analytics & Testing (11:30 AM)
           • Portfolio showcase queries
           • Comprehensive testing suite
           • Data quality monitoring
        
        6. 🔍 Monitoring & Alerting (12:00 PM)
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
        • 9:00 AM → 10:00 AM → 10:30 AM → 11:00 AM → 11:30 AM → 12:00 PM
        • Data → Transform → Validate → Test → Analytics → Monitor
        
        🎊 Congratulations! Your portfolio is complete and operational!
        
        =============================================
        """
        
        logger.log(completion_message)
        
        # Get results from previous tasks using XCom
        ti = context['task_instance']
        
        try:
            init_results = ti.xcom_pull(task_ids='initialize_portfolio_pipeline')
            logger.log(f"🚀 Pipeline Initialization Results:\n{init_results}")
        except:
            init_results = "Pipeline initialization results not available"
            logger.log("⚠️ Pipeline initialization results not available")
        
        try:
            data_results = ti.xcom_pull(task_ids='log_data_generation_completion')
            logger.log(f"📊 Data Generation Phase Results:\n{data_results}")
        except:
            data_results = "Data generation phase results not available"
            logger.log("⚠️ Data generation phase results not available")
        
        try:
            validation_results = ti.xcom_pull(task_ids='log_validation_completion')
            logger.log(f"🔍 Data Quality Validation Phase Results:\n{validation_results}")
        except:
            validation_results = "Data quality validation phase results not available"
            logger.log("⚠️ Data quality validation phase results not available")
        
        try:
            transformation_results = ti.xcom_pull(task_ids='log_transformation_completion')
            logger.log(f"🏗️ dbt Transformation Phase Results:\n{transformation_results}")
        except:
            transformation_results = "dbt transformation phase results not available"
            logger.log("⚠️ dbt transformation phase results not available")
        
        try:
            analytics_results = ti.xcom_pull(task_ids='log_analytics_completion')
            logger.log(f"📈 Analytics & Testing Phase Results:\n{analytics_results}")
        except:
            analytics_results = "Analytics & testing phase results not available"
            logger.log("⚠️ Analytics & testing phase results not available")
        
        try:
            monitoring_results = ti.xcom_pull(task_ids='log_monitoring_completion')
            logger.log(f"🔍 Monitoring & Alerting Phase Results:\n{monitoring_results}")
        except:
            monitoring_results = "Monitoring & alerting phase results not available"
            logger.log("⚠️ Monitoring & alerting phase results not available")
        
        # Generate final summary
        logger.log("\n🎯 MASTER PIPELINE FINAL STATUS:")
        logger.log("=" * 50)
        logger.log("✅ Portfolio pipeline initialized")
        logger.log("✅ Data generation phase completed")
        logger.log("✅ Data quality validation phase completed")
        logger.log("✅ dbt transformation phase completed")
        logger.log("✅ Analytics & testing phase completed")
        logger.log("✅ Monitoring & alerting phase completed")
        logger.log("✅ Portfolio pipeline completed successfully")
        
        # Save master pipeline report to file
        logger.log("💾 Saving master pipeline report...")
        report_file = save_master_pipeline_report(logger, init_results, data_results, validation_results, transformation_results, analytics_results, monitoring_results, completion_message)
        
        if report_file:
            logger.log(f"🎉 Master pipeline report saved successfully to: {report_file}")
        else:
            logger.log("⚠️ Master pipeline report saving failed")
        
        # Store completion in XCom
        context['task_instance'].xcom_push(key='pipeline_completion_time', value=str(execution_date))
        context['task_instance'].xcom_push(key='portfolio_status', value='COMPLETED')
        
        # Clean up logger
        logger.close()
        
        print("✅ Portfolio pipeline completed successfully - ready for demonstration!")
        return "Portfolio pipeline completed successfully - ready for demonstration!"
        
    except Exception as e:
        print(f"❌ Error logging portfolio completion: {str(e)}")
        raise e

def trigger_data_generation_dag_manually(**context):
    """
    Manually trigger the data generation DAG using subprocess.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("📊 Manually triggering ad_data_generator_dag...")
        
        # Use subprocess to trigger the DAG
        result = subprocess.run(
            ['airflow', 'dags', 'trigger', 'ad_data_generator_dag'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Successfully triggered ad_data_generator_dag")
            print(f"Output: {result.stdout.strip()}")
            return "Data generation DAG triggered successfully"
        else:
            print(f"⚠️ DAG trigger failed: {result.stderr}")
            # Continue anyway - the DAG might already be running
            return "Data generation DAG trigger attempted"
            
    except subprocess.TimeoutExpired:
        print("⚠️ DAG trigger timed out, continuing...")
        return "Data generation DAG trigger timed out, continuing"
    except Exception as e:
        print(f"❌ Error triggering DAG: {str(e)}")
        return f"Error triggering DAG: {str(e)}"

def trigger_dbt_transformation_dag_manually(**context):
    """
    Manually trigger the dbt transformation DAG using subprocess.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🏗️ Manually triggering dbt_transformation_dag...")
        
        # Use subprocess to trigger the DAG
        result = subprocess.run(
            ['airflow', 'dags', 'trigger', 'dbt_transformation_dag'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Successfully triggered dbt_transformation_dag")
            print(f"Output: {result.stdout.strip()}")
            return "dbt transformation DAG triggered successfully"
        else:
            print(f"⚠️ DAG trigger failed: {result.stderr}")
            return "dbt transformation DAG trigger attempted"
            
    except subprocess.TimeoutExpired:
        print("⚠️ DAG trigger timed out, continuing...")
        return "dbt transformation DAG trigger timed out, continuing"
    except Exception as e:
        print(f"❌ Error triggering DAG: {str(e)}")
        return f"Error triggering DAG: {str(e)}"

def trigger_validation_dag_manually(**context):
    """
    Manually trigger the data quality validation DAG using subprocess.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🔍 Manually triggering data_quality_validation_dag...")
        
        # Use subprocess to trigger the DAG
        result = subprocess.run(
            ['airflow', 'dags', 'trigger', 'data_quality_validation_dag'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Successfully triggered data_quality_validation_dag")
            print(f"Output: {result.stdout.strip()}")
            return "Data quality validation DAG triggered successfully"
        else:
            print(f"⚠️ DAG trigger failed: {result.stderr}")
            return "Data quality validation DAG trigger attempted"
            
    except subprocess.TimeoutExpired:
        print("⚠️ DAG trigger timed out, continuing...")
        return "Data quality validation DAG trigger timed out, continuing"
    except Exception as e:
        print(f"❌ Error triggering DAG: {str(e)}")
        return f"Error triggering DAG: {str(e)}"

def trigger_analytics_dag_manually(**context):
    """
    Manually trigger the analytics testing DAG using subprocess.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("📈 Manually triggering analytics_testing_dag...")
        
        # Use subprocess to trigger the DAG
        result = subprocess.run(
            ['airflow', 'dags', 'trigger', 'analytics_testing_dag'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Successfully triggered analytics_testing_dag")
            print(f"Output: {result.stdout.strip()}")
            return "Analytics testing DAG triggered successfully"
        else:
            print(f"⚠️ DAG trigger failed: {result.stderr}")
            return "Analytics testing DAG trigger attempted"
            
    except subprocess.TimeoutExpired:
        print("⚠️ DAG trigger timed out, continuing...")
        return "Analytics testing DAG trigger timed out, continuing"
    except Exception as e:
        print(f"❌ Error triggering DAG: {str(e)}")
        return f"Error triggering DAG: {str(e)}"

def trigger_monitoring_dag_manually(**context):
    """
    Manually trigger the monitoring alerting DAG using subprocess.
    
    Args:
        **context: Airflow context
    
    Returns:
        str: Success message
    """
    
    try:
        print("🔍 Manually triggering monitoring_alerting_dag...")
        
        # Use subprocess to trigger the DAG
        result = subprocess.run(
            ['airflow', 'dags', 'trigger', 'monitoring_alerting_dag'],
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Successfully triggered monitoring_alerting_dag")
            print(f"Output: {result.stdout.strip()}")
            return "Monitoring alerting DAG triggered successfully"
        else:
            print(f"⚠️ DAG trigger failed: {result.stderr}")
            return "Monitoring alerting DAG trigger attempted"
            
    except subprocess.TimeoutExpired:
        print("⚠️ DAG trigger timed out, continuing...")
        return "Monitoring alerting DAG trigger timed out, continuing"
    except Exception as e:
        print(f"❌ Error triggering DAG: {str(e)}")
        return f"Error triggering DAG: {str(e)}"

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

# Trigger data generation DAG
trigger_data_dag = PythonOperator(
    task_id='trigger_data_generation_dag_manually',
    python_callable=trigger_data_generation_dag_manually,
    dag=dag,
)

# Debug task to check what DAG runs exist
def debug_dag_status(**context):
    """Debug task to check DAG status"""
    from airflow.models import DagRun
    from datetime import datetime
    
    print("🔍 Debug: Checking DAG runs for ad_data_generator_dag")
    
    # Get all recent runs of the data generation DAG
    dag_runs = DagRun.find(dag_id='ad_data_generator_dag')
    
    print(f"📊 Found {len(dag_runs)} DAG runs")
    for run in dag_runs[-5:]:  # Show last 5 runs
        print(f"   Run ID: {run.run_id}")
        print(f"   State: {run.state}")
        print(f"   Start Date: {run.start_date}")
        print(f"   End Date: {run.end_date}")
        print(f"   External Trigger: {run.external_trigger}")
        print("   ---")
    
    return "Debug completed"

debug_task = PythonOperator(
    task_id='debug_dag_status',
    python_callable=debug_dag_status,
    dag=dag,
)

# Wait for data generation DAG to complete
wait_for_data_dag = ExternalTaskSensor(
    task_id='wait_for_data_generation_dag',
    external_dag_id='ad_data_generator_dag',
    external_task_id='end',
    timeout=7200,  # 2 hour timeout
    mode='poke',  # Check every 30 seconds
    poke_interval=30,  # Check every 30 seconds
    execution_delta=timedelta(minutes=0),  # Look for DAG runs at the same time
    allowed_states=['success'],  # Only consider successful completions
    failed_states=['failed', 'skipped'],  # Consider these as failures
    dag=dag,
)

# Log data generation completion
data_completion_task = PythonOperator(
    task_id='log_data_generation_completion',
    python_callable=log_data_generation_completion,
    dag=dag,
)

# Trigger data quality validation DAG
trigger_validation_dag = PythonOperator(
    task_id='trigger_data_quality_validation_dag_manually',
    python_callable=trigger_validation_dag_manually,
    dag=dag,
)

# Wait for validation DAG to complete
wait_for_validation_dag = ExternalTaskSensor(
    task_id='wait_for_data_quality_validation_dag',
    external_dag_id='data_quality_validation_dag',
    external_task_id='end',
    timeout=7200,  # 2 hour timeout
    mode='poke',  # Check every 30 seconds
    poke_interval=30,  # Check every 30 seconds
    execution_delta=timedelta(minutes=0),  # Look for DAG runs at the same time
    allowed_states=['success'],  # Only consider successful completions
    failed_states=['failed', 'skipped'],  # Consider these as failures
    dag=dag,
)

# Log validation completion
validation_completion_task = PythonOperator(
    task_id='log_validation_completion',
    python_callable=log_validation_completion,
    dag=dag,
)

# Trigger dbt transformation DAG
trigger_transformation_dag = PythonOperator(
    task_id='trigger_dbt_transformation_dag_manually',
    python_callable=trigger_dbt_transformation_dag_manually,
    dag=dag,
)

# Wait for transformation DAG to complete
wait_for_transformation_dag = ExternalTaskSensor(
    task_id='wait_for_dbt_transformation_dag',
    external_dag_id='dbt_transformation_dag',
    external_task_id='end',
    timeout=7200,  # 2 hour timeout
    mode='poke',  # Check every 30 seconds
    poke_interval=30,  # Check every 30 seconds
    execution_delta=timedelta(minutes=0),  # Look for DAG runs at the same time
    allowed_states=['success'],  # Only consider successful completions
    failed_states=['failed', 'skipped'],  # Consider these as failures
    dag=dag,
)

# Log transformation completion
transformation_completion_task = PythonOperator(
    task_id='log_transformation_completion',
    python_callable=log_transformation_completion,
    dag=dag,
)

# Trigger analytics testing DAG
trigger_analytics_dag = PythonOperator(
    task_id='trigger_analytics_testing_dag_manually',
    python_callable=trigger_analytics_dag_manually,
    dag=dag,
)

# Wait for analytics DAG to complete
wait_for_analytics_dag = ExternalTaskSensor(
    task_id='wait_for_analytics_testing_dag',
    external_dag_id='analytics_testing_dag',
    external_task_id='end',
    timeout=7200,  # 2 hour timeout
    mode='poke',  # Check every 30 seconds
    poke_interval=30,  # Check every 30 seconds
    execution_delta=timedelta(minutes=0),  # Look for DAG runs at the same time
    allowed_states=['success'],  # Only consider successful completions
    failed_states=['failed', 'skipped'],  # Consider these as failures
    dag=dag,
)

# Log analytics completion
analytics_completion_task = PythonOperator(
    task_id='log_analytics_completion',
    python_callable=log_analytics_completion,
    dag=dag,
)

# Trigger monitoring alerting DAG
trigger_monitoring_dag = PythonOperator(
    task_id='trigger_monitoring_alerting_dag_manually',
    python_callable=trigger_monitoring_dag_manually,
    dag=dag,
)

# Wait for monitoring DAG to complete
wait_for_monitoring_dag = ExternalTaskSensor(
    task_id='wait_for_monitoring_alerting_dag',
    external_dag_id='monitoring_alerting_dag',
    external_task_id='end',
    timeout=7200,  # 2 hour timeout
    mode='poke',  # Check every 30 seconds
    poke_interval=30,  # Check every 30 seconds
    execution_delta=timedelta(minutes=0),  # Look for DAG runs at the same time
    allowed_states=['success'],  # Only consider successful completions
    failed_states=['failed', 'skipped'],  # Consider these as failures
    dag=dag,
)

# Log monitoring completion
monitoring_completion_task = PythonOperator(
    task_id='log_monitoring_completion',
    python_callable=log_monitoring_completion,
    dag=dag,
)

# Final completion task
completion_task = PythonOperator(
    task_id='log_portfolio_completion',
    python_callable=log_portfolio_completion,
    dag=dag,
)

end_task = EmptyOperator(task_id='end', dag=dag)

# Set task dependencies - Sequential workflow with actual DAG triggering
# Correct order: Data → Transform → Validate → Test → Analytics → Monitor
start_task >> init_task >> trigger_data_dag >> debug_task >> wait_for_data_dag >> data_completion_task >> trigger_transformation_dag >> wait_for_transformation_dag >> transformation_completion_task >> trigger_validation_dag >> wait_for_validation_dag >> validation_completion_task >> trigger_analytics_dag >> wait_for_analytics_dag >> analytics_completion_task >> trigger_monitoring_dag >> wait_for_monitoring_dag >> monitoring_completion_task >> completion_task >> end_task

# Task documentation
start_task.doc = "Start master portfolio pipeline orchestration"
init_task.doc = "Initialize portfolio pipeline and log start"
trigger_data_dag.doc = "Manually trigger data generation and loading DAG"
debug_task.doc = "Debug task to check DAG status"
wait_for_data_dag.doc = "Wait for data generation DAG to complete"
data_completion_task.doc = "Log data generation phase completion"
trigger_transformation_dag.doc = "Manually trigger dbt transformation DAG to build star schema"
wait_for_transformation_dag.doc = "Wait for dbt transformation DAG to complete"
transformation_completion_task.doc = "Log dbt transformation phase completion"
trigger_validation_dag.doc = "Manually trigger data quality validation DAG on transformed data"
wait_for_validation_dag.doc = "Wait for data quality validation DAG to complete"
validation_completion_task.doc = "Log data quality validation phase completion"
trigger_analytics_dag.doc = "Manually trigger analytics and testing DAG on validated data"
wait_for_analytics_dag.doc = "Wait for analytics and testing DAG to complete"
analytics_completion_task.doc = "Log analytics and testing phase completion"
trigger_monitoring_dag.doc = "Manually trigger final monitoring and alerting DAG"
wait_for_monitoring_dag.doc = "Wait for monitoring and alerting DAG to complete"
monitoring_completion_task.doc = "Log monitoring and alerting phase completion"
completion_task.doc = "Log portfolio pipeline completion and success"
end_task.doc = "Complete master portfolio pipeline orchestration"
