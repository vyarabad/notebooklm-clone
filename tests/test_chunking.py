from src.chunking import chunk_sections, split_text
from src.ingestion import Section


def test_short_text_is_one_chunk():
    assert split_text("hello world", 100, 10) == ["hello world"]


def test_empty_text():
    assert split_text("   ", 100, 10) == []


def test_chunks_respect_size_and_cover_text():
    text = " ".join(f"Sentence number {i} is here." for i in range(300))
    chunks = split_text(text, 500, 80)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    assert "Sentence number 0" in chunks[0]
    assert "Sentence number 299" in chunks[-1]


def test_metadata_kept_for_citations():
    secs = [Section("a " * 600, "page 1"), Section("b " * 50, "page 2")]
    chunks = chunk_sections(secs, "src1", "doc.pdf", "pdf", 500, 50)
    assert chunks[0]["metadata"]["location"] == "page 1"
    assert chunks[-1]["metadata"]["location"] == "page 2"
    assert [c["metadata"]["chunk_index"] for c in chunks] == list(range(len(chunks)))
    assert len({c["id"] for c in chunks}) == len(chunks)
