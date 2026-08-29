-- ==============================================================================
-- SNOWFLAKE DYNAMIC TABLES & NEAR REAL-TIME STREAMS / TASKS
-- Continuous Lag-Free Incremental Transformation for SCCT Agent
-- ==============================================================================

USE DATABASE VS_SUPPLY_CHAIN_DB;

-- 1. Dynamic Table for Real-Time Supply Chain Executive KPI Aggregation
CREATE OR REPLACE DYNAMIC TABLE VS_SUPPLY_CHAIN_DB.GOLD.DT_EXECUTIVE_KPI_SUMMARY
    TARGET_LAG = '5 MINUTES'
    WAREHOUSE = COMPUTE_WH
AS
SELECT
    sourcing_country,
    brand,
    category,
    COUNT(DISTINCT po_number) AS active_pos,
    SUM(units_ordered) AS total_units_ordered,
    SUM(units_fulfilled) AS total_units_fulfilled,
    ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS otd_pct,
    ROUND(SUM(units_fulfilled) * 100.0 / NULLIF(SUM(units_ordered), 0), 2) AS fill_rate_pct,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_landed_cost_usd,
    ROUND(SUM(customs_duty_usd), 2) AS total_tariffs_paid_usd,
    SUM(CASE WHEN is_iot_anomaly = TRUE THEN 1 ELSE 0 END) AS iot_alert_count
FROM VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS
GROUP BY sourcing_country, brand, category;

-- 2. Stream on Ingestion Tables for Anomaly Detection
CREATE OR REPLACE STREAM VS_SUPPLY_CHAIN_DB.BRONZE.STREAM_RAW_TMS_SHIPMENTS 
ON TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_TMS_SHIPMENTS;

-- 3. Automated Serverless Task for IoT Shock/Temp Disruption Alerting
CREATE OR REPLACE TASK VS_SUPPLY_CHAIN_DB.GOLD.TASK_DETECT_IOT_DISRUPTIONS
    WAREHOUSE = COMPUTE_WH
    SCHEDULE = 'USING CRON */5 * * * * UTC'
WHEN
    SYSTEM('VS_SUPPLY_CHAIN_DB.BRONZE.STREAM_RAW_TMS_SHIPMENTS')
AS
INSERT INTO VS_SUPPLY_CHAIN_DB.GOLD.SCCT_INCIDENT_ALERTS (
    incident_type,
    po_number,
    details,
    severity,
    created_at
)
SELECT 
    'IOT_TEMPERATURE_EXCURSION',
    po_number,
    CONCAT('Container temperature anomaly recorded: ', iot_temp_celsius, 'C on carrier ', carrier_scac),
    'HIGH',
    CURRENT_TIMESTAMP()
FROM VS_SUPPLY_CHAIN_DB.BRONZE.STREAM_RAW_TMS_SHIPMENTS
WHERE iot_temp_celsius > 35.0 OR iot_temp_celsius < 5.0;
