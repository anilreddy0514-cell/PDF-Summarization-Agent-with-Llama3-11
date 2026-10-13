from fastapi.testclient import TestClient

from app import main
from app.ollama import OllamaServiceError
from app.pdf_utils import ExtractedDocument


client = TestClient(main.app)


def test_home_page_renders_upload_interface():
    response = client.get("/")

    assert response.status_code == 200
    assert "Drop your PDF here" in response.text


def test_upload_rejects_non_pdf_filename():
    response = client.post("/api/summarize", files={"file": ("notes.txt", b"text")})

    assert response.status_code == 400
    assert response.json()["detail"] == "Choose a PDF file to continue."


def test_upload_returns_summary_and_document_metadata(monkeypatch):
    async def fake_summary(text):
        assert text == "Extracted document text"
        return "A concise summary."

    monkeypatch.setattr(
        main,
        "extract_pdf_text",
        lambda contents: ExtractedDocument(text="Extracted document text", page_count=3),
    )
    monkeypatch.setattr(main, "summarize_document", fake_summary)
    response = client.post(
        "/api/summarize",
        files={"file": ("report.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "summary": "A concise summary.",
        "filename": "report.pdf",
        "page_count": 3,
        "character_count": len("Extracted document text"),
    }


def test_upload_returns_service_unavailable_for_ollama_errors(monkeypatch):
    async def failed_summary(text):
        raise OllamaServiceError("Couldn't connect to Ollama.")

    monkeypatch.setattr(
        main,
        "extract_pdf_text",
        lambda contents: ExtractedDocument(text="Extracted document text", page_count=1),
    )
    monkeypatch.setattr(main, "summarize_document", failed_summary)
    response = client.post(
        "/api/summarize",
        files={"file": ("report.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Couldn't connect to Ollama."
