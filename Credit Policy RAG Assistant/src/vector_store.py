"""
Vector Store module.
Interfaces with local ChromaDB and uses Ollama nomic-embed-text for local embeddings.
"""

import requests
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

from src.config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
)


def get_ollama_embedding(text: str, model: str = OLLAMA_EMBED_MODEL) -> List[float]:
    """Generates an embedding vector using Ollama's local embedding API."""
    url = f"{OLLAMA_BASE_URL}/api/embeddings"
    response = requests.post(url, json={"model": model, "prompt": text}, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["embedding"]


def get_ollama_embeddings_batch(texts: List[str], model: str = OLLAMA_EMBED_MODEL) -> List[List[float]]:
    """Batch-generates embeddings using Ollama's embed API or falls back to individual calls."""
    try:
        url = f"{OLLAMA_BASE_URL}/api/embed"
        response = requests.post(url, json={"model": model, "input": texts}, timeout=120)
        if response.status_code == 200:
            data = response.json()
            if "embeddings" in data:
                return data["embeddings"]
    except Exception:
        pass

    # Fallback to sequential individual requests
    return [get_ollama_embedding(t, model=model) for t in texts]


class PolicyVectorStore:
    """Manages the local persistent ChromaDB vector collection."""

    def __init__(self, chroma_path=CHROMA_DIR, collection_name=COLLECTION_NAME):
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Australian Credit Policy knowledge base"}
        )

    def count(self) -> int:
        """Returns the number of indexed chunks."""
        return self.collection.count()

    def reset(self):
        """Clears the existing collection for a fresh re-index."""
        self.client.delete_collection(name=self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"description": "Australian Credit Policy knowledge base"}
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Generates embeddings and stores policy chunks into ChromaDB."""
        if not chunks:
            return

        texts = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [c["metadata"]["chunk_id"] for c in chunks]

        print(f"Generating embeddings for {len(texts)} chunks using Ollama ({OLLAMA_EMBED_MODEL})...")
        embeddings = get_ollama_embeddings_batch(texts)

        # ChromaDB adds documents
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        print(f"Successfully indexed {len(texts)} chunks into ChromaDB.")

    def search(self, query: str, n_results: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieves the most semantically relevant policy clauses for a given query.
        """
        query_embedding = get_ollama_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, dists):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "relevance_score": round(1.0 - dist, 4) if dist <= 1.0 else round(1.0 / (1.0 + dist), 4),
                })

        return formatted_results
