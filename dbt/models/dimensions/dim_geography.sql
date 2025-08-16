{{ config(materialized='table') }}

WITH geo_data AS (
    SELECT DISTINCT
        geo as country_code,
        geo as geo_id  -- Using country code as ID for simplicity
    FROM {{ ref('stg_ad_data') }}
    WHERE geo IS NOT NULL
),

enriched AS (
    SELECT 
        geo_id,
        country_code,
        
        -- Country names
        CASE country_code
            WHEN 'US' THEN 'United States'
            WHEN 'CA' THEN 'Canada'
            WHEN 'GB' THEN 'United Kingdom'
            WHEN 'DE' THEN 'Germany'
            WHEN 'FR' THEN 'France'
            WHEN 'AU' THEN 'Australia'
            WHEN 'JP' THEN 'Japan'
            WHEN 'IN' THEN 'India'
            WHEN 'BR' THEN 'Brazil'
            WHEN 'MX' THEN 'Mexico'
            WHEN 'NL' THEN 'Netherlands'
            WHEN 'IT' THEN 'Italy'
            WHEN 'ES' THEN 'Spain'
            WHEN 'SE' THEN 'Sweden'
            ELSE country_code
        END as country_name,
        
        -- Continent
        CASE 
            WHEN country_code IN ('US', 'CA', 'MX') THEN 'North America'
            WHEN country_code IN ('BR') THEN 'South America'
            WHEN country_code IN ('GB', 'DE', 'FR', 'NL', 'IT', 'ES', 'SE') THEN 'Europe'
            WHEN country_code IN ('AU', 'JP') THEN 'Asia-Pacific'
            WHEN country_code IN ('IN') THEN 'Asia'
            ELSE 'Other'
        END as continent,
        
        -- Market type
        CASE 
            WHEN country_code IN ('US', 'CA', 'GB', 'DE', 'FR', 'AU', 'JP') THEN 'Developed'
            WHEN country_code IN ('IN', 'BR', 'MX') THEN 'Emerging'
            ELSE 'Developing'
        END as market_type,
        
        -- Regional grouping
        CASE 
            WHEN country_code IN ('US', 'CA') THEN 'North America'
            WHEN country_code IN ('GB', 'DE', 'FR', 'NL', 'IT', 'ES', 'SE') THEN 'Western Europe'
            WHEN country_code IN ('AU', 'JP') THEN 'Asia-Pacific'
            WHEN country_code IN ('IN', 'BR', 'MX') THEN 'Emerging Markets'
            ELSE 'Other Regions'
        END as region,
        
        -- Currency (for spend analysis)
        CASE 
            WHEN country_code IN ('US', 'CA') THEN 'USD'
            WHEN country_code IN ('GB') THEN 'GBP'
            WHEN country_code IN ('DE', 'FR', 'NL', 'IT', 'ES', 'SE') THEN 'EUR'
            WHEN country_code IN ('AU') THEN 'AUD'
            WHEN country_code IN ('JP') THEN 'JPY'
            WHEN country_code IN ('IN') THEN 'INR'
            WHEN country_code IN ('BR') THEN 'BRL'
            WHEN country_code IN ('MX') THEN 'MXN'
            ELSE 'USD'
        END as currency,
        
        -- Metadata
        CURRENT_TIMESTAMP as _loaded_at,
        'dimension' as _model_type
        
    FROM geo_data
)

SELECT * FROM enriched
ORDER BY continent, market_type, country_name
