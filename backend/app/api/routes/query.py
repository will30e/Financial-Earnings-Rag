from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import List

from app.models.schemas import (
    IngestionJob,
    IngestionJobBase,
    QueryRequest,
    QueryResponse,
)
from app.pipeline.ingestion import get_job, list_jobs, run_ingestion_pipeline
from app.rag.chain import run_rag_query

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def rag_query(request: QueryRequest) -> QueryResponse:
    try:
        return run_rag_query(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/pipeline/ingest", response_model=IngestionJob)
async def trigger_ingestion(body: IngestionJobBase) -> IngestionJob:
    job = await run_ingestion_pipeline(ticker=body.ticker)
    return job


@router.get("/pipeline/jobs", response_model=List[IngestionJob])
async def get_jobs() -> List[IngestionJob]:
    return list_jobs()


@router.get("/pipeline/jobs/{job_id}", response_model=IngestionJob)
async def get_job_status(job_id: str) -> IngestionJob:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
