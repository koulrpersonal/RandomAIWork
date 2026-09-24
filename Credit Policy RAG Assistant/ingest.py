"""
Ingestion Pipeline Script.
Scans the data/policies directory, parses all PDF, Word, and Markdown documents,
computes vector embeddings via Ollama nomic-embed-text, and indexes them into ChromaDB.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import POLICIES_DIR, CHROMA_DIR
from src.document_loader import load_all_policy_documents
from src.vector_store import PolicyVectorStore


def run_ingestion(reset: bool = True):
    print("=" * 65)
    print("  AUSTRALIAN CREDIT POLICY RAG — INGESTION PIPELINE")
    print("=" * 65)
    print(f"Scanning policy directory: {POLICIES_DIR}")

    # Check for policy files
    files = list(POLICIES_DIR.glob("*.*"))
    if not files:
        print("\nNo policy documents found in data/policies/!")
        print("Please place your PDF, DOCX, or Markdown files into data/policies/ and rerun.")
        return

    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  • {f.name} ({f.stat().st_size / 1024:.1f} KB)")

    # 1. Load and chunk documents
    print("\n[Step 1/3] Parsing documents and generating section-aware chunks...")
    chunks = load_all_policy_documents(POLICIES_DIR)
    print(f"-> Generated {len(chunks)} text chunks with metadata.")

    # 2. Initialize ChromaDB
    print(f"\n[Step 2/3] Connecting to local ChromaDB at: {CHROMA_DIR}...")
    store = PolicyVectorStore()
    if reset:
        print("-> Resetting previous collection for clean index...")
        store.reset()

    # 3. Embed and Index
    print("\n[Step 3/3] Generating embeddings via Ollama and indexing into ChromaDB...")
    store.add_chunks(chunks)
    print(f"\nIngestion Complete! Total indexed chunks: {store.count()}")

    # 4. Quick Verification Query
    print("\n" + "-" * 65)
    print("Running verification search for: 'What is the maximum LVR for an apartment?'")
    test_results = store.search("What is the maximum LVR for an apartment?", n_results=2)
    for i, r in enumerate(test_results, 1):
        meta = r['metadata']
        print(f"  [{i}] Source: {meta.get('source')} | {meta.get('clause')} (Relevance: {r['relevance_score']})")
        print(f"      Snippet: {r['content'][:150].strip()}...")
    print("-" * 65)
    print("\nKnowledge base is ready for Google ADK Agent!")


if __name__ == "__main__":
    run_ingestion()
