from infrastructure.cloud_provider import CloudProvider

from domain.enums import (
    Category,
    Department,
    ModelStatus,
    Provider,
    Urgency,
)

from domain.schemas import Incident


def test_cloud_provider_returns_valid_result():
    """CloudProvider debe devolver un resultado válido."""

    incident = Incident(
        text="El cliente no tiene conexión a internet"
    )

    provider = CloudProvider()

    result = provider.analyze(incident)

    assert result.provider == Provider.CLOUD
    assert result.model == "mock-cloud"
    assert result.status == ModelStatus.SUCCESS
    assert result.error is None

    assert result.classification is not None

    assert result.classification.category == Category.CONNECTIVITY
    assert result.classification.urgency == Urgency.MEDIUM
    assert (
        result.classification.department
        == Department.TECHNICAL_SUPPORT
    )

    assert result.classification.confidence == 0.92