from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CompanyBase(BaseModel):
    ticker: str
    name: str
    sector: str
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EarningsReportBase(BaseModel):
    company_id: int
    fiscal_quarter: str
    fiscal_year: int
    report_date: datetime
    revenue: float
    revenue_yoy: float
    eps: float
    eps_yoy: float
    net_income: float
    operating_cash_flow: float
    guidance_revenue: Optional[float] = None
    guidance_eps: Optional[float] = None
    summary: str
    management_commentary: str
    beat_estimate: bool


class EarningsReportCreate(EarningsReportBase):
    pass


class EarningsReport(EarningsReportBase):
    id: int
    created_at: datetime
    company: Optional[Company] = None

    model_config = {"from_attributes": True}


class IngestionJobBase(BaseModel):
    ticker: Optional[str] = None


class IngestionJob(BaseModel):
    id: str
    status: PipelineStatus
    ticker: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    chunks_indexed: int = 0
    error: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000)
    ticker: Optional[str] = None
    fiscal_year: Optional[int] = None
    top_k: int = Field(default=5, ge=1, le=20)


class SourceChunk(BaseModel):
    ticker: str
    company_name: str
    fiscal_quarter: str
    fiscal_year: int
    text: str
    relevance_score: float


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceChunk]
    latency_ms: float
    retrieval_latency_ms: float
    generation_latency_ms: float


class HealthStatus(BaseModel):
    status: str
    version: str
    database: str
    vector_store: str
    companies_tracked: int
    reports_indexed: int
    uptime_seconds: float


class MetricsSnapshot(BaseModel):
    total_requests: int
    avg_request_latency_ms: float
    total_rag_queries: int
    avg_rag_latency_ms: float
    pipeline_records_processed: int
    companies_tracked: int
    reports_indexed: int
