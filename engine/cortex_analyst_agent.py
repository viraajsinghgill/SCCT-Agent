import json, os, yaml
from typing import Dict, Any, Optional
from engine.db_engine import db_engine
from engine.ontology_engine import ontology_engine
from engine.semantic_router import semantic_router
from engine.guardrails import guardrails

class CortexAnalystAgent:
    """
    Simulates Snowflake Cortex Analyst:
    Translates business natural language into governed Snowflake SQL grounded
    in the semantic data model, verifies semantic constraints, and executes queries.
    """
    def __init__(self):
        self.verified_queries = self._load_verified_queries()

    def _load_verified_queries(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ontology', 'snowflake_cortex_semantic_model.yaml')
        if os.path.exists(model_path):
            with open(model_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('verified_queries', [])
        return []

    def generate_and_execute(self, user_question: str, persona: str = "EXECUTIVE") -> Dict[str, Any]:
        routing = semantic_router.route_query(user_question, persona)
        
        # 1. Check verified golden queries first
        matched_vq = None
        for vq in self.verified_queries:
            if vq['question'].lower() in user_question.lower() or user_question.lower() in vq['question'].lower():
                matched_vq = vq
                break

        if matched_vq:
            sql = matched_vq['sql']
            is_golden = True
        else:
            is_golden = False
            sql = self._synthesize_governed_sql(routing)

        # 2. Validate via Guardrails
        val = guardrails.validate_sql(sql)
        if not val['is_valid']:
            return {
                "success": False,
                "error": val['reason'],
                "generated_sql": sql,
                "routing": routing
            }

        # 3. Execute query
        try:
            df = db_engine.execute_query(sql)
            return {
                "success": True,
                "user_question": user_question,
                "persona": persona,
                "primary_metric": routing['primary_metric'],
                "is_verified_golden_query": is_golden,
                "generated_sql": sql,
                "data": df.to_dict(orient='records'),
                "row_count": len(df),
                "summary": self._generate_business_summary(routing, df)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_sql": sql,
                "routing": routing
            }

    def _synthesize_governed_sql(self, routing: Dict[str, Any]) -> str:
        metric = routing.get('primary_metric', 'on_time_delivery_rate')
        filters = routing.get('filters', {})
        
        where_clauses = []
        if 'sourcing_country' in filters:
            where_clauses.append(f"sourcing_country = '{filters['sourcing_country']}'")
        if 'category' in filters:
            where_clauses.append(f"category = '{filters['category']}'")
        if 'rdc_name' in filters:
            where_clauses.append(f"rdc_name = '{filters['rdc_name']}'")

        where_stmt = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        if metric == 'days_of_inventory':
            return f"""SELECT 
    rdc_name, 
    sku_name,
    category,
    units_on_hand,
    units_in_transit,
    days_of_inventory,
    stock_health_status
FROM VS_GOLD_INVENTORY_LEDGER_METRICS{where_stmt}
ORDER BY days_of_inventory DESC
LIMIT 15;"""
        elif metric == 'landed_cost_per_unit':
            return f"""SELECT 
    sourcing_country,
    category,
    ROUND(AVG(unit_fob_price_usd), 2) AS avg_fob_cost,
    ROUND(AVG(allocated_freight_usd), 2) AS avg_freight,
    ROUND(AVG(customs_duty_usd), 2) AS avg_customs_tariff,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_total_landed_cost,
    COUNT(po_number) AS total_orders
FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS{where_stmt}
GROUP BY sourcing_country, category
ORDER BY avg_total_landed_cost ASC;"""
        elif metric == 'order_fill_rate':
            return f"""SELECT 
    destination_channel,
    category,
    SUM(units_ordered) AS total_ordered,
    SUM(units_fulfilled) AS total_fulfilled,
    ROUND(SUM(units_fulfilled) * 100.0 / NULLIF(SUM(units_ordered), 0), 2) AS canonical_fill_rate_pct
FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS{where_stmt}
GROUP BY destination_channel, category
ORDER BY canonical_fill_rate_pct DESC;"""
        else: # on_time_delivery_rate default
            return f"""SELECT 
    sourcing_country,
    category,
    COUNT(*) AS total_shipments,
    ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS canonical_otd_pct,
    ROUND(AVG(lead_time_days), 1) AS avg_lead_time_days,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_landed_cost_usd
FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS{where_stmt}
GROUP BY sourcing_country, category
ORDER BY canonical_otd_pct DESC;"""

    def _generate_business_summary(self, routing: Dict[str, Any], df) -> str:
        if df.empty:
            return "No matching supply chain records found for the requested filters."
        
        metric = routing.get('primary_metric', 'on_time_delivery_rate')
        if 'canonical_otd_pct' in df.columns:
            avg_otd = df['canonical_otd_pct'].mean()
            top_country = df.iloc[0]['sourcing_country']
            return f"Across {len(df)} segments, average On-Time Delivery is {avg_otd:.1f}%. Top performer is {top_country} ({df.iloc[0]['canonical_otd_pct']}% OTD)."
        elif 'avg_total_landed_cost' in df.columns:
            lowest_cost = df.iloc[0]['sourcing_country']
            return f"Landed cost analysis shows {lowest_cost} offers the lowest total delivered unit cost (${df.iloc[0]['avg_total_landed_cost']:.2f}/unit)."
        elif 'days_of_inventory' in df.columns:
            avg_doi = df['days_of_inventory'].mean()
            return f"Average inventory cover is {avg_doi:.1f} days across evaluated distribution hubs."
        return f"Successfully retrieved {len(df)} governed rows grounded in the Victoria's Secret supply chain ontology."

cortex_analyst_agent = CortexAnalystAgent()
