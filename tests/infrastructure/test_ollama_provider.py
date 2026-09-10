import json

from infrastructure.ollama_provider import OllamaProvider

from domain.enums import (
    Category,
    Department,
    ModelStatus,
    Provider,
    Urgency,
)

from domain.schemas import Incident


class FakeResponse:
    """Respuesta simulada de Ollama."""

    def raise_for_status(self):
        """Simula una respuesta HTTP correcta."""

    def json(self):
        """Devuelve una respuesta simulada del modelo."""

        return {
            "response": json.dumps(
                {
                    "category": "connectivity",
                    "urgency": "medium",
                    "department": "technical_support",
                    "summary": (
                        "Cliente sin conexión requiere revisión técnica del servicio de internet"
                    ),
                    "explanation": (
                        "La incidencia describe una pérdida de conectividad a internet."
                    ),
                    "confidence": 0.95,
                }
            ),
            "prompt_eval_count": 50,
            "eval_count": 50,
        }


def test_ollama_provider_returns_valid_result(monkeypatch):
    """OllamaProvider debe convertir la respuesta en ModelResult."""

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "infrastructure.ollama_provider.requests.post",
        fake_post,
    )

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    provider = OllamaProvider()

    result = provider.analyze(incident)

    assert result.provider == Provider.LOCAL
    assert result.model == "llama3.2:3b"
    assert result.status == ModelStatus.SUCCESS
    assert result.error is None

    assert result.classification is not None

    assert result.classification.category == Category.CONNECTIVITY
    assert result.classification.urgency == Urgency.MEDIUM
    assert (
        result.classification.department
        == Department.TECHNICAL_SUPPORT
    )

    assert result.classification.confidence == 0.95

    assert result.metrics.input_tokens == 50
    assert result.metrics.output_tokens == 50
    assert result.metrics.total_tokens == 100


def test_ollama_provider_handles_connection_error(monkeypatch):
    """OllamaProvider debe manejar errores de conexión."""

    def fake_post(*args, **kwargs):
        raise ConnectionError("Ollama no está disponible")

    monkeypatch.setattr(
        "infrastructure.ollama_provider.requests.post",
        fake_post,
    )

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    provider = OllamaProvider()

    result = provider.analyze(incident)

    assert result.provider == Provider.LOCAL
    assert result.model == "llama3.2:3b"
    assert result.status == ModelStatus.ERROR
    assert result.classification is None
    assert result.error == "Ollama no está disponible"