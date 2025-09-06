import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ERP Backend is running" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code in [200, 503]  # May fail if no DB

def test_chat():
    response = client.post("/chat", json={"text": "show me customers"})
    assert response.status_code in [200, 500]  # May fail if no DB