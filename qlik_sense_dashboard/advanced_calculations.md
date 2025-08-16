# 🧮 Advanced Qlik Sense Expressions for Portfolio Dashboard

## 🎯 **Advanced Calculated Fields**

### 1. **Performance Scoring & Ranking**

#### **Campaign Performance Score**
```qlik
// Composite performance score (0-100)
(
  (Sum([Clicks]) / Sum([Impressions])) * 50 +  // CTR Component
  (Sum([Conversions]) / Sum([Clicks])) * 30 +   // Conversion Rate Component
  (1 / (Sum([Spend]) / Sum([Conversions]))) * 20  // Cost Efficiency Component
)
```

#### **Platform Ranking**
```qlik
// Rank platforms by performance
Rank(Sum([Conversions]) / Sum([Spend]))
```

#### **Geographic Performance Index**
```qlik
// Normalized performance by region
(Sum([Conversions]) / Sum([Spend])) / 
Avg(TOTAL Sum([Conversions]) / Sum([Spend]))
```

### 2. **Time-Based Analysis**

#### **Moving Averages**
```qlik
// 7-day moving average for conversions
RangeSum(Sum([Conversions]), -6, 0) / 7

// 30-day moving average for spend
RangeSum(Sum([Spend]), -29, 0) / 30

// 90-day moving average for CTR
RangeSum(Sum([Clicks]) / Sum([Impressions]), -89, 0) / 90
```

#### **Period-over-Period Growth**
```qlik
// Week-over-week growth
(Sum([Conversions]) - Above(Sum([Conversions]), 7)) / 
Above(Sum([Conversions]), 7)

// Month-over-month growth
(Sum([Conversions]) - Above(Sum([Conversions]), 30)) / 
Above(Sum([Conversions]), 30)

// Year-over-year growth
(Sum([Conversions]) - Above(Sum([Conversions]), 365)) / 
Above(Sum([Conversions]), 365)
```

#### **Seasonal Analysis**
```qlik
// Day of week performance
WeekDay([Date])

// Month performance
Month([Date])

// Quarter performance
Quarter([Date])
```

### 3. **Statistical Analysis**

#### **Z-Score for Outliers**
```qlik
// Z-score for conversion rate
(Sum([Conversions]) / Sum([Clicks]) - 
Avg(TOTAL Sum([Conversions]) / Sum([Clicks]))) / 
StDev(TOTAL Sum([Conversions]) / Sum([Clicks]))
```

#### **Percentile Rankings**
```qlik
// Campaign performance percentile
Fractile(Sum([Conversions]) / Sum([Spend]), 0.5)

// Platform efficiency percentile
Fractile(Sum([Clicks]) / Sum([Impressions]), 0.75)
```

#### **Correlation Analysis**
```qlik
// Spend vs Performance correlation
Correl(Sum([Spend]), Sum([Conversions]))

// Impressions vs Clicks correlation
Correl(Sum([Impressions]), Sum([Clicks]))
```

### 4. **Business Intelligence Metrics**

#### **Customer Lifetime Value (CLV)**
```qlik
// Estimated CLV based on conversion value
Sum([Conversions]) * Avg([Conversion_Value]) * 
(1 / (1 - Avg([Retention_Rate])))
```

#### **Return on Ad Spend (ROAS)**
```qlik
// Basic ROAS
Sum([Conversion_Value]) / Sum([Spend])

// Adjusted ROAS (considering costs)
(Sum([Conversion_Value]) - Sum([Spend]) - Sum([Other_Costs])) / Sum([Spend])
```

#### **Customer Acquisition Cost (CAC)**
```qlik
// CAC by platform
Sum([Spend]) / Sum([Conversions])

// CAC by campaign type
Sum([Spend]) / Sum([Conversions])
```

### 5. **Predictive Analytics**

#### **Trend Projection**
```qlik
// Linear trend for next 7 days
LinEst_M(Sum([Conversions]), Date([Date])) * 7 + 
LinEst_B(Sum([Conversions]), Date([Date]))
```

#### **Forecasting Confidence**
```qlik
// Confidence interval for predictions
StDev(TOTAL Sum([Conversions])) * 1.96
```

### 6. **Advanced Filtering**

#### **Dynamic Date Ranges**
```qlik
// Last N days parameter
[Date] >= Today() - [Days_Parameter]

// Rolling 30-day window
[Date] >= Max([Date]) - 30
```

#### **Conditional Aggregation**
```qlik
// High-performing campaigns only
If(Sum([Conversions]) / Sum([Spend]) > 
Avg(TOTAL Sum([Conversions]) / Sum([Spend])) * 1.5,
Sum([Conversions]), 0)
```

### 7. **Data Quality & Validation**

