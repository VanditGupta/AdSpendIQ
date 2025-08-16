# 🚀 Airflow DAG Overview - Ad Campaign Analytics Portfolio

## 📊 **Complete DAG Architecture**

This document provides a comprehensive overview of all Airflow DAGs in the Ad Campaign Analytics portfolio project.

## 🏗️ **DAG Structure & Workflow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MASTER PORTFOLIO PIPELINE                        │
│                              (8:00 AM)                                     │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DATA GENERATION & LOADING                      │
│                              (9:00 AM)                                     │
│                    ad_data_generator_dag.py                                │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   PHASE 2: DATA QUALITY VALIDATION                         │
│                              (9:30 AM)                                     │
│                data_quality_validation_dag.py                              │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: DBT TRANSFORMATION                           │
│                              (10:00 AM)                                    │
│                   dbt_transformation_dag.py                                │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: ANALYTICS & TESTING                            │
│                              (11:00 AM)                                    │
│                  analytics_testing_dag.py                                  │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  PHASE 5: MONITORING & ALERTING                            │
│                              (12:00 PM)                                    │
│                monitoring_alerting_dag.py                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📋 **Detailed DAG Descriptions**

### **1. Master Portfolio Pipeline DAG**
- **File**: `master_portfolio_pipeline_dag.py`
- **Schedule**: Daily at 8:00 AM
- **Purpose**: Orchestrates the entire portfolio pipeline workflow
- **Key Features**:
  - Initializes portfolio pipeline
  - Triggers each phase sequentially
  - Monitors overall pipeline health
  - Logs completion status

### **2. Data Generation & Loading DAG**
- **File**: `ad_data_generator_dag.py`
- **Schedule**: Daily at 9:00 AM
- **Purpose**: Generates and loads daily ad campaign data
- **Key Features**:
  - Generates 5,000 realistic ad campaign records
  - Loads data to Snowflake with duplicate prevention
  - Manages data retention (90-day policy)
  - Archives old data automatically

### **3. Data Quality Validation DAG**
- **File**: `data_quality_validation_dag.py`
- **Schedule**: Daily at 9:30 AM
- **Purpose**: Validates data quality using Great Expectations
- **Key Features**:
  - Fetches sample data from Snowflake
  - Runs 28 comprehensive validation checks
  - Validates schema, business logic, and values
  - Triggers next phase if validation passes

### **4. dbt Transformation DAG**
- **File**: `dbt_transformation_dag.py`
- **Schedule**: Daily at 10:00 AM
- **Purpose**: Builds Kimball star schema using dbt
- **Key Features**:
  - Installs dbt dependencies
  - Runs staging, dimension, fact, and mart models
  - Executes dbt tests for data quality
  - Generates dbt documentation

### **5. Analytics & Testing DAG**
- **File**: `analytics_testing_dag.py`
- **Schedule**: Daily at 11:00 AM
- **Purpose**: Runs analytics queries and comprehensive testing
- **Key Features**:
  - Executes portfolio showcase queries
  - Runs PyTest test suite
  - Performs data quality monitoring
  - Generates analytics reports

### **6. Monitoring & Alerting DAG**
- **File**: `monitoring_alerting_dag.py`
- **Schedule**: Daily at 12:00 PM
- **Purpose**: Final monitoring and portfolio completion
- **Key Features**:
  - Checks pipeline health and status
  - Generates portfolio summary
  - Sends success notifications
  - Logs final completion status

## ⏰ **Daily Schedule & Timing**

| Time | Phase | DAG | Description |
|------|-------|-----|-------------|
| **8:00 AM** | **Initialization** | `master_portfolio_pipeline_dag` | Portfolio pipeline orchestration |
| **9:00 AM** | **Data Generation** | `ad_data_generator_dag` | Generate & load daily data |
| **9:30 AM** | **Data Quality** | `data_quality_validation_dag` | Validate data quality |
| **10:00 AM** | **Transformation** | `dbt_transformation_dag` | Build Kimball star schema |
| **11:00 AM** | **Analytics** | `analytics_testing_dag` | Run queries & tests |
| **12:00 PM** | **Monitoring** | `monitoring_alerting_dag` | Final checks & completion |

