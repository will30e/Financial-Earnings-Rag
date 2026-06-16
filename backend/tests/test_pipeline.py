import pytest
from app.pipeline.processor import chunk_text, build_document_text
from app.pipeline.ingestion import _generate_report, COMPANIES


def test_chunk_text_short():
    text = "short text"
    chunks = chunk_text(text)
    assert chunks == ["short text"]


def test_chunk_text_long():
    text = "word " * 300
    chunks = chunk_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 600


def test_generate_report_deterministic():
    company = COMPANIES[0]
    r1 = _generate_report(company, "Q4", 2024)
    r2 = _generate_report(company, "Q4", 2024)
    assert r1["revenue"] == r2["revenue"]
    assert r1["eps"] == r2["eps"]


def test_generate_report_fields():
    company = COMPANIES[0]
    report = _generate_report(company, "Q1", 2024)
    assert report["ticker"] == company["ticker"]
    assert report["fiscal_quarter"] == "1"
    assert report["fiscal_year"] == 2024
    assert report["revenue"] > 0
    assert report["eps"] > 0
    assert isinstance(report["beat_estimate"], bool)


def test_build_document_text():
    company = COMPANIES[0]
    report = _generate_report(company, "Q2", 2024)
    text = build_document_text(report)
    assert company["ticker"] in text
    assert "Revenue" in text
    assert "EPS" in text
