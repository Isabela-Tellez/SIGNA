from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_triage_endpoint_returns_valid_result():
    """El endpoint debe procesar correctamente una incidencia válida."""

    response = client.post(
        "/triage",
        json={
            "text": "El cliente no tiene conexión a internet",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "incident" in data
    assert "local_result" in data
    assert "cloud_result" in data
    assert "comparison" in data
    assert "decision" in data
    assert "processed_at" in data

    assert data["incident"]["text"] == (
        "El cliente no tiene conexión a internet"
    )

    assert data["local_result"]["status"] == "success"
    assert data["cloud_result"]["status"] == "success"

    assert data["comparison"]["models_agree"] is True

    assert data["decision"]["decision"] == "automatic"