from application.decision_engine import DecisionEngine

from domain.enums import (
    Category,
    ClassificationField,
    Decision,
    DecisionReason,
    Department,
    ModelStatus,
    Provider,
    RiskLevel,
    Urgency,
)

from domain.schemas import (
    Classification,
    Comparison,
    ModelMetrics,
    ModelResult,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_classification(
    *,
    urgency: Urgency = Urgency.MEDIUM,
    confidence: float = 0.90,
) -> Classification:
    """Construye una clasificación válida para los tests."""

    return Classification(
        category=Category.CONNECTIVITY,
        urgency=urgency,
        department=Department.TECHNICAL_SUPPORT,
        summary=(
            "Cliente reporta problemas de conexión con internet "
            "en su domicilio"
        ),
        explanation="Clasificación generada para las pruebas del motor",
        confidence=confidence,
    )


def build_model_result(
    *,
    provider: Provider,
    classification: Classification | None = None,
    status: ModelStatus = ModelStatus.SUCCESS,
) -> ModelResult:
    """Construye un resultado de modelo válido para los tests."""

    metrics = ModelMetrics(
        input_tokens=50,
        output_tokens=50,
        total_tokens=100,
        latency_ms=100.0,
        cost=0.0,
        retries=0,
    )

    if status == ModelStatus.SUCCESS:
        return ModelResult(
            provider=provider,
            model=f"mock-{provider.value}",
            classification=classification or build_classification(),
            metrics=metrics,
            status=status,
        )

    return ModelResult(
        provider=provider,
        model=f"mock-{provider.value}",
        classification=None,
        metrics=metrics,
        status=status,
        error="Mock model error",
    )


def build_agreement() -> Comparison:
    """Construye una comparación donde ambos modelos coinciden."""

    return Comparison(
        comparable=True,
        category_agrees=True,
        urgency_agrees=True,
        department_agrees=True,
        models_agree=True,
        disagreements=[],
    )


def build_disagreement() -> Comparison:
    """Construye una comparación donde los modelos discrepan."""

    return Comparison(
        comparable=True,
        category_agrees=False,
        urgency_agrees=True,
        department_agrees=False,
        models_agree=False,
        disagreements=[
            {
                "field": ClassificationField.CATEGORY,
                "local_value": Category.CONNECTIVITY.value,
                "cloud_value": Category.BILLING.value,
            },
            {
                "field": ClassificationField.DEPARTMENT,
                "local_value": Department.TECHNICAL_SUPPORT.value,
                "cloud_value": Department.BILLING.value,
            },
        ],
    )


# ---------------------------------------------------------------------------
# Decision Engine
# ---------------------------------------------------------------------------

def test_decision_engine_returns_automatic_when_models_agree():
    """Modelos coinciden y tienen confianza suficiente."""

    local_result = build_model_result(
        provider=Provider.LOCAL
    )

    cloud_result = build_model_result(
        provider=Provider.CLOUD
    )

    engine = DecisionEngine()

    decision = engine.decide(
        local_result,
        cloud_result,
        build_agreement(),
    )

    assert decision.decision == Decision.AUTOMATIC
    assert decision.risk == RiskLevel.LOW
    assert decision.reason == DecisionReason.MODELS_AGREE
    assert decision.confidence_threshold == 0.80


def test_decision_engine_sends_disagreement_to_human_review():
    """El desacuerdo entre modelos requiere revisión humana."""

    local_result = build_model_result(
        provider=Provider.LOCAL
    )

    cloud_result = build_model_result(
        provider=Provider.CLOUD
    )

    engine = DecisionEngine()

    decision = engine.decide(
        local_result,
        cloud_result,
        build_disagreement(),
    )

    assert decision.decision == Decision.HUMAN_REVIEW
    assert decision.risk == RiskLevel.HIGH
    assert decision.reason == DecisionReason.MODEL_DISAGREEMENT


def test_decision_engine_sends_low_confidence_to_human_review():
    """Una confianza inferior al umbral requiere revisión humana."""

    local_result = build_model_result(
        provider=Provider.LOCAL,
        classification=build_classification(
            confidence=0.70,
        ),
    )

    cloud_result = build_model_result(
        provider=Provider.CLOUD,
        classification=build_classification(
            confidence=0.95,
        ),
    )

    engine = DecisionEngine()

    decision = engine.decide(
        local_result,
        cloud_result,
        build_agreement(),
    )

    assert decision.decision == Decision.HUMAN_REVIEW
    assert decision.risk == RiskLevel.MEDIUM
    assert decision.reason == DecisionReason.LOW_CONFIDENCE


def test_decision_engine_sends_critical_incident_to_human_review():
    """Una incidencia crítica requiere revisión humana."""

    local_result = build_model_result(
        provider=Provider.LOCAL,
        classification=build_classification(
            urgency=Urgency.CRITICAL,
        ),
    )

    cloud_result = build_model_result(
        provider=Provider.CLOUD,
        classification=build_classification(
            urgency=Urgency.CRITICAL,
        ),
    )

    engine = DecisionEngine()

    decision = engine.decide(
        local_result,
        cloud_result,
        build_agreement(),
    )

    assert decision.decision == Decision.HUMAN_REVIEW
    assert decision.risk == RiskLevel.CRITICAL
    assert decision.reason == DecisionReason.CRITICAL_INCIDENT


def test_decision_engine_sends_invalid_model_result_to_human_review():
    """Un resultado inválido requiere revisión humana."""

    local_result = build_model_result(
        provider=Provider.LOCAL,
        status=ModelStatus.ERROR,
    )

    cloud_result = build_model_result(
        provider=Provider.CLOUD,
    )

    engine = DecisionEngine()

    decision = engine.decide(
        local_result,
        cloud_result,
        build_agreement(),
    )

    assert decision.decision == Decision.HUMAN_REVIEW
    assert decision.risk == RiskLevel.HIGH
    assert decision.reason == DecisionReason.INVALID_MODEL_RESULT