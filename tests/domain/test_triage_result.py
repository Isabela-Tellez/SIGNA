from datetime import datetime, timezone

import pytest

from domain.enums import (
    Category, Department, Decision, DecisionReason, ModelStatus,
    Provider, RiskLevel, Urgency,
)
from domain.schemas import (
    Classification, Comparison, HumanReview, ModelMetrics,
    ModelResult, SignaDecision, TriageResult,
)
from domain.enums import ReviewStatus
from domain.schemas import Incident


def create_valid_incident() -> Incident:
    """Crea un incidente válido para los tests."""
    return Incident(
        text="Cliente sin conexión a internet",
    )


def create_valid_classification() -> Classification:
    """Crea una clasificación válida para los tests."""
    return Classification(
        category=Category.CONNECTIVITY,
        urgency=Urgency.HIGH,
        department=Department.TECHNICAL_SUPPORT,
        summary="Cliente reporta pérdida total de conexión a internet doméstica hoy",
        explanation="La incidencia indica una pérdida de conectividad.",
        confidence=0.90,
    )


def create_valid_model_result() -> ModelResult:
    """Crea un resultado de modelo válido."""
    classification = create_valid_classification()

    metrics = ModelMetrics(
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        latency_ms=250.0,
        cost=0.01,
        retries=0,
    )

    return ModelResult(
        provider=Provider.LOCAL,
        model="test-model",
        classification=classification,
        metrics=metrics,
        status=ModelStatus.SUCCESS,
    )


def create_valid_comparison() -> Comparison:
    """Crea una comparación válida."""
    return Comparison(
        comparable=True,
        category_agrees=True,
        urgency_agrees=True,
        department_agrees=True,
        models_agree=True,
    )


def create_automatic_decision() -> SignaDecision:
    """Crea una decisión automática válida."""
    return SignaDecision(
        decision=Decision.AUTOMATIC,
        risk=RiskLevel.LOW,
        reason=DecisionReason.MODELS_AGREE,
        confidence_threshold=0.75,
    )


def create_human_review_decision() -> SignaDecision:
    """Crea una decisión que requiere revisión humana."""
    return SignaDecision(
        decision=Decision.HUMAN_REVIEW,
        risk=RiskLevel.HIGH,
        reason=DecisionReason.MODEL_DISAGREEMENT,
        confidence_threshold=0.75,
    )


def create_completed_human_review() -> HumanReview:
    """Crea una revisión humana completada."""
    return HumanReview(
        status=ReviewStatus.ACCEPTED,
        final_classification=create_valid_classification(),
        reviewed_at=datetime.now(timezone.utc),
    )


def test_triage_result_automatic_creates_successfully():
    """Un triaje automático válido debe crearse correctamente."""
    incident = create_valid_incident()
    local_result = create_valid_model_result()
    cloud_result = create_valid_model_result()
    comparison = create_valid_comparison()
    decision = create_automatic_decision()

    result = TriageResult(
        incident=incident,
        local_result=local_result,
        cloud_result=cloud_result,
        comparison=comparison,
        decision=decision,
    )

    assert result.incident == incident
    assert result.local_result == local_result
    assert result.cloud_result == cloud_result
    assert result.comparison == comparison
    assert result.decision == decision
    assert result.human_review is None


def test_triage_result_human_review_creates_successfully():
    """Un triaje con revisión humana debe crearse correctamente."""
    incident = create_valid_incident()
    local_result = create_valid_model_result()
    cloud_result = create_valid_model_result()
    comparison = create_valid_comparison()
    decision = create_human_review_decision()
    human_review = create_completed_human_review()

    result = TriageResult(
        incident=incident,
        local_result=local_result,
        cloud_result=cloud_result,
        comparison=comparison,
        decision=decision,
        human_review=human_review,
    )

    assert result.decision.decision == Decision.HUMAN_REVIEW
    assert result.human_review == human_review


def test_triage_result_generates_id_automatically():
    """El identificador debe generarse automáticamente."""
    result = TriageResult(
        incident=create_valid_incident(),
        local_result=create_valid_model_result(),
        cloud_result=create_valid_model_result(),
        comparison=create_valid_comparison(),
        decision=create_automatic_decision(),
    )

    assert result.id is not None


def test_triage_result_generates_processed_at_automatically():
    """La fecha de procesamiento debe generarse automáticamente."""
    result = TriageResult(
        incident=create_valid_incident(),
        local_result=create_valid_model_result(),
        cloud_result=create_valid_model_result(),
        comparison=create_valid_comparison(),
        decision=create_automatic_decision(),
    )

    assert result.processed_at is not None
    assert result.processed_at.tzinfo is not None


def test_automatic_decision_rejects_human_review():
    """Una decisión automática no puede contener revisión humana."""
    with pytest.raises(ValueError):
        TriageResult(
            incident=create_valid_incident(),
            local_result=create_valid_model_result(),
            cloud_result=create_valid_model_result(),
            comparison=create_valid_comparison(),
            decision=create_automatic_decision(),
            human_review=create_completed_human_review(),
        )


def test_human_review_decision_requires_human_review():
    """Una decisión de revisión humana requiere una revisión."""
    with pytest.raises(ValueError):
        TriageResult(
            incident=create_valid_incident(),
            local_result=create_valid_model_result(),
            cloud_result=create_valid_model_result(),
            comparison=create_valid_comparison(),
            decision=create_human_review_decision(),
        )


def test_triage_result_preserves_all_pipeline_components():
    """El resultado debe conservar todos los componentes del pipeline."""
    incident = create_valid_incident()
    local_result = create_valid_model_result()
    cloud_result = create_valid_model_result()
    comparison = create_valid_comparison()
    decision = create_automatic_decision()

    result = TriageResult(
        incident=incident,
        local_result=local_result,
        cloud_result=cloud_result,
        comparison=comparison,
        decision=decision,
    )

    assert result.incident is incident
    assert result.local_result is local_result
    assert result.cloud_result is cloud_result
    assert result.comparison is comparison
    assert result.decision is decision