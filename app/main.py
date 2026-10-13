import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ollama import OllamaServiceError, summarize_document
from app.pdf_utils import extract_pdf_text


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024

app = FastAPI(title="Folio PDF Summarizer")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/summarize")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Choose a PDF file to continue.")

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"This PDF is too large. The limit is {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    try:
        document = extract_pdf_text(contents)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        summary = await summarize_document(document.text)
    except OllamaServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "summary": summary,
        "filename": Path(file.filename).name,
        "page_count": document.page_count,
        "character_count": len(document.text),
    }
