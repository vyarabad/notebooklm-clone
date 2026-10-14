"""Central configuration. Everything is read from environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Storage
DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()

# Models
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# LLM (any OpenAI-compatible API: Gemini, Groq, OpenAI, ...)
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))        # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))   # characters

# Retrieval
DEFAULT_TOP_K = int(os.getenv("TOP_K", "5"))
RERANK_CANDIDATES = int(os.getenv("RERANK_CANDIDATES", "20"))

# Artifacts
ARTIFACT_CONTEXT_CHARS = int(os.getenv("ARTIFACT_CONTEXT_CHARS", "24000"))
