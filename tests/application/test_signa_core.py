from application.signa_core import SignaCore
from domain.enums import (
    Category,
    ClassificationField,
    Department,
    ModelStatus,
    Provider,
    Urgency,
)
from domain.schemas import (
    Classification,
    Incident,
    ModelMetrics,
    ModelResult,
)
from infrastructure.mocks import (
    MockCloudProvider,
    MockLocalProvider,
)


# ---------------------------------------------------------------------------
# Test Provider
# ---------------------------------------------------------------------------

class DisagreeingCloudProvider:
    """Provider de prueba que devuelve una clasificación diferente."""

    def analyze(self, incident: Incident) -> ModelResult:
        """Devuelve deliberadamente una clasificación diferente."""

        classification = Classification(
            category=Category.BILLING,
            urgency=Urgency.MEDIUM,
            department=Department.BILLING,
            summary=(
                "Cliente reporta problema de facturación pendiente "
                "en su cuenta bancaria"
            ),
            explanation="Clasificación simulada para probar desacuerdos",
            confidence=0.90,
        )

        metrics = ModelMetrics(
            input_tokens=50,
            output_tokens=50,
            total_tokens=100,
            latency_ms=100.0,
            cost=0.0,
            retries=0,
        )

        return ModelResult(
            provider=Provider.CLOUD,
            model="mock-cloud-disagreement",
            classification=classification,
            metrics=metrics,
            status=ModelStatus.SUCCESS,
        )


# ---------------------------------------------------------------------------
# SIGNA Core
# ---------------------------------------------------------------------------

def test_signa_core_executes_local_and_cloud():
    """El Core debe ejecutar los proveedores Local y Cloud."""

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    core = SignaCore(
        local_provider=MockLocalProvider(),
        cloud_provider=MockCloudProvider(),
    )

    local_result, cloud_result = core.triage(incident)

    assert local_result.provider == Provider.LOCAL
    assert local_result.status == ModelStatus.SUCCESS

    assert cloud_result.provider == Provider.CLOUD
    assert cloud_result.status == ModelStatus.SUCCESS


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def test_signa_core_detects_model_agreement():
    """El Core debe detectar cuando Local y Cloud coinciden."""

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    core = SignaCore(
        local_provider=MockLocalProvider(),
        cloud_provider=MockCloudProvider(),
    )

    local_result, cloud_result = core.triage(incident)

    comparison = core._compare_results(
        local_result,
        cloud_result,
    )

    assert comparison.comparable is True
    assert comparison.category_agrees is True
    assert comparison.urgency_agrees is True
    assert comparison.department_agrees is True
    assert comparison.models_agree is True
    assert comparison.disagreements == []


# ---------------------------------------------------------------------------
# Disagreement
# ---------------------------------------------------------------------------

def test_signa_core_detects_model_disagreement():
    """El Core debe detectar los campos diferentes entre los modelos."""

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    core = SignaCore(
        local_provider=MockLocalProvider(),
        cloud_provider=DisagreeingCloudProvider(),
    )

    local_result, cloud_result = core.triage(incident)

    comparison = core._compare_results(
        local_result,
        cloud_result,
    )

    assert comparison.comparable is True

    assert comparison.category_agrees is False
    assert comparison.urgency_agrees is True
    assert comparison.department_agrees is False

    assert comparison.models_agree is False

    assert len(comparison.disagreements) == 2

    fields = {
        disagreement.field
        for disagreement in comparison.disagreements
    }

    assert fields == {
        ClassificationField.CATEGORY,
        ClassificationField.DEPARTMENT,
    }