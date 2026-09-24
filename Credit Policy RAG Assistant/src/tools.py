"""
Tools module for the Google ADK Agent.
Contains the policy retrieval tool registered with the agent.
"""

from src.vector_store import PolicyVectorStore

# Singleton vector store instance
_vector_store = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = PolicyVectorStore()
    return _vector_store


def search_credit_policy(query: str) -> str:
    """
    Searches the Australian Credit Policy guidelines for relevant lending rules,
    LVR cut-offs, LMI requirements, income shading percentages, living expense (HEM) rules,
    genuine savings criteria, and Delegated Lending Authority (DLA) approval exception tiers.

    Args:
        query: The natural language question or scenario (e.g. 'overtime shading percentage',
               'max LVR for 45 sqm apartment', 'genuine savings required for 85% LVR').

    Returns:
        A structured string containing matching credit policy clauses with section numbers,
        clause citations, and source documents.
    """
    store = get_vector_store()
    if store.count() == 0:
        return (
            "NOTICE: The credit policy database is currently empty. "
            "Please run 'python ingest.py' to index the credit policy documents."
        )

    results = store.search(query=query, n_results=4)
    if not results:
        return f"No matching credit policy clauses found for query: '{query}'."

    output_lines = [f"=== RETRIEVED CREDIT POLICY CLAUSES (Query: '{query}') ==="]
    
    for i, res in enumerate(results, 1):
        meta = res["metadata"]
        source = meta.get("source", "Unknown Document")
        section = meta.get("section", "General")
        clause = meta.get("clause", "General")
        rel = res.get("relevance_score", 0.0)

        output_lines.append(f"\n--- [Result {i}] Source: {source} | {section} | {clause} (Relevance: {rel}) ---")
        output_lines.append(res["content"])

    output_lines.append("\n=== END OF POLICY RETRIEVAL ===")
    return "\n".join(output_lines)
