# 🎨 **Apache Superset Dashboard for AdSpendIQ**

This folder contains the Apache Superset dashboard setup and configuration for the AdSpendIQ ad campaign analytics project.

## 📊 **Overview**

Apache Superset is a modern, enterprise-ready business intelligence web application that provides:
- **Interactive Dashboards**: Rich, customizable visualizations
- **SQL Editor**: Powerful query interface for data exploration
- **Chart Library**: 50+ chart types for comprehensive analytics
- **Security**: Role-based access control and authentication
- **Scalability**: Handles large datasets efficiently

## 🚀 **Quick Start**

### **1. Install Apache Superset**
```bash
# Using pip
pip install apache-superset

# Using Docker (recommended)
docker run -d -p 8080:8088 --name superset apache/superset
```

### **2. Initialize Superset**
```bash
# Set environment variables
export FLASK_APP=superset

# Create admin user
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@adspendiq.com \
    --password admin

# Initialize database
superset db upgrade

# Load example data (optional)
superset load_examples

# Create default roles and permissions
superset init
```

### **3. Start Superset**
```bash
# Development server
superset run -p 8088 --with-threads --reload --host=0.0.0.0

# Production server
gunicorn \
    -w 10 \
    -k gevent \
    --timeout 120 \
    -b 0.0.0.0:8088 \
    --limit-request-line 0 \
    --limit-request-field_size 0 \
    "superset.app:create_app()"
```

## 🔗 **Database Connections**

### **Snowflake Connection**
```sql
-- Connection String
snowflake://username:password@account/database/schema?warehouse=warehouse_name

-- Parameters
Host: your_account.snowflakecomputing.com
Port: 443
Database: AD_CAMPAIGNS
Schema: RAW
Warehouse: COMPUTE_WH
```

### **Connection Settings**
- **Engine**: `snowflake-sqlalchemy`
- **Extra**: 
```json
{
    "account": "your_account",
    "warehouse": "COMPUTE_WH",
    "role": "ACCOUNTADMIN"
}
```

## 📈 **Dashboard Components**

### **1. Campaign Performance Dashboard**
- **Campaign Overview**: Total spend, impressions, clicks, conversions
- **Performance Metrics**: CTR, CPC, CVR, ROAS trends
- **Budget Analysis**: Spend by campaign type and budget tier
- **Geographic Performance**: Performance by country and region

### **2. Platform Analytics Dashboard**
- **Platform Comparison**: Performance across Google, Facebook, LinkedIn, TikTok, Twitter
- **Ad Format Analysis**: Video vs. static ad performance
- **Device Performance**: Mobile vs. desktop conversion rates
- **Time Series Analysis**: Daily/weekly performance trends

### **3. Business Intelligence Dashboard**
- **ROI Analysis**: Return on ad spend by campaign and platform
- **Audience Insights**: Geographic and demographic performance
- **Campaign Effectiveness**: Objective-based performance analysis
- **Predictive Metrics**: Trend forecasting and seasonality

## 🎨 **Chart Types & Visualizations**

### **Key Performance Indicators**
- **Big Number Charts**: Total spend, impressions, conversions
- **Gauge Charts**: CTR, CVR, ROAS targets
- **Progress Bars**: Budget utilization and campaign progress

### **Trend Analysis**
- **Line Charts**: Time series performance trends
- **Area Charts**: Cumulative performance metrics
- **Bar Charts**: Comparative performance analysis

### **Geographic Visualization**
- **World Map**: Global performance heatmap
- **Country Charts**: Regional performance comparison
- **Heat Maps**: Geographic performance density

### **Campaign Analysis**
- **Pivot Tables**: Multi-dimensional data analysis
- **Treemaps**: Hierarchical campaign structure
- **Scatter Plots**: Correlation between metrics

## 🔧 **Advanced Features**

### **SQL Lab**
```sql
-- Campaign Performance Query
SELECT 
    c.campaign_type,
    c.budget_tier,
    COUNT(DISTINCT f.campaign_id) as campaign_count,
    SUM(f.impressions) as total_impressions,
    SUM(f.clicks) as total_clicks,
    SUM(f.spend_usd) as total_spend,
    SUM(f.conversions) as total_conversions,
    AVG(f.ctr) as avg_ctr,
    AVG(f.cpc) as avg_cpc,
    AVG(f.roas) as avg_roas
FROM fact_ad_performance f
JOIN dim_campaigns c ON f.campaign_id = c.campaign_id
GROUP BY c.campaign_type, c.budget_tier
ORDER BY total_spend DESC;
```

