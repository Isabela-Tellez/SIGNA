"""
Rutas HTTP de SIGNA.
"""

from fastapi import APIRouter, HTTPException

from application.signa_core import SignaCore
from domain.schemas import Incident, TriageResult
from infrastructure.mocks import (
    MockCloudProvider,
    MockLocalProvider,
)

router = APIRouter()

@router.get("/")
def health_check() -> dict [str, str]:
    """Comprueba que la API de SIGNA está disponible."""

    return{
        "application": "SIGNA",
        "status": "running",
    }

# Providers temporales para la integración inicial,
# Más adelante serían sustituidos por Ollama y el Cloud Provider real.
signa_core = SignaCore(
    local_provider = MockLocalProvider(),
    cloud_provider = MockCloudProvider(),
)

@router.post(
    "/triage",
    response_model = TriageResult,
)

def triage_incident(incident: Incident) -> TriageResult:
    """
    Recibe una incidencia y ejecuta el flujo completo de SIGNA.
    """

    try:
        return signa_core.triage(incident)

    except Exception as exc:
        raise HTTPException(
            status_code = 500,
            detail = f"Error procesando la incidencia: {exc}",
        ) from exc