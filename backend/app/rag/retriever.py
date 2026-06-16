import time
from typing import Any, Dict, List, Optional, Tuple

from app.core.metrics import RETRIEVAL_LATENCY
from app.pipeline.embeddings import embed_query
from app.pipeline.indexer import query_collection


def retrieve(
    query: str,
    ticker: Optional[str] = None,
    fiscal_year: Optional[int] = None,
    top_k: int = 5,
) -> Tuple[List[Dict[str, Any]], float]:
    t0 = time.perf_counter()
    query_vec = embed_query(query)

    where: Optional[Dict[str, Any]] = None
    filters = {}
    if ticker:
        filters["ticker"] = ticker
    if fiscal_year:
        filters["fiscal_year"] = fiscal_year

    if len(filters) == 1:
        key, val = next(iter(filters.items()))
        where = {key: {"$eq": val}}
    elif len(filters) == 2:
        where = {"$and": [{k: {"$eq": v}} for k, v in filters.items()]}

    results = query_collection(query_vec, n_results=top_k, where=where)

    latency_ms = (time.perf_counter() - t0) * 1000
    RETRIEVAL_LATENCY.observe(latency_ms / 1000)

    chunks = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunks.append(
                {
                    "text": doc,
                    "ticker": meta.get("ticker", ""),
                    "company_name": meta.get("company_name", ""),
                    "fiscal_quarter": meta.get("fiscal_quarter", ""),
                    "fiscal_year": meta.get("fiscal_year", 0),
                    "relevance_score": round(1 - dist, 4),
                }
            )

    return chunks, latency_ms
