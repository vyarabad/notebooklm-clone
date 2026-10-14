"""Notebook management: create, rename, delete, list."""
import uuid

from .storage import NotebookStorage, now_iso
from .vectorstore import VectorStore


class NotebookManager:
    def __init__(self, storage: NotebookStorage, vectors: VectorStore):
        self.storage = storage
        self.vectors = vectors

    def create(self, name: str) -> str:
        nb_id = uuid.uuid4().hex
        name = (name or "").strip() or "Untitled notebook"
        self.storage.init_notebook(nb_id, {
            "id": nb_id,
            "name": name,
            "created_at": now_iso(),
            "sources": [],
        })
        return nb_id

    def rename(self, nb_id: str, new_name: str) -> None:
        new_name = (new_name or "").strip()
        if not new_name:
            raise ValueError("Notebook name can't be empty.")
        meta = self.storage.read_meta(nb_id)
        meta["name"] = new_name
        self.storage.write_meta(nb_id, meta)

    def delete(self, nb_id: str) -> None:
        self.vectors.delete_notebook(nb_id)
        self.storage.delete_notebook(nb_id)

    def get(self, nb_id: str) -> dict:
        return self.storage.read_meta(nb_id)

    def list(self) -> list[tuple[str, str]]:
        """Returns [(display_name, id)] sorted oldest first."""
        metas = []
        for nb_id in self.storage.list_ids():
            try:
                metas.append(self.storage.read_meta(nb_id))
            except Exception:
                continue
        metas.sort(key=lambda m: m.get("created_at", ""))
        return [(m["name"], m["id"]) for m in metas]
