from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_users_returns_list():
    response = client.get("/api/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 2


def test_create_user():
    response = client.post("/api/users", json={"name": "Test", "email": "test@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "Test"
    assert "id" in response.json()


def test_get_orders_returns_list():
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_metrics_endpoint_exposes_prometheus_format():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
