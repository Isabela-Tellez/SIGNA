from datetime import datetime, timezone

import pytest

from domain.enums import (
    Category,
    Department,
    ReviewStatus,
    Urgency,
)
from domain.schemas import Classification, HumanReview


def create_valid_classification() -> Classification:
    """Crea una clasificación válida para reutilizar en los tests."""
    return Classification(
        category=Category.CONNECTIVITY,
        urgency=Urgency.HIGH,
        department=Department.TECHNICAL_SUPPORT,
        summary="Cliente reporta pérdida total de conexión a internet doméstica hoy",
        explanation="La incidencia indica una pérdida de conectividad.",
        confidence=0.90,
    )


def test_pending_review_creates_successfully():
    """Una revisión pendiente no debe tener clasificación final ni fecha."""
    review = HumanReview(
        status=ReviewStatus.PENDING,
    )

    assert review.status == ReviewStatus.PENDING
    assert review.final_classification is None
    assert review.reviewed_at is None
    assert review.reviewer_comment is None


def test_accepted_review_creates_successfully():
    """Una revisión aceptada debe tener clasificación final y fecha."""
    reviewed_at = datetime.now(timezone.utc)

    review = HumanReview(
        status=ReviewStatus.ACCEPTED,
        final_classification=create_valid_classification(),
        reviewed_at=reviewed_at,
    )

    assert review.status == ReviewStatus.ACCEPTED
    assert review.final_classification is not None
    assert review.reviewed_at == reviewed_at


def test_corrected_review_creates_successfully():
    """Una revisión corregida debe tener clasificación final y fecha."""
    reviewed_at = datetime.now(timezone.utc)

    review = HumanReview(
        status=ReviewStatus.CORRECTED,
        final_classification=create_valid_classification(),
        reviewed_at=reviewed_at,
        reviewer_comment="La categoría original era incorrecta.",
    )

    assert review.status == ReviewStatus.CORRECTED
    assert review.final_classification is not None
    assert review.reviewed_at == reviewed_at
    assert review.reviewer_comment == (
        "La categoría original era incorrecta."
    )


def test_pending_review_rejects_final_classification():
    """Una revisión pendiente no puede tener clasificación final."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.PENDING,
            final_classification=create_valid_classification(),
        )


def test_pending_review_rejects_reviewed_at():
    """Una revisión pendiente no puede tener fecha de revisión."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.PENDING,
            reviewed_at=datetime.now(timezone.utc),
        )


def test_accepted_review_requires_final_classification():
    """Una revisión aceptada debe tener clasificación final."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.ACCEPTED,
            reviewed_at=datetime.now(timezone.utc),
        )


def test_accepted_review_requires_reviewed_at():
    """Una revisión aceptada debe tener fecha de revisión."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.ACCEPTED,
            final_classification=create_valid_classification(),
        )


def test_corrected_review_requires_final_classification():
    """Una revisión corregida debe tener clasificación final."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.CORRECTED,
            reviewed_at=datetime.now(timezone.utc),
        )


def test_corrected_review_requires_reviewed_at():
    """Una revisión corregida debe tener fecha de revisión."""
    with pytest.raises(ValueError):
        HumanReview(
            status=ReviewStatus.CORRECTED,
            final_classification=create_valid_classification(),
        )