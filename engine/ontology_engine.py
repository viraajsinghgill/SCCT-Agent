import os, json, yaml
from collections import deque


class _SimpleDigraph:
    """Minimal directed graph with BFS shortest path — no external deps."""

    def __init__(self):
        self._nodes = {}
        self._edges = {}          # (src, tgt) -> attrs
        self._succ  = {}          # src -> {tgt: attrs}
        self._pred  = {}          # tgt -> {src: attrs}

    def add_node(self, name, **attrs):
        self._nodes[name] = attrs
        self._succ.setdefault(name, {})
        self._pred.setdefault(name, {})

    def add_edge(self, src, tgt, **attrs):
        self.add_node(src)
        self.add_node(tgt)
        self._succ[src][tgt] = attrs
        self._pred[tgt][src] = attrs
        self._edges[(src, tgt)] = attrs

    def __contains__(self, name):
        return name in self._nodes

    def get_edge_data(self, src, tgt):
        return self._edges.get((src, tgt), {})

    def predecessors(self, name):
        return list(self._pred.get(name, {}).keys())

    def successors(self, name):
        return list(self._succ.get(name, {}).keys())

    def nodes(self):
        return dict(self._nodes)

    def edges(self):
        return list(self._edges.keys())

    def shortest_path(self, source, target):
        """BFS shortest path; raises KeyError / ValueError on failure."""
        if source not in self._nodes:
            raise KeyError(source)
        if target not in self._nodes:
            raise KeyError(target)
        visited = {source: None}
        queue   = deque([source])
        while queue:
            current = queue.popleft()
            if current == target:
                path = []
                while current is not None:
                    path.append(current)
                    current = visited[current]
                path.reverse()
                return path
            for neighbour in self._succ.get(current, {}):
                if neighbour not in visited:
                    visited[neighbour] = current
                    queue.append(neighbour)
        raise ValueError(f"No path between {source!r} and {target!r}")


class OntologyEngine:
    """
    Supply Chain Knowledge Graph & Ontology Engine for Victoria's Secret & Co.
    Provides graph traversal, entity relationships, hierarchy navigation,
    and metric lookups.  No third-party graph library required.
    """

    def __init__(self, ontology_path=None, metrics_path=None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if ontology_path is None:
            ontology_path = os.path.join(base_dir, 'ontology', 'supply_chain_ontology.json')
        if metrics_path is None:
            metrics_path = os.path.join(base_dir, 'ontology', 'metrics_catalog.yaml')

        self.ontology_path = ontology_path
        self.metrics_path  = metrics_path
        self.ontology_data = {}
        self.metrics_data  = {}
        self.graph         = _SimpleDigraph()
        self._load_ontology()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_ontology(self):
        if os.path.exists(self.ontology_path):
            with open(self.ontology_path, 'r', encoding='utf-8') as f:
                self.ontology_data = json.load(f)

        if os.path.exists(self.metrics_path):
            with open(self.metrics_path, 'r', encoding='utf-8') as f:
                self.metrics_data = yaml.safe_load(f)

        # Build directed graph
        for entity_name, entity_def in self.ontology_data.get('entities', {}).items():
            self.graph.add_node(
                entity_name,
                description=entity_def.get('description', ''),
                properties=entity_def.get('properties', []),
                primary_key=entity_def.get('primary_key', '')
            )

        for rel in self.ontology_data.get('relationships', []):
            self.graph.add_edge(
                rel['source'],
                rel['target'],
                relation=rel['relation'],
                cardinality=rel.get('cardinality', '1:N')
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_entities(self):
        return self.ontology_data.get('entities', {})

    def get_relationships(self):
        return self.ontology_data.get('relationships', [])

    def get_canonical_metrics(self):
        return self.metrics_data.get('canonical_metrics', {})

    def get_metric(self, metric_key: str):
        return self.metrics_data.get('canonical_metrics', {}).get(metric_key)

    def find_shortest_path(self, source_entity: str, target_entity: str):
        """Find relationship path between two supply chain entities."""
        try:
            path = self.graph.shortest_path(source_entity, target_entity)
            edge_details = []
            for i in range(len(path) - 1):
                edge_data = self.graph.get_edge_data(path[i], path[i + 1])
                edge_details.append({
                    'from':     path[i],
                    'to':       path[i + 1],
                    'relation': edge_data.get('relation', 'CONNECTS_TO')
                })
            return {'path': path, 'hops': len(path) - 1, 'edges': edge_details}
        except (KeyError, ValueError):
            return None

    def get_entity_neighbors(self, entity_name: str):
        if entity_name not in self.graph:
            return {'upstream': [], 'downstream': []}
        upstream   = self.graph.predecessors(entity_name)
        downstream = self.graph.successors(entity_name)
        return {'entity': entity_name, 'upstream': upstream, 'downstream': downstream}


ontology_engine = OntologyEngine()
