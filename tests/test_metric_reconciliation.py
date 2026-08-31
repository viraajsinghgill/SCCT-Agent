from engine.persona_reconciler import persona_reconciler
from engine.cortex_analyst_agent import cortex_analyst_agent
from engine.tariff_optimizer import tariff_optimizer

def test_cross_persona_reconciliation_zero_variance():
    result = persona_reconciler.reconcile_metric()
    assert result['canonical_otd_pct'] > 50.0
    assert result['canonical_otd_pct'] <= 100.0
    assert result['canonical_landed_cost_usd'] > 10.0

    personas = result['persona_comparison']
    assert "Planning" in personas
    assert "Procurement" in personas
    assert "Logistics" in personas
    assert "Finance" in personas

    for p_name, p_data in personas.items():
        if p_name != "Finance":
            assert f"{result['canonical_otd_pct']:.2f}%" == p_data['governed_canonical_value']
        assert p_data['is_reconciled'] is True

def test_cortex_analyst_verified_query_execution():
    res = cortex_analyst_agent.generate_and_execute("What is the On-Time Delivery rate and Landed Cost by sourcing country for Q3?")
    assert res['success'] is True
    assert res['is_verified_golden_query'] is True
    assert len(res['data']) >= 3

def test_tariff_simulation_logic():
    sim = tariff_optimizer.simulate_tariff_impact({'Vietnam': 25.0, 'Mexico': 0.0})
    comps = {c['country']: c for c in sim['factory_comparisons']}
    assert comps['Vietnam']['tariff_rate_pct'] == 25.0
    assert comps['Mexico']['tariff_rate_pct'] == 0.0
    assert comps['Mexico']['tariff_duty_usd'] == 0.0
