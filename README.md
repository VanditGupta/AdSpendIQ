# 🚀 Ad Campaign Spend Tracker

A comprehensive **Data Engineering Portfolio Project** demonstrating end-to-end data pipeline development, from data generation to business intelligence.

## 📊 Project Overview

This project simulates a real-world **Ad Campaign Analytics** system, processing data from multiple advertising platforms (Google, Facebook, LinkedIn, TikTok, Twitter) to provide actionable insights for marketing teams.

### 🎯 **Portfolio Highlights**

- **End-to-End Data Pipeline**: Airflow → Snowflake → dbt → Analytics
- **Real Business Intelligence**: 4.58B impressions, $109.6M spend analysis
- **Professional Star Schema**: Kimball methodology implementation with visual diagrams
- **Data Quality Assurance**: Great Expectations + PyTest testing
- **Modern Data Stack**: Airflow, Snowflake, dbt, Python
- **Production-Ready Code**: Comprehensive testing, documentation, error handling

## 🏗️ Architecture

### 🌟 **Star Schema Data Model**

Our data architecture follows the **Kimball Star Schema** methodology, featuring:

- **1 Fact Table**: `FACT_CAMPAIGN_PERFORMANCE` - Central hub for all metrics
- **6 Dimension Tables**: Campaigns, Platforms, Geography, Devices, Time, Ad Formats
- **Optimized Performance**: Indexed foreign keys, denormalized structure
- **Business Focus**: Aligned with marketing analytics requirements

**📁 Complete diagrams and documentation available in `star_schema_diagrams/` folder**

