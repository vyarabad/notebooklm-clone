"""Gradio UI. This file only handles the interface; all logic lives in src/."""
import logging
import os

import gradio as gr

from src.config import DATA_DIR
from src.ingestion import IngestionError
from src.llm import LLMError
from src.retrieval import METHODS
from src.service import NotebookApp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

svc = NotebookApp()

USER_ERRORS = (ValueError, IngestionError, LLMError, FileNotFoundError)


def _fail(e: Exception):
    """Show a friendly error toast instead of a stack trace."""
    if isinstance(e, USER_ERRORS):
        raise gr.Error(str(e))
    log.exception("Unexpected error")
    raise gr.Error(f"Something went wrong: {e}")


def _require(nb_id):
    if not nb_id or not svc.storage.exists(nb_id):
        raise gr.Error("Create or select a notebook first.")


# ---------- view helpers ----------
def sources_markdown(nb_id):
    if not nb_id or not svc.storage.exists(nb_id):
        return "_No notebook selected._"
    sources = svc.list_sources(nb_id)
    if not sources:
        return "_No sources yet. Upload a file or add a URL._"
    lines = [f"- **{s['name']}** ({s['type'].upper()}, {s['chunks']} chunks)" for s in sources]
    return f"**{len(sources)} source(s)**\n\n" + "\n".join(lines)


def source_choices(nb_id):
    if not nb_id or not svc.storage.exists(nb_id):
        return []
    return [(s["name"], s["id"]) for s in svc.list_sources(nb_id)]


def chat_display(nb_id):
    if not nb_id or not svc.storage.exists(nb_id):
        return []
    return [{"role": m["role"], "content": m["content"]} for m in svc.chat_history(nb_id)]


def chunks_markdown(result):
    if not result.get("chunks"):
        return ""
    parts = [f"**Method:** `{result['method']}`  |  **Retrieval:** {result['retrieval_time']:.2f}s  |  "
             f"**Total:** {result['total_time']:.2f}s\n"]
    for i, c in enumerate(result["chunks"], start=1):
        m = c["metadata"]
        loc = f", {m['location']}" if m.get("location") else ""
        text = c["text"][:500].replace("\n", " ")
        parts.append(f"**[{i}] {m['source_name']}{loc}** (score {c['score']})\n\n> {text}...\n")
    return "\n".join(parts)


def load_notebook(nb_id):
    """Refresh everything on the page for the selected notebook."""
    arts = svc.storage.list_artifacts(nb_id) if nb_id and svc.storage.exists(nb_id) else []
    return (
        sources_markdown(nb_id),
        gr.update(choices=source_choices(nb_id), value=None),
        chat_display(nb_id),
        "",
        gr.update(choices=arts, value=None),
        "",
        None,
    )


# ---------- notebook handlers ----------
def on_init():
    notebooks = svc.notebooks.list()
    if not notebooks:
        svc.notebooks.create("My first notebook")
        notebooks = svc.notebooks.list()
    return gr.update(choices=notebooks, value=notebooks[0][1])


def on_create(name):
    try:
        nb_id = svc.notebooks.create(name)
    except Exception as e:
        _fail(e)
    gr.Info("Notebook created.")
    return gr.update(choices=svc.notebooks.list(), value=nb_id), ""


def on_rename(nb_id, new_name):
    _require(nb_id)
    try:
        svc.notebooks.rename(nb_id, new_name)
    except Exception as e:
        _fail(e)
    gr.Info("Notebook renamed.")
    return gr.update(choices=svc.notebooks.list(), value=nb_id), ""


def on_delete(nb_id):
    if not nb_id:  # user cancelled the confirm dialog
        return gr.update()
    _require(nb_id)
    try:
        svc.notebooks.delete(nb_id)
    except Exception as e:
        _fail(e)
    notebooks = svc.notebooks.list()
    gr.Info("Notebook deleted.")
    return gr.update(choices=notebooks, value=notebooks[0][1] if notebooks else None)


# ---------- source handlers ----------
def on_add_files(nb_id, files, progress=gr.Progress()):
    _require(nb_id)
    if not files:
        raise gr.Error("Choose at least one file to upload.")
    added, failed = [], []
    for f in progress.tqdm(files, desc="Ingesting"):
        path = f if isinstance(f, str) else f.name
        name = os.path.basename(path)
        try:
            src = svc.add_file(nb_id, path)
            added.append(f"{src['name']} ({src['chunks']} chunks)")
        except Exception as e:
            log.warning("Failed to ingest %s: %s", name, e)
            failed.append(f"{name}: {e}")
    if added:
        gr.Info("Added: " + ", ".join(added))
    for msg in failed:
        gr.Warning(msg)
    return sources_markdown(nb_id), gr.update(choices=source_choices(nb_id), value=None), None


def on_add_url(nb_id, url):
    _require(nb_id)
    try:
        src = svc.add_url(nb_id, url)
    except Exception as e:
        _fail(e)
    gr.Info(f"Added: {src['name']} ({src['chunks']} chunks)")
    return sources_markdown(nb_id), gr.update(choices=source_choices(nb_id), value=None), ""


def on_remove_source(nb_id, source_id):
    _require(nb_id)
    if not source_id:
        raise gr.Error("Pick a source to remove.")
    try:
        svc.remove_source(nb_id, source_id)
    except Exception as e:
        _fail(e)
    gr.Info("Source removed.")
    return sources_markdown(nb_id), gr.update(choices=source_choices(nb_id), value=None)


# ---------- chat handlers ----------
def on_ask(nb_id, question, method, k):
    _require(nb_id)
    try:
        result = svc.ask(nb_id, question, method, int(k))
    except Exception as e:
        _fail(e)
    return chat_display(nb_id), "", chunks_markdown(result)


