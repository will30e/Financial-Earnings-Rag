from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.pipeline.ingestion import COMPANIES, _generate_report, QUARTERS

router = APIRouter()


@router.get("/earnings/{ticker}")
async def get_company_earnings(
    ticker: str,
    year: Optional[int] = None,
    quarter: Optional[str] = None,
) -> List[dict]:
    company = next((c for c in COMPANIES if c["ticker"].upper() == ticker.upper()), None)
    if not company:
        raise HTTPException(status_code=404, detail=f"Company '{ticker}' not found")

    years = [year] if year else [2023, 2024]
    quarters = [quarter.upper()] if quarter else QUARTERS

    reports = []
    for y in years:
        for q in quarters:
            reports.append(_generate_report(company, q, y))

    return sorted(reports, key=lambda r: (r["fiscal_year"], r["fiscal_quarter"]), reverse=True)


@router.get("/earnings")
async def get_latest_earnings(
    limit: int = Query(default=20, ge=1, le=100),
    sector: Optional[str] = None,
) -> List[dict]:
    companies = COMPANIES
    if sector:
        companies = [c for c in companies if c["sector"].lower() == sector.lower()]

    reports = []
    for company in companies[:limit]:
        report = _generate_report(company, "Q4", 2024)
        reports.append(report)

    return reports
