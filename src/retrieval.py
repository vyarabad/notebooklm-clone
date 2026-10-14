"""Retrieval strategies compared in the RAG evaluation.

  vector : top-k cosine similarity search in ChromaDB
  rerank : fetch RERANK_CANDIDATES by vector search, re-score each
           (question, chunk) pair with a cross-encoder, keep top-k
"""
import threading
import time

from .config import DEFAULT_TOP_K, RERANK_CANDIDATES, RERANK_MODEL
from .embeddings import Embedder
from .vectorstore import VectorStore

METHODS = ["vector", "rerank"]


class Retriever:
    def __init__(self, vectors: VectorStore, embedder: Embedder, rerank_model: str = RERANK_MODEL):
        self.vectors = vectors
        self.embedder = embedder
        self.rerank_model_name = rerank_model
        self._reranker = None
        self._lock = threading.Lock()

    @property
    def reranker(self):
        if self._reranker is None:
            with self._lock:
                if self._reranker is None:
                    from sentence_transformers import CrossEncoder
                    self._reranker = CrossEncoder(self.rerank_model_name, device="cpu")
        return self._reranker

    def vector_search(self, nb_id: str, question: str, k: int = DEFAULT_TOP_K) -> list[dict]:
        q = self.embedder.embed_query(question)
        return self.vectors.query(nb_id, q, k)

    def rerank_search(self, nb_id: str, question: str, k: int = DEFAULT_TOP_K,
                      candidates: int = RERANK_CANDIDATES) -> list[dict]:
        cands = self.vector_search(nb_id, question, max(candidates, k))
        if not cands:
            return []
        scores = self.reranker.predict([(question, c["text"]) for c in cands])
        for c, s in zip(cands, scores):
            c["vector_score"] = c["score"]
            c["score"] = round(float(s), 4)
        cands.sort(key=lambda c: c["score"], reverse=True)
        return cands[:k]

    def retrieve(self, nb_id: str, question: str, method: str = "vector",
                 k: int = DEFAULT_TOP_K) -> tuple[list[dict], float]:
        """Returns (chunks, seconds_taken)."""
        t0 = time.perf_counter()
        if method == "rerank":
            chunks = self.rerank_search(nb_id, question, k)
        else:
            chunks = self.vector_search(nb_id, question, k)
        return chunks, time.perf_counter() - t0
