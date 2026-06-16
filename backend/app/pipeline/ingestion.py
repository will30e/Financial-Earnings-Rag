"""
Data ingestion pipeline — generates realistic earnings data for 50+ companies,
processes each report through chunking, embedding, and vector indexing.
"""
import asyncio
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.core.logging_config import logger
from app.core.metrics import (
    PIPELINE_LATENCY,
    PIPELINE_RECORDS_PROCESSED,
    REPORTS_INDEXED,
)
from app.models.schemas import IngestionJob, PipelineStatus
from app.pipeline.embeddings import embed_texts
from app.pipeline.indexer import delete_company_chunks, index_chunks
from app.pipeline.processor import build_document_text, chunk_text

COMPANIES = [
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financials"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
    {"ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples"},
    {"ticker": "MA", "name": "Mastercard Inc.", "sector": "Financials"},
    {"ticker": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "BAC", "name": "Bank of America Corp.", "sector": "Financials"},
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare"},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Technology"},
    {"ticker": "COST", "name": "Costco Wholesale Corp.", "sector": "Consumer Staples"},
    {"ticker": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Staples"},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples"},
    {"ticker": "TMO", "name": "Thermo Fisher Scientific", "sector": "Healthcare"},
    {"ticker": "CSCO", "name": "Cisco Systems Inc.", "sector": "Technology"},
    {"ticker": "ACN", "name": "Accenture plc", "sector": "Technology"},
    {"ticker": "MCD", "name": "McDonald's Corporation", "sector": "Consumer Discretionary"},
    {"ticker": "DHR", "name": "Danaher Corporation", "sector": "Healthcare"},
    {"ticker": "ABT", "name": "Abbott Laboratories", "sector": "Healthcare"},
    {"ticker": "DIS", "name": "The Walt Disney Company", "sector": "Communication Services"},
    {"ticker": "VZ", "name": "Verizon Communications", "sector": "Communication Services"},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Technology"},
    {"ticker": "CMCSA", "name": "Comcast Corporation", "sector": "Communication Services"},
    {"ticker": "NKE", "name": "NIKE Inc.", "sector": "Consumer Discretionary"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Technology"},
    {"ticker": "TXN", "name": "Texas Instruments Inc.", "sector": "Technology"},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials"},
    {"ticker": "LIN", "name": "Linde plc", "sector": "Materials"},
    {"ticker": "PM", "name": "Philip Morris International", "sector": "Consumer Staples"},
    {"ticker": "NEE", "name": "NextEra Energy Inc.", "sector": "Utilities"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "sector": "Technology"},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Technology"},
    {"ticker": "HON", "name": "Honeywell International", "sector": "Industrials"},
    {"ticker": "IBM", "name": "IBM Corporation", "sector": "Technology"},
    {"ticker": "GE", "name": "GE Aerospace", "sector": "Industrials"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials"},
    {"ticker": "UPS", "name": "United Parcel Service", "sector": "Industrials"},
    {"ticker": "RTX", "name": "RTX Corporation", "sector": "Industrials"},
    {"ticker": "GS", "name": "Goldman Sachs Group", "sector": "Financials"},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials"},
    {"ticker": "SPGI", "name": "S&P Global Inc.", "sector": "Financials"},
    {"ticker": "BLK", "name": "BlackRock Inc.", "sector": "Financials"},
    {"ticker": "AXP", "name": "American Express Company", "sector": "Financials"},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy"},
    {"ticker": "MRK", "name": "Merck & Co. Inc.", "sector": "Healthcare"},
    {"ticker": "BMY", "name": "Bristol Myers Squibb", "sector": "Healthcare"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Healthcare"},
    {"ticker": "AMGN", "name": "Amgen Inc.", "sector": "Healthcare"},
]

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

COMMENTARY_TEMPLATES = [
    (
        "We delivered exceptional results this quarter, with revenue growth surpassing our internal targets. "
        "Our core business segments continue to demonstrate strong demand dynamics, and we are seeing accelerating "
        "adoption across enterprise and consumer channels. Our focus on operational efficiency has driven meaningful "
        "margin expansion while we continue investing in high-ROI growth initiatives. We remain confident in our "
        "long-term strategy and are raising full-year guidance to reflect this momentum."
    ),
    (
        "This quarter's performance reflects the strength of our diversified business model. We saw robust growth "
        "in our cloud and services segments, which now represent an increasingly meaningful portion of total revenue. "
        "Supply chain improvements enabled us to meet elevated demand while protecting gross margins. Our balance "
        "sheet remains fortress-like, and we returned significant capital to shareholders through buybacks and dividends. "
        "Looking ahead, we see multiple tailwinds including AI integration, geographic expansion, and new product cycles."
    ),
    (
        "Results this quarter came in ahead of consensus on both the top and bottom line. Gross margins held firm "
        "despite an inflationary cost environment, a testament to our pricing power and procurement discipline. "
        "Our international segment showed particular strength, with double-digit growth in key markets. "
        "We are actively investing in R&D and M&A pipeline to sustain our competitive moat. Management is focused "
        "on disciplined capital allocation while pursuing profitable growth opportunities across all geographies."
    ),
    (
        "We are pleased to report another quarter of solid execution. Customer retention remains best-in-class, "
        "and net new customer additions exceeded plan. We are observing strong cross-sell and upsell momentum "
        "within our installed base, which supports durable recurring revenue. Integration of our recent acquisition "
        "is ahead of schedule, and synergy realization is tracking above the targets we laid out at deal close. "
        "We enter the next quarter with a healthy pipeline and high confidence in our outlook."
    ),
    (
        "Q results reflect headwinds from macro uncertainty and FX translation impacts, partially offset by "
        "continued strength in our premium product mix. We took deliberate steps to reduce inventory levels and "
        "right-size our cost structure, which positions us well for margin recovery as conditions normalize. "
        "Despite a challenging environment, we maintained market share and deepened relationships with our "
        "largest customers. Our technology investments are creating a widening gap versus competitors, and "
        "we believe we are well positioned to capitalize on an eventual demand recovery."
    ),
]

_active_jobs: Dict[str, IngestionJob] = {}


def get_job(job_id: str) -> Optional[IngestionJob]:
    return _active_jobs.get(job_id)


def list_jobs() -> List[IngestionJob]:
    return list(_active_jobs.values())


def _generate_report(company: dict, quarter: str, year: int) -> dict:
    rng = random.Random(f"{company['ticker']}-{quarter}-{year}")

    base_revenue = rng.uniform(5.0, 120.0)
    revenue_yoy = rng.uniform(-5.0, 35.0)
    revenue = base_revenue * (1 + revenue_yoy / 100)

    eps_base = rng.uniform(0.5, 12.0)
    eps_yoy = rng.uniform(-8.0, 40.0)
    eps = eps_base * (1 + eps_yoy / 100)

    net_income = revenue * rng.uniform(0.10, 0.35)
    ocf = net_income * rng.uniform(1.1, 1.5)
    beat = rng.random() > 0.25

    q_num = int(quarter[1])
    report_date = datetime(year, q_num * 3, rng.randint(15, 28))

    commentary = rng.choice(COMMENTARY_TEMPLATES)

    summary = (
        f"{company['name']} reported {quarter} {year} earnings with revenue of ${revenue:.2f}B, "
        f"representing {revenue_yoy:+.1f}% year-over-year growth. Diluted EPS came in at ${eps:.2f}, "
        f"{'beating' if beat else 'missing'} analyst consensus estimates. "
        f"Net income was ${net_income:.2f}B and operating cash flow reached ${ocf:.2f}B. "
        f"The company {'raised' if beat else 'maintained'} full-year guidance, projecting "
        f"${revenue * 1.04:.2f}B in revenue for the coming quarter."
    )

    return {
        "ticker": company["ticker"],
        "company_name": company["name"],
        "sector": company["sector"],
        "fiscal_quarter": quarter[1],
        "fiscal_year": year,
        "report_date": report_date.strftime("%Y-%m-%d"),
        "revenue": round(revenue, 2),
        "revenue_yoy": round(revenue_yoy, 2),
        "eps": round(eps, 2),
        "eps_yoy": round(eps_yoy, 2),
        "net_income": round(net_income, 2),
        "operating_cash_flow": round(ocf, 2),
        "guidance_revenue": round(revenue * 1.04, 2),
        "guidance_eps": round(eps * 1.05, 2),
        "beat_estimate": beat,
        "summary": summary,
        "management_commentary": commentary,
    }


async def run_ingestion_pipeline(
    ticker: Optional[str] = None,
) -> IngestionJob:
    job_id = str(uuid.uuid4())
    job = IngestionJob(
        id=job_id,
        status=PipelineStatus.PENDING,
        ticker=ticker,
        started_at=datetime.utcnow(),
    )
    _active_jobs[job_id] = job

    asyncio.create_task(_execute_pipeline(job_id, ticker))
    return job


async def _execute_pipeline(job_id: str, ticker: Optional[str]) -> None:
    job = _active_jobs[job_id]
    _active_jobs[job_id] = job.model_copy(update={"status": PipelineStatus.RUNNING})

    try:
        companies = [c for c in COMPANIES if c["ticker"] == ticker] if ticker else COMPANIES
        total_records = 0
        total_chunks = 0

        for company in companies:
            for year in [2023, 2024]:
                for quarter in QUARTERS:
                    t0 = time.perf_counter()
                    report = _generate_report(company, quarter, year)
                    doc_text = build_document_text(report)
                    chunks = chunk_text(doc_text)

                    embeddings = embed_texts(chunks)
                    metadatas = [
                        {
                            "ticker": company["ticker"],
                            "company_name": company["name"],
                            "sector": company["sector"],
                            "fiscal_quarter": quarter,
                            "fiscal_year": year,
                        }
                        for _ in chunks
                    ]
                    ids = [
                        f"{company['ticker']}-{quarter}-{year}-chunk{i}"
                        for i in range(len(chunks))
                    ]

                    index_chunks(chunks, embeddings, metadatas, ids)

                    elapsed = time.perf_counter() - t0
                    PIPELINE_LATENCY.observe(elapsed)
                    PIPELINE_RECORDS_PROCESSED.labels(company=company["ticker"]).inc()

                    total_records += 1
                    total_chunks += len(chunks)
                    await asyncio.sleep(0)

        REPORTS_INDEXED.set(total_chunks)
        _active_jobs[job_id] = _active_jobs[job_id].model_copy(
            update={
                "status": PipelineStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "records_processed": total_records,
                "chunks_indexed": total_chunks,
            }
        )
        logger.info("pipeline_completed", job_id=job_id, records=total_records, chunks=total_chunks)

    except Exception as exc:
        logger.error("pipeline_failed", job_id=job_id, error=str(exc))
        _active_jobs[job_id] = _active_jobs[job_id].model_copy(
            update={
                "status": PipelineStatus.FAILED,
                "completed_at": datetime.utcnow(),
                "error": str(exc),
            }
        )
