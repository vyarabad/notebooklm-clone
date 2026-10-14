# NotebookLM Clone

A full-stack RAG app inspired by Google NotebookLM. Create notebooks, add sources (PDF, PPTX, TXT, web URLs), chat with them and get answers with citations, and generate a report or a quiz with an answer key.

- **Live app:** https://notebook-app-614268852432.us-central1.run.app
- **GitHub:** https://github.com/vyarabad/notebooklm-clone
- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **RAG evaluation:** [eval/results.md](eval/results.md)

## Features

- **Notebooks:** create, rename, delete, switch. Each notebook has its own sources, chat, and artifacts.
- **Ingestion:** PDF, PPTX (including tables and speaker notes), TXT, single-page URLs. Text is extracted, chunked, embedded, and stored in ChromaDB with page/slide metadata.
- **RAG chat:** answers are grounded in the notebook's sources with numbered citations like `[1]`, plus a panel showing the exact retrieved chunks and response time. Chat history is saved per notebook.
- **Two retrieval methods:** plain vector search, or vector search + cross-encoder reranking (switchable in the UI).
- **Artifacts:** report and quiz (with answer key) saved as `.md`, viewable and downloadable. Old artifacts can be reopened.
- **Error handling:** friendly messages for bad files, scanned PDFs, bad URLs, empty notebooks, missing API keys, and LLM errors.

## Tech stack

| Part | Tool |
|---|---|
| UI | Gradio 5 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Vector DB | ChromaDB (persistent) |
| LLM | Groq, GPT OSS 120B (OpenAI-compatible API) |
| Extraction | pypdf, python-pptx, requests + BeautifulSoup |
| Hosting | Google Cloud Run (Docker container) |
| CI/CD | Cloud Build trigger (deploy) + GitHub Actions (tests) |

**Why Groq:** Gemini was tested first but returned frequent 503 "high demand" errors and slow responses. Groq is fast (about 500 tokens/sec) and reliable. The LLM client is OpenAI-compatible, so switching providers only means changing `LLM_BASE_URL` and `LLM_MODEL`.

## Run locally

```bash
git clone https://github.com/vyarabad/notebooklm-clone.git
cd notebooklm-clone
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then put your Groq key in .env
python app.py
```

Open http://localhost:7860. The first question or upload takes a little longer while the embedding model downloads.

Run tests: `pip install -r requirements-dev.txt && pytest`

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `LLM_API_KEY` | yes | | API key for the LLM provider (Groq) |
| `LLM_BASE_URL` | no | `https://api.groq.com/openai/v1` | Any OpenAI-compatible endpoint |
| `LLM_MODEL` | no | `openai/gpt-oss-120b` | Model name |
| `LLM_REASONING_EFFORT` | no | (unset) | `low` makes reasoning models answer faster |
| `DATA_DIR` | no | `data` | Where notebooks and the vector DB are stored |
| `EMBED_MODEL` | no | `all-MiniLM-L6-v2` | Embedding model |
| `RERANK_MODEL` | no | `ms-marco-MiniLM-L-6-v2` | Reranker model |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | no | `1000` / `150` | Chunking settings (characters) |
| `PORT` | no | `7860` (Cloud Run sets `8080`) | Port the app listens on |

API keys are never committed. Locally they live in `.env` (gitignored). On Cloud Run the key is stored in **Google Secret Manager** and injected as `LLM_API_KEY` at deploy time.

## Project structure

```
app.py                 Gradio UI only (layout + event handlers)
src/
  config.py            settings from environment variables
  storage.py           storage abstraction: all paths and file I/O
  notebooks.py         create / rename / delete / list notebooks
  ingestion.py         text extraction for PDF, PPTX, TXT, URL
  chunking.py          chunking strategy + citation metadata
  embeddings.py        embedding model wrapper
  vectorstore.py       ChromaDB wrapper (one collection per notebook)
  retrieval.py         vector search and reranking
  llm.py               LLM client (OpenAI-compatible)
  rag.py               RAG pipeline: retrieve, prompt, answer, citations
  artifacts.py         report and quiz generation
  service.py           service layer the UI calls; wires everything together
eval/
  run_eval.py          compares the two retrieval methods
  questions.json       test questions
  results.md           evaluation results
tests/                 unit tests (run in GitHub Actions)
docs/architecture.md   architecture document
Dockerfile             container image for Cloud Run
cloudbuild.yaml        build, push, and deploy steps for Cloud Build
.github/workflows/     GitHub Actions CI (syntax check + unit tests)
```

## How data is stored

```
data/
  chroma/                          ChromaDB, one collection per notebook (nb_<id>)
  notebooks/<notebook_id>/
    meta.json                      name, timestamps, list of sources
    chat.json                      chat history (with citations and response times)
    raw/                           original uploaded files
    extracted/                     extracted text for each source
    artifacts/                     report_*.md, quiz_*.md
```

Each notebook gets a UUID. Sources, chats, and artifacts all live under that ID, and every chunk in ChromaDB carries `source_id`, `source_name`, `location` (page/slide), and `chunk_index` for citations. Everything is reloaded from disk when the app restarts.

### Storage limitations

Cloud Run's local disk is **ephemeral**. Data survives while the container is running, but is wiped when the service scales to zero, restarts, or redeploys (for example after every push). Running locally, `data/` persists normally.

If persistence on Cloud Run were needed, the storage layer (`storage.py`) could be swapped for Firestore or Cloud Storage without touching the rest of the app. This was not added, since the assignment says to document storage limits rather than add unnecessary infrastructure.

## How to use

1. Pick a notebook from the dropdown, or type a name and click **Create**.
2. Upload PDF/PPTX/TXT files and click **Add files**, or paste a URL and click **Add URL**.
3. In the **Chat** tab, ask a question. Answers cite sources as `[1]`, `[2]`. Open **Retrieved chunks** to see the exact text used. Switch **Retrieval method** to compare vector vs rerank.
4. In the **Artifacts** tab, click **Generate report** or **Generate quiz**. View it on the page and download the `.md`. Previous artifacts are in the **Saved artifacts** dropdown.
5. Rename or delete notebooks from the left panel.

## Deployment (Google Cloud Run + Cloud Build)

One-time setup in Google Cloud:

1. Create a project and link billing.
2. Enable APIs: Cloud Run Admin, Cloud Build, Artifact Registry, Secret Manager.
3. Artifact Registry: create a Docker repo `notebook-repo` in `us-central1`.
4. Secret Manager: create secret `LLM_API_KEY` with the Groq key.
5. IAM: give the default compute service account Cloud Run Admin, Service Account User, Artifact Registry Writer, Logs Writer, and Secret Manager Secret Accessor.
6. Cloud Build: connect the GitHub repo (2nd gen) and create a trigger on push to `main` that uses `cloudbuild.yaml`.

CI/CD flow:

```
code change > git push (main)
   ├─ GitHub Actions: syntax check + unit tests
   └─ Cloud Build trigger: docker build > push to Artifact Registry > deploy to Cloud Run
                                                                      > updated app live
```

The container uses 2 GiB of memory, scales from 0 to 2 instances, and has a 900s request timeout so slow LLM calls aren't cut off. The first request after idle is slow (cold start + model load).

## RAG evaluation

See [eval/results.md](eval/results.md). To rerun:

```bash
# put 2-3 docs in eval/docs/ and edit eval/questions.json
python -m eval.run_eval --judge
```