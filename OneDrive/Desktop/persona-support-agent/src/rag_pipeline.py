"""
rag_pipeline.py — Document ingestion, embedding, ChromaDB storage, and retrieval.

Public API
----------
    pipeline = LocalRAGPipeline()
    pipeline.build_index()                  # one-time ingestion of ./data files
    chunks   = pipeline.retrieve(query)     # returns list[dict] with text/source/score
"""

import os
import logging
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from google import genai

from src.config import (
    GEMINI_API_KEY,
    GEMINI_EMBED_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K_RESULTS,
    CHROMA_DB_DIR,
    CHROMA_COLLECTION,
    DATA_DIR,
)

logger = logging.getLogger(__name__)


class LocalRAGPipeline:
    """
    Encapsulates the full Retrieve-and-Generate knowledge-base pipeline.

    Lifecycle
    ---------
    1. ``build_index()``  — parse docs → chunk → embed → store in ChromaDB
    2. ``retrieve(query)``— embed query → cosine similarity search → return top-K chunks
    """

    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise EnvironmentError("GEMINI_API_KEY is not set in your .env file.")

        self._genai_client = genai.Client(api_key=GEMINI_API_KEY)
        self._chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self._collection = self._chroma_client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},   # ensure cosine distance
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    # ── Public helpers ──────────────────────────────────────────────────────────

    def is_index_empty(self) -> bool:
        """Returns True if no documents have been ingested yet."""
        return self._collection.count() == 0

    def build_index(self) -> int:
        """
        Reads every .txt / .md / .pdf file from DATA_DIR,
        chunks them, embeds them, and upserts into ChromaDB.

        Returns the total number of chunks stored.
        """
        data_path = Path(DATA_DIR)
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")

        files = list(data_path.glob("**/*"))
        supported = [f for f in files if f.suffix.lower() in {".txt", ".md", ".pdf"}]

        if not supported:
            raise ValueError(f"No .txt / .md / .pdf files found in {DATA_DIR}")

        total_chunks = 0
        for file_path in supported:
            logger.info("Ingesting: %s", file_path.name)
            text = self._read_file(file_path)
            if not text.strip():
                logger.warning("Skipping empty file: %s", file_path.name)
                continue
            n = self._ingest_text(doc_name=file_path.name, content=text)
            total_chunks += n
            logger.info("  → %d chunks added", n)

        logger.info("Index built: %d total chunks across %d files", total_chunks, len(supported))
        return total_chunks

    def retrieve(self, query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
        """
        Embeds the query and returns the top-K most relevant chunks.

        Each returned dict has:
            text   : str   — the raw chunk text
            source : str   — filename the chunk came from
            score  : float — cosine similarity (0 – 1, higher = more relevant)
        """
        if self._collection.count() == 0:
            logger.warning("Collection is empty — run build_index() first.")
            return []

        query_vector = self._embed(query)
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self._collection.count()),
        )

        items: list[dict] = []
        if results and results["documents"]:
            docs      = results["documents"][0]
            metas     = results["metadatas"][0]
            distances = results.get("distances", [[]])[0]

            for i, doc in enumerate(docs):
                # ChromaDB cosine distance → similarity: similarity = 1 – distance
                distance = distances[i] if distances else 0.0
                score    = max(0.0, 1.0 - distance)
                items.append({
                    "text":   doc,
                    "source": metas[i].get("source", "unknown"),
                    "score":  round(score, 4),
                })

        items.sort(key=lambda x: x["score"], reverse=True)
        return items

    # ── Private helpers ─────────────────────────────────────────────────────────

    def _read_file(self, path: Path) -> str:
        """Dispatch to the correct reader based on file extension."""
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._read_pdf(path)
        # .txt and .md are plain UTF-8
        return path.read_text(encoding="utf-8", errors="ignore")

    @staticmethod
    def _read_pdf(path: Path) -> str:
        reader   = PdfReader(str(path))
        raw_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
        return raw_text

    def _embed(self, text: str) -> list[float]:
        """Call Gemini embedding model and return the float vector."""
        response = self._genai_client.models.embed_content(
            model=GEMINI_EMBED_MODEL,
            contents=text,
        )
        return response.embeddings[0].values

    def _ingest_text(self, doc_name: str, content: str) -> int:
        """Split content into chunks, embed each, and upsert into ChromaDB."""
        chunks = self._splitter.split_text(content)
        for idx, chunk in enumerate(chunks):
            chunk_id  = f"{doc_name}_chunk_{idx}"
            embedding = self._embed(chunk)
            self._collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{"source": doc_name, "chunk_index": idx}],
                documents=[chunk],
            )
        return len(chunks)


# ── Quick manual test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = LocalRAGPipeline()
    if pipeline.is_index_empty():
        pipeline.build_index()
    hits = pipeline.retrieve("How do I reset my password?")
    for h in hits:
        print(f"\n[score={h['score']:.3f}] [{h['source']}]\n{h['text'][:200]}")
