import pytest

from domain.enums import Category, Department, Urgency
from domain.schemas import Classification


def test_classification_creates_successfully():
    """ Una clasificación válida debe crearse correctamente. """
    classification = Classification(
        category=Category.CONNECTIVITY,
        urgency=Urgency.HIGH,
        department=Department.TECHNICAL_SUPPORT,
        summary="Cliente reporta pérdida total de conexión a internet doméstica hoy",
        explanation="La incidencia indica una pérdida de conectividad.",
        confidence=0.90,
    )

    assert classification.category == Category.CONNECTIVITY
    assert classification.urgency == Urgency.HIGH
    assert classification.department == Department.TECHNICAL_SUPPORT
    assert classification.summary == (
        "Cliente reporta pérdida total de conexión a internet doméstica hoy"
    )
    assert classification.explanation == (
        "La incidencia indica una pérdida de conectividad."
    )
    assert classification.confidence == 0.90


def test_classification_normalizes_summary_whitespace():
    """El resumen debe normalizar espacios innecesarios."""
    classification = Classification(
        category=Category.CONNECTIVITY,
        urgency=Urgency.MEDIUM,
        department=Department.TECHNICAL_SUPPORT,
        summary="  Cliente      reporta     pérdida    total    de    conexión   a   internet      doméstica      hoy",
        explanation="La incidencia indica una pérdida de conectividad.",
        confidence=0.85,
    )

    assert classification.summary == (
        "Cliente reporta pérdida total de conexión a internet doméstica hoy"
    )


def test_classification_rejects_summary_with_wrong_word_count():
    """El resumen debe contener exactamente 10 palabras."""
    with pytest.raises(ValueError):
        Classification(
            category=Category.CONNECTIVITY,
            urgency=Urgency.HIGH,
            department=Department.TECHNICAL_SUPPORT,
            summary="Cliente sin conexión a internet",
            explanation="La incidencia indica una pérdida de conectividad.",
            confidence=0.90,
        )


def test_classification_rejects_confidence_below_zero():
    """La confianza no puede ser inferior a 0."""
    with pytest.raises(ValueError):
        Classification(
            category=Category.CONNECTIVITY,
            urgency=Urgency.HIGH,
            department=Department.TECHNICAL_SUPPORT,
            summary="Cliente sin conexión a internet desde esta mañana",
            explanation="La incidencia indica una pérdida de conectividad.",
            confidence=-0.1,
        )


def test_classification_rejects_confidence_above_one():
    """La confianza no puede ser superior a 1."""
    with pytest.raises(ValueError):
        Classification(
            category=Category.CONNECTIVITY,
            urgency=Urgency.HIGH,
            department=Department.TECHNICAL_SUPPORT,
            summary="Cliente sin conexión a internet desde esta mañana",
            explanation="La incidencia indica una pérdida de conectividad.",
            confidence=1.1,
        )


def test_classification_rejects_empty_explanation():
    """La explicación no puede estar vacía."""
    with pytest.raises(ValueError):
        Classification(
            category=Category.CONNECTIVITY,
            urgency=Urgency.HIGH,
            department=Department.TECHNICAL_SUPPORT,
            summary="Cliente sin conexión a internet desde esta mañana",
            explanation="   ",
            confidence=0.90,
        )