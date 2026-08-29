-- ==============================================================================
-- SNOWFLAKE MEDALLION ARCHITECTURE: GOLD LAYER (GOVERNED SEMANTIC VIEWS)
-- Unified Supply Chain Control Tower Views with Canonical Metrics Embedded
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS VS_SUPPLY_CHAIN_DB.GOLD;

-- 1. Master Governed Control Tower Performance View
CREATE OR REPLACE VIEW VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS AS
SELECT
    po.po_number,
    po.sku_id,
    p.sku_name,
    p.brand,
    p.category,
    p.subcategory,
    f.factory_name,
    f.country AS sourcing_country,
    f.region AS sourcing_region,
    s.carrier_code AS carrier_name,
    s.transport_mode,
    s.origin_port,
    s.dest_port,
    s.dest_rdc_code AS rdc_name,
    o.channel_code AS destination_channel,
    po.po_date AS order_date,
    o.promised_delivery_date,
    o.actual_delivery_date,
    po.units_ordered,
    o.units_fulfilled,
    COALESCE(qa.total_defect_count, 0) AS defect_count,
    s.is_iot_anomaly,
    po.unit_fob_price_usd,
    (s.freight_cost_usd / NULLIF(po.units_ordered, 0)) AS allocated_freight_usd,
    (po.unit_fob_price_usd * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) AS customs_duty_usd,
    1.25 AS drayage_handling_usd,
    -- Canonical Landed Cost Calculation
    (po.unit_fob_price_usd + 
     (s.freight_cost_usd / NULLIF(po.units_ordered, 0)) + 
     (po.unit_fob_price_usd * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) + 
     1.25) AS unit_landed_cost_usd,
    -- Total Landed Spend
    (po.units_ordered * (po.unit_fob_price_usd + (s.freight_cost_usd / NULLIF(po.units_ordered, 0)) + (po.unit_fob_price_usd * CASE WHEN f.country = 'Vietnam' THEN 0.12 WHEN f.country = 'Sri Lanka' THEN 0.08 WHEN f.country = 'Mexico' THEN 0.00 ELSE 0.15 END) + 1.25)) AS total_landed_cost_usd,
    DATEDIFF(day, po.po_date, o.actual_delivery_date) AS lead_time_days,
    (CASE WHEN f.country = 'Vietnam' THEN 12.0 WHEN f.country = 'Sri Lanka' THEN 8.0 WHEN f.country = 'Mexico' THEN 0.0 ELSE 15.0 END) AS tariff_rate_pct
FROM VS_SUPPLY_CHAIN_DB.SILVER.CNF_PURCHASE_ORDERS po
LEFT JOIN VS_SUPPLY_CHAIN_DB.SILVER.CNF_SHIPMENTS s ON po.po_number = s.po_number
LEFT JOIN VS_SUPPLY_CHAIN_DB.SILVER.CNF_OMNICHANNEL_ORDERS o ON po.sku_id = o.sku_id
LEFT JOIN VS_SUPPLY_CHAIN_DB.SILVER.CNF_QA_INSPECTIONS qa ON po.sku_id = qa.sku_id
LEFT JOIN VS_SUPPLY_CHAIN_DB.SILVER.DIM_FACTORIES f ON po.vendor_code = f.vendor_code
LEFT JOIN VS_SUPPLY_CHAIN_DB.SILVER.DIM_PRODUCTS p ON po.sku_id = p.sku_id;

-- 2. Governed Inventory & DOI Semantic View
CREATE OR REPLACE VIEW VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_INVENTORY_LEDGER_METRICS AS
SELECT
    inv.inventory_id,
    inv.rdc_name,
    inv.sku_id,
    p.sku_name,
    p.category,
    inv.units_on_hand,
    inv.units_in_transit,
    inv.safety_stock_threshold,
    p.unit_standard_cost_usd,
    inv.units_on_hand * p.unit_standard_cost_usd AS total_inventory_valuation_usd,
    inv.daily_sales_velocity,
    -- Canonical Days of Inventory (DOI)
    ROUND(inv.units_on_hand / NULLIF(inv.daily_sales_velocity, 0), 1) AS days_of_inventory,
    CASE 
        WHEN inv.units_on_hand < inv.safety_stock_threshold THEN 'CRITICAL_STOCKOUT_RISK'
        WHEN inv.units_on_hand > (inv.safety_stock_threshold * 3.5) THEN 'EXCESS_INVENTORY_RISK'
        ELSE 'OPTIMAL_COVER'
    END AS stock_health_status
FROM VS_SUPPLY_CHAIN_DB.SILVER.CNF_INVENTORY_LEDGER inv
JOIN VS_SUPPLY_CHAIN_DB.SILVER.DIM_PRODUCTS p ON inv.sku_id = p.sku_id;

-- 3. Governed Reverse Logistics & Returns View
CREATE OR REPLACE VIEW VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_REVERSE_LOGISTICS_METRICS AS
SELECT
    r.return_id,
    r.sku_id,
    p.sku_name,
    p.category,
    r.return_reason_raw AS return_reason,
    r.hygiene_inspection_grade,
    r.disposition_code AS restock_disposition,
    r.refund_amount_usd,
    CASE WHEN r.disposition_code = 'SELLABLE_RESTOCK' THEN 1 ELSE 0 END AS is_restocked,
    CASE WHEN r.disposition_code = 'LIQUIDATION' THEN 1 ELSE 0 END AS is_liquidated,
    CASE WHEN r.disposition_code = 'DESTROY_HYGIENE' THEN 1 ELSE 0 END AS is_destroyed
FROM VS_SUPPLY_CHAIN_DB.BRONZE.RAW_CUSTOMER_RETURNS r
JOIN VS_SUPPLY_CHAIN_DB.SILVER.DIM_PRODUCTS p ON r.sku_id = p.sku_id;
