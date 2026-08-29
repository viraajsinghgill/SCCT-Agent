import re
from typing import Dict, Any, List, Optional
from engine.ontology_engine import ontology_engine

class SemanticRouter:
    """
    Translates free-form business questions into grounded semantic queries,
    identifying canonical metrics, entity dimensions, filters, and persona context.
    """
    def __init__(self):
        self.metrics = ontology_engine.get_canonical_metrics()

    def route_query(self, user_query: str, persona: str = "EXECUTIVE") -> Dict[str, Any]:
        q_lower = user_query.lower()
        
        detected_metrics = []
        for m_key, m_def in self.metrics.items():
            # Check main key & display name
            if m_key.replace('_', ' ') in q_lower or m_def['display_name'].lower() in q_lower:
                detected_metrics.append((m_key, m_def))
                continue
            # Check synonyms
            for syn in m_def.get('synonyms', []):
                if syn.lower() in q_lower:
                    detected_metrics.append((m_key, m_def))
                    break

        # Detect filters and entities
        filters = {}
        if 'vietnam' in q_lower:
            filters['sourcing_country'] = 'Vietnam'
        elif 'sri lanka' in q_lower:
            filters['sourcing_country'] = 'Sri Lanka'
        elif 'mexico' in q_lower:
            filters['sourcing_country'] = 'Mexico'
        elif 'india' in q_lower:
            filters['sourcing_country'] = 'India'

        if 'bra' in q_lower or 'bras' in q_lower:
            filters['category'] = 'Bras'
        elif 'panty' in q_lower or 'panties' in q_lower:
            filters['category'] = 'Panties'
        elif 'fragrance' in q_lower or 'perfume' in q_lower or 'bombshell' in q_lower:
            filters['category'] = 'Fragrance'
        elif 'sleepwear' in q_lower or 'pajama' in q_lower:
            filters['category'] = 'Sleepwear'

        if 'columbus' in q_lower:
            filters['rdc_name'] = 'Columbus Central Omnichannel DC'
        elif 'ontario' in q_lower or 'inland empire' in q_lower:
            filters['rdc_name'] = 'Inland Empire Gateway DC'
        elif 'atlanta' in q_lower:
            filters['rdc_name'] = 'Southeast Regional Logistics Hub'

        # Intent classification
        intent = "METRIC_AGGREGATION"
        if any(w in q_lower for w in ['contract', 'agreement', 'sla', 'penalty', 'clause', 'sop', 'policy', 'oeko-tex', 'oekotex', 'audit', 'strike', 'dwell']):
            intent = "UNSTRUCTURED_DOCUMENT_SEARCH"
        elif any(w in q_lower for w in ['tariff', 'duty', 'landed cost comparison', 'shift sourcing', 'usmca', 'section 301', 'nearshore']):
            intent = "TARIFF_AND_SOURCING_SIMULATION"
        elif any(w in q_lower for w in ['reconcile', 'difference', 'compare personas', 'why does planning see', 'procurement says']):
            intent = "CROSS_PERSONA_RECONCILIATION"
        elif any(w in q_lower for w in ['expedite', 'create ticket', 'raise alert', 'slack', 'jira', 'take action']):
            intent = "OPERATIONAL_ACTION"

        return {
            "raw_query": user_query,
            "persona": persona,
            "intent": intent,
            "detected_metrics": [m[0] for m in detected_metrics],
            "primary_metric": detected_metrics[0][0] if detected_metrics else "on_time_delivery_rate",
            "filters": filters
        }

semantic_router = SemanticRouter()
