"""
Abstracciones principales de SIGNA Core.

El Core trabaja con proveedores de modelos sin depender de una
implementación concreta como Ollama o una API cloud.
"""

from typing import Protocol

from application.decision_engine import DecisionEngine

from domain.enums import (
    ClassificationField,
    Decision,
    ModelStatus,
    ReviewStatus,
)

from domain.schemas import (
    Comparison,
    Disagreement,
    HumanReview,
    Incident,
    ModelResult,
    TriageResult,
)


class ModelProvider(Protocol):
    """Interfaz que debe cumplir cualquier proveedor de modelos."""

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

        self.decision_engine = DecisionEngine(
            confidence_threshold=confidence_threshold
        )

    def triage(self, incident: Incident) -> TriageResult:
        """Ejecuta el flujo completo de triaje de SIGNA."""

        # Ejecutar los dos proveedores
        local_result = self.local_provider.analyze(incident)
        cloud_result = self.cloud_provider.analyze(incident)

        # Comparar los resultados
        comparison = self._compare_results(
            local_result,
            cloud_result,
        )

        # Tomar la decisión
        decision = self.decision_engine.decide(
            local_result,
            cloud_result,
            comparison,
        )

        # Crear revisión humana cuando sea necesaria
        human_review = None

        if decision.decision == Decision.HUMAN_REVIEW:
            human_review = HumanReview(
                status=ReviewStatus.PENDING,
            )

        # Devolver el resultado completo del pipeline
        return TriageResult(
            incident=incident,
            local_result=local_result,
            cloud_result=cloud_result,
            comparison=comparison,
            decision=decision,
            human_review=human_review,
        )

    def _compare_results(
        self,
        local_result: ModelResult,
        cloud_result: ModelResult,
    ) -> Comparison:
        """Compara las clasificaciones de Local y Cloud."""

        local_classification = local_result.classification
        cloud_classification = cloud_result.classification

        # Los resultados solo son comparables si ambos modelos
        # terminaron correctamente y tienen una clasificación.
        if (
            local_result.status != ModelStatus.SUCCESS
            or cloud_result.status != ModelStatus.SUCCESS
            or local_classification is None
            or cloud_classification is None
        ):
            return Comparison(
                comparable=False,
            )

        # Comparación de los campos relevantes para la decisión.
        category_agrees = (
            local_classification.category
            == cloud_classification.category
        )

        urgency_agrees = (
            local_classification.urgency
            == cloud_classification.urgency
        )

        department_agrees = (
            local_classification.department
            == cloud_classification.department
        )

        disagreements = []

        # Se registran exactamente qué campos son diferentes.
        if not category_agrees:
            disagreements.append(
                Disagreement(
                    field=ClassificationField.CATEGORY,
                    local_value=local_classification.category.value,
                    cloud_value=cloud_classification.category.value,
                )
            )

        if not urgency_agrees:
            disagreements.append(
                Disagreement(
                    field=ClassificationField.URGENCY,
                    local_value=local_classification.urgency.value,
                    cloud_value=local_classification.urgency.value,
                )
            )

        if not department_agrees:
            disagreements.append(
                Disagreement(
                    field=ClassificationField.DEPARTMENT,
                    local_value=local_classification.department.value,
                    cloud_value=cloud_classification.department.value,
                )
            )

        models_agree = (
            category_agrees
            and urgency_agrees
            and department_agrees
        )

        return Comparison(
            comparable=True,
            category_agrees=category_agrees,
            urgency_agrees=urgency_agrees,
            department_agrees=department_agrees,
            models_agree=models_agree,
            disagreements=disagreements,
        )