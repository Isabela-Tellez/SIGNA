from domain.enums import ModelStatus, Provider
from application.signa_core import SignaCore
from domain.schemas import Incident
from infrastructure.mocks import (
    MockCloudProvider, MockLocalProvider,
)

# ---------------------------------------------------------------------------
# SIGNA Core
# ---------------------------------------------------------------------------

def test_signa_core_executes_local_and_cloud():
    """El Core debe ejecutar los proveedores Local y Cloud."""

    incident = Incident(
        text = "El cliente no tiene conexión a internt"
    )

    core = SignaCore(
        local_provider = MockLocalProvider(),
        cloud_provider = MockCloudProvider(),
    )

    local_result, cloud_result = core.triage(incident)

    assert local_result.provider == Provider.LOCAL
    assert local_result.status == ModelStatus.SUCCESS

    assert cloud_result.provider == Provider.CLOUD
    assert cloud_result.status == ModelStatus.SUCCESS