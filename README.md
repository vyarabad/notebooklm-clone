

# NotebookLM Clone

A full-stack RAG app inspired by Google NotebookLM. Create notebooks, add sources (PDF, PPTX, TXT, web URLs), chat with them and get answers with citations, and generate a report or a quiz with an answer key.

- **Live app:** https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
- **GitHub:** https://github.com/YOUR_USERNAME/YOUR_REPO
- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **RAG evaluation:** [eval/results.md](eval/results.md)

## Features

- **Notebooks:** create, rename, delete, switch. Each notebook has its own sources, chat, and artifacts.
- **Ingestion:** PDF, PPTX (including tables and speaker notes), TXT, single-page URLs. Text is extracted, chunked, embedded, and stored in ChromaDB with page/slide metadata.
- **RAG chat:** answers are grounded in the notebook's sources with numbered citations like `[1]`, plus a panel showing the exact retrieved chunks and response time. Chat history is saved per notebook.
- **Two retrieval methods:** plain vector search, or vector search + cross-encoder reranking (switchable in the UI).
- **Artifacts:** report and quiz (with answer key) saved as `.md`, viewable and downloadable. Old artifacts can be reopened.
- **Error handling:** friendly messages for bad files, scanned PDFs, bad URLs, empty notebooks, and missing API keys.

## Tech stack

| Part | Tool |
|---|---|
| UI | Gradio 5 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Vector DB | ChromaDB (persistent) |
| LLM | Any OpenAI-compatible API (default: Gemini 2.5 Flash) |
| Extraction | pypdf, python-pptx, requests + BeautifulSoup |
| Hosting | Hugging Face Spaces |
| CI/CD | GitHub Actions |

## Run locally

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then put your API key in .env
python app.py
```

Open http://localhost:7860. The first question or upload takes a little longer while the embedding model downloads.

Run tests: `pip install -r requirements-dev.txt && pytest`

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `LLM_API_KEY` | yes | | API key for the LLM provider |
| `LLM_BASE_URL` | no | Gemini OpenAI-compatible URL | Change to use Groq, OpenAI, etc. |
| `LLM_MODEL` | no | `gemini-2.5-flash` | Model name |
| `DATA_DIR` | no | `data` | Where notebooks and the vector DB are stored |
| `EMBED_MODEL` | no | `all-MiniLM-L6-v2` | Embedding model |
| `RERANK_MODEL` | no | `ms-marco-MiniLM-L-6-v2` | Reranker model |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | no | `1000` / `150` | Chunking settings (characters) |

API keys are never committed. Locally they live in `.env` (gitignored). On Hugging Face they are Space secrets, and the deploy token is a GitHub Actions secret.

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
tests/                 unit tests (run in CI)
docs/architecture.md   architecture document
.github/workflows/     CI/CD to Hugging Face Spaces
Dockerfile             optional, for Cloud Run / Render / Railway
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

On free Hugging Face Spaces the disk is **ephemeral**: data survives page refreshes and app sleep/wake within the same container, but is wiped when the Space restarts or redeploys (for example after every push). Two options if this matters:
1. Enable paid persistent storage on the Space and set the `DATA_DIR` secret/variable to `/data`.
2. Run locally, where `data/` persists normally.

No extra infrastructure was added to work around this, as the assignment allows.

## How to use

1. Pick a notebook from the dropdown, or type a name and click **Create**.
2. Upload PDF/PPTX/TXT files and click **Add files**, or paste a URL and click **Add URL**.
3. In the **Chat** tab, ask a question. Answers cite sources as `[1]`, `[2]`. Open **Retrieved chunks** to see the exact text used. Switch **Retrieval method** to compare vector vs rerank.
4. In the **Artifacts** tab, click **Generate report** or **Generate quiz**. View it on the page and download the `.md`. Previous artifacts are in the **Saved artifacts** dropdown.
5. Rename or delete notebooks from the left panel.

## Deployment (Hugging Face Spaces + GitHub Actions)

1. Create a new **Gradio** Space on Hugging Face (CPU basic is enough).
2. In the Space settings, add a **secret** `LLM_API_KEY` (and `LLM_BASE_URL` / `LLM_MODEL` if not using Gemini).
3. Create a Hugging Face access token with **write** permission.
4. In the GitHub repo: **Settings > Secrets and variables > Actions**
   - Secret: `HF_TOKEN` = your write token
   - Variables: `HF_USERNAME` = your HF username, `HF_SPACE` = your Space name
5. Push to `main`. The workflow runs tests, then pushes the code to the Space, which rebuilds automatically.

Flow: `code change > git push > GitHub Actions (test, deploy) > HF Space rebuild > updated app`

## RAG evaluation

See [eval/results.md](eval/results.md). To rerun:

```bash
# put 2-3 docs in eval/docs/ and edit eval/questions.json
python -m eval.run_eval --judge
```
