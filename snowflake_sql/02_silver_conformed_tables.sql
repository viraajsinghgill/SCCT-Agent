-- ==============================================================================
-- SNOWFLAKE MEDALLION ARCHITECTURE: SILVER LAYER (CONFORMED & DIMENSIONS)
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS VS_SUPPLY_CHAIN_DB.SILVER;

-- 1. Dimension Tables: Products
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.DIM_PRODUCTS (
    sku_id VARCHAR(50) PRIMARY KEY,
    sku_name VARCHAR(100),
    brand VARCHAR(50),
    category VARCHAR(50),
    subcategory VARCHAR(50),
    unit_standard_cost_usd DECIMAL(10,2),
    base_msrp_usd DECIMAL(10,2),
    primary_material VARCHAR(100)
);

INSERT INTO VS_SUPPLY_CHAIN_DB.SILVER.DIM_PRODUCTS VALUES
('VS-BRA-001', 'Dream Angels Wicked Unlined Bra', 'Victoria''s Secret', 'Bras', 'Unlined', 14.50, 49.50, 'Recycled Lace & Nylon'),
('VS-BRA-002', 'Body by Victoria Smooth Demi Bra', 'Victoria''s Secret', 'Bras', 'T-Shirt & Demi', 12.80, 44.50, 'Microfiber & Memory Foam'),
('VS-BRA-003', 'Very Sexy Push-Up Shine Strap Bra', 'Victoria''s Secret', 'Bras', 'Push-Up', 18.20, 69.50, 'Satin, Rhinestones & Underwire'),
('VS-PAN-101', 'Cotton Modal Seamless Hipster Panty', 'Victoria''s Secret', 'Panties', 'Hipster', 3.20, 14.50, 'Supima Cotton & Modal'),
('VS-PAN-102', 'Lace-Trim Cheeky Panty 5-Pack', 'Victoria''s Secret', 'Panties', 'Cheeky', 8.50, 35.00, 'Stretch Lace & Elastane'),
('PK-HOD-201', 'PINK Everyday Lounge Fleece Hoodie', 'PINK', 'Loungewear', 'Hoodies & Sweats', 16.00, 59.95, 'Organic Cotton Fleece'),
('PK-LEG-202', 'PINK High-Waist Pocket Workout Legging', 'PINK', 'Activewear', 'Leggings', 13.50, 49.95, 'Recycled Spandex & Polyester'),
('VB-FRG-301', 'Bombshell Eau de Parfum 100ml', 'VS Beauty', 'Fragrance', 'Fine Fragrance', 11.20, 79.95, 'Glass Flacon & Essential Oils'),
('VB-MST-302', 'Bare Vanilla Shimmer Fragrance Mist', 'VS Beauty', 'Beauty', 'Body Mist', 2.80, 19.95, 'PET Bottle & Vanilla Extract'),
('VS-SLP-401', 'Luxe Satin Button-Down Long Pajama Set', 'Victoria''s Secret', 'Sleepwear', 'Pajama Sets', 21.00, 89.50, '100% Glossy Mulberry Silk/Satin');

-- 2. Dimension Tables: Factories (Tier 1)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.DIM_FACTORIES (
    vendor_code VARCHAR(50) PRIMARY KEY,
    factory_name VARCHAR(100),
    country VARCHAR(50),
    region VARCHAR(50),
    lead_time_baseline_days INT,
    labor_audit_score INT,
    tariff_base_rate_pct DECIMAL(5,2),
    monthly_capacity_units INT
);

INSERT INTO VS_SUPPLY_CHAIN_DB.SILVER.DIM_FACTORIES VALUES
('VEN-MAS-01', 'MAS Holdings Active Fab', 'Sri Lanka', 'South Asia', 45, 96, 8.0, 500000),
('VEN-CRY-02', 'Crystal International Vietnam Ltd', 'Vietnam', 'Southeast Asia', 38, 92, 12.0, 750000),
('VEN-TEG-03', 'Tegra Global Nearshore Plant', 'Mexico', 'North America', 14, 89, 0.0, 300000),
('VEN-BDX-04', 'Brandix Apparel Eco-Campus', 'India', 'South Asia', 50, 94, 10.0, 400000),
('VEN-SRI-05', 'PT Sritex Intimates Indonesia', 'Indonesia', 'Southeast Asia', 42, 90, 11.5, 350000);

