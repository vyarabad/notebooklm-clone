"""Artifact generation: report and quiz (with answer key), saved as .md files."""
from collections import defaultdict
from datetime import datetime

from .config import ARTIFACT_CONTEXT_CHARS
from .llm import LLMClient
from .rag import citation_label
from .storage import NotebookStorage
from .vectorstore import VectorStore

REPORT_PROMPT = """Write a well-organized study report in markdown using ONLY the numbered source excerpts.
Structure:
# <descriptive title>
## Summary  (one short paragraph)
## Key Topics  (use ### subheadings for each main topic, with explanations)
## Important Terms  (bulleted term: definition)
## Takeaways  (3 to 6 bullets)
Cite excerpts inline like [3]. Do not invent information that isn't in the excerpts."""

QUIZ_PROMPT = """Create a quiz with exactly {n} multiple-choice questions using ONLY the numbered source excerpts.
Cover different topics across the sources. Each question has 4 options and exactly one correct answer.
Use exactly this markdown format:

# Quiz: <topic>

## Questions

**1. <question>**
- A) <option>
- B) <option>
- C) <option>
- D) <option>

(continue for all {n} questions)

## Answer Key

1. **B** : <one-sentence explanation> [excerpt number]
(continue for all {n} questions)"""


class ArtifactGenerator:
    def __init__(self, storage: NotebookStorage, vectors: VectorStore, llm: LLMClient):
        self.storage = storage
        self.vectors = vectors
        self.llm = llm

    def select_context(self, nb_id: str, max_chars: int = ARTIFACT_CONTEXT_CHARS) -> list[dict]:
        """Pick chunks spread evenly across every source so the artifact covers all of them."""
        all_chunks = self.vectors.get_all(nb_id)
        if not all_chunks:
            raise ValueError("Add at least one source before generating artifacts.")
        by_source = defaultdict(list)
        for c in all_chunks:
            by_source[c["metadata"]["source_id"]].append(c)
        budget = max_chars // len(by_source)
        picked = []
        for chunks in by_source.values():
            chunks.sort(key=lambda c: c["metadata"].get("chunk_index", 0))
            total = sum(len(c["text"]) for c in chunks)
            if total <= budget:
                picked.extend(chunks)
                continue
            avg = max(total / len(chunks), 1)
            n_take = max(1, int(budget // avg))
            step = len(chunks) / n_take
            picked.extend(chunks[int(i * step)] for i in range(n_take))
        return picked

    def _context_text(self, chunks: list[dict]) -> str:
        return "\n\n".join(f"[{i}] ({citation_label(c['metadata'])})\n{c['text']}"
                           for i, c in enumerate(chunks, start=1))

    def _footer(self, chunks: list[dict]) -> str:
        lines = [f"- [{i}] {citation_label(c['metadata'])}" for i, c in enumerate(chunks, start=1)]
        return "\n\n---\n\n<details><summary>Source excerpts referenced</summary>\n\n" + "\n".join(lines) + "\n\n</details>\n"

    def _header(self, nb_id: str, kind: str) -> str:
        meta = self.storage.read_meta(nb_id)
        sources = ", ".join(s["name"] for s in meta.get("sources", [])) or "none"
        return (f"> **Notebook:** {meta['name']}  \n> **Type:** {kind}  \n"
                f"> **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
                f"> **Sources:** {sources}\n\n")

    def _generate(self, nb_id: str, kind: str, instructions: str) -> tuple[str, str]:
        chunks = self.select_context(nb_id)
        body = self.llm.chat([
            {"role": "system", "content": "You create accurate study materials grounded only in provided sources."},
            {"role": "user", "content": f"{instructions}\n\nSource excerpts:\n\n{self._context_text(chunks)}"},
        ], temperature=0.3)
        content = self._header(nb_id, kind) + body + self._footer(chunks)
        path = self.storage.save_artifact(nb_id, kind.lower(), content)
        return content, str(path)

    def generate_report(self, nb_id: str) -> tuple[str, str]:
        return self._generate(nb_id, "Report", REPORT_PROMPT)

    def generate_quiz(self, nb_id: str, n_questions: int = 8) -> tuple[str, str]:
        n_questions = max(1, min(int(n_questions), 30))
        return self._generate(nb_id, "Quiz", QUIZ_PROMPT.format(n=n_questions))
