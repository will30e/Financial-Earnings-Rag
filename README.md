# EarningsRAG — Financial Intelligence Platform

A production-grade Retrieval-Augmented Generation (RAG) pipeline for querying financial earnings data across 57 S&P 500 large-cap companies using semantic search and LLM generation.

## Features

- **Semantic Search** — ChromaDB vector store with `all-MiniLM-L6-v2` embeddings for contextual retrieval across 1,368+ indexed chunks
- **LLM Generation** — OpenAI GPT-4o-mini generates structured answers from retrieved earnings context (mock mode available with no API key)
- **Earnings Pipeline** — Ingests and chunks earnings reports across 57 companies, tracking revenue, EPS, net income, beat/miss estimates, and forward guidance
- **React Dashboard** — Real-time pipeline dashboard with sector performance charts, job tracking, and a RAG query interface
- **REST API** — FastAPI backend with versioned endpoints for companies, earnings, and query
- **Observability** — Prometheus metrics, structured logging via `structlog`, and per-request latency headers
- **Deployable** — Docker Compose for local, Kubernetes manifests for production, CircleCI for CI/CD

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.11, SQLAlchemy, aiosqlite |
| Vector Store | ChromaDB |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | OpenAI GPT-4o-mini |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Database | SQLite (local) / PostgreSQL (prod) |
| Infrastructure | Docker, Kubernetes, CircleCI |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key (optional — runs in mock mode without one)

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set OPENAI_API_KEY to enable LLM generation
# Leave USE_MOCK_LLM=true to run without an API key

./run.sh
