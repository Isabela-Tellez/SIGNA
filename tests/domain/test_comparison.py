import pytest

from domain.enums import ClassificationField
from domain.schemas import Comparison, Disagreement


def test_comparison_models_agree():
    """Una comparación válida debe indicar agreement total."""
    comparison = Comparison(
        comparable=True,
        category_agrees=True,
        urgency_agrees=True,
        department_agrees=True,
        models_agree=True,
    )

    assert comparison.comparable is True
    assert comparison.category_agrees is True
    assert comparison.urgency_agrees is True
    assert comparison.department_agrees is True
    assert comparison.models_agree is True
    assert comparison.disagreements == []


def test_comparison_models_disagree():
    """Una discrepancia en un campo implica disagreement."""
    disagreement = Disagreement(
        field=ClassificationField.CATEGORY,
        local_value="connectivity",
        cloud_value="hardware",
    )

    comparison = Comparison(
        comparable=True,
        category_agrees=False,
        urgency_agrees=True,
        department_agrees=True,
        models_agree=False,
        disagreements=[disagreement],
    )

    assert comparison.models_agree is False
    assert len(comparison.disagreements) == 1
    assert comparison.disagreements[0].field == ClassificationField.CATEGORY


def test_comparison_rejects_inconsistent_models_agree():
    """models_agree debe coincidir con el agreement de los campos."""
    with pytest.raises(ValueError):
        Comparison(
            comparable=True,
            category_agrees=True,
            urgency_agrees=True,
            department_agrees=True,
            models_agree=False,
        )


def test_comparison_rejects_missing_agreement_value():
    """Una comparación comparable debe tener todos los agreements."""
    with pytest.raises(ValueError):
        Comparison(
            comparable=True,
            category_agrees=True,
            urgency_agrees=None,
            department_agrees=True,
            models_agree=True,
        )


def test_non_comparable_comparison_has_no_agreement():
    """Una comparación no comparable no debe tener agreement."""
    comparison = Comparison(
        comparable=False,
    )

    assert comparison.comparable is False
    assert comparison.category_agrees is None
    assert comparison.urgency_agrees is None
    assert comparison.department_agrees is None
    assert comparison.models_agree is None
    assert comparison.disagreements == []


def test_non_comparable_rejects_agreement_values():
    """Una comparación no comparable no puede tener agreements."""
    with pytest.raises(ValueError):
        Comparison(
            comparable=False,
            category_agrees=True,
        )


def test_non_comparable_rejects_disagreements():
    """Una comparación no comparable no puede tener discrepancias."""
    disagreement = Disagreement(
        field=ClassificationField.CATEGORY,
        local_value="connectivity",
        cloud_value="hardware",
    )

    with pytest.raises(ValueError):
        Comparison(
            comparable=False,
            disagreements=[disagreement],
        )


def test_disagreement_stores_field_and_values():
    """Una discrepancia debe guardar campo y valores de ambos modelos."""
    disagreement = Disagreement(
        field=ClassificationField.URGENCY,
        local_value="high",
        cloud_value="critical",
    )

    assert disagreement.field == ClassificationField.URGENCY
    assert disagreement.local_value == "high"
    assert disagreement.cloud_value == "critical"