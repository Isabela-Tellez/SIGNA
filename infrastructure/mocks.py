"""
Mock Providers utilizados durante el desarrollo de SIGNA.

Simulan las respuestas de un modelo Local y un modelo de Cloud ç
sin depender todavía de Ollama ni de una API externa.
"""

from domain.enums import (
    Category, Department, ModelStatus, 
    Provider, Urgency
)

from domain.schemas import(
    Classification, Incident, ModelMetrics, ModelResult
)

def _build_metrics() -> ModelMetrics:
    """Genera métricas ficticias para los modelos mock."""

    return ModelMetrics(
        input_tokens = 50,
        output_tokens = 50,
        total_tokens = 100,
        latency_ms = 100.0,
        cost = 0.0,
        retries = 0,
    )

def _build_classification(
    incident: Incident,
    *,
    category: Category,
    urgency: Urgency,
    department: Department,
    confidence: float,
) -> Classification:
    """Construye una clasificación mock válida"""

    return Classification(
        category = category,
        urgency = urgency,
        department = department,
        summary = "Incidencia simulada para realizar pruebas completas del sistema SIGNA hoy",
        explanation = (
            f"Clasificación simulada para la incidencia {incident.text}"
        ),
        confidence = confidence,
    )

class MockLocalProvider:
    """Simula el modoelo local de SIGNA"""

    def analyze(self, incident: Incident) -> ModelResult:
        """Devuelve una clasificación simulada."""

        Classification = _build_classification(
            incident,
            category = Category.CONNECTIVITY,
            urgency = Urgency.MEDIUM,
            department = Department.TECHNICAL_SUPPORT,
            confidence = 0.95,
        )

        return ModelResult(
            provider=Provider.LOCAL,
            model="mock-local",
            classification= Classification,
            metrics=_build_metrics(),
            status=ModelStatus.SUCCESS,
            error=None,
        )


class MockCloudProvider:
    """Simula el modelo Cloud de SIGNA."""

    def analyze(self, incident: Incident) -> ModelResult:
        """Devuelve una clasificación simulada."""

        classification = _build_classification(
            incident,
            category=Category.CONNECTIVITY,
            urgency=Urgency.MEDIUM,
            department=Department.TECHNICAL_SUPPORT,
            confidence=0.92,
        )

        return ModelResult(
            provider=Provider.CLOUD,
            model="mock-cloud",
            classification=classification,
            metrics=_build_metrics(),
            status=ModelStatus.SUCCESS,
            error=None,
        )