#### **Data Completeness Check**
```qlik
// Percentage of complete records
Count(If([Spend] > 0 AND [Impressions] > 0, [Campaign_ID])) / 
Count([Campaign_ID])
```

#### **Anomaly Detection**
```qlik
// Flag unusual performance
If(Abs(Sum([Clicks]) / Sum([Impressions]) - 
Avg(TOTAL Sum([Clicks]) / Sum([Impressions]))) > 
StDev(TOTAL Sum([Clicks]) / Sum([Impressions])) * 2,
'Anomaly', 'Normal')
```

## 🔧 **Advanced Functions**

### 1. **Set Analysis**
```qlik
// Current selection vs total
Sum({1} [Conversions]) / Sum({$} [Conversions])

// Exclude current selection
Sum({1-$} [Conversions])

// Include specific values
Sum({<Platform={'Facebook','Google'}>} [Spend])
```

### 2. **Aggregation Functions**
```qlik
// Complex aggregations
Aggr(Sum([Conversions]), [Platform], [Campaign_Type])

// Nested aggregations
Sum(Aggr(Sum([Conversions]), [Platform]))

// Conditional aggregations
Sum(If([ROI] > 2, [Spend], 0))
```

### 3. **Time Functions**
```qlik
// Previous period
Above(Sum([Conversions]), 1)

// Next period
Below(Sum([Conversions]), 1)

// First value in dimension
FirstValue(Sum([Conversions]))

// Last value in dimension
LastValue(Sum([Conversions]))
```

## 📊 **Advanced Chart Types**

### 1. **Bullet Charts**
```qlik
// Performance vs Target
// Target: Sum([Target_Conversions])
// Actual: Sum([Conversions])
// Range: Avg(TOTAL Sum([Conversions]))
```

### 2. **Box Plots**
```qlik
// Distribution of CTR by platform
// Use built-in box plot with:
// Dimensions: Platform Name
// Measures: CTR (calculated field)
```

### 3. **Waterfall Charts**
```qlik
// Budget allocation breakdown
// Use running total for cumulative effect
```

### 4. **Gantt Charts**
```qlik
// Campaign timeline
// Start Date: Campaign Start Date
// Duration: Campaign Duration
// Color: Campaign Type
```

## 🎨 **Conditional Formatting**

### 1. **Performance-Based Colors**
```qlik
// Green for above average, red for below
If(Sum([Conversions]) / Sum([Spend]) > 
Avg(TOTAL Sum([Conversions]) / Sum([Spend])),
'Good', 'Needs Attention')
```

### 2. **Dynamic Sizing**
```qlik
// Size by performance relative to average
Sum([Conversions]) / Avg(TOTAL Sum([Conversions]))
```

### 3. **Alert Indicators**
```qlik
// Warning for low performance
If(Sum([Clicks]) / Sum([Impressions]) < 0.01,
'⚠️ Low CTR', '✅ Good CTR')
```

## 🚀 **Performance Optimization**

### 1. **Efficient Expressions**
```qlik
// Use RangeSum instead of Above for large datasets
// Pre-calculate complex metrics in data model
// Use set analysis for better performance
```

### 2. **Data Model Optimization**
```qlik
// Limit data with filters before calculations
// Use appropriate data types
// Implement incremental refresh
```

### 3. **Visualization Performance**
```qlik
// Limit chart data points
// Use appropriate chart types
// Implement lazy loading for large datasets
```

## 📈 **Portfolio Showcase Examples**

### 1. **Executive Dashboard**
```qlik
// KPI with trend indicators
If(Sum([Conversions]) > Above(Sum([Conversions]), 7),
'↗️ Trending Up', '↘️ Trending Down')
```

### 2. **Campaign Analysis**
```qlik
// Performance categories
Pick(Match(Sum([Conversions]) / Sum([Spend]),
  If(Sum([Conversions]) / Sum([Spend]) > 2, 1,
   If(Sum([Conversions]) / Sum([Spend]) > 1, 2,
    If(Sum([Conversions]) / Sum([Spend]) > 0.5, 3, 4))),
  'High Performer', 'Good Performer', 'Average Performer', 'Needs Optimization')
```

### 3. **Geographic Insights**
```qlik
// Market maturity indicator
If(Sum([Conversions]) / Sum([Spend]) > 
Avg(TOTAL Sum([Conversions]) / Sum([Spend])),
'Mature Market', 'Emerging Market')
```

---

## 🎯 **Implementation Tips**

1. **Start Simple**: Begin with basic expressions and add complexity
2. **Test Thoroughly**: Verify all expressions with sample data
3. **Document Everything**: Keep track of expression logic
4. **Performance Monitor**: Watch for slow expressions
5. **User Experience**: Ensure expressions add value, not confusion

**These advanced expressions will make your dashboard stand out and demonstrate sophisticated Qlik Sense skills!** 🚀✨
