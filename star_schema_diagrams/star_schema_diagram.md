# 🌟 Ad Campaign Analytics Star Schema Diagram

## 📊 **Complete Data Model Visualization**

```mermaid
erDiagram
    %% Fact Table - Central Hub
    FACT_CAMPAIGN_PERFORMANCE {
        bigint campaign_performance_id PK
        bigint campaign_id FK
        bigint platform_id FK
        bigint geo_id FK
        bigint device_id FK
        bigint date_id FK
        bigint ad_format_id FK
        decimal spend
        bigint impressions
        bigint clicks
        bigint conversions
        decimal conversion_value
        timestamp created_at
        timestamp updated_at
    }

    %% Dimension Tables - Surrounding the Fact Table
    DIM_CAMPAIGNS {
        bigint campaign_id PK
        varchar campaign_name
        varchar campaign_type
        varchar campaign_status
        varchar campaign_objective
        date start_date
        date end_date
        decimal budget
        varchar target_audience
        varchar creative_theme
        timestamp created_at
        timestamp updated_at
    }

    DIM_PLATFORMS {
        bigint platform_id PK
        varchar platform_name
        varchar platform_type
        varchar platform_category
        varchar platform_version
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    DIM_GEOGRAPHY {
        bigint geo_id PK
        varchar country_name
        varchar country_code
        varchar region_name
        varchar city_name
        varchar timezone
        varchar currency
        decimal latitude
        decimal longitude
        varchar market_type
        timestamp created_at
        timestamp updated_at
    }

    DIM_DEVICES {
        bigint device_id PK
        varchar device_type
        varchar device_category
        varchar device_platform
        varchar device_brand
        varchar device_model
        varchar screen_resolution
        varchar browser_type
        varchar os_version
        timestamp created_at
        timestamp updated_at
    }

    DIM_TIME {
        bigint date_id PK
        date full_date
        int year
        int quarter
        int month
        int month_name
        int week_of_year
        int day_of_year
        int day_of_week
        varchar day_name
        boolean is_weekend
        boolean is_holiday
        varchar season
        timestamp created_at
        timestamp updated_at
    }

    DIM_AD_FORMATS {
        bigint ad_format_id PK
        varchar format_name
        varchar format_type
        varchar format_category
        varchar dimensions
        varchar aspect_ratio
        varchar file_size_limit
        boolean is_video
        boolean is_interactive
        timestamp created_at
        timestamp updated_at
    }

    %% Relationships - Star Schema Connections
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_CAMPAIGNS : "campaign_id"
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_PLATFORMS : "platform_id"
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_GEOGRAPHY : "geo_id"
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_DEVICES : "device_id"
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_TIME : "date_id"
    FACT_CAMPAIGN_PERFORMANCE ||--|| DIM_AD_FORMATS : "ad_format_id"
```

## 🔗 **Relationship Details**

### **Primary Keys (PK)**
- `campaign_performance_id` - Unique identifier for each performance record
- `campaign_id` - Campaign dimension identifier
- `platform_id` - Platform dimension identifier
- `geo_id` - Geography dimension identifier
- `device_id` - Device dimension identifier
- `date_id` - Time dimension identifier
- `ad_format_id` - Ad format dimension identifier

### **Foreign Keys (FK)**
- All dimension IDs in the fact table link to their respective dimension tables
- This creates the classic star schema pattern with the fact table at the center

### **Data Flow**
```
Raw Data → Staging → Dimensions → Fact Table → Analytics Mart
```

## 📈 **Star Schema Benefits**

### **1. Query Performance**
- **Fast Aggregations**: Pre-joined dimensions for quick calculations
- **Indexed Keys**: Optimized foreign key relationships
- **Denormalized Structure**: Reduces JOIN operations

### **2. Business Intelligence**
- **Intuitive Navigation**: Easy to understand business concepts
- **Flexible Analysis**: Multiple dimensional perspectives
- **Consistent Metrics**: Single source of truth for KPIs

### **3. Scalability**
- **Incremental Loading**: Add new data without full refresh
- **Partitioning**: Efficient data management by date
- **Compression**: Optimized storage for large datasets

## 🎯 **How to Generate This Diagram**

### **Method 1: Using dbt (Recommended)**

1. **Install dbt-docs**:
```bash
pip install dbt-docs
```

2. **Generate Documentation**:
```bash
cd dbt_project
dbt docs generate
dbt docs serve
```

3. **View in Browser**: Open `http://localhost:8080` to see your data model

### **Method 2: Using Mermaid Live Editor**

1. Go to [Mermaid Live Editor](https://mermaid.live/)
2. Copy the Mermaid code above
3. View the interactive diagram
4. Export as PNG, SVG, or PDF

### **Method 3: Using GitHub**

1. Create a `.md` file in your repository
2. Paste the Mermaid code
3. GitHub automatically renders the diagram
4. View in your repository

### **Method 4: Using Snowflake**

1. **Connect to Snowflake**:
```sql
-- View table relationships
SHOW TABLES IN ANALYTICS_MART;

-- View table structure
DESCRIBE TABLE FACT_CAMPAIGN_PERFORMANCE;
DESCRIBE TABLE DIM_CAMPAIGNS;
-- ... repeat for all tables
```

2. **Use Snowflake's Schema Browser**:
   - Navigate to your database
   - Use the visual schema browser
   - Export relationships

## 🔧 **Customizing the Diagram**

### **Add More Dimensions**
```mermaid
erDiagram
    %% Add new dimension
    DIM_CAMPAIGN_CATEGORIES {
        bigint category_id PK
        varchar category_name
        varchar category_description
        varchar parent_category
    }
    
    %% Add relationship
    DIM_CAMPAIGNS ||--|| DIM_CAMPAIGN_CATEGORIES : "category_id"
```

### **Add Bridge Tables**
```mermaid
erDiagram
    %% Bridge table for many-to-many relationships
    BRIDGE_CAMPAIGN_TARGETS {
        bigint campaign_id FK
        bigint target_audience_id FK
        varchar target_type
    }
```

## 📊 **Portfolio Integration**

### **Include in Your Portfolio**
1. **Technical Documentation**: Show data modeling skills
2. **Architecture Diagrams**: Demonstrate system design knowledge
3. **Business Understanding**: Show how data supports business needs
4. **Performance Optimization**: Highlight scalability considerations

### **Presentation Tips**
1. **Start with Business Context**: Why this schema design?
2. **Show Performance Benefits**: How it improves query speed
3. **Explain Design Decisions**: Why star vs. snowflake?
4. **Demonstrate Flexibility**: How easy to add new dimensions

---

## 🚀 **Next Steps**

1. **Generate the Diagram**: Use one of the methods above
2. **Customize**: Add your specific business requirements
3. **Document**: Explain design decisions and benefits
4. **Present**: Include in your portfolio showcase

**This star schema diagram will be a powerful addition to your portfolio, demonstrating advanced data modeling and architecture skills!** 🌟✨
