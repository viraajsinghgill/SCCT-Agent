import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))

from engine.db_engine import db_engine

SCHEMA_PROMPT = """You are Snowflake Cortex Analyst for Victoria's Secret & Co. (VS_SUPPLY_CHAIN_DB).
Schema:
1. VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS (po_number, sku_id, sku_name, brand, category, subcategory, factory_name, sourcing_country, carrier_name, transport_mode, rdc_name, destination_channel, order_date, promised_delivery_date, actual_delivery_date, units_ordered, units_fulfilled, defect_count, unit_fob_price_usd, allocated_freight_usd, customs_duty_usd, unit_landed_cost_usd, lead_time_days, tariff_rate_pct)
2. VS_GOLD_INVENTORY_LEDGER_METRICS (rdc_name, sku_name, category, units_on_hand, units_in_transit, days_of_inventory, stock_health_status)

Return ONLY valid Snowflake SQL (SELECT statement only). No markdown, no quotes, no explanation.

Question: """

questions = [
    "how many unique products vs supploer do we have",
    "how many supploer having tariff give me top 5",
    "which product is the highest costing to us"
]

for q in questions:
    full_prompt = SCHEMA_PROMPT + q
    # Escape quotes
    safe_prompt = full_prompt.replace("'", "''")
    cortex_query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', '{safe_prompt}') AS sql_resp;"
    df = db_engine.execute_query(cortex_query)
    raw_sql = df.iloc[0]['sql_resp'].strip().replace('```sql', '').replace('```', '').strip()
    print("=" * 60)
    print("Question:", q)
    print("Generated SQL:\n", raw_sql)
    # Execute the generated SQL
    try:
        res_df = db_engine.execute_query(raw_sql)
        print("Data:\n", res_df.to_string())
    except Exception as e:
        print("Execution error:", e)
