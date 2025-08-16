# DAG Visualizations

This folder contains visual representations of all Airflow DAGs in the Ad Campaign Spend Tracker project.

## 📊 Available Visualizations

### 1. **ad_data_generator_dag**
- **PNG**: `ad_data_generator_dag.png` (15.9 KB)
- **Purpose**: Data generation pipeline that creates realistic ad campaign data daily

### 2. **data_quality_validation_dag**
- **PNG**: `data_quality_validation_dag.png` (16.6 KB)
- **Purpose**: Data quality validation using Great Expectations after data loading

### 3. **dbt_transformation_dag**
- **PNG**: `dbt_transformation_dag.png` (16.4 KB)
- **Purpose**: dbt transformation pipeline to build Kimball star schema

### 4. **analytics_testing_dag**
- **PNG**: `analytics_testing_dag.png` (17.7 KB)
- **Purpose**: Analytics queries and comprehensive testing after dbt transformation

### 5. **monitoring_alerting_dag**
- **PNG**: `monitoring_alerting_dag.png` (16.0 KB)
- **Purpose**: Final monitoring, alerting, and pipeline health checks

### 6. **master_portfolio_pipeline_dag**
- **PNG**: `master_portfolio_pipeline_dag.png` (25.1 KB)
- **Purpose**: Master orchestration DAG that coordinates all other DAGs

## 🎨 File Format

- **PNG Files**: Raster images, good for web, email, and presentations

## 🚀 Usage

These visualizations can be used for:
- **Portfolio Documentation**: Showcase your data pipeline architecture
- **Team Presentations**: Explain workflow and dependencies
- **Technical Documentation**: Visual reference for pipeline design
- **Client Demos**: Demonstrate the complexity and sophistication of your solution

## 🔧 Generation

Images were generated using:
- **Airflow**: `airflow dags show <dag_name>` command
- **Graphviz**: DOT to image conversion (included in requirements.txt)
- **Python Script**: Automated generation for all DAGs

## 📁 Project Structure

```
ad_campaign_spend_tracker/
├── dags/                          # Airflow DAG definitions
├── dag_visualizations/            # This folder
│   ├── README.md                 # This documentation
│   └── *.png                     # PNG visualizations
├── dbt/                          # dbt transformation models
├── scripts/                      # Data generation and utility scripts
└── ...
```

---

*Generated on: August 16, 2025*  
*Author: Vandit Gupta*  
*Project: Ad Campaign Spend Tracker - Portfolio Demo*
