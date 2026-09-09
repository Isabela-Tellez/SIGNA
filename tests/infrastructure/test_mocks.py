from domain.schemas import Incident
from domain.enums import(
    Category, Department, ModelStatus,
    Provider, Urgency
)
from infrastructure.mocks import(
    MockCloudProvider, MockLocalProvider,
)

# ---------------------------------------------------------------------------
# Mock Local Provider
# ---------------------------------------------------------------------------

def test_mock_local_provider_returns_valid_result():
    """El Mock Local debe devolver un ModelResult válido"""

    incident = Incident(
        text = "El cliente no tiene conexión a internet"
    )

    provider = MockLocalProvider()

    result = provider.analyze(incident)

    assert result.provider == Provider.LOCAL
    assert result.model == "mock-local"
    assert result.status == ModelStatus.SUCCESS
    assert result.classification is not None

    assert result.classification.category == Category.CONNECTIVITY
    assert result.classification.urgency == Urgency.MEDIUM
    assert (
        result.classification.department == Department.TECHNICAL_SUPPORT
    )

# ---------------------------------------------------------------------------
# Mock Cloud Provider
# ---------------------------------------------------------------------------

def test_mock_cloud_provider_returns_valid_result():
    """El Mock Cloud debe devolver un ModelResult válido"""

    incident = Incident(
        text = "El cliente no tiene conexión a internet"
    )

    provider = MockCloudProvider()

    result = provider.analyze(incident)
    
    assert result.provider == Provider.CLOUD
    assert result.model == "mock-cloud"
    assert result.status == ModelStatus.SUCCESS
    assert result.classification is not None

    assert result.classification.category == Category.CONNECTIVITY
    assert result.classification.urgency == Urgency.MEDIUM
    assert (
        result.classification.department == Department.TECHNICAL_SUPPORT
    )