-- ==============================================================================
-- SNOWFLAKE MEDALLION ARCHITECTURE: SILVER LAYER (CONFORMED & CLEANED)
-- Standardized Data Types, Validated Dates, Foreign Key Enforcements
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS VS_SUPPLY_CHAIN_DB.SILVER;

-- 1. Conformed Sourcing POs
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_PURCHASE_ORDERS AS
SELECT
    po_number,
    po_line_num,
    sku_id,
    vendor_code,
    factory_site_code,
    ordered_qty AS units_ordered,
    TRY_TO_DECIMAL(REPLACE(REPLACE(unit_price_raw, '$', ''), ',', ''), 10, 2) AS unit_fob_price_usd,
    TRY_TO_DATE(po_creation_timestamp) AS po_date,
    TRY_TO_DATE(vendor_ack_date) AS factory_ack_date,
    TRY_TO_DATE(target_ex_factory_date) AS target_ex_factory_date,
    UPPER(TRIM(raw_status)) AS po_status,
    CURRENT_TIMESTAMP() AS _processed_at
FROM VS_SUPPLY_CHAIN_DB.BRONZE.RAW_ERP_PURCHASE_ORDERS;

-- 2. Conformed Logistics Shipments
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_SHIPMENTS AS
SELECT
    shipment_raw_id AS shipment_id,
    container_num,
    bill_of_lading,
    po_number,
    carrier_scac AS carrier_code,
    origin_port,
    dest_port,
    dest_rdc_code,
    UPPER(TRIM(mode)) AS transport_mode,
    TRY_TO_DATE(etd_date) AS estimated_departure_date,
    TRY_TO_DATE(atd_date) AS actual_departure_date,
    TRY_TO_DATE(eta_date) AS estimated_arrival_date,
    TRY_TO_DATE(ata_date) AS actual_arrival_date,
    TRY_TO_DECIMAL(REPLACE(REPLACE(freight_charge_raw, '$', ''), ',', ''), 10, 2) AS freight_cost_usd,
    iot_temp_celsius,
    iot_shock_g_force,
    CASE 
        WHEN iot_temp_celsius > 35.0 OR iot_temp_celsius < 5.0 OR iot_shock_g_force > 3.0 THEN TRUE 
        ELSE FALSE 
    END AS is_iot_anomaly,
    CURRENT_TIMESTAMP() AS _processed_at
FROM VS_SUPPLY_CHAIN_DB.BRONZE.RAW_TMS_SHIPMENTS;

-- 3. Conformed QA & Material Compliance Lots
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_QA_INSPECTIONS AS
SELECT
    inspection_id,
    batch_lot_number,
    vendor_code,
    fabric_mill_code,
    sku_id,
    oeko_tex_cert_id,
    gots_cert_id,
    UPPER(TRIM(reach_chemical_test)) AS reach_status,
    colorfastness_score,
    dimensional_shrinkage_pct,
    tensile_strength_n,
    UPPER(TRIM(inspection_verdict)) AS inspection_result,
    (defect_critical_count + defect_major_count) AS total_defect_count,
    TRY_TO_DATE(inspection_timestamp) AS inspection_date,
    CURRENT_TIMESTAMP() AS _processed_at
FROM VS_SUPPLY_CHAIN_DB.BRONZE.RAW_QA_INSPECTIONS;

-- 4. Conformed Omnichannel Fulfillment
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_OMNICHANNEL_ORDERS AS
SELECT
    order_id,
    channel_code,
    customer_id,
    sku_id,
    units_ordered,
    units_fulfilled,
    TRY_TO_DATE(order_placed_ts) AS order_date,
    TRY_TO_DATE(promised_delivery_ts) AS promised_delivery_date,
    TRY_TO_DATE(actual_delivery_ts) AS actual_delivery_date,
    UPPER(TRIM(order_status)) AS order_status,
    CASE 
        WHEN TRY_TO_DATE(actual_delivery_ts) <= TRY_TO_DATE(promised_delivery_ts) THEN TRUE 
        ELSE FALSE 
    END AS is_delivered_on_time,
    CURRENT_TIMESTAMP() AS _processed_at
FROM VS_SUPPLY_CHAIN_DB.BRONZE.RAW_OMNICHANNEL_ORDERS;