## 🔄 **DAG Dependencies & Flow**

### **Sequential Execution**
1. **Master DAG** initializes at 8:00 AM
2. **Data Generation** runs at 9:00 AM
3. **Data Quality** waits for data loading completion
4. **dbt Transformation** waits for validation success
5. **Analytics** waits for transformation completion
6. **Monitoring** waits for analytics completion

### **Trigger Mechanisms**
- Each DAG uses `TriggerDagRunOperator` to trigger the next phase
- DAGs have `depends_on_past=True` to ensure proper sequencing
- XCom communication between DAGs for data sharing

## 🎯 **Portfolio Value & Skills Demonstrated**

### **Technical Skills**
- **Apache Airflow**: Complex workflow orchestration
- **DAG Design**: Multi-phase pipeline architecture
- **Task Dependencies**: Sequential and parallel execution
- **XCom Communication**: Inter-DAG data sharing
- **Error Handling**: Retry mechanisms and failure handling
- **Scheduling**: Cron-based automation

### **Data Engineering Skills**
- **End-to-End Pipeline**: Complete data lifecycle management
- **Data Quality**: Automated validation and monitoring
- **Data Transformation**: dbt modeling and testing
- **Testing**: Comprehensive test automation
- **Monitoring**: Pipeline health and performance tracking

### **Business Understanding**
- **Portfolio Management**: Professional project demonstration
- **Documentation**: Comprehensive task and DAG documentation
- **Best Practices**: Production-ready pipeline design
- **Scalability**: Cloud-native architecture

## 🚀 **How to Use These DAGs**

### **1. Testing Individual DAGs**
```bash
# Test data generation DAG
airflow dags test ad_data_generator_dag 2025-01-15

# Test data quality validation DAG
airflow dags test data_quality_validation_dag 2025-01-15

# Test dbt transformation DAG
airflow dags test dbt_transformation_dag 2025-01-15
```

### **2. Running Complete Pipeline**
```bash
# Trigger master portfolio pipeline
airflow dags trigger master_portfolio_pipeline_dag

# Monitor pipeline progress
airflow dags list
airflow tasks list master_portfolio_pipeline_dag
```

### **3. Monitoring Pipeline Health**
- **Airflow UI**: View DAG status and logs
- **XCom**: Check inter-task communication
- **Logs**: Monitor execution and error logs
- **Health Checks**: Automated pipeline status monitoring

## 📊 **DAG Performance Metrics**

### **Expected Execution Times**
- **Data Generation**: 2-3 minutes
- **Data Quality Validation**: 1-2 minutes
- **dbt Transformation**: 3-5 minutes
- **Analytics & Testing**: 2-3 minutes
- **Monitoring**: 1-2 minutes
- **Total Pipeline**: 9-15 minutes

### **Success Criteria**
- **Data Generation**: 5,000+ records created
- **Data Quality**: 28/28 validations passed
- **dbt Models**: All models built successfully
- **Testing**: All tests passed
- **Health Score**: 80%+ pipeline health

## 🔧 **Configuration & Customization**

### **Environment Variables**
All DAGs use environment variables for:
- Snowflake connection details
- Database and schema names
- Warehouse configurations
- Retry and timeout settings

### **Scheduling**
- DAGs can be customized for different time zones
- Retry mechanisms configurable per DAG
- Email notifications configurable
- Failure handling strategies

## 🎉 **Portfolio Ready Status**

### **✅ What's Complete**
- **5 Comprehensive DAGs**: Covering entire data pipeline
- **Automated Workflow**: Daily execution with proper sequencing
- **Error Handling**: Robust retry and failure mechanisms
- **Documentation**: Complete task and DAG documentation
- **Testing**: Automated validation and quality checks

### **🚀 Ready for Demonstration**
- **Technical Interviews**: Showcase Airflow expertise
- **Portfolio Reviews**: Demonstrate end-to-end capabilities
- **Code Reviews**: Professional, production-ready code
- **Skill Validation**: Comprehensive data engineering skills

---

**🎯 Your Ad Campaign Analytics portfolio now has a complete, professional Airflow DAG architecture that demonstrates enterprise-level data engineering capabilities!**
