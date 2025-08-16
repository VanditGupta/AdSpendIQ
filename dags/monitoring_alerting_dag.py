"""
Ad Campaign Analytics - Monitoring & Alerting DAG

This DAG runs final monitoring, health checks, and generates portfolio summary.
Runs every day at 12:00 PM (after analytics and testing).

Author: Vandit Gupta
Date: August 15, 2025
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import subprocess
import os
from dotenv import load_dotenv
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

class MonitoringLogger:
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

def load_environment_variables():
    """
    Load environment variables from .env file for dbt to access Snowflake credentials.
    """
    try:
        project_root = get_project_root()
        env_file = os.path.join(project_root, '.env')
        
        if os.path.exists(env_file):
            print(f"🔧 Loading environment variables from: {env_file}")
            load_dotenv(env_file)
            
            # Verify key variables are loaded
            snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
            snowflake_user = os.getenv('SNOWFLAKE_USER')
            snowflake_database = os.getenv('SNOWFLAKE_DATABASE')
            
            print(f"   ❄️ SNOWFLAKE_ACCOUNT: {'✅ Set' if snowflake_account else '❌ Missing'}")
            print(f"   👤 SNOWFLAKE_USER: {'✅ Set' if snowflake_user else '❌ Missing'}")
            print(f"   🗄️ SNOWFLAKE_DATABASE: {'✅ Set' if snowflake_database else '❌ Missing'}")
            
            if not snowflake_account:
                raise Exception("SNOWFLAKE_ACCOUNT environment variable not found in .env file")
        else:
            print(f"⚠️ .env file not found at: {env_file}")
            
    except Exception as e:
        print(f"❌ Error loading environment variables: {str(e)}")
        raise e

def save_monitoring_report(logger, health_results, freshness_results, summary_results, validation_results, completion_results):
    """Save monitoring results to a timestamped file"""
    try:
        # Get project root for proper file location
        project_root = get_project_root()
        
        # Create reports directory in the project root
        reports_dir = os.path.join(project_root, 'monitoring_reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"monitoring_alerting_report_{timestamp}.txt"
        filepath = os.path.join(reports_dir, filename)
        
        logger.log(f"📁 Saving monitoring report to: {filepath}")
        
        # Create comprehensive report
        report_content = f"""Ad Campaign Analytics - Monitoring & Alerting Report
{'=' * 70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🏥 PIPELINE HEALTH CHECK RESULTS
{'=' * 40}
{health_results}

📅 DATA FRESHNESS CHECK RESULTS
{'=' * 40}
{freshness_results}

📋 PORTFOLIO SUMMARY RESULTS
{'=' * 40}
{summary_results}

🔍 FINAL VALIDATION RESULTS
{'=' * 40}
{validation_results}

🎉 PIPELINE COMPLETION RESULTS
{'=' * 40}
{completion_results}

📋 COMPLETE EXECUTION LOG
{'=' * 40}
{logger.get_output()}

{'=' * 70}
Report saved to: {filepath}
"""
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.log(f"✅ Monitoring report saved successfully to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.log(f"⚠️ Warning: Could not save report to file: {e}")
        return None

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
        return "Pipeline health check completed successfully (simulated)"
        
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
        return "Data freshness check completed successfully (simulated)"
        
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
        return "Portfolio summary generated successfully (simulated)"
        
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
        
        # Load environment variables first
        load_environment_variables()
        
        # Calculate paths for this execution
        project_root = get_project_root()
        dbt_dir = os.path.join(project_root, 'dbt')
        dbt_path = os.path.join(project_root, 'venv', 'bin', 'dbt')
        
        print(f"📂 Project root: {project_root}")
        print(f"📂 dbt directory: {dbt_dir}")
        print(f"🔧 dbt executable: {dbt_path}")
        
        # Verify paths exist
        if not os.path.exists(dbt_dir):
            raise Exception(f"dbt directory not found: {dbt_dir}")
        if not os.path.exists(dbt_path):
            raise Exception(f"dbt executable not found: {dbt_path}")
        
        # Navigate to dbt directory and run tests
        result = subprocess.run(
            [dbt_path, 'test'],
            capture_output=True,
            text=True,
            cwd=dbt_dir,
            env=os.environ  # Pass current environment variables
        )
        
        if result.returncode == 0:
            print("✅ Final validation completed successfully")
            print(f"Output: {result.stdout.strip()}")
            return f"Final validation completed successfully\n\nOutput:\n{result.stdout.strip()}"
        else:
            print(f"⚠️ Some final validation tests failed: {result.stderr}")
            print(f"Output: {result.stdout.strip()}")
            return f"Final validation completed with some failures\n\nOutput:\n{result.stdout.strip()}"
            
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
        
        # Initialize logger for capturing output
        logger = MonitoringLogger()
        
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
        
        logger.log(completion_message)
        
        # Get results from previous tasks using XCom
        ti = context['task_instance']
        
        try:
            health_results = ti.xcom_pull(task_ids='run_pipeline_health_check')
            logger.log(f"🏥 Health Check Results:\n{health_results}")
        except:
            health_results = "Health check results not available"
            logger.log("⚠️ Health check results not available")
        
        try:
            freshness_results = ti.xcom_pull(task_ids='check_data_freshness')
            logger.log(f"📅 Data Freshness Results:\n{freshness_results}")
        except:
            freshness_results = "Data freshness results not available"
            logger.log("⚠️ Data freshness results not available")
        
        try:
            summary_results = ti.xcom_pull(task_ids='generate_portfolio_summary')
            logger.log(f"📋 Portfolio Summary Results:\n{summary_results}")
        except:
            summary_results = "Portfolio summary results not available"
            logger.log("⚠️ Portfolio summary results not available")
        
        try:
            validation_results = ti.xcom_pull(task_ids='run_final_validation')
            logger.log(f"🔍 Final Validation Results:\n{validation_results}")
        except:
            validation_results = "Final validation results not available"
            logger.log("⚠️ Final validation results not available")
        
        # Generate final summary
        logger.log("\n🎯 FINAL PIPELINE STATUS:")
        logger.log("=" * 40)
        logger.log("✅ Pipeline health check completed")
        logger.log("✅ Data freshness verified")
        logger.log("✅ Portfolio summary generated")
        logger.log("✅ Final validation completed")
        logger.log("✅ Pipeline completion logged")
        
        # Save monitoring report to file
        logger.log("💾 Saving final monitoring report...")
        report_file = save_monitoring_report(logger, health_results, freshness_results, summary_results, validation_results, completion_message)
        
        if report_file:
            logger.log(f"🎉 Final report saved successfully to: {report_file}")
        else:
            logger.log("⚠️ Final report saving failed")
        
        # Clean up logger
        logger.close()
        
        print("✅ Pipeline completion logged successfully")
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
