-- ==============================================================================
-- SNOWFLAKE MEDALLION ARCHITECTURE: BRONZE LAYER (RAW INGESTION)
-- Victoria's Secret & Co. Global Supply Chain Control Tower
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS VS_SUPPLY_CHAIN_DB;
CREATE SCHEMA IF NOT EXISTS VS_SUPPLY_CHAIN_DB.BRONZE;

-- 1. Raw ERP Purchase Orders (SAP S/4HANA Extract)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_ERP_PURCHASE_ORDERS (
    po_raw_id VARCHAR(50),
    po_number VARCHAR(50),
    po_line_num INT,
    sku_id VARCHAR(50),
    vendor_code VARCHAR(50),
    factory_site_code VARCHAR(50),
    ordered_qty INT,
    unit_price_raw VARCHAR(30),
    currency VARCHAR(10),
    po_creation_timestamp VARCHAR(50),
    vendor_ack_date VARCHAR(50),
    target_ex_factory_date VARCHAR(50),
    raw_status VARCHAR(30),
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Raw WMS & TMS Logistics Shipments (Manhattan / Blue Yonder Extract)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_TMS_SHIPMENTS (
    shipment_raw_id VARCHAR(50),
    container_num VARCHAR(50),
    bill_of_lading VARCHAR(50),
    po_number VARCHAR(50),
    carrier_scac VARCHAR(20),
    origin_port VARCHAR(50),
    dest_port VARCHAR(50),
    dest_rdc_code VARCHAR(50),
    mode VARCHAR(20),
    etd_date VARCHAR(50),
    atd_date VARCHAR(50),
    eta_date VARCHAR(50),
    ata_date VARCHAR(50),
    freight_charge_raw VARCHAR(30),
    iot_temp_celsius FLOAT,
    iot_shock_g_force FLOAT,
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 3. Raw Quality & Laboratory Audit Inspection Records (Intertek / SGS / In-House QA)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_QA_INSPECTIONS (
    inspection_id VARCHAR(50),
    batch_lot_number VARCHAR(50),
    vendor_code VARCHAR(50),
    fabric_mill_code VARCHAR(50),
    sku_id VARCHAR(50),
    oeko_tex_cert_id VARCHAR(50),
    gots_cert_id VARCHAR(50),
    reach_chemical_test VARCHAR(20),
    colorfastness_score FLOAT,
    dimensional_shrinkage_pct FLOAT,
    tensile_strength_n FLOAT,
    inspection_verdict VARCHAR(30),
    defect_critical_count INT,
    defect_major_count INT,
    inspection_timestamp VARCHAR(50),
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 4. Raw Omnichannel Point of Sale & Store/E-Com Orders
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_OMNICHANNEL_ORDERS (
    order_id VARCHAR(50),
    channel_code VARCHAR(50),
    customer_id VARCHAR(50),
    sku_id VARCHAR(50),
    units_ordered INT,
    units_fulfilled INT,
    order_placed_ts VARCHAR(50),
    promised_delivery_ts VARCHAR(50),
    actual_delivery_ts VARCHAR(50),
    order_status VARCHAR(30),
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- 5. Raw Reverse Logistics & Customer Returns
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.BRONZE.RAW_CUSTOMER_RETURNS (
    return_id VARCHAR(50),
    order_id VARCHAR(50),
    sku_id VARCHAR(50),
    return_request_ts VARCHAR(50),
    return_reason_raw VARCHAR(100),
    hygiene_inspection_grade VARCHAR(20),
    disposition_code VARCHAR(30),
    refund_amount_usd FLOAT,
    _ingested_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
