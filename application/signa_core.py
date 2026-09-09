"""
Abstracciones principales de SIGNA Core.

El Core trabaja con proveedores de modelos sin depender de una 
implementación concreta como Ollama o una API cloud.
"""

from typing import Protocol
from domain.schemas import Incident, ModelResult

class ModelProvider(Protocol):
    """Interfaz que debe cumplor cualquier proveedor de modelos."""

    def analyze(self, incident: Incident) -> ModelResult:
        """Analiza una incidencia y devuelve el resultado del modelo."""

class SignaCore:
    """Motor principal de triaje de SIGNA."""

    def __init__(
        self,
        local_provider: ModelProvider,
        cloud_provider: ModelProvider,
        confidence_threshold: float = 0.80,
    ):
        self.local_provider = local_provider
        self.cloud_provider = cloud_provider
        self.confidence_provider = confidence_threshold

    def triage(self, incident:Incident) -> tuple[ModelResult, ModelResult]:
        """Ejecuta el triaje utilizando los modelos Local y Cloud."""
        local_result = self.local_provider.analyze(incident)
        cloud_result = self.cloud_provider.analyze(incident)

        return local_result, cloud_result