# Folio PDF Summarizer

A local PDF summarization app built with FastAPI, pypdf, and Ollama. PDF text is extracted and sent to a locally running Llama 3.1 model; uploaded documents are not sent to a hosted LLM service.

## Run locally

Requirements: Python 3.10+ and [Ollama](https://ollama.com/) installed.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
ollama pull llama3.1:8b
ollama serve
```

In a second terminal, from the project directory:

```sh
source .venv/bin/activate
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Adjust `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT_SECONDS`, or `MAX_UPLOAD_MB` in `.env` as needed. The default model is `llama3.1:8b`.

## Tests

```sh
pytest
```

## Behavior and limits

- Accepts `.pdf` uploads up to 20 MB by default and 250 pages.
- Extracts embedded text; image-only/scanned PDFs require OCR and are reported clearly.
- Splits text into overlapping character-bounded segments, summarizes each, then combines summaries for long documents.
- Ollama must be reachable from the FastAPI process and the configured model must already be pulled.

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for architecture, request flow, error handling, and extension points.
