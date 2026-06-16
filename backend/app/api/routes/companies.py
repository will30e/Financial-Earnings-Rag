from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.pipeline.ingestion import COMPANIES

router = APIRouter()


@router.get("/companies")
async def list_companies(sector: Optional[str] = None) -> List[dict]:
    companies = COMPANIES
    if sector:
        companies = [c for c in companies if c["sector"].lower() == sector.lower()]
    return companies


@router.get("/companies/{ticker}")
async def get_company(ticker: str) -> dict:
    company = next((c for c in COMPANIES if c["ticker"].upper() == ticker.upper()), None)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")
    return company


@router.get("/sectors")
async def list_sectors() -> List[str]:
    return sorted(set(c["sector"] for c in COMPANIES))