def on_clear_chat(nb_id):
    _require(nb_id)
    svc.clear_chat(nb_id)
    return [], ""


# ---------- artifact handlers ----------
def _artifact_outputs(nb_id, content, path):
    return content, path, gr.update(choices=svc.storage.list_artifacts(nb_id),
                                    value=os.path.basename(path))


def on_report(nb_id):
    _require(nb_id)
    try:
        content, path = svc.artifacts.generate_report(nb_id)
    except Exception as e:
        _fail(e)
    gr.Info("Report generated.")
    return _artifact_outputs(nb_id, content, path)


def on_quiz(nb_id, n):
    _require(nb_id)
    try:
        content, path = svc.artifacts.generate_quiz(nb_id, int(n))
    except Exception as e:
        _fail(e)
    gr.Info("Quiz generated.")
    return _artifact_outputs(nb_id, content, path)


def on_view_artifact(nb_id, filename):
    if not nb_id or not filename:
        return "", None
    try:
        path = svc.storage.artifact_path(nb_id, filename)
    except Exception as e:
        _fail(e)
    return path.read_text(encoding="utf-8"), str(path)


# ---------- layout ----------
with gr.Blocks(title="NotebookLM Clone", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📓 NotebookLM Clone\nAdd sources to a notebook, chat with them, and generate study materials.")

    with gr.Row():
        # Left: notebooks + sources
        with gr.Column(scale=1, min_width=330):
            gr.Markdown("### Notebooks")
            nb_dd = gr.Dropdown(label="Current notebook", choices=[], interactive=True)
            with gr.Row():
                new_name = gr.Textbox(placeholder="New notebook name", show_label=False, scale=3)
                create_btn = gr.Button("Create", variant="primary", scale=1)
            with gr.Row():
                rename_box = gr.Textbox(placeholder="Rename current notebook", show_label=False, scale=3)
                rename_btn = gr.Button("Rename", scale=1)
            delete_btn = gr.Button("Delete notebook", variant="stop", size="sm")

            gr.Markdown("### Sources")
            file_upload = gr.File(label="Upload PDF, PPTX, or TXT", file_count="multiple",
                                  file_types=[".pdf", ".pptx", ".txt"])
            add_files_btn = gr.Button("Add files", variant="primary")
            with gr.Row():
                url_box = gr.Textbox(placeholder="https://example.com/article", show_label=False, scale=3)
                add_url_btn = gr.Button("Add URL", scale=1)
            sources_md = gr.Markdown()
            with gr.Row():
                source_dd = gr.Dropdown(label="Remove a source", choices=[], scale=3)
                remove_btn = gr.Button("Remove", scale=1)

        # Right: chat + artifacts
        with gr.Column(scale=2):
            with gr.Tab("Chat"):
                chatbot = gr.Chatbot(type="messages", height=460, show_copy_button=True,
                                     label="Chat (answers cite your sources)")
                with gr.Row():
                    question = gr.Textbox(placeholder="Ask a question about your sources...",
                                          show_label=False, scale=5)
                    ask_btn = gr.Button("Send", variant="primary", scale=1)
                with gr.Row():
                    method = gr.Radio(METHODS, value="rerank", label="Retrieval method")
                    top_k = gr.Slider(2, 10, value=5, step=1, label="Chunks to retrieve")
                with gr.Accordion("Retrieved chunks for the last answer", open=False):
                    chunks_md = gr.Markdown()
                clear_btn = gr.Button("Clear chat history", size="sm")

            with gr.Tab("Artifacts"):
                with gr.Row():
                    report_btn = gr.Button("Generate report", variant="primary")
                    quiz_btn = gr.Button("Generate quiz", variant="primary")
                    n_questions = gr.Slider(3, 20, value=8, step=1, label="Quiz questions")
                artifact_dd = gr.Dropdown(label="Saved artifacts (select to view)", choices=[])
                artifact_file = gr.File(label="Download .md", interactive=False)
                artifact_md = gr.Markdown()

    page_outputs = [sources_md, source_dd, chatbot, chunks_md, artifact_dd, artifact_md, artifact_file]

    demo.load(on_init, outputs=nb_dd)
    nb_dd.change(load_notebook, nb_dd, page_outputs)

    create_btn.click(on_create, new_name, [nb_dd, new_name])
    new_name.submit(on_create, new_name, [nb_dd, new_name])
    rename_btn.click(on_rename, [nb_dd, rename_box], [nb_dd, rename_box])
    delete_btn.click(on_delete, nb_dd, nb_dd, js="(id) => confirm('Delete this notebook and all its data?') ? id : null")

    add_files_btn.click(on_add_files, [nb_dd, file_upload], [sources_md, source_dd, file_upload])
    add_url_btn.click(on_add_url, [nb_dd, url_box], [sources_md, source_dd, url_box])
    url_box.submit(on_add_url, [nb_dd, url_box], [sources_md, source_dd, url_box])
    remove_btn.click(on_remove_source, [nb_dd, source_dd], [sources_md, source_dd])

    ask_btn.click(on_ask, [nb_dd, question, method, top_k], [chatbot, question, chunks_md])
    question.submit(on_ask, [nb_dd, question, method, top_k], [chatbot, question, chunks_md])
    clear_btn.click(on_clear_chat, nb_dd, [chatbot, chunks_md])

    report_btn.click(on_report, nb_dd, [artifact_md, artifact_file, artifact_dd])
    quiz_btn.click(on_quiz, [nb_dd, n_questions], [artifact_md, artifact_file, artifact_dd])
    artifact_dd.input(on_view_artifact, [nb_dd, artifact_dd], [artifact_md, artifact_file])


if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        allowed_paths=[str(DATA_DIR)],
    )
