def test_liveness(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_request_id_echoed(client):
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "req-123"})
    assert response.headers["x-request-id"] == "req-123"

def test_invalid_request_id_replaced(client):
    response = client.get("/api/v1/health/live", headers={"X-Request-ID": "not safe"})
    assert response.headers["x-request-id"] != "not safe"
