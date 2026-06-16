import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import companies, earnings, health, query
from app.core.config import settings
from app.core.logging_config import configure_logging, logger
from app.core.metrics import REQUEST_COUNT, REQUEST_LATENCY


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("startup", app=settings.APP_NAME, version=settings.VERSION)
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Production RAG pipeline for financial earnings data across 50+ companies.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next) -> Response:
    t0 = time.perf_counter()
    response = await call_next(request)
    latency = time.perf_counter() - t0

    endpoint = request.url.path
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint, status_code=response.status_code
    ).inc()

    response.headers["X-Response-Time-Ms"] = str(round(latency * 1000, 2))
    return response


app.include_router(health.router, tags=["Observability"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies"])
app.include_router(earnings.router, prefix="/api/v1", tags=["Earnings"])
app.include_router(query.router, prefix="/api/v1", tags=["RAG"])
