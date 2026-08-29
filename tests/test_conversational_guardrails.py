from engine.guardrails import guardrails
from engine.cortex_search_agent import cortex_search_agent

def test_guardrails_allow_governed_views():
    val = guardrails.validate_sql("SELECT sourcing_country, AVG(unit_landed_cost_usd) FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS GROUP BY sourcing_country;")
    assert val['is_valid'] is True

def test_guardrails_block_destructive_sql():
    val = guardrails.validate_sql("DROP TABLE RAW_ERP_PURCHASE_ORDERS;")
    assert val['is_valid'] is False
    assert "SECURITY_VIOLATION" in val['reason']

def test_guardrails_block_ungoverned_raw_tables():
    val = guardrails.validate_sql("SELECT * FROM SOME_RANDOM_SECRET_TABLE;")
    assert val['is_valid'] is False
    assert "GOVERNANCE_VIOLATION" in val['reason']

def test_cortex_search_retrieves_contracts():
    ans = cortex_search_agent.answer_query("What is the late delivery penalty for Crystal International in Vietnam?")
    assert "Crystal International" in ans['top_match_title']
    assert len(ans['matched_documents']) > 0
