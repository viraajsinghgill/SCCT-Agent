#!/usr/bin/env python3
"""
SCCT Agent CLI (Supply Chain Control Tower Agent)
Command-line interface for Victoria's Secret & Co. Supply Chain Governance & Conversational Analytics.
"""
import sys, os, json, argparse
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from engine import (
    cortex_analyst_agent,
    cortex_search_agent,
    persona_reconciler,
    tariff_optimizer,
    action_executor,
    ontology_engine,
    guardrails
)

def print_banner():
    print("=" * 80)
    print("  * SCCT AGENT: VICTORIA'S SECRET & CO. SUPPLY CHAIN CONTROL TOWER *")
    print("      Governed Conversational Analytics & Multi-Tier Sourcing Engine")
    print("=" * 80)

def handle_ask(question: str, persona: str):
    print(f"\n[QUERY] Persona: {persona.upper()} | Question: '{question}'")
    res = cortex_analyst_agent.generate_and_execute(question, persona)
    if res['success']:
        print(f"\n[SUMMARY] {res.get('summary')}")
        print(f"\n[GOVERNED SQL GENERATED]:\n{res['generated_sql']}")
        df = pd.DataFrame(res['data'])
        if not df.empty:
            print("\n[RESULT DATA (Top 10 rows)]:")
            print(df.head(10).to_string(index=False))
        print(f"\n[GOVERNANCE] Verified Golden Query: {res.get('is_verified_golden_query')} | Rows: {res.get('row_count')}")
    else:
        print(f"\n[ERROR / GUARDRAIL REJECTION]: {res.get('error')}")

def handle_reconcile(metric: str, category: str = None):
    print(f"\n[RECONCILIATION] Reconciling Metric: {metric.upper()} (Category: {category or 'ALL'})")
    filters = {'category': category} if category else None
    res = persona_reconciler.reconcile_metric(metric, filters)
    print(f"Canonical OTD: {res['canonical_otd_pct']}% | Canonical Landed Cost: ${res['canonical_landed_cost_usd']}/unit")
    print(f"Total Evaluated Records: {res['total_records_evaluated']}")
    print("\n" + "-" * 80)
    print(f"{'PERSONA':<15} | {'LEGACY SILO VALUE':<20} | {'GOVERNED CANONICAL VALUE':<25} | {'STATUS'}")
    print("-" * 80)
    for p_name, p_data in res['persona_comparison'].items():
        print(f"{p_name:<15} | {p_data['legacy_value']:<20} | {p_data['governed_canonical_value']:<25} | {'RECONCILED (0% VAR)' if p_data['is_reconciled'] else 'DIVERGENT'}")
    print("-" * 80)
    print(f"\n[PROOF] {res['governance_summary']}")

def handle_tariff(vietnam_tariff: float, demand: int):
    print(f"\n[SIMULATION] Simulating Section 301 Tariff Adjustments (Vietnam: {vietnam_tariff}%, Demand: {demand:,} units)")
    res = tariff_optimizer.simulate_tariff_impact({'Vietnam': vietnam_tariff}, demand)
    print("\n[LANDED COST COMPARISON ACROSS TIER 1 SOURCING FACTORIES]:")
    df = pd.DataFrame(res['factory_comparisons'])[['country', 'factory_name', 'base_fob_usd', 'tariff_rate_pct', 'tariff_duty_usd', 'freight_usd', 'unit_landed_cost_usd', 'lead_time_days']]
    print(df.to_string(index=False))
    
    split = res['recommended_split']
    print(f"\n[OPTIMAL DUAL-SOURCING SPLIT]:")
    print(f"  * Primary:   {split['primary_supplier']} ({split['primary_country']}) -> {split['primary_allocation_pct']}% allocation")
    print(f"  * Secondary: {split['secondary_supplier']} ({split['secondary_country']}) -> {split['secondary_allocation_pct']}% allocation")
    print(f"  * Blended Landed Cost: ${split['blended_unit_landed_cost_usd']:.2f}/unit | Blended Lead Time: {split['blended_lead_time_days']} days")
    print(f"  * Rationale: {split['rationale']}")

def handle_search(query: str):
    print(f"\n[CORTEX SEARCH RAG] Query: '{query}'")
    ans = cortex_search_agent.answer_query(query)
    print(f"\n{ans['answer']}")
    if ans.get('matched_documents'):
        print(f"\n[SOURCE CONTRACT]: {ans['matched_documents'][0]['title']} ({ans['matched_documents'][0]['category']})")

def handle_action(action_type: str, target: str, details: str):
    print(f"\n[MCP ACTION EXECUTION] Type: {action_type} | Target: {target}")
    if action_type == "PO_EXPEDITE":
        res = action_executor.expedite_purchase_order(target, details or "Disruption buffer expedite")
    elif action_type == "CREATE_JIRA":
        res = action_executor.create_jira_supply_incident(target, "HIGH", details=details)
    elif action_type == "SLACK_ALERT":
        res = action_executor.send_slack_governance_alert(target, details)
    else:
        res = {"success": False, "message": "Unknown action"}
    print(f"Result: {res['message']}")

def main():
    parser = argparse.ArgumentParser(description="Victoria's Secret Supply Chain Control Tower (SCCT) CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Ask
    ask_p = subparsers.add_parser("ask", help="Query Governed Conversational Analytics (Cortex Analyst)")
    ask_p.add_argument("question", type=str, help="Business question")
    ask_p.add_argument("--persona", type=str, default="EXECUTIVE", choices=["EXECUTIVE", "PLANNING", "PROCUREMENT", "LOGISTICS", "FINANCE"])

    # Reconcile
    rec_p = subparsers.add_parser("reconcile", help="Reconcile metric across Planning, Procurement, Logistics, Finance")
    rec_p.add_argument("--metric", type=str, default="on_time_delivery_rate")
    rec_p.add_argument("--category", type=str, default=None)

    # Tariff
    tar_p = subparsers.add_parser("tariff", help="Simulate multi-sourcing and tariffs")
    tar_p.add_argument("--vietnam", type=float, default=25.0, help="Simulated Vietnam tariff rate percentage")
    tar_p.add_argument("--demand", type=int, default=100000, help="Unit demand volume")

    # Search
    search_p = subparsers.add_parser("search", help="Search contracts, SLAs, and SOPs (Cortex Search)")
    search_p.add_argument("query", type=str, help="Contract search terms")

    # Action
    act_p = subparsers.add_parser("action", help="Dispatch operational MCP intervention")
    act_p.add_argument("type", choices=["PO_EXPEDITE", "CREATE_JIRA", "SLACK_ALERT"])
    act_p.add_argument("target", type=str, help="PO number, channel, or ticket title")
    act_p.add_argument("--details", type=str, default="", help="Context details")

    args = parser.parse_args()
    print_banner()

    if args.command == "ask":
        handle_ask(args.question, args.persona)
    elif args.command == "reconcile":
        handle_reconcile(args.metric, args.category)
    elif args.command == "tariff":
        handle_tariff(args.vietnam, args.demand)
    elif args.command == "search":
        handle_search(args.query)
    elif args.command == "action":
        handle_action(args.type, args.target, args.details)
    else:
        print("\nDemonstrating SCCT Agent Capabilities:")
        handle_ask("What is the On-Time Delivery rate and Landed Cost by sourcing country for Q3?", "EXECUTIVE")
        handle_reconcile("on_time_delivery_rate")
        handle_tariff(25.0, 100000)

if __name__ == '__main__':
    main()
