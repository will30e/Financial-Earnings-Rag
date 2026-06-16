import time
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.logging_config import logger


def _build_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['company_name']} ({chunk['ticker']}) "
            f"Q{chunk['fiscal_quarter']} {chunk['fiscal_year']}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    return (
        "You are a financial analyst assistant specializing in earnings analysis. "
        "Answer the question below using ONLY the provided earnings report context. "
        "Be precise with numbers and cite the source company and period.\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {query}\n\n"
        "ANSWER:"
    )


def _mock_generate(query: str, chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return (
            "No relevant earnings data found for your query. "
            "Try running the ingestion pipeline first or broadening your search."
        )

    best = chunks[0]
    companies_mentioned = list({c["company_name"] for c in chunks[:3]})
    company_str = ", ".join(companies_mentioned)

    return (
        f"Based on the available earnings reports for {company_str}, here is what I found:\n\n"
        f"{best['text'][:400]}...\n\n"
        f"The data shows relevant financial information across {len(chunks)} source segments. "
        f"The most relevant result comes from {best['company_name']} ({best['ticker']}) "
        f"Q{best['fiscal_quarter']} {best['fiscal_year']} with a relevance score of "
        f"{best['relevance_score']:.2%}.\n\n"
        f"Note: For production-grade analysis, configure OPENAI_API_KEY to enable full LLM generation."
    )


def generate_answer(query: str, chunks: List[Dict[str, Any]]) -> Tuple[str, float]:
    t0 = time.perf_counter()

    use_mock = settings.USE_MOCK_LLM or not settings.OPENAI_API_KEY

    if use_mock:
        answer = _mock_generate(query, chunks)
    else:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            prompt = _build_prompt(query, chunks)
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=800,
            )
            answer = response.choices[0].message.content or ""
        except Exception as exc:
            logger.warning("llm_generation_failed", error=str(exc))
            answer = _mock_generate(query, chunks)

    generation_latency_ms = (time.perf_counter() - t0) * 1000
    return answer, generation_latency_ms
