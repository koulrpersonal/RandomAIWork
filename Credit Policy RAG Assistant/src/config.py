"""
Configuration module for Credit Policy RAG Assistant.
Handles paths, Ollama endpoints, and model configurations.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
POLICIES_DIR = DATA_DIR / "policies"
CHROMA_DIR = DATA_DIR / "chroma_db"

# Ollama Settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_LLM_MODEL = "ollama_chat/llama3.2"
OLLAMA_EMBED_MODEL = "nomic-embed-text"

# Vector Store Settings
COLLECTION_NAME = "aus_credit_policy"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 120

# Ensure directories exist
POLICIES_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