**🚀 Generate Custom Diagrams:**
```bash
cd star_schema_diagrams/
python generate_star_schema.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Apache        │    │   Snowflake     │    │   dbt           │
│   (Simulated)   │───▶│   Airflow       │───▶│   Data          │───▶│   Transform     │
│                 │    │   Orchestration │    │   Warehouse     │    │   & Modeling   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │                       │
                                ▼                       ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                       │   Data Quality  │    │   Data          │    │   Business      │
                       │   Validation    │    │   Retention     │    │   Intelligence  │
                       │   (Great        │    │   Management    │    │   & Analytics   │
                       │    Expectations)│    │                 │    │                 │
                       └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 Current Data Volume

- **Total Records**: 84,000+ ad campaign records
- **Date Range**: Last 90 days (rolling retention)
- **Platforms**: Google, Facebook, LinkedIn, TikTok, Twitter
- **Geographies**: 14 major markets (US, CA, GB, DE, FR, AU, JP, IN, BR, MX, NL, IT, ES, SE)
- **Campaign Types**: 7 objectives (brand awareness, conversions, traffic, etc.)
- **Daily Volume**: 5,000 new records per day

## 🚀 **Project Status**

| Component | Status | Description |
|-----------|--------|-------------|
| **Data Generation** | ✅ **COMPLETE** | Realistic ad campaign data with business logic |
| **Airflow Orchestration** | ✅ **COMPLETE** | Daily pipeline with smart data management |
| **Snowflake Integration** | ✅ **COMPLETE** | Cloud data warehouse with optimized loading |
| **dbt Transformation** | ✅ **COMPLETE** | Kimball star schema with 4 marts |
| **Data Quality Testing** | ✅ **COMPLETE** | Great Expectations + PyTest suite |
| **Business Intelligence** | ✅ **COMPLETE** | Portfolio showcase queries & analytics |
| **Documentation** | ✅ **COMPLETE** | Auto-generated dbt docs & project docs |
| **Tableau Integration** | 🔄 **NEXT** | Visualization & dashboards |
| **Great Expectations** | 🔄 **NEXT** | Advanced data validation |
| **Unit Testing** | 🔄 **NEXT** | Automated test coverage |

## 🛠️ **Technology Stack**

### **Core Technologies**
- **Python 3.11+**: Data processing, API integration
- **Apache Airflow 3.0**: Workflow orchestration
- **Snowflake**: Cloud data warehouse
- **dbt**: Data transformation & modeling
- **Pandas**: Data manipulation & analysis

### **Data Quality & Testing**
- **Great Expectations**: Data validation & quality assurance
- **PyTest**: Unit testing & test automation
- **Coverage**: Code coverage reporting

### **Infrastructure**
- **Virtual Environment**: Dependency management
- **Environment Variables**: Secure credential management
- **Logging**: Comprehensive pipeline monitoring

## 📁 **Project Structure**

```
ad_campaign_spend_tracker/
├── 📊 dags/                          # Airflow DAGs
│   └── ad_data_generator_dag.py     # Main pipeline orchestration
├── 🔧 scripts/                       # Data processing scripts
│   ├── generate_fake_ads.py         # Daily data generation
│   ├── generate_backfill_ads.py     # Historical data generation
│   ├── load_backfill_to_snowflake.py # Initial data loading
│   ├── load_daily_snowflake.py      # Daily incremental loading
│   └── data_retention_manager.py    # Data lifecycle management
├── 🗄️ dbt/                          # Data transformation
│   ├── models/                      # dbt models
│   │   ├── staging/                # Data cleaning & validation
│   │   ├── dimensions/             # Dimension tables
│   │   └── marts/                  # Business intelligence marts
│   ├── dbt_project.yml             # dbt configuration
│   └── profiles.yml                # Snowflake connection
├── 🧪 tests/                        # Test suite
│   └── test_data_generation.py     # Data generation tests
├── 🔍 great_expectations/           # Data quality validation
├── 🌟 star_schema_diagrams/         # Star schema diagrams & documentation
│   ├── star_schema_simple.png       # Overview diagram
│   ├── star_schema_detailed.png     # Detailed field diagram
│   ├── star_schema_diagram.md       # Mermaid diagram for GitHub
│   ├── STAR_SCHEMA_GUIDE.md         # Complete usage guide
│   └── generate_star_schema.py      # Custom diagram generator
│   ├── great_expectations.yml      # GE configuration
│   ├── expectations/                # Data quality expectations
│   └── validate_ad_data.py         # Validation script
├── 📚 sql/                         # SQL scripts
│   └── create_raw_table.sql        # Snowflake table creation
├── 📖 docs/                        # Documentation
│   └── PORTFOLIO_SUMMARY.md        # Project overview
├── 🚀 run_portfolio_queries.py     # Analytics showcase
├── 🧪 run_tests.py                 # Test runner
├── 📋 requirements.txt              # Python dependencies
├── 📋 requirements-test.txt         # Testing dependencies
├── ⚙️ pytest.ini                   # PyTest configuration
├── 🔐 .env                         # Environment variables
└── 📖 README.md                    # This file
```

## 🚀 **Quick Start**

### **1. Environment Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd ad_campaign_spend_tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### **2. Snowflake Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Snowflake credentials
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PROGRAMMATIC_TOKEN=your_token
SNOWFLAKE_DATABASE=AD_CAMPAIGNS
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

### **3. Data Pipeline Execution**
```bash
# Generate and load initial data
python scripts/generate_backfill_ads.py
python scripts/load_backfill_to_snowflake.py

# Run daily pipeline
python scripts/generate_fake_ads.py
python scripts/load_daily_snowflake.py
```

### **4. Data Transformation**
```bash
# Navigate to dbt directory
cd dbt

# Install dbt dependencies
dbt deps

# Run transformations
dbt run

# Generate documentation
dbt docs generate
dbt docs serve
```

### **5. Run Analytics**
```bash
# Execute portfolio showcase queries
python run_portfolio_queries.py
```

## 🧪 **Testing & Quality Assurance**

### **PyTest Test Suite**
```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=scripts --cov=dbt --cov-report=html
```

### **Great Expectations Validation**
```bash
# Run data quality validation
python great_expectations/validate_ad_data.py
```

### **Test Coverage**
- **Data Generation**: 10 comprehensive tests
- **Business Logic**: Data quality rules validation
- **Data Types**: Schema validation
- **Value Ranges**: Business rule enforcement
- **Coverage Target**: 80%+ code coverage

## 📊 **Data Model**

### **Kimball Star Schema**
```
                    ┌─────────────────┐
                    │   Fact Tables   │
                    │                 │
                    │ • fact_ad_      │
                    │   performance   │
                    │ • mart_campaign_│
                    │   performance   │
                    │ • mart_platform_│
                    │   performance   │
                    │ • mart_daily_   │
                    │   performance   │
                    └─────────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Dimensions  │    │ Dimensions  │    │ Dimensions  │
