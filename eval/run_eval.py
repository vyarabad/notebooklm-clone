"""RAG evaluation: compares plain vector search vs. vector search + reranking.

Usage:
    1. Put 2-3 test documents (PDF/PPTX/TXT) in eval/docs/
    2. Edit eval/questions.json with questions about those documents
    3. python -m eval.run_eval            (add --judge to let the LLM score answers 1-5)

Writes eval/results.md (tables + retrieved chunks + answers) and eval/results.json.
The 'Answer Quality' column is yours to fill in after reading the answers
(or use --judge for an automatic first pass).
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from src.rag import citation_label
from src.retrieval import METHODS
from src.service import NotebookApp

HERE = Path(__file__).parent

JUDGE_PROMPT = """Rate the ANSWER to the QUESTION on a 1-5 scale for how correct, complete,
and grounded it is in the CONTEXT (5 = fully correct and grounded, 1 = wrong or unsupported).
Reply with only the number.

QUESTION: {q}

CONTEXT:
{ctx}

ANSWER:
{a}"""


def build_notebook(app: NotebookApp, docs_dir: Path) -> str:
    files = [p for p in sorted(docs_dir.iterdir()) if p.suffix.lower() in (".pdf", ".pptx", ".txt")]
    urls_file = docs_dir / "urls.txt"
    urls = [u.strip() for u in urls_file.read_text().splitlines() if u.strip()] if urls_file.exists() else []
    if not files and not urls:
        raise SystemExit(f"No documents found in {docs_dir}. Add PDFs/PPTX/TXT or a urls.txt file.")
    nb_id = app.notebooks.create(f"RAG Eval {time.strftime('%Y-%m-%d %H:%M')}")
    for f in files:
        src = app.add_file(nb_id, str(f))
        print(f"  ingested {src['name']}: {src['chunks']} chunks")
    for u in urls:
        src = app.add_url(nb_id, u)
        print(f"  ingested {src['name']}: {src['chunks']} chunks")
    return nb_id


def judge(app: NotebookApp, q: str, chunks: list, answer: str) -> str:
    ctx = "\n\n".join(c["text"][:800] for c in chunks)
    try:
        score = app.llm.chat([{"role": "user", "content": JUDGE_PROMPT.format(q=q, ctx=ctx, a=answer)}],
                             temperature=0)
        return score.strip()[:3]
    except Exception as e:
        return f"err: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default=str(HERE / "docs"))
    ap.add_argument("--questions", default=str(HERE / "questions.json"))
    ap.add_argument("--notebook-id", help="Reuse an existing notebook instead of ingesting eval/docs")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--judge", action="store_true", help="Use the LLM to score answers 1-5")
    args = ap.parse_args()

    app = NotebookApp()
    questions = json.loads(Path(args.questions).read_text())
    nb_id = args.notebook_id or build_notebook(app, Path(args.docs))

    # Warm up models so load time doesn't skew the first measurement
    print("Warming up models...")
    for m in METHODS:
        app.retriever.retrieve(nb_id, "warm up", m, args.k)

    rows = []
    for qi, item in enumerate(questions, start=1):
        q = item["question"] if isinstance(item, dict) else item
        for method in METHODS:
            print(f"Q{qi} [{method}] {q[:60]}")
            res = app.rag.answer(nb_id, q, [], method, args.k)
            row = {
                "qid": qi, "question": q, "method": method,
                "expected": item.get("expected", "") if isinstance(item, dict) else "",
                "n_chunks": len(res["chunks"]),
                "retrieval_time": round(res["retrieval_time"], 3),
                "total_time": round(res["total_time"], 2),
                "chunks": [{"label": citation_label(c["metadata"]), "score": c["score"],
                            "chunk_id": f"{c['metadata']['source_id']}-{c['metadata']['chunk_index']}",
                            "text": c["text"][:200].replace("\n", " ")} for c in res["chunks"]],
                "answer": res["answer"],
                "quality": judge(app, q, res["chunks"], res["answer"]) if args.judge else "",
            }
            rows.append(row)

    (HERE / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    write_markdown(rows, args.k)
    print(f"\nDone. See {HERE / 'results.md'}")


def write_markdown(rows: list[dict], k: int):
    md = ["# RAG Evaluation Results\n",
          f"Methods compared: **vector** (cosine top-{k}) vs **rerank** "
          f"(vector top-20, re-scored with a cross-encoder, keep top-{k}).\n",
          "## Summary table\n",
          "| Q | Question | Method | Retrieved Chunks | Retrieval Time (s) | Total Response Time (s) | Answer Quality |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['qid']} | {r['question'][:60]} | {r['method']} | {r['n_chunks']} | "
                  f"{r['retrieval_time']} | {r['total_time']} | {r['quality'] or '_fill in_'} |")

    md.append("\n## Averages\n\n| Method | Avg Retrieval (s) | Avg Total (s) |\n|---|---|---|")
    for m in METHODS:
        mr = [r for r in rows if r["method"] == m]
        if mr:
            md.append(f"| {m} | {statistics.mean(r['retrieval_time'] for r in mr):.3f} | "
                      f"{statistics.mean(r['total_time'] for r in mr):.2f} |")

    md.append("\n## Chunk overlap between methods\n")
    md.append("How many of the top chunks both methods agreed on (low overlap = reranking changed what the LLM saw).\n")
    md.append("| Q | Shared chunks |\n|---|---|")
    for qid in sorted({r["qid"] for r in rows}):
        sets = [{c["chunk_id"] for c in r["chunks"]} for r in rows if r["qid"] == qid]
        if len(sets) == 2:
            md.append(f"| {qid} | {len(sets[0] & sets[1])} / {k} |")

    md.append("\n## Details per question\n")
    for r in rows:
        md.append(f"### Q{r['qid']} [{r['method']}]: {r['question']}\n")
        if r["expected"]:
            md.append(f"**Expected:** {r['expected']}\n")
        md.append("**Retrieved chunks:**\n")
        for i, c in enumerate(r["chunks"], start=1):
            md.append(f"{i}. *{c['label']}* (score {c['score']}): {c['text']}...")
        md.append(f"\n**Answer** ({r['total_time']}s):\n\n{r['answer']}\n")

    md.append("\n## Conclusions\n\n_Write 1-2 paragraphs: which method gave better answers, how much slower "
              "reranking was, where it helped or didn't, and which method you chose as the default and why._\n")
    (HERE / "results.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main()
