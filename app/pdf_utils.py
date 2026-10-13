from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader


MAX_PDF_PAGES = 250


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    page_count: int


def extract_pdf_text(pdf_bytes: bytes) -> ExtractedDocument:
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("This file does not appear to be a valid PDF.")

    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError(f"PDFs are limited to {MAX_PDF_PAGES} pages.")

        page_text = [page.extract_text() or "" for page in reader.pages]
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("We couldn't read this PDF. It may be damaged or malformed.") from exc

    text = "\n\n".join(part.strip() for part in page_text if part.strip()).strip()
    if not text:
        raise ValueError("No readable text was found. Scanned PDFs need OCR before summarizing.")

    return ExtractedDocument(text=text, page_count=len(reader.pages))


def chunk_text(text: str, max_chars: int = 12_000, overlap: int = 500) -> list[str]:
    if max_chars <= 0 or overlap < 0 or overlap >= max_chars:
        raise ValueError("Chunk size must be positive and larger than the overlap.")

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            floor = start + int(max_chars * 0.65)
            boundaries = (
                text.rfind("\n\n", floor, end),
                text.rfind("\n", floor, end),
                text.rfind(". ", floor, end) + 1,
                text.rfind(" ", floor, end),
            )
            boundary = max(boundaries)
            if boundary > floor:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(start + 1, end - overlap)

    return chunks
