"""
config.py — Central configuration and thresholds for the support agent.
All tunable parameters live here so nothing is scattered across the codebase.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API ────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

# ── Models ─────────────────────────────────────────────────────────────────────
GEMINI_CHAT_MODEL: str    = "gemini-2.5-flash"
GEMINI_EMBED_MODEL: str   = "text-embedding-004"

# ── RAG / Chunking ─────────────────────────────────────────────────────────────
CHUNK_SIZE: int     = 500   # characters per chunk
CHUNK_OVERLAP: int  = 50    # overlap between adjacent chunks
TOP_K_RESULTS: int  = 3     # number of chunks returned per query

# ── Vector Database ────────────────────────────────────────────────────────────
CHROMA_DB_DIR: str       = "./chroma_db"
CHROMA_COLLECTION: str   = "support_kb"

# ── Escalation Thresholds ──────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD: float = 0.45   # cosine-similarity floor; below → escalate

SENSITIVE_KEYWORDS: list[str] = [
    "billing", "refund", "charge", "payment", "legal", "lawsuit",
    "account deletion", "fraud", "dispute", "cancel subscription",
    "duplicate charge", "overcharge",
]

# ── Data directory ─────────────────────────────────────────────────────────────
DATA_DIR: str = "./data"

# ── Persona labels ─────────────────────────────────────────────────────────────
PERSONAS: list[str] = [
    "Technical Expert",
    "Frustrated User",
    "Business Executive",
]
