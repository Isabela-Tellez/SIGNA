"""
Proveedor Cloud de SIGNA.

Simula el comportamiento de un proveedor de modelos
ejecutado mediante una API cloud.

La implementación mantiene el mismo contrato que
OllamaProvider y los proveedores mock, permitiendo
cambiar posteriormente a un proveedor real como Gemini
sin modificar SIGNA Core.
"""

import time

from domain.enums import (
    Category,
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


class CloudProvider:
    """Proveedor Cloud simulado para SIGNA."""

    def __init__(self, model: str = "mock-cloud"):
        self.model = model

    def analyze(self, incident: Incident) -> ModelResult:
        """
        Analiza una incidencia simulando una llamada
        a un proveedor cloud.
        """

        start_time = time.perf_counter()

        try:
            # Simulamos el procesamiento de una API cloud.
            classification = Classification(
                category=Category.CONNECTIVITY,
                urgency=Urgency.MEDIUM,
                department=Department.TECHNICAL_SUPPORT,
                summary=(
                    "Incidencia simulada para realizar "
                    "pruebas completas del sistema SIGNA hoy"
                ),
                explanation=(
                    f"Clasificación simulada para la incidencia "
                    f"{incident.text}"
                ),
                confidence=0.92,
            )

            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            metrics = ModelMetrics(
                input_tokens=50,
                output_tokens=50,
                total_tokens=100,
                latency_ms=latency_ms,
                cost=0.0,
                retries=0,
            )

            return ModelResult(
                provider=Provider.CLOUD,
                model=self.model,
                classification=classification,
                metrics=metrics,
                status=ModelStatus.SUCCESS,
                error=None,
            )

        except Exception as exc:
            latency_ms = (
                time.perf_counter() - start_time
            ) * 1000

            metrics = ModelMetrics(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                latency_ms=latency_ms,
                cost=0.0,
                retries=0,
            )

            return ModelResult(
                provider=Provider.CLOUD,
                model=self.model,
                classification=None,
                metrics=metrics,
                status=ModelStatus.ERROR,
                error=str(exc),
            )