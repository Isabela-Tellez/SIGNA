"""
Motor de decisión de SIGNA.

Transforma los resultados de Local y Cloud y su comparación en una
decisión automática o una solicitud de revisión humana.
"""

from domain.enums import(
    Decision,
    DecisionReason,
    ModelStatus,
    RiskLevel,
    Urgency,
)
from domain.schemas import (
    Comparison,
    ModelResult,
    SignaDecision,
)

class DecisionEngine:
    """Determina si SIGNA puede automatizar una clasificación."""
    DEFAULT_CONFIDENCE_THRESHOLD = 0.80

    def __init__(
        self,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    ):
        """Inicializa el motor con un umbral de confianza."""
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError(
                "Confidence threshold must be between 0 and 1"
            )

        self.confidence_threshold = confidence_threshold

    def decide(
        self,
        local_result: ModelResult,
        cloud_result: ModelResult,
        comparison: Comparison,
    ) -> SignaDecision:
        """Genera la decisión final de SIGNA."""

        # ---------------------------------------------------------------------------
        # Regla 1º: Resultados inválidos
        # ---------------------------------------------------------------------------

        if(
            local_result.status != ModelStatus.SUCCESS
            or cloud_result.status != ModelStatus.SUCCESS
        ):
            return SignaDecision(
                decision = Decision.HUMAN_REVIEW,
                risk = RiskLevel.HIGH,
                reason = DecisionReason.INVALID_MODEL_RESULT,
                confidence_threshold = self.confidence_threshold,
            )

        # A partir de este punto ambos resultados tienen clasificación
        local_classification = local_result.classification
        cloud_classification = cloud_result.classification

        # ---------------------------------------------------------------------------
        # Regla 2º: Incidencia Crítica
        # ---------------------------------------------------------------------------

        if(
            local_classification.urgency == Urgency.CRITICAL
            or cloud_classification.urgency == Urgency.CRITICAL 
        ):
            return SignaDecision(
                decision = Decision.HUMAN_REVIEW,
                risk = RiskLevel.CRITICAL,
                reason = DecisionReason.CRITICAL_INCIDENT,
                confidence_threshold = self.confidence_threshold,
            )

        # ---------------------------------------------------------------------------
        # Regla 3º: Desacuerdo entre modelos
        # ---------------------------------------------------------------------------

        if comparison.models_agree is not True:
            return SignaDecision(
                decision = Decision.HUMAN_REVIEW,
                risk = RiskLevel.HIGH,
                reason = DecisionReason.MODEL_DISAGREEMENT,
                confidence_threshold = self.confidence_threshold,
            )

        # ---------------------------------------------------------------------------
        # Regla 4º: Baja Confianza
        # ---------------------------------------------------------------------------

        if(
            local_classification.confidence < self.confidence_threshold
            or cloud_classification.confidence < self.confidence_threshold
        ):
            return SignaDecision(
                decision = Decision.HUMAN_REVIEW,
                risk = RiskLevel.MEDIUM,
                reason = DecisionReason.LOW_CONFIDENCE,
                confidence_threshold = self.confidence_threshold,
            )

        # ---------------------------------------------------------------------------
        # Regla 5º: modelos Coinciden y Confianza Suficiente
        # ---------------------------------------------------------------------------

        return SignaDecision(
            decision = Decision.AUTOMATIC,
            risk = RiskLevel.LOW,
            reason = DecisionReason.MODELS_AGREE,
            confidence_threshold = self.confidence_threshold,
        )