# Optional: only needed if you deploy to Google Cloud Run / Render / Railway instead of HF Spaces.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    DATA_DIR=/app/data \
    HF_HOME=/app/.cache/huggingface

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Pre-download models into the image so cold starts are faster
RUN python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"

EXPOSE 8080
CMD ["python", "app.py"]