│             │    │             │    │             │
│ • dim_      │    │ • dim_      │    │ • dim_      │
│   platforms │    │   geography │    │   dates     │
│ • dim_      │    │ • dim_      │    │ • dim_      │
│   campaigns │    │   devices   │    │   ad_formats│
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔍 **Data Quality & Validation**

### **Great Expectations Suite**
- **Schema Validation**: Column presence, data types
- **Business Rules**: CTR ≤ 100%, impressions ≥ clicks
- **Value Ranges**: Reasonable spend, impression limits
- **Data Integrity**: Unique constraints, referential integrity

### **Automated Testing**
- **Unit Tests**: Function behavior validation
- **Integration Tests**: End-to-end pipeline testing
- **Data Quality Tests**: Business rule enforcement
- **Performance Tests**: Pipeline efficiency validation

## 📈 **Business Intelligence**

### **Key Metrics**
- **CTR (Click-Through Rate)**: Click performance
- **CPC (Cost Per Click)**: Cost efficiency
- **CVR (Conversion Rate)**: Conversion performance
- **ROAS (Return on Ad Spend)**: ROI measurement
- **CPM (Cost Per Mille)**: Impression cost

### **Analytics Capabilities**
- **Platform Performance**: Cross-platform comparison
- **Geographic Analysis**: Market performance insights
- **Campaign Effectiveness**: Objective-based analysis
- **Time Series Analysis**: Trend identification
- **Device Performance**: Cross-device optimization

## 🚀 **Portfolio Value**

### **Technical Skills Demonstrated**
- **Data Engineering**: ETL/ELT pipeline development
- **Cloud Platforms**: Snowflake data warehouse
- **Orchestration**: Apache Airflow workflow management
- **Data Modeling**: Kimball star schema design
- **Testing**: Comprehensive test automation
- **Documentation**: Professional project documentation

### **Business Understanding**
- **Marketing Analytics**: Ad campaign performance metrics
- **Data Quality**: Production-ready validation
- **Performance Optimization**: Efficient data processing
- **Scalability**: Cloud-native architecture
- **Monitoring**: Pipeline health tracking

## 🔮 **Future Enhancements**

### **Phase 4: Advanced Analytics**
- [ ] **Tableau Integration**: Interactive dashboards
- [ ] **Machine Learning**: Predictive analytics
- [ ] **Real-time Processing**: Streaming data pipeline
- [ ] **Advanced Testing**: Performance benchmarking

### **Phase 5: Production Features**
- [ ] **CI/CD Pipeline**: Automated deployment
- [ ] **Monitoring**: Advanced alerting & metrics
- [ ] **Security**: Role-based access control
- [ ] **Compliance**: GDPR, CCPA compliance

## 📚 **Documentation Resources**

- **dbt Documentation**: `dbt docs serve` (http://localhost:8080)
- **Project Summary**: [PORTFOLIO_SUMMARY.md](docs/PORTFOLIO_SUMMARY.md)
- **Code Coverage**: `htmlcov/index.html`
- **Test Results**: `pytest` output with coverage

## 🤝 **Contributing**

This is a portfolio project demonstrating data engineering skills. For questions or feedback:

1. **Review the code**: All scripts are well-documented
2. **Run the tests**: Ensure quality with `python run_tests.py`
3. **Explore the data**: Use `run_portfolio_queries.py`
4. **Check documentation**: `dbt docs serve`

## 📄 **License**

This project is created for portfolio demonstration purposes. Feel free to use as a reference for your own projects.

---

**🎯 Ready to showcase your data engineering skills!** 

This project demonstrates **enterprise-level data pipeline development** with modern tools and best practices. Perfect for technical interviews and portfolio reviews.
