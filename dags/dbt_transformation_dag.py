"""
Ad Campaign Analytics - dbt Transformation DAG

This DAG runs dbt models to transform raw data into a complete star schema.
Creates dimension tables, fact tables, and mart tables for analytics.

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
        
        # Navigate to dbt directory and run debug
        result = subprocess.run(
            [dbt_path, 'debug'],
            capture_output=True,
            text=True,
            cwd=dbt_dir,
            env=os.environ  # Pass current environment variables
        )
        
        if result.returncode == 0:
            print("✅ dbt debug successful")
            print(f"Output: {result.stdout.strip()}")
            return "dbt configuration is valid"
        else:
            print(f"❌ dbt debug failed: {result.stderr}")
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
        
        # Load environment variables first
        load_environment_variables()
        
        # Calculate paths for this execution
        project_root = get_project_root()
        dbt_dir = os.path.join(project_root, 'dbt')
        dbt_path = os.path.join(project_root, 'venv', 'bin', 'dbt')
        
        print(f"📂 Running dbt from: {dbt_dir}")
        
        # Verify paths exist
        if not os.path.exists(dbt_dir):
            raise Exception(f"dbt directory not found: {dbt_dir}")
        if not os.path.exists(dbt_path):
            raise Exception(f"dbt executable not found: {dbt_path}")
        
        # Navigate to dbt directory and run all models
        result = subprocess.run(
            [dbt_path, 'run'],
            capture_output=True,
            text=True,
            cwd=dbt_dir,
            env=os.environ  # Pass current environment variables
        )
        
        if result.returncode == 0:
            print("✅ dbt models created successfully")
            print(f"Output: {result.stdout.strip()}")
            return "Star schema created successfully with all dimension, fact, and mart tables"
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
        str: Success message
    """
    
    try:
        print("🧪 Running dbt tests...")
        
        # Load environment variables first
        load_environment_variables()
        
        # Calculate paths for this execution
        project_root = get_project_root()
        dbt_dir = os.path.join(project_root, 'dbt')
        dbt_path = os.path.join(project_root, 'venv', 'bin', 'dbt')
        
        print(f"📂 Running dbt tests from: {dbt_dir}")
        
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
            print("✅ dbt tests passed")
            print(f"Output: {result.stdout.strip()}")
            return "All dbt tests passed successfully"
        else:
            print(f"⚠️ Some dbt tests failed: {result.stderr}")
            print(f"Output: {result.stdout.strip()}")
            return "dbt tests completed with some failures (continuing pipeline)"
            
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
        
        # Load environment variables first
        load_environment_variables()
        
        # Calculate paths for this execution
        project_root = get_project_root()
        dbt_dir = os.path.join(project_root, 'dbt')
        dbt_path = os.path.join(project_root, 'venv', 'bin', 'dbt')
        
        print(f"📂 Generating docs from: {dbt_dir}")
        
        # Verify paths exist
        if not os.path.exists(dbt_dir):
            raise Exception(f"dbt directory not found: {dbt_dir}")
        if not os.path.exists(dbt_path):
            raise Exception(f"dbt executable not found: {dbt_path}")
        
        # Navigate to dbt directory and generate docs
        result = subprocess.run(
            [dbt_path, 'docs', 'generate'],
            capture_output=True,
            text=True,
            cwd=dbt_dir,
            env=os.environ  # Pass current environment variables
        )
        
        if result.returncode == 0:
            print("✅ dbt documentation generated")
            print(f"Output: {result.stdout.strip()}")
            return "dbt documentation generated successfully"
        else:
            print(f"⚠️ dbt docs generation failed: {result.stderr}")
            print(f"Output: {result.stdout.strip()}")
            return "dbt docs generation failed (continuing pipeline)"
            
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
