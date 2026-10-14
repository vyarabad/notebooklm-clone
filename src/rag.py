"""RAG pipeline: retrieve -> build grounded prompt -> LLM -> answer + citations."""
import re
import time

from .config import DEFAULT_TOP_K
from .llm import LLMClient
from .retrieval import Retriever

SYSTEM_PROMPT = """You are a research assistant answering questions about a notebook of sources.
Rules:
- Use ONLY the numbered source excerpts provided. Do not use outside knowledge.
- Cite every factual claim with the excerpt number in square brackets, like [1] or [2][3].
- If the excerpts don't contain the answer, say you couldn't find it in this notebook's sources.
- Never invent citations. Keep the answer clear and concise, using markdown when helpful."""


def citation_label(meta: dict) -> str:
    loc = meta.get("location") or ""
    return f"{meta.get('source_name', 'source')}{', ' + loc if loc else ''}"


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{i}] ({citation_label(c['metadata'])})\n{c['text']}"
                       for i, c in enumerate(chunks, start=1))


def used_citations(answer: str, n: int) -> list[int]:
    nums = sorted({int(x) for x in re.findall(r"\[(\d+)\]", answer) if 1 <= int(x) <= n})
    return nums


class RAGPipeline:
    def __init__(self, retriever: Retriever, llm: LLMClient):
        self.retriever = retriever
        self.llm = llm

    def answer(self, nb_id: str, question: str, history: list[dict] | None = None,
               method: str = "vector", k: int = DEFAULT_TOP_K) -> dict:
        t0 = time.perf_counter()
        chunks, retrieval_time = self.retriever.retrieve(nb_id, question, method, k)
        if not chunks:
            return {
                "answer": "This notebook has no sources yet. Add a PDF, PPTX, TXT, or URL first.",
                "chunks": [], "citations": [], "retrieval_time": retrieval_time,
                "total_time": time.perf_counter() - t0, "method": method,
            }

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in (history or [])[-6:]:  # short memory for follow-up questions
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user",
                         "content": f"Source excerpts:\n\n{format_context(chunks)}\n\nQuestion: {question}"})

        answer = self.llm.chat(messages)
        cited = used_citations(answer, len(chunks)) or list(range(1, len(chunks) + 1))
        citations = [{"n": n, "label": citation_label(chunks[n - 1]["metadata"]),
                      "snippet": chunks[n - 1]["text"][:300]} for n in cited]
        return {
            "answer": answer, "chunks": chunks, "citations": citations,
            "retrieval_time": retrieval_time, "total_time": time.perf_counter() - t0,
            "method": method,
        }