-- 3. Dimension Tables: Fabric Mills (Tier 2) & Raw Suppliers (Tier 3)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.DIM_FABRIC_MILLS (
    mill_code VARCHAR(50) PRIMARY KEY,
    mill_name VARCHAR(100),
    country VARCHAR(50),
    material_type VARCHAR(100),
    reach_compliant VARCHAR(10),
    oeko_tex_status VARCHAR(20)
);

INSERT INTO VS_SUPPLY_CHAIN_DB.SILVER.DIM_FABRIC_MILLS VALUES
('MIL-FOR-01', 'Formosa Taffeta Tech Mills', 'Taiwan', 'Recycled Polyamide & Microfiber', 'YES', 'CERTIFIED'),
('MIL-TOR-02', 'Toray Advanced Textile Mills', 'Japan', 'High-Elongation Spandex Mesh', 'YES', 'CERTIFIED'),
('MIL-OCN-03', 'Ocean Lanka Knitting Mills', 'Sri Lanka', 'Organic Cotton Single Jersey', 'YES', 'CERTIFIED'),
('MIL-PAC-04', 'Pacific Textiles Ltd', 'China', 'Jacquard Stretch Lace & Satin', 'YES', 'CERTIFIED');

CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.DIM_RAW_SUPPLIERS (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(100),
    country VARCHAR(50),
    raw_material VARCHAR(100),
    gots_certified VARCHAR(10)
);

INSERT INTO VS_SUPPLY_CHAIN_DB.SILVER.DIM_RAW_SUPPLIERS VALUES
('RAW-SUP-01', 'Supima Cotton Growers Guild', 'USA', 'Extra-Long Staple Supima Cotton', 'YES'),
('RAW-SUP-02', 'Asahi Kasei Fibers Corp', 'Japan', 'Roica Recycled Elastane', 'NO'),
('RAW-SUP-03', 'Lenzing AG Austria', 'Austria', 'TENCEL MicroModal Fibers', 'YES'),
('RAW-SUP-04', 'Huntsman Textile Chemicals', 'USA', 'AVITERA Eco-Dyes & Finishes', 'YES');

-- 4. Dimension Tables: Regional Distribution Centers (RDCs)
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.DIM_RDC (
    rdc_code VARCHAR(50) PRIMARY KEY,
    rdc_name VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(20),
    capacity_units INT,
    region VARCHAR(50)
);

INSERT INTO VS_SUPPLY_CHAIN_DB.SILVER.DIM_RDC VALUES
('RDC-COL-01', 'Columbus Central Omnichannel DC', 'Columbus', 'OH', 15000000, 'Midwest'),
('RDC-ONT-02', 'Inland Empire Gateway DC', 'Ontario', 'CA', 10000000, 'West Coast'),
('RDC-ATL-03', 'Southeast Regional Logistics Hub', 'Atlanta', 'GA', 8000000, 'Southeast'),
('RDC-TOR-04', 'Greater Toronto Distribution Center', 'Mississauga', 'ON', 5000000, 'Canada');

-- 5. Conformed Sourcing POs
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

-- 6. Conformed Logistics Shipments
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

-- 7. Conformed QA & Material Compliance Lots
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_QA_INSPECTIONS AS
SELECT
    inspection_id,
    batch_lot_number,
    vendor_code,
    fabric_mill_code,
    sku_id,
    po_number,
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

-- 8. Conformed Omnichannel Fulfillment
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_OMNICHANNEL_ORDERS AS
SELECT
    order_id,
    po_number,
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

-- 9. Conformed Inventory Ledger
CREATE OR REPLACE TABLE VS_SUPPLY_CHAIN_DB.SILVER.CNF_INVENTORY_LEDGER (
    inventory_id VARCHAR(50) PRIMARY KEY,
    rdc_name VARCHAR(100),
    sku_id VARCHAR(50),
    units_on_hand INT,
    units_in_transit INT,
    units_allocated INT,
    safety_stock_threshold INT,
    daily_sales_velocity INT,
    carrying_cost_per_unit DECIMAL(10,4)
);
