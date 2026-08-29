import json, sys, os
from typing import Dict, Any, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from engine import (
    cortex_analyst_agent,
    cortex_search_agent,
    persona_reconciler,
    tariff_optimizer,
    action_executor,
    ontology_engine
)

class SupplyChainMCPServer:
    """
    Model Context Protocol (MCP) Server for SCCT Agent.
    Exposes high-leverage tools for agent orchestration, external data integration,
    semantic querying, and enterprise workflow execution.
    """
    def __init__(self):
        self.tools = [
            {
                "name": "query_governed_metrics",
                "description": "Natural language query against Snowflake Cortex Analyst semantic model for canonical supply chain metrics (OTD, Fill Rate, DOI, Landed Cost).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Natural language business question"},
                        "persona": {"type": "string", "enum": ["EXECUTIVE", "PLANNING", "PROCUREMENT", "LOGISTICS", "FINANCE"], "default": "EXECUTIVE"}
                    },
                    "required": ["question"]
                }
            },
            {
                "name": "search_contracts_and_slas",
                "description": "Cortex Search tool to query unstructured supplier contracts, SLAs, OEKO-TEX audits, and disruption advisories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term or question regarding contracts, SLAs, or disruption policies"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "reconcile_persona_metrics",
                "description": "Simulates and reconciles metric divergence across Planning, Procurement, Logistics, and Finance personas.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string", "default": "on_time_delivery_rate"},
                        "category": {"type": "string", "description": "Optional product category filter"}
                    }
                }
            },
            {
                "name": "simulate_tariffs_and_sourcing",
                "description": "Simulates landed cost and multi-sourcing allocation shifts across Vietnam, Sri Lanka, Mexico, and India under tariff adjustments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "vietnam_tariff_pct": {"type": "number", "default": 12.0},
                        "sri_lanka_tariff_pct": {"type": "number", "default": 8.0},
                        "mexico_tariff_pct": {"type": "number", "default": 0.0},
                        "demand_units": {"type": "integer", "default": 100000}
                    }
                }
            },
            {
                "name": "execute_supply_chain_action",
                "description": "Dispatches operational interventions: expedite POs, create Jira incident tickets, post Slack governance alerts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {"type": "string", "enum": ["PO_EXPEDITE", "CREATE_JIRA_INCIDENT", "POST_SLACK_ALERT"]},
                        "target_id": {"type": "string", "description": "PO Number, Ticket Title, or Channel"},
                        "details": {"type": "string", "description": "Reason or context for operational intervention"}
                    },
                    "required": ["action_type", "target_id"]
                }
            }
        ]

    def list_tools(self) -> List[Dict[str, Any]]:
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "query_governed_metrics":
            return cortex_analyst_agent.generate_and_execute(arguments.get("question", ""), arguments.get("persona", "EXECUTIVE"))
        elif tool_name == "search_contracts_and_slas":
            return cortex_search_agent.answer_query(arguments.get("query", ""))
        elif tool_name == "reconcile_persona_metrics":
            cat = arguments.get("category")
            filters = {"category": cat} if cat else None
            return persona_reconciler.reconcile_metric(arguments.get("metric_name", "on_time_delivery_rate"), filters)
        elif tool_name == "simulate_tariffs_and_sourcing":
            tariffs = {
                'Vietnam': arguments.get('vietnam_tariff_pct', 12.0),
                'Sri Lanka': arguments.get('sri_lanka_tariff_pct', 8.0),
                'Mexico': arguments.get('mexico_tariff_pct', 0.0)
            }
            return tariff_optimizer.simulate_tariff_impact(tariffs, arguments.get('demand_units', 100000))
        elif tool_name == "execute_supply_chain_action":
            atype = arguments.get("action_type")
            target = arguments.get("target_id")
            details = arguments.get("details", "")
            if atype == "PO_EXPEDITE":
                return action_executor.expedite_purchase_order(target, details)
            elif atype == "CREATE_JIRA_INCIDENT":
                return action_executor.create_jira_supply_incident(target, "HIGH", details=details)
            elif atype == "POST_SLACK_ALERT":
                return action_executor.send_slack_governance_alert(target, details)
        return {"error": f"Tool '{tool_name}' not recognized."}

mcp_server = SupplyChainMCPServer()

if __name__ == '__main__':
    print(json.dumps(mcp_server.list_tools(), indent=2))
