from app import create_app


def test_health_endpoint_returns_service_status():
    app = create_app({"TESTING": True})
    response = app.test_client().get("/api/v1/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "ai-finance-assistant-api",
    }
