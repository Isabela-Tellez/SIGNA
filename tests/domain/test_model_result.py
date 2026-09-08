import pytest

from domain.enums import (
    Category,
    Department,
    ModelStatus,
    Provider,
    Urgency,
)
from domain.schemas import Classification, ModelMetrics, ModelResult


def create_valid_classification() -> Classification:
    """Crea una clasificación válida para reutilizar en los tests."""
    return Classification(
        category=Category.CONNECTIVITY,
        urgency=Urgency.HIGH,
        department=Department.TECHNICAL_SUPPORT,
        summary="Cliente reporta pérdida total de conexión a internet doméstica hoy",
        explanation="La incidencia indica una pérdida de conectividad.",
        confidence=0.90,
    )


def create_valid_metrics() -> ModelMetrics:
    """Crea unas métricas válidas para reutilizar en los tests."""
    return ModelMetrics(
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        latency_ms=250.5,
        cost=0.002,
        retries=0,
    )


def test_model_result_success_with_classification():
    """Un resultado SUCCESS debe incluir una clasificación."""
    result = ModelResult(
        provider=Provider.LOCAL,
        model="test-model",
        classification=create_valid_classification(),
        metrics=create_valid_metrics(),
        status=ModelStatus.SUCCESS,
    )

    assert result.provider == Provider.LOCAL
    assert result.model == "test-model"
    assert result.classification is not None
    assert result.metrics.total_tokens == 150
    assert result.status == ModelStatus.SUCCESS
    assert result.error is None


def test_model_result_success_without_classification_is_invalid():
    """Un resultado SUCCESS sin clasificación debe rechazarse."""
    with pytest.raises(ValueError):
        ModelResult(
            provider=Provider.LOCAL,
            model="test-model",
            classification=None,
            metrics=create_valid_metrics(),
            status=ModelStatus.SUCCESS,
        )


def test_model_result_success_with_error_is_invalid():
    """Un resultado SUCCESS no puede contener un error."""
    with pytest.raises(ValueError):
        ModelResult(
            provider=Provider.LOCAL,
            model="test-model",
            classification=create_valid_classification(),
            metrics=create_valid_metrics(),
            status=ModelStatus.SUCCESS,
            error="Something went wrong",
        )


def test_model_result_failed_without_error_is_invalid():
    """Un resultado fallido debe incluir un mensaje de error."""
    with pytest.raises(ValueError):
        ModelResult(
            provider=Provider.LOCAL,
            model="test-model",
            classification=None,
            metrics=create_valid_metrics(),
            status=ModelStatus.ERROR,
        )


def test_model_result_failed_with_error_is_valid():
    """Un resultado fallido con error debe ser válido."""
    result = ModelResult(
        provider=Provider.CLOUD,
        model="test-model",
        classification=None,
        metrics=create_valid_metrics(),
        status=ModelStatus.ERROR,
        error="Model request failed",
    )

    assert result.status == ModelStatus.ERROR
    assert result.classification is None
    assert result.error == "Model request failed"


def test_model_metrics_reject_negative_input_tokens():
    """Los tokens de entrada no pueden ser negativos."""
    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=-1,
            output_tokens=50,
            total_tokens=150,
            latency_ms=250.5,
            cost=0.002,
            retries=0,
        )


def test_model_metrics_reject_negative_output_tokens():
    """Los tokens de salida no pueden ser negativos."""
    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=100,
            output_tokens=-1,
            total_tokens=150,
            latency_ms=250.5,
            cost=0.002,
            retries=0,
        )


def test_model_metrics_reject_negative_latency():
    """La latencia no puede ser negativa."""
    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            latency_ms=-1,
            cost=0.002,
            retries=0,
        )


def test_model_metrics_reject_negative_cost():
    """El coste no puede ser negativo."""
    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            latency_ms=250.5,
            cost=-0.001,
            retries=0,
        )


def test_model_metrics_reject_negative_retries():
    """Los reintentos no pueden ser negativos."""
    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            latency_ms=250.5,
            cost=0.002,
            retries=-1,
        )

def test_model_metrics_reject_incorrect_total_tokens():
    """El total de tokens debe coincidir con entrada más salida."""

    with pytest.raises(ValueError):
        ModelMetrics(
            input_tokens=100,
            output_tokens=50,
            total_tokens=999,
            latency_ms=250.5,
            cost=0.002,
            retries=0,
        )