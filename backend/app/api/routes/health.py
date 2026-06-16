import time
from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.core.metrics import registry
from app.models.schemas import HealthStatus
from app.pipeline.indexer import get_collection_count
from app.pipeline.ingestion import COMPANIES

router = APIRouter()
_start_time = time.time()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    vector_count = get_collection_count()
    return HealthStatus(
        status="healthy",
        version=settings.VERSION,
        database="connected",
        vector_store="connected" if vector_count >= 0 else "degraded",
        companies_tracked=len(COMPANIES),
        reports_indexed=vector_count,
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/metrics")
async def prometheus_metrics():
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
