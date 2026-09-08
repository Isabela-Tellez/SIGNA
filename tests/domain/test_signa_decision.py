import pytest

from domain.enums import Decision, DecisionReason, RiskLevel
from domain.schemas import SignaDecision


def test_signa_decision_creates_successfully():
    """Una decisión válida debe crearse correctamente."""
    decision = SignaDecision(
        decision=Decision.AUTOMATIC,
        risk=RiskLevel.LOW,
        reason=DecisionReason.MODELS_AGREE,
        confidence_threshold=0.75,
    )

    assert decision.decision == Decision.AUTOMATIC
    assert decision.risk == RiskLevel.LOW
    assert decision.reason == DecisionReason.MODELS_AGREE
    assert decision.confidence_threshold == 0.75


def test_signa_decision_accepts_zero_threshold():
    """El umbral de confianza puede ser 0."""
    decision = SignaDecision(
        decision=Decision.AUTOMATIC,
        risk=RiskLevel.LOW,
        reason=DecisionReason.MODELS_AGREE,
        confidence_threshold=0.0,
    )

    assert decision.confidence_threshold == 0.0


def test_signa_decision_accepts_one_threshold():
    """El umbral de confianza puede ser 1."""
    decision = SignaDecision(
        decision=Decision.HUMAN_REVIEW,
        risk=RiskLevel.HIGH,
        reason=DecisionReason.LOW_CONFIDENCE,
        confidence_threshold=1.0,
    )

    assert decision.confidence_threshold == 1.0


def test_signa_decision_rejects_threshold_below_zero():
    """El umbral de confianza no puede ser inferior a 0."""
    with pytest.raises(ValueError):
        SignaDecision(
            decision=Decision.AUTOMATIC,
            risk=RiskLevel.LOW,
            reason=DecisionReason.MODELS_AGREE,
            confidence_threshold=-0.1,
        )


def test_signa_decision_rejects_threshold_above_one():
    """El umbral de confianza no puede ser superior a 1."""
    with pytest.raises(ValueError):
        SignaDecision(
            decision=Decision.AUTOMATIC,
            risk=RiskLevel.LOW,
            reason=DecisionReason.MODELS_AGREE,
            confidence_threshold=1.1,
        )


def test_signa_decision_supports_human_review():
    """SIGNA debe poder representar una decisión de revisión humana."""
    decision = SignaDecision(
        decision=Decision.HUMAN_REVIEW,
        risk=RiskLevel.HIGH,
        reason=DecisionReason.MODEL_DISAGREEMENT,
        confidence_threshold=0.75,
    )

    assert decision.decision == Decision.HUMAN_REVIEW
    assert decision.risk == RiskLevel.HIGH
    assert decision.reason == DecisionReason.MODEL_DISAGREEMENT