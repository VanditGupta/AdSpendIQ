# 📊 Qlik Sense App Template - Step-by-Step Guide

## 🎯 **App Structure**
```
Ad_Campaign_Analytics_Portfolio.qvf
├── Data Connections
│   ├── Snowflake Connection
│   └── Table Associations
├── Visualizations
│   ├── 01_KPI_Metrics
│   ├── 02_Platform_Performance
│   ├── 03_Geographic_Map
│   ├── 04_Time_Series_Trends
│   ├── 05_Campaign_Analysis
│   ├── 06_Device_Performance
│   ├── 07_ROI_Analysis
│   └── 08_Conversion_Funnel
└── Dashboards
    ├── Executive_Summary
    ├── Campaign_Performance
    ├── Geographic_Insights
    └── Device_Analysis
```

## 🔌 **Step 1: Data Connection Setup**

### 1.1 Connect to Snowflake
1. Open Qlik Sense Desktop or Enterprise
2. Create new app or open existing app
3. Click "Add data" → "Create new connection"
4. Select "Snowflake" connector
5. Enter connection details:
   ```
   Server: [your-snowflake-account].snowflakecomputing.com
   Warehouse: COMPUTE_WH
   Database: AD_CAMPAIGN_ANALYTICS
   Schema: ANALYTICS_MART
   Username: [your-username]
   Password: [your-password]
   ```

### 1.2 Select Tables
Connect to these tables:
- `FACT_CAMPAIGN_PERFORMANCE` (Main fact table)
- `DIM_CAMPAIGNS` (Campaign details)
- `DIM_PLATFORMS` (Platform information)
- `DIM_GEOGRAPHY` (Geographic data)
- `DIM_DEVICES` (Device information)
- `DIM_TIME` (Time dimensions)

### 1.3 Set Up Associations
```
FACT_CAMPAIGN_PERFORMANCE
├── CAMPAIGN_ID → DIM_CAMPAIGNS.CAMPAIGN_ID
├── PLATFORM_ID → DIM_PLATFORMS.PLATFORM_ID
├── GEO_ID → DIM_GEOGRAPHY.GEO_ID
├── DEVICE_ID → DIM_DEVICES.DEVICE_ID
└── DATE_ID → DIM_TIME.DATE_ID
```

## 📈 **Step 2: Create Visualizations**

### 2.1 KPI Metrics Visualization
**Purpose**: Display key performance indicators

**Fields to Add**:
- **Dimensions**: None
- **Measures**: Create calculated fields for KPIs

**Calculated Fields**:
```qlik
// Total Spend
Sum([Spend])

// Total Impressions
Sum([Impressions])

// Total Clicks
Sum([Clicks])

// Total Conversions
Sum([Conversions])

// Click-Through Rate
Sum([Clicks]) / Sum([Impressions])

// Cost Per Click
Sum([Spend]) / Sum([Clicks])

// Cost Per Conversion
Sum([Spend]) / Sum([Conversions])

// Conversion Rate
Sum([Conversions]) / Sum([Clicks])
```

**Visualization**: KPI objects with text display

### 2.2 Platform Performance Visualization
**Purpose**: Compare performance across platforms

**Fields to Add**:
- **Dimensions**: Platform Name
- **Measures**: Sum(Spend), Sum(Impressions), Sum(Clicks), Sum(Conversions)
- **Color**: Platform Name

**Calculated Fields**:
```qlik
// Platform CTR
Sum([Clicks]) / Sum([Impressions])

// Platform Conversion Rate
Sum([Conversions]) / Sum([Clicks])

// Platform ROAS
Sum([Conversions]) / Sum([Spend])
```

**Visualization**: Horizontal bar chart

### 2.3 Geographic Map Visualization
**Purpose**: Show geographic performance distribution

**Fields to Add**:
- **Dimensions**: Country Name
- **Measures**: Sum(Spend) or Sum(Conversions)
- **Color**: Sum(Conversions) or CTR

**Map Setup**:
1. Use built-in map visualization
2. Set geographic role for Country field
3. Configure color coding by performance

**Visualization**: Filled map

### 2.4 Time Series Trends Visualization
**Purpose**: Show performance over time

**Fields to Add**:
- **Dimensions**: Date (continuous)
- **Measures**: Sum(Spend), Sum(Impressions), Sum(Clicks), Sum(Conversions)
- **Color**: Platform Name (optional)

**Date Setup**:
1. Set date format appropriately
2. Use date hierarchy for different time views
3. Configure line chart with multiple measures

**Visualization**: Line chart

### 2.5 Campaign Analysis Visualization
**Purpose**: Detailed campaign performance comparison

**Fields to Add**:
- **Dimensions**: Campaign Name
- **Measures**: Sum(Spend), Sum(Impressions), Sum(Clicks), Sum(Conversions)
- **Color**: Campaign Type
- **Size**: Sum(Spend)

**Calculated Fields**:
```qlik
// Campaign ROI
(Sum([Conversions]) - Sum([Spend])) / Sum([Spend])

// Campaign Efficiency
Sum([Conversions]) / Sum([Spend])
```

**Visualization**: Scatter plot (Spend vs Conversions)

### 2.6 Device Performance Visualization
**Purpose**: Analyze performance by device type

**Fields to Add**:
- **Dimensions**: Device Type
- **Measures**: Sum(Spend), Sum(Impressions), Sum(Clicks), Sum(Conversions)
- **Color**: Device Type

**Calculated Fields**:
```qlik
// Device CTR
Sum([Clicks]) / Sum([Impressions])

// Device Conversion Rate
Sum([Conversions]) / Sum([Clicks])
```

**Visualization**: Bar chart

### 2.7 ROI Analysis Visualization
**Purpose**: Return on investment analysis

**Fields to Add**:
- **Dimensions**: Platform Name
- **Measures**: Sum(Spend), Sum(Conversions)
- **Color**: Platform Name
- **Size**: Campaign Type

**Calculated Fields**:
```qlik
// ROAS (Return on Ad Spend)
Sum([Conversions]) / Sum([Spend])

// Profit Margin
(Sum([Conversions]) - Sum([Spend])) / Sum([Spend])
```

**Visualization**: Scatter plot with trend line

### 2.8 Conversion Funnel Visualization
**Purpose**: Show conversion journey

**Fields to Add**:
- **Dimensions**: Stage (Impressions, Clicks, Conversions)
- **Measures**: Sum(Impressions), Sum(Clicks), Sum(Conversions)
- **Color**: Stage

**Funnel Setup**:
1. Create calculated field for Stage:
```qlik
If(Sum([Impressions]) > 0, 'Impressions',
 If(Sum([Clicks]) > 0, 'Clicks',
 If(Sum([Conversions]) > 0, 'Conversions', 'Unknown')))
```

**Visualization**: Funnel chart

## 🎨 **Step 3: Build Dashboards**

### 3.1 Executive Summary Dashboard
**Layout**: Single page with key metrics

**Components**:
1. **Header**: Title and date filter
2. **KPI Cards**: 4 main metrics (Spend, Impressions, Clicks, Conversions)
3. **Platform Chart**: Platform performance comparison
4. **Geographic Map**: World map with performance overlay
5. **Trend Chart**: Daily performance line chart

**Filters**:
- Date Range (Selection)
- Platform (Multiple Selection)
- Campaign Type (Multiple Selection)

### 3.2 Campaign Performance Dashboard
**Layout**: Multi-page with detailed analysis

**Page 1 - Overview**:
- KPI summary
- Platform performance
- Recent trends

**Page 2 - Campaign Analysis**:
- Campaign performance table
- ROI scatter plot
- Budget allocation

**Page 3 - A/B Testing**:
- Campaign comparison
- Statistical significance
- Performance metrics

**Page 4 - Budget Efficiency**:
- Spend vs performance
- Cost optimization
- ROI analysis

### 3.3 Geographic Insights Dashboard
**Layout**: Interactive map with supporting charts

**Components**:
1. **World Map**: Performance heatmap
2. **Country Table**: Top/bottom performers
3. **Regional Chart**: Performance by region
4. **Local Insights**: Market-specific analysis

**Interactivity**:
- Click on map to filter other views
- Country selection affects all charts
- Region comparison tools

### 3.4 Device Analysis Dashboard
**Layout**: Device-focused analysis

**Components**:
1. **Device Performance**: Bar chart comparison
2. **Format Effectiveness**: Ad format analysis
3. **Cross-Device Journey**: User behavior mapping
4. **Optimization Tips**: Performance recommendations

## 🔧 **Step 4: Add Interactivity**

### 4.1 Dashboard Actions
**Cross-Filtering**:
1. Select source visualization
2. Right-click → "Add to dashboard actions"
3. Choose target visualizations
4. Set action type (Filter, Highlight, Navigate)

**Example Actions**:
- Click platform → Filter all charts
- Select date range → Update all views
- Choose campaign → Highlight related data

### 4.2 Selection Controls
**Date Range Selection**:
1. Create date field with appropriate format
2. Add date picker or slider control
3. Configure selection behavior

**Platform Selection**:
1. Create platform list box
2. Configure multiple selection
3. Set default selections

### 4.3 Filters
**Global Filters**:
- Date Range
- Platform
- Campaign Type
- Geographic Region

**Local Filters**:
- Device Type
- Ad Format
- Campaign Status

## 🎯 **Step 5: Portfolio Enhancement**

### 5.1 Advanced Features
**Calculated Fields**:
```qlik
// Moving Average (7-day)
RangeSum(Sum([Conversions]), -6, 0) / 7

// Year-over-Year Growth
(Sum([Conversions]) - Above(Sum([Conversions]), 365)) / Above(Sum([Conversions]), 365)

// Performance Score
(Sum([Clicks]) / Sum([Impressions])) * (Sum([Conversions]) / Sum([Clicks])) * 1000
```

**Advanced Functions**:
- Aggr() for complex aggregations
- P() and E() for set analysis
- Above() and Below() for time comparisons

### 5.2 Performance Optimization
**Data Model Optimization**:
- Use synthetic keys for complex associations
- Optimize field names and data types
- Implement incremental refresh

**Visualization Performance**:
- Limit data points in charts
- Use appropriate chart types
- Implement lazy loading

## 📤 **Step 6: Export and Share**

### 6.1 Export Options
**Qlik Sense App (.qvf)**:
- Includes all data and connections
- Portable across Qlik Sense installations
- Best for sharing with stakeholders

**Qlik Sense Cloud**:
- Host on Qlik Sense Cloud
- Accessible to anyone with internet
- Good for portfolio showcase

### 6.2 Portfolio Integration
**Documentation**:
- Screenshots of key dashboards
- Description of technical implementation
- Business value demonstration

**Presentation**:
- Live dashboard walkthrough
- Key insights and findings
- Technical challenges and solutions

---

## 🚀 **Quick Start Checklist**

- [ ] Install Qlik Sense Desktop
- [ ] Set up Snowflake connection
- [ ] Create data model with associations
- [ ] Build KPI visualization
- [ ] Create platform performance chart
- [ ] Build geographic map
- [ ] Create time series trends
- [ ] Assemble executive summary dashboard
- [ ] Add interactivity and filters
- [ ] Test dashboard functionality
- [ ] Export as app file
- [ ] Create portfolio documentation

**This template will help you build a professional-grade Qlik Sense dashboard that showcases your data visualization skills!** 🎨✨
