"""Chunking strategy.

Character-based sliding window (default 1000 chars, 150 overlap) that snaps
to natural boundaries: paragraph, then line, then sentence, then word. Each
section (page/slide) is chunked separately so every chunk keeps an exact
page or slide number for citations.
"""
import re

from .config import CHUNK_OVERLAP, CHUNK_SIZE

_BOUNDARIES = ("\n\n", "\n", ". ", "? ", "! ", "; ", " ")


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = re.sub(r"[ \t]+", " ", text or "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    overlap = min(overlap, chunk_size // 2)

    chunks, start, n = [], 0, len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            window = text[start:end]
            for sep in _BOUNDARIES:
                idx = window.rfind(sep)
                if idx >= chunk_size * 0.5:
                    end = start + idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= n:
            break
        # step back for overlap, then move forward to the next word start
        new_start = max(end - overlap, start + 1)
        space = text.find(" ", new_start, end)
        start = space + 1 if space != -1 else new_start
    return chunks


def chunk_sections(sections, source_id: str, source_name: str, source_type: str,
                   chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Turn extracted sections into chunk dicts ready for the vector store."""
    out, idx = [], 0
    for sec in sections:
        for piece in split_text(sec.text, chunk_size, overlap):
            out.append({
                "id": f"{source_id}-{idx}",
                "text": piece,
                "metadata": {
                    "source_id": source_id,
                    "source_name": source_name,
                    "source_type": source_type,
                    "location": sec.location or "",
                    "chunk_index": idx,
                },
            })
            idx += 1
    return out
