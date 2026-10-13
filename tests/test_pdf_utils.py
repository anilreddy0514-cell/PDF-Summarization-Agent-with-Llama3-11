import pytest

from app.pdf_utils import chunk_text, extract_pdf_text


def test_chunk_text_respects_size_and_overlaps():
    text = "A sentence. " * 100
    chunks = chunk_text(text, max_chars=120, overlap=20)

    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)
    assert all(left[-20:] == right[:20] for left, right in zip(chunks, chunks[1:]))


def test_chunk_text_handles_empty_input():
    assert chunk_text(" \n ") == []


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError, match="larger than the overlap"):
        chunk_text("text", max_chars=10, overlap=10)


def test_extract_pdf_text_rejects_non_pdf_bytes():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf_text(b"not a PDF")
