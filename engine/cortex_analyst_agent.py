import json, os, yaml
from typing import Dict, Any, Optional
from engine.db_engine import db_engine
from engine.ontology_engine import ontology_engine
from engine.semantic_router import semantic_router
from engine.guardrails import guardrails

def _gold_view(name: str) -> str:
    """Return fully-qualified Gold view name for the active backend."""
    if db_engine.backend == "Snowflake":
        db  = db_engine._sf_database  # VS_SUPPLY_CHAIN_DB
        sch = db_engine._sf_schema    # GOLD
        return f"{db}.{sch}.{name}"
    return name  # SQLite uses unqualified name

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

    def _generate_sql_via_cortex(self, user_question: str, conversation_context: str = "") -> Optional[str]:
        context_block = ""
        if conversation_context:
            context_block = f"\nPrevious Conversation (use for context only, generate SQL for the LATEST question):\n{conversation_context}\n"

        prompt = f"""You are Snowflake Cortex Analyst for SCCT Agent (VS_SUPPLY_CHAIN_DB).
Schema available:
1. VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS (po_number, sku_id, sku_name, brand, category, subcategory, factory_name, sourcing_country, sourcing_region, carrier_name, transport_mode, origin_port, dest_port, rdc_name, destination_channel, order_date, promised_delivery_date, actual_delivery_date, units_ordered, units_fulfilled, defect_count, is_iot_anomaly, unit_fob_price_usd, allocated_freight_usd, customs_duty_usd, unit_landed_cost_usd, total_landed_cost_usd, lead_time_days, tariff_rate_pct)
2. VS_GOLD_INVENTORY_LEDGER_METRICS (inventory_id, rdc_name, sku_id, sku_name, category, units_on_hand, units_in_transit, safety_stock_threshold, unit_standard_cost_usd, total_inventory_valuation_usd, daily_sales_velocity, days_of_inventory, stock_health_status)
{context_block}
Rules:
- Generate ONLY valid Snowflake SELECT SQL query, no markdown fences, no comments, no explanation.
- Ground all queries on Gold views above.
- ALWAYS give clean alphanumeric aliases to all aggregate columns (e.g. SUM(units_ordered) AS total_units_ordered, COUNT(DISTINCT sku_name) AS unique_products_count, AVG(unit_landed_cost_usd) AS avg_landed_cost). NEVER omit AS aliases.
- Canonical OTD formula: ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS canonical_otd_pct

User Question: {user_question}"""
        try:
            raw_resp = db_engine.execute_cortex_llm(prompt, model='llama3.1-70b')
            if raw_resp:
                cleaned = raw_resp.strip().replace('```sql', '').replace('```', '').strip()
                if cleaned.upper().startswith('SELECT'):
                    return cleaned
        except Exception:
            pass
        return None

    def generate_and_execute(self, user_question: str, persona: str = "EXECUTIVE", conversation_context: str = "") -> Dict[str, Any]:
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
        elif db_engine.backend == "Snowflake":
            cortex_sql = self._generate_sql_via_cortex(user_question, conversation_context)
            if cortex_sql:
                sql = cortex_sql
                is_golden = False
            else:
                sql = self._synthesize_governed_sql(routing)
                is_golden = False
        else:
            is_golden = False
            sql = self._synthesize_governed_sql(routing)

        # 2. Validate via Guardrails
        val = guardrails.validate_sql(sql)
        if not val['is_valid']:
            # Fallback to synthesized template if dynamic sql was blocked
            sql = self._synthesize_governed_sql(routing)
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
                "backend": db_engine.backend,
                "user_question": user_question,
                "persona": persona,
                "primary_metric": routing['primary_metric'],
                "is_verified_golden_query": is_golden,
                "generated_sql": sql,
                "data": df.to_dict(orient='records'),
                "row_count": len(df),
                "summary": self._generate_business_summary(routing, df, conversation_context)
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

        is_sku_level = routing.get('is_sku_level', False)

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
            if is_sku_level:
                return f"""SELECT 
    sku_name,
    category,
    sourcing_country,
    ROUND(AVG(unit_fob_price_usd), 2) AS avg_fob_cost,
    ROUND(AVG(allocated_freight_usd), 2) AS avg_freight,
    ROUND(AVG(customs_duty_usd), 2) AS avg_customs_tariff,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_total_landed_cost,
    COUNT(po_number) AS total_orders
FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS{where_stmt}
GROUP BY sku_name, category, sourcing_country
ORDER BY avg_total_landed_cost DESC
LIMIT 10;"""
            else:
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
ORDER BY avg_total_landed_cost DESC;"""
        elif metric == 'supplier_network_directory':
            return f"""SELECT 
    factory_name,
    sourcing_country,
    category,
    COUNT(po_number) AS total_orders,
    ROUND(AVG(unit_fob_price_usd), 2) AS avg_fob_price,
    ROUND(AVG(unit_landed_cost_usd), 2) AS avg_landed_cost,
    ROUND(SUM(CASE WHEN actual_delivery_date <= promised_delivery_date AND defect_count = 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) AS otd_pct
FROM VS_GOLD_SUPPLY_CHAIN_UNIFIED_METRICS{where_stmt}
GROUP BY factory_name, sourcing_country, category
ORDER BY total_orders DESC;"""
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

    def _generate_business_summary(self, routing: Dict[str, Any], df, conversation_context: str = "") -> str:
        if df.empty:
            return "No matching supply chain records found for the requested filters."
        
        user_question = routing.get('raw_query', '')

        # 1. In Snowflake mode, use Cortex LLM to synthesize a natural conversational executive insight
        if db_engine.backend == "Snowflake" and len(df) <= 50 and user_question:
            try:
                context_block = ""
                if conversation_context:
                    context_block = f"\nPrevious Conversation:\n{conversation_context}\n"
                # Take top 10 records as JSON for concise context
                records_snippet = df.head(10).to_json(orient='records')
                cortex_prompt = f"""You are Snowflake Cortex Analyst for Victoria's Secret & Co.{context_block}
User asked: "{user_question}"
Retrieved Data from Gold Semantic View: {records_snippet}
Provide a natural, professional, 1-2 sentence executive answer directly answering the user's question using the retrieved data. If the user references something from a previous question, use the conversation context. Do NOT mention SQL, JSON, or databases."""
                summary = db_engine.execute_cortex_llm(cortex_prompt, model='llama3.1-70b')
                if summary:
                    return summary.strip().replace('"', '').replace('**', '')
            except Exception:
                pass

        # 2. Deterministic Template Fallback
        metric = routing.get('primary_metric', 'on_time_delivery_rate')
        if metric == 'supplier_network_directory' and 'factory_name' in df.columns:
            n_suppliers = df['factory_name'].nunique()
            countries = [str(c) for c in df['sourcing_country'].dropna().unique()]
            return f"Victoria's Secret & Co. maintains {n_suppliers} unique Tier 1 manufacturing suppliers across {len(countries)} global sourcing hubs ({', '.join(countries[:4])})."
        elif 'canonical_otd_pct' in df.columns:
            avg_otd = df['canonical_otd_pct'].mean()
            top_country = df.iloc[0]['sourcing_country']
            return f"Across {len(df)} segments, average On-Time Delivery is {avg_otd:.1f}%. Top performer is {top_country} ({df.iloc[0]['canonical_otd_pct']}% OTD)."
        elif 'avg_total_landed_cost' in df.columns:
            top_row = df.iloc[0]
            if 'sku_name' in df.columns:
                return f"Highest costing product is '{top_row['sku_name']}' ({top_row['category']}) with an average landed cost of ${top_row['avg_total_landed_cost']:.2f}/unit (sourced from {top_row['sourcing_country']})."
            else:
                return f"Landed cost analysis shows {top_row['sourcing_country']} ({top_row['category']}) has average landed cost of ${top_row['avg_total_landed_cost']:.2f}/unit."
        elif 'days_of_inventory' in df.columns:
            avg_doi = df['days_of_inventory'].mean()
            return f"Average inventory cover is {avg_doi:.1f} days across evaluated distribution hubs."
        return f"Successfully retrieved {len(df)} governed rows grounded in the Victoria's Secret supply chain ontology."

    def answer(self, user_question: str, persona: str = "EXECUTIVE") -> Dict[str, Any]:
        """Convenience alias for generate_and_execute()."""
        return self.generate_and_execute(user_question, persona)


cortex_analyst_agent = CortexAnalystAgent()
