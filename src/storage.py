"""Storage abstraction layer.

This is the only module that knows where files live on disk. Every other
module asks NotebookStorage for paths and data, so the backend could be
swapped (e.g. for S3 or GCS) by rewriting just this file.

Layout:
    data/
      chroma/                       vector database (one collection per notebook)
      notebooks/{notebook_id}/
        meta.json                   name, timestamps, list of sources
        chat.json                   chat history
        raw/                        original uploaded files
        extracted/                  extracted plain text per source
        artifacts/                  generated .md files (reports, quizzes)
"""
import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR

_ID_RE = re.compile(r"^[a-f0-9]{32}$")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def safe_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return (name or "file")[:100]


def _check_id(nb_id: str) -> None:
    # Prevents path traversal and garbage IDs
    if not nb_id or not _ID_RE.match(nb_id):
        raise ValueError("Invalid notebook id.")


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # atomic write


def _read_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class NotebookStorage:
    def __init__(self, root: Path = DATA_DIR):
        self.root = Path(root)
        self.notebooks_dir = self.root / "notebooks"
        self.chroma_dir = self.root / "chroma"
        self.notebooks_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

    # ---------- paths ----------
    def nb_dir(self, nb_id: str) -> Path:
        _check_id(nb_id)
        return self.notebooks_dir / nb_id

    def raw_dir(self, nb_id: str) -> Path:
        return self.nb_dir(nb_id) / "raw"

    def extracted_dir(self, nb_id: str) -> Path:
        return self.nb_dir(nb_id) / "extracted"

    def artifacts_dir(self, nb_id: str) -> Path:
        return self.nb_dir(nb_id) / "artifacts"

    # ---------- notebooks ----------
    def init_notebook(self, nb_id: str, meta: dict) -> None:
        for d in (self.raw_dir(nb_id), self.extracted_dir(nb_id), self.artifacts_dir(nb_id)):
            d.mkdir(parents=True, exist_ok=True)
        self.write_meta(nb_id, meta)
        self.write_chat(nb_id, [])

    def list_ids(self) -> list[str]:
        return [p.name for p in self.notebooks_dir.iterdir()
                if p.is_dir() and _ID_RE.match(p.name) and (p / "meta.json").exists()]

    def exists(self, nb_id: str) -> bool:
        try:
            return (self.nb_dir(nb_id) / "meta.json").exists()
        except ValueError:
            return False

    def read_meta(self, nb_id: str) -> dict:
        meta = _read_json(self.nb_dir(nb_id) / "meta.json", None)
        if meta is None:
            raise FileNotFoundError("Notebook not found.")
        return meta

    def write_meta(self, nb_id: str, meta: dict) -> None:
        meta["updated_at"] = now_iso()
        _write_json(self.nb_dir(nb_id) / "meta.json", meta)

    def delete_notebook(self, nb_id: str) -> None:
        shutil.rmtree(self.nb_dir(nb_id), ignore_errors=True)

    # ---------- chat ----------
    def read_chat(self, nb_id: str) -> list[dict]:
        return _read_json(self.nb_dir(nb_id) / "chat.json", [])

    def write_chat(self, nb_id: str, messages: list[dict]) -> None:
        _write_json(self.nb_dir(nb_id) / "chat.json", messages)

    # ---------- sources ----------
    def save_raw(self, nb_id: str, src_path: str, source_id: str, name: str) -> Path:
        dest = self.raw_dir(nb_id) / f"{source_id}_{safe_filename(name)}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src_path, dest)
        return dest

    def save_extracted(self, nb_id: str, source_id: str, text: str) -> Path:
        dest = self.extracted_dir(nb_id) / f"{source_id}.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        return dest

    def delete_source_files(self, nb_id: str, source_id: str) -> None:
        for p in self.raw_dir(nb_id).glob(f"{source_id}_*"):
            p.unlink(missing_ok=True)
        (self.extracted_dir(nb_id) / f"{source_id}.txt").unlink(missing_ok=True)

    # ---------- artifacts ----------
    def save_artifact(self, nb_id: str, kind: str, content: str) -> Path:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = self.artifacts_dir(nb_id) / f"{safe_filename(kind)}_{ts}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        return dest

    def list_artifacts(self, nb_id: str) -> list[str]:
        d = self.artifacts_dir(nb_id)
        if not d.exists():
            return []
        return sorted((p.name for p in d.glob("*.md")), reverse=True)

    def artifact_path(self, nb_id: str, filename: str) -> Path:
        path = self.artifacts_dir(nb_id) / safe_filename(filename)
        if not path.exists():
            raise FileNotFoundError("Artifact not found.")
        return path