### **Custom Metrics**
```python
# Custom Python functions for advanced calculations
def calculate_effectiveness_score(ctr, cpc, cvr, roas):
    """Calculate campaign effectiveness score (0-100)"""
    score = (ctr * 25) + \
            (max(0, 25 - (cpc - 2.00) * 5)) + \
            (cvr * 200) + \
            (min(25, roas * 1250))
    return min(100, max(0, score))

# Usage in Superset
effectiveness_score = calculate_effectiveness_score(ctr, cpc, cvr, roas)
```

### **Dashboard Filters**
- **Date Range**: Rolling 30/60/90 day views
- **Campaign Type**: Brand awareness, conversions, traffic
- **Platform**: Google, Facebook, LinkedIn, TikTok, Twitter
- **Geography**: Country and region selection
- **Device**: Mobile, desktop, tablet

## 📱 **Responsive Design**

### **Mobile Optimization**
- **Touch-friendly**: Optimized for mobile devices
- **Responsive Layout**: Adapts to different screen sizes
- **Mobile Navigation**: Simplified navigation for small screens

### **Desktop Experience**
- **Full Dashboard**: Complete visualization suite
- **Advanced Controls**: Detailed filtering and customization
- **Export Options**: PDF, PNG, CSV export capabilities

## 🔐 **Security & Access Control**

### **User Management**
- **Admin Users**: Full system access and configuration
- **Analyst Users**: Dashboard creation and data access
- **Viewer Users**: Read-only dashboard access

### **Data Access Control**
- **Row-level Security**: User-specific data filtering
- **Column-level Security**: Sensitive data protection
- **Database-level Security**: Connection and query restrictions

## 🚀 **Deployment Options**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
superset run -p 8088 --reload
```

### **Docker Deployment**
```bash
# Pull latest image
docker pull apache/superset

# Run with custom configuration
docker run -d \
    -p 8080:8088 \
    -e SUPERSET_SECRET_KEY='your-secret-key' \
    -e SUPERSET_DB_URI='your-database-uri' \
    --name superset \
    apache/superset
```

### **Production Deployment**
```bash
# Using Docker Compose
docker-compose up -d

# Using Kubernetes
kubectl apply -f k8s/
```

## 📊 **Sample Dashboards**

### **Dashboard 1: Executive Overview**
- **KPIs**: Total spend, impressions, conversions
- **Trends**: Monthly performance comparison
- **Platform Mix**: Spend distribution by platform
- **Geographic Performance**: Top performing markets

### **Dashboard 2: Campaign Manager**
- **Campaign Details**: Individual campaign performance
- **Budget Tracking**: Spend vs. budget analysis
- **Performance Metrics**: CTR, CPC, CVR by campaign
- **Optimization Insights**: Recommendations for improvement

### **Dashboard 3: Data Analyst**
- **Deep Dive Analysis**: Detailed performance metrics
- **Correlation Analysis**: Metric relationships
- **Anomaly Detection**: Performance outliers
- **Forecasting**: Trend predictions and seasonality

## 🔗 **Integration with AdSpendIQ**

### **Data Pipeline Integration**
- **Real-time Updates**: Connect to live data pipeline
- **Scheduled Refresh**: Automated dashboard updates
- **Data Quality**: Integration with Great Expectations
- **Alerting**: Performance threshold notifications

### **Technology Stack Integration**
- **Airflow**: Automated data pipeline orchestration
- **Snowflake**: Cloud data warehouse
- **dbt**: Data transformation and modeling
- **Great Expectations**: Data quality validation

## 📚 **Resources & Documentation**

### **Official Documentation**
- [Apache Superset Docs](https://superset.apache.org/docs/intro)
- [Installation Guide](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose)
- [User Guide](https://superset.apache.org/docs/using-superset/exploring-data)

### **Community Resources**
- [GitHub Repository](https://github.com/apache/superset)
- [Community Forum](https://github.com/apache/superset/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apache-superset)

### **Tutorials & Examples**
- [Getting Started](https://superset.apache.org/docs/using-superset/exploring-data)
- [Chart Types](https://superset.apache.org/docs/using-superset/exploring-data/visualization-types)
- [Dashboard Creation](https://superset.apache.org/docs/using-superset/dashboards)

---

## 🎯 **Next Steps**

1. **Set up Superset** using the installation guide above
2. **Connect to Snowflake** using your AdSpendIQ database
3. **Create sample charts** for key metrics
4. **Build dashboards** for different user roles
5. **Integrate with pipeline** for automated updates

**Perfect for showcasing advanced BI and visualization skills in your data engineering portfolio!** 🚀
