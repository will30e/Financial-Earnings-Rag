from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
    registry=registry,
)

PIPELINE_RECORDS_PROCESSED = Counter(
    "pipeline_records_processed_total",
    "Total records ingested through the pipeline",
    ["company"],
    registry=registry,
)

PIPELINE_LATENCY = Histogram(
    "pipeline_processing_duration_seconds",
    "Time to process a single earnings report through the pipeline",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=registry,
)

RAG_QUERY_COUNT = Counter(
    "rag_queries_total",
    "Total RAG queries executed",
    ["status"],
    registry=registry,
)

RAG_QUERY_LATENCY = Histogram(
    "rag_query_duration_seconds",
    "End-to-end RAG query latency",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
    registry=registry,
)

RETRIEVAL_LATENCY = Histogram(
    "retrieval_duration_seconds",
    "Vector retrieval latency",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25],
    registry=registry,
)

COMPANIES_TRACKED = Gauge(
    "companies_tracked_total",
    "Number of companies tracked",
    registry=registry,
)

REPORTS_INDEXED = Gauge(
    "reports_indexed_total",
    "Total earnings reports indexed in vector store",
    registry=registry,
)
