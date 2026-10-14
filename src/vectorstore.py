"""ChromaDB wrapper. One collection per notebook (named nb_<notebook_id>)."""
import chromadb
from chromadb.config import Settings

from .config import DATA_DIR


class VectorStore:
    def __init__(self, path=None):
        path = path or (DATA_DIR / "chroma")
        self.client = chromadb.PersistentClient(
            path=str(path), settings=Settings(anonymized_telemetry=False)
        )

    @staticmethod
    def _name(nb_id: str) -> str:
        return f"nb_{nb_id}"

    def _col(self, nb_id: str):
        return self.client.get_or_create_collection(
            name=self._name(nb_id), metadata={"hnsw:space": "cosine"}
        )

    def add(self, nb_id: str, chunks: list[dict], embeddings: list[list[float]], batch: int = 500) -> None:
        col = self._col(nb_id)
        for i in range(0, len(chunks), batch):
            part = chunks[i:i + batch]
            col.add(
                ids=[c["id"] for c in part],
                documents=[c["text"] for c in part],
                metadatas=[c["metadata"] for c in part],
                embeddings=embeddings[i:i + batch],
            )

    def count(self, nb_id: str) -> int:
        return self._col(nb_id).count()

    def query(self, nb_id: str, query_embedding: list[float], k: int) -> list[dict]:
        col = self._col(nb_id)
        total = col.count()
        if total == 0:
            return []
        res = col.query(query_embeddings=[query_embedding], n_results=min(k, total),
                        include=["documents", "metadatas", "distances"])
        out = []
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            out.append({"text": doc, "metadata": meta, "score": round(1 - float(dist), 4)})
        return out

    def get_all(self, nb_id: str) -> list[dict]:
        col = self._col(nb_id)
        if col.count() == 0:
            return []
        res = col.get(include=["documents", "metadatas"])
        return [{"id": i, "text": d, "metadata": m}
                for i, d, m in zip(res["ids"], res["documents"], res["metadatas"])]

    def delete_source(self, nb_id: str, source_id: str) -> None:
        self._col(nb_id).delete(where={"source_id": source_id})

    def delete_notebook(self, nb_id: str) -> None:
        try:
            self.client.delete_collection(self._name(nb_id))
        except Exception:
            pass  # collection never created
