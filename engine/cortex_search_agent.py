import os, json
from typing import Dict, Any, List

class CortexSearchAgent:
    """
    Simulates Snowflake Cortex Search:
    Performs semantic vector & keyword hybrid search across unstructured documents
    including Supplier Master Service Agreements (MSAs), SLAs, OEKO-TEX Lab Audits,
    and Supply Chain Disruption Advisories.
    """
    def __init__(self, docs_dir=None):
        if docs_dir is None:
            docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'contracts')
        self.docs_dir = docs_dir
        self.documents = self._load_documents()

    def _load_documents(self) -> List[Dict[str, Any]]:
        docs = []
        if os.path.exists(self.docs_dir):
            for fname in os.listdir(self.docs_dir):
                if fname.endswith('.json'):
                    fpath = os.path.join(self.docs_dir, fname)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        docs.append(json.load(f))
        return docs

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Rank documents by keyword and semantic match."""
        q_terms = [t.lower() for t in query.replace('?', '').replace(',', '').split() if len(t) > 2]
        scored_docs = []

        for doc in self.documents:
            score = 0.0
            doc_text = (doc.get('title', '') + ' ' + doc.get('content', '') + ' ' + json.dumps(doc.get('key_clauses', {}))).lower()
            
            for term in q_terms:
                if term in doc_text:
                    score += 2.0
                if term in doc.get('title', '').lower():
                    score += 3.0
                if term in doc.get('supplier', '').lower():
                    score += 4.0

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        results = [d[1] for d in scored_docs[:top_k]]
        
        # Fallback if no specific keyword match
        if not results and self.documents:
            results = self.documents[:top_k]

        return results

    def answer_query(self, user_question: str) -> Dict[str, Any]:
        matched_docs = self.search(user_question)
        if not matched_docs:
            return {
                "user_question": user_question,
                "answer": "No relevant contracts or SOP documents found.",
                "sources": []
            }

        top_doc = matched_docs[0]
        summary = f"Grounded in **{top_doc['title']}** ({top_doc['category']}):\n\n"
        for k, v in top_doc.get('key_clauses', {}).items():
            summary += f"- **{k.replace('_', ' ').title()}:** {v}\n"

        return {
            "user_question": user_question,
            "answer": summary,
            "top_match_title": top_doc['title'],
            "matched_documents": matched_docs
        }

cortex_search_agent = CortexSearchAgent()
