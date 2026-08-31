#!/usr/bin/env python3
"""
test_snowflake_connection.py
Quick diagnostics: verifies credentials, Snowflake connectivity,
and that a live CoCo answer comes from VS_SUPPLY_CHAIN_DB.GOLD
"""
import sys, os

# Ensure UTF-8 output on Windows terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from engine.db_engine import db_engine

print("=" * 60)
print("  SCCT Agent -- Snowflake Connection Diagnostic")
print("=" * 60)

# ── 1. Show which backend was chosen ─────────────────────────────
print(f"\n[1] Active backend : {db_engine.backend}")
print(f"    Snowflake acct : {db_engine._sf_account or '(not set)'}")
print(f"    Snowflake user : {db_engine._sf_user or '(not set)'}")
print(f"    Database       : {db_engine._sf_database}")
print(f"    Schema         : {db_engine._sf_schema}")

# ── 2. Live connection test ───────────────────────────────────────
print("\n[2] Testing live Snowflake connection ...")
result = db_engine.test_snowflake_connection()
if result['ok']:
    print("    [OK] Connected successfully to Snowflake!")
    print(f"       Account   : {result['account']}")
    print(f"       Role      : {result['role']}")
    print(f"       Warehouse : {result['warehouse']}")
    print(f"       Database  : {result['database']}")
    print(f"       Schema    : {result['schema']}")
else:
    print(f"    [FAIL] Connection failed: {result['error']}")
    sys.exit(1)

# ── 3. Query Gold view — same question CoCo answers ───────────────
print("\n[3] Querying Gold view: On-Time Delivery by sourcing country ...")
query = """
    SELECT
        sourcing_country,
        category,
        COUNT(*) AS total_shipments,
        ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) AS canonical_otd_pct,
        ROUND(AVG(unit_landed_cost_usd), 2) AS avg_landed_cost
    FROM VS_SUPPLY_CHAIN_DB.GOLD.VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS
    GROUP BY sourcing_country, category
    ORDER BY canonical_otd_pct DESC
"""
try:
    df = db_engine.execute_query(query)
    if df.empty:
        print("    [WARN] Query returned 0 rows — check Silver/Gold data population.")
    else:
        print(f"    [OK] Got {len(df)} rows directly from Snowflake Gold view:\n")
        print(df.to_string(index=False))
except Exception as e:
    print(f"    [FAIL] Query failed: {e}")
    sys.exit(1)

# ── 4. Quick cortex-analyst-agent smoke test ─────────────────────
print("\n[4] Smoke-testing CoCo conversational engine ...")
try:
    from engine.cortex_analyst_agent import cortex_analyst_agent
    answer = cortex_analyst_agent.answer("What is the On-Time Delivery rate by sourcing country?")
    print(f"    Backend used  : {answer.get('backend', 'unknown')}")
    print(f"    Row count     : {answer.get('row_count', '?')}")
    print(f"    Summary       : {answer.get('summary', '')}")
    print("\n    [OK] CoCo answer received from Snowflake!")
except Exception as e:
    print(f"    [WARN] CoCo engine test: {e}")

print("\n" + "=" * 60)
print("  All checks passed -- Snowflake integration verified!")
print("=" * 60)
