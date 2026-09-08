"""
Schemas Pydantic del dominio de SIGNA.

Definen la estructura y validación de los datos utilizados
por el motor de triaje.
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator

from .enums import (
    Category, ClassificationField, Decision, DecisionReason, Department,
    ModelStatus, Provider, ReviewStatus, RiskLevel, Urgency,
)

# ---------------------------------------------------------------------------
# Incident
# ---------------------------------------------------------------------------

class Incident(BaseModel):
    """Representa la comunicación original del cliente."""
    id: UUID = Field(default_factory=uuid4)

    text: str = Field(min_length=1)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """Normaliza espacios sin modificar el contenido."""

        value = " ".join(value.split())

        if not value:
            raise ValueError("Incident text cannot be empty")

        return value


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


class Classification(BaseModel):
    """Clasificación producida por un modelo."""
    category: Category

    urgency: Urgency

    department: Department

    summary: str = Field(min_length=1)

    explanation: str = Field(min_length=1)

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        """El resumen debe contener exactamente 10 palabras."""
        value = " ".join(value.split())

        if len(value.split()) != 10:
            raise ValueError(
                "Summary must contain exactly 10 words"
            )

        return value

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, value: str) -> str:
        """La explicación no puede estar vacía."""
        value = value.strip()

        if not value:
            raise ValueError("Explanation cannot be empty")

        return value


# ---------------------------------------------------------------------------
# Model Metrics
# ---------------------------------------------------------------------------


class ModelMetrics(BaseModel):
    """Métricas asociadas a la ejecución de un modelo."""
    input_tokens: int = Field(ge=0)

    output_tokens: int = Field(ge=0)

    total_tokens: int = Field(ge=0)

    latency_ms: float = Field(ge=0)

    cost: float = Field(ge=0)

    retries: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total_tokens(self):
        """Valida que el total coincida con entrada más salida."""

        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError(
                "Total tokens must equal input tokens plus output tokens"
            )

        return self


# ---------------------------------------------------------------------------
# Model Result
# ---------------------------------------------------------------------------


class ModelResult(BaseModel):
    """Resultado completo de una ejecución de modelo."""
    provider: Provider

    model: str = Field(min_length=1)

    classification: Classification | None = None

    metrics: ModelMetrics

    status: ModelStatus

    error: str | None = None

    @model_validator(mode="after")
    def validate_result(self):
        """Valida la coherencia entre estado y resultado."""
        if self.status == ModelStatus.SUCCESS:

            if self.classification is None:
                raise ValueError(
                    "Successful model result requires classification"
                )

            if self.error is not None:
                raise ValueError(
                    "Successful model result cannot contain an error"
                )

        else:

            if self.error is None or not self.error.strip():
                raise ValueError(
                    "Failed model result requires an error"
                )

        return self


# ---------------------------------------------------------------------------
# Disagreement
# ---------------------------------------------------------------------------


class Disagreement(BaseModel):
    """Representa una discrepancia entre Local y Cloud."""
    field: ClassificationField

    local_value: str

    cloud_value: str


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


class Comparison(BaseModel):
    """Comparación entre las clasificaciones de Local y Cloud."""
    comparable: bool

    category_agrees: bool | None = None

    urgency_agrees: bool | None = None

    department_agrees: bool | None = None

    models_agree: bool | None = None

    disagreements: list[Disagreement] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_comparison(self):
        """Mantiene la coherencia interna de la comparación."""

        # Si no es comparable, no puede existir información
        # sobre agreement ni discrepancias.
        if not self.comparable:

            if any(
                value is not None
                for value in (
                    self.category_agrees,
                    self.urgency_agrees,
                    self.department_agrees,
                    self.models_agree,
                )
            ):
                raise ValueError(
                    "Non-comparable results cannot have agreement values"
                )

            if self.disagreements:
                raise ValueError(
                    "Non-comparable results cannot have disagreements"
                )

            return self

        # Una comparación comparable necesita conocer
        # el agreement de los tres campos.
        if any(
            value is None
            for value in (
                self.category_agrees,
                self.urgency_agrees,
                self.department_agrees,
            )
        ):
            raise ValueError(
                "Comparable results require agreement values"
            )

        # Una comparación comparable también debe indicar
        # si los modelos coinciden globalmente.
        if self.models_agree is None:
            raise ValueError(
                "Comparable results require models_agree"
            )

        # models_agree debe ser coherente con los tres campos.
        expected_models_agree = (
            self.category_agrees
            and self.urgency_agrees
            and self.department_agrees
        )

        if self.models_agree != expected_models_agree:
            raise ValueError(
                "models_agree must match field agreement values"
            )

        return self


# ---------------------------------------------------------------------------
# SIGNA Decision
# ---------------------------------------------------------------------------


class SignaDecision(BaseModel):
    """Decisión final tomada por SIGNA Core."""
    decision: Decision

    risk: RiskLevel

    reason: DecisionReason

    confidence_threshold: float = Field(
        ge=0.0,
        le=1.0,
    )


# ---------------------------------------------------------------------------
# Human Review
# ---------------------------------------------------------------------------


class HumanReview(BaseModel):
    """Representa la intervención de un operador humano."""
    id: UUID = Field(default_factory=uuid4)

    status: ReviewStatus

    final_classification: Classification | None = None

    reviewer_comment: str | None = None

    reviewed_at: datetime | None = None

    @model_validator(mode="after")
    def validate_review(self):
        """Valida la coherencia del estado de la revisión."""

        if self.status == ReviewStatus.PENDING:

            if self.final_classification is not None:
                raise ValueError(
                    "Pending review cannot have final classification"
                )

            if self.reviewed_at is not None:
                raise ValueError(
                    "Pending review cannot have reviewed_at"
                )

        else:

            if self.final_classification is None:
                raise ValueError(
                    "Completed review requires final classification"
                )

            if self.reviewed_at is None:
                raise ValueError(
                    "Completed review requires reviewed_at"
                )

        return self


# ---------------------------------------------------------------------------
# Triage Result
# ---------------------------------------------------------------------------


class TriageResult(BaseModel):
    """Resultado completo de una ejecución de SIGNA."""
    id: UUID = Field(default_factory=uuid4)

    incident: Incident

    local_result: ModelResult

    cloud_result: ModelResult

    comparison: Comparison

    decision: SignaDecision

    human_review: HumanReview | None = None

    processed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @model_validator(mode="after")
    def validate_human_review(self):
        """Valida la coherencia entre decisión y revisión humana."""

        if self.decision.decision == Decision.AUTOMATIC:

            if self.human_review is not None:
                raise ValueError(
                    "Automatic decision cannot have human review"
                )

        elif self.decision.decision == Decision.HUMAN_REVIEW:

            if self.human_review is None:
                raise ValueError(
                    "Human review decision requires human review"
                )

        return self