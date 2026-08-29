-- ==============================================================================
-- VERIFIED BENCHMARK QUERIES (CORTEX ANALYST BENCHMARK SUITE)
-- ==============================================================================

-- Benchmark 1: Canonical On-Time Delivery by Sourcing Country & Category
SELECT 
    sourcing_country,
    category,
    COUNT(*) AS total_shipments,
    ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS canonical_otd_pct,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_landed_cost_usd
FROM VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS
GROUP BY sourcing_country, category
ORDER BY canonical_otd_pct DESC;

-- Benchmark 2: Cross-Persona Reconciled Landed Cost Breakdown
SELECT 
    factory_name,
    sourcing_country,
    ROUND(AVG(unit_fob_price_usd), 2) AS fob_purchase_cost,
    ROUND(AVG(allocated_freight_usd), 2) AS ocean_freight_cost,
    ROUND(AVG(customs_duty_usd), 2) AS tariff_duties_cost,
    ROUND(AVG(drayage_handling_usd), 2) AS drayage_handling_cost,
    ROUND(AVG(unit_landed_cost_usd), 2) AS total_canonical_landed_cost
FROM VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS
GROUP BY factory_name, sourcing_country;

-- Benchmark 3: Days of Inventory & Stockout Risk by Regional Distribution Center
SELECT 
    rdc_name,
    COUNT(sku_id) AS sku_count,
    SUM(units_on_hand) AS total_units_in_warehouse,
    ROUND(AVG(days_of_inventory), 1) AS avg_days_of_inventory,
    SUM(CASE WHEN stock_health_status = 'CRITICAL_STOCKOUT_RISK' THEN 1 ELSE 0 END) AS stockout_alert_skus
FROM VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_INVENTORY_LEDGER_METRICS
GROUP BY rdc_name
ORDER BY total_units_in_warehouse DESC;
