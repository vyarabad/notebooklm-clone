"""Application service layer. The UI talks only to this class.

Wires storage, ingestion, chunking, embeddings, vector store, retrieval,
RAG, and artifact generation together.
"""
import uuid
from pathlib import Path

from .artifacts import ArtifactGenerator
from .chunking import chunk_sections
from .embeddings import Embedder
from .ingestion import SUPPORTED_EXTENSIONS, IngestionError, extract_file, extract_url
from .llm import LLMClient
from .notebooks import NotebookManager
from .rag import RAGPipeline
from .retrieval import Retriever
from .storage import NotebookStorage, now_iso
from .vectorstore import VectorStore


class NotebookApp:
    def __init__(self, data_dir=None):
        self.storage = NotebookStorage(data_dir) if data_dir else NotebookStorage()
        self.vectors = VectorStore(self.storage.chroma_dir)
        self.embedder = Embedder()
        self.retriever = Retriever(self.vectors, self.embedder)
        self.llm = LLMClient()
        self.rag = RAGPipeline(self.retriever, self.llm)
        self.notebooks = NotebookManager(self.storage, self.vectors)
        self.artifacts = ArtifactGenerator(self.storage, self.vectors, self.llm)

    # ---------- ingestion ----------
    def _index(self, nb_id: str, name: str, source_type: str, sections, origin: str,
               raw_path: str | None = None) -> dict:
        source_id = uuid.uuid4().hex[:12]
        if raw_path:
            self.storage.save_raw(nb_id, raw_path, source_id, name)
        self.storage.save_extracted(
            nb_id, source_id,
            "\n\n".join(f"[{s.location}]\n{s.text}" if s.location else s.text for s in sections),
        )
        chunks = chunk_sections(sections, source_id, name, source_type)
        if not chunks:
            raise IngestionError("No text could be extracted.")
        embeddings = self.embedder.embed([c["text"] for c in chunks])
        self.vectors.add(nb_id, chunks, embeddings)

        source = {"id": source_id, "name": name, "type": source_type, "origin": origin,
                  "chunks": len(chunks), "added_at": now_iso()}
        meta = self.storage.read_meta(nb_id)
        meta.setdefault("sources", []).append(source)
        self.storage.write_meta(nb_id, meta)
        return source

    def add_file(self, nb_id: str, path: str) -> dict:
        p = Path(path)
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise IngestionError(f"'{p.name}' is not supported. Use PDF, PPTX, or TXT.")
        sections = extract_file(str(p))
        return self._index(nb_id, p.name, p.suffix.lower().lstrip("."), sections,
                           origin=p.name, raw_path=str(p))

    def add_url(self, nb_id: str, url: str) -> dict:
        title, sections = extract_url(url)
        return self._index(nb_id, title, "url", sections, origin=url.strip())

    def remove_source(self, nb_id: str, source_id: str) -> None:
        self.vectors.delete_source(nb_id, source_id)
        self.storage.delete_source_files(nb_id, source_id)
        meta = self.storage.read_meta(nb_id)
        meta["sources"] = [s for s in meta.get("sources", []) if s["id"] != source_id]
        self.storage.write_meta(nb_id, meta)

    def list_sources(self, nb_id: str) -> list[dict]:
        return self.storage.read_meta(nb_id).get("sources", [])

    # ---------- chat ----------
    def ask(self, nb_id: str, question: str, method: str = "vector", k: int = 5) -> dict:
        question = (question or "").strip()
        if not question:
            raise ValueError("Type a question first.")
        history = self.storage.read_chat(nb_id)
        result = self.rag.answer(nb_id, question, history, method, k)

        sources_md = "\n".join(f"[{c['n']}] {c['label']}" for c in result["citations"])
        display = result["answer"] + (f"\n\n**Sources**\n\n{sources_md}" if sources_md else "")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": display,
                        "citations": result["citations"], "method": method,
                        "response_time": round(result["total_time"], 2)})
        self.storage.write_chat(nb_id, history)
        result["history"] = history
        return result

    def chat_history(self, nb_id: str) -> list[dict]:
        return self.storage.read_chat(nb_id)

    def clear_chat(self, nb_id: str) -> None:
        self.storage.write_chat(nb_id, [])
