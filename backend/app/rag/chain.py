import time
from typing import Optional

from app.core.metrics import RAG_QUERY_COUNT, RAG_QUERY_LATENCY
from app.models.schemas import QueryRequest, QueryResponse, SourceChunk
from app.rag.generator import generate_answer
from app.rag.retriever import retrieve


def run_rag_query(request: QueryRequest) -> QueryResponse:
    t0 = time.perf_counter()

    try:
        chunks, retrieval_latency_ms = retrieve(
            query=request.query,
            ticker=request.ticker,
            fiscal_year=request.fiscal_year,
            top_k=request.top_k,
        )

        answer, generation_latency_ms = generate_answer(request.query, chunks)

        total_latency_ms = (time.perf_counter() - t0) * 1000
        RAG_QUERY_LATENCY.observe(total_latency_ms / 1000)
        RAG_QUERY_COUNT.labels(status="success").inc()

        sources = [
            SourceChunk(
                ticker=c["ticker"],
                company_name=c["company_name"],
                fiscal_quarter=c["fiscal_quarter"],
                fiscal_year=c["fiscal_year"],
                text=c["text"][:300],
                relevance_score=c["relevance_score"],
            )
            for c in chunks
        ]

        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            latency_ms=round(total_latency_ms, 2),
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            generation_latency_ms=round(generation_latency_ms, 2),
        )

    except Exception as exc:
        RAG_QUERY_COUNT.labels(status="error").inc()
        raise
