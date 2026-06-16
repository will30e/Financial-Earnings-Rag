from typing import List
from app.core.config import settings


def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP

    if len(text) <= size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += size - overlap

    return chunks


def build_document_text(report: dict) -> str:
    """Combine report fields into a single rich text document for indexing."""
    return (
        f"Company: {report['company_name']} ({report['ticker']})\n"
        f"Period: Q{report['fiscal_quarter']} {report['fiscal_year']}\n"
        f"Report Date: {report['report_date']}\n\n"
        f"Financial Results:\n"
        f"- Revenue: ${report['revenue']:.2f}B ({report['revenue_yoy']:+.1f}% YoY)\n"
        f"- EPS: ${report['eps']:.2f} ({report['eps_yoy']:+.1f}% YoY)\n"
        f"- Net Income: ${report['net_income']:.2f}B\n"
        f"- Operating Cash Flow: ${report['operating_cash_flow']:.2f}B\n"
        f"- Beat Estimates: {'Yes' if report['beat_estimate'] else 'No'}\n\n"
        f"Guidance:\n"
        f"- Revenue Guidance: ${report.get('guidance_revenue', 0):.2f}B\n"
        f"- EPS Guidance: ${report.get('guidance_eps', 0):.2f}\n\n"
        f"Summary:\n{report['summary']}\n\n"
        f"Management Commentary:\n{report['management_commentary']}"
    )
