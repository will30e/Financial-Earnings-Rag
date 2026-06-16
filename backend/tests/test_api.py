import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["companies_tracked"] == 57


def test_list_companies():
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 50


def test_get_company():
    response = client.get("/api/v1/companies/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["name"] == "Apple Inc."


def test_get_company_not_found():
    response = client.get("/api/v1/companies/FAKE")
    assert response.status_code == 404


def test_list_sectors():
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    sectors = response.json()
    assert "Technology" in sectors
    assert "Financials" in sectors


def test_get_earnings():
    response = client.get("/api/v1/earnings/MSFT")
    assert response.status_code == 200
    reports = response.json()
    assert len(reports) == 8


def test_get_latest_earnings():
    response = client.get("/api/v1/earnings?limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_trigger_ingestion():
    response = client.post("/api/v1/pipeline/ingest", json={"ticker": "AAPL"})
    assert response.status_code == 200
    job = response.json()
    assert "id" in job
    assert job["status"] in ["pending", "running"]
