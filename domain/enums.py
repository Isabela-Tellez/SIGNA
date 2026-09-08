"""
Enums del Dominio de SIGNA.

Definen los valores controlados utilizados por los modelos de dominio
evitando strings arbitrarios y manteniendo consistencias en todo el sistema.
"""

from enum import Enum

# ---------------------------------------------------------------------------
# Clasificación de incidencias
# ---------------------------------------------------------------------------

class category(str, Enum):
    """ Categoría principal de la incidencia. """
    TECHNICAL_VISIT = "technical_visit"
    MOBILE_NETWORK = "mobile_network"
    INSTALLATION = "installation"
    CONNECTIVITY = "connectivity"
    TV_SERVICE = "tv_service"
    CONTRACT = "contract"
    HARDWARE = "hardware"
    ACCOUNT = "account"
    BILLING = "billing"
    OTHER = "other"

class Urgency(str, Enum):
    """ Nivel de urgencia de la incidencia. """
    LOW  = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Departament(str, Enum):
    """ Departamento responsable de gestionar la incidencia. """
    TECHNICAL_SUPPORT = "technical_support"
    CUSTOMER_SERVICE = "customer_service"
    FIELDD_SERVICE = "field_service"
    SECURITY = "security"
    BILLING = "billing"
    SALES = "sales"

# ---------------------------------------------------------------------------
# Ejecución de modelos
# ---------------------------------------------------------------------------

class Provider(str, Enum):
    """ Proveedor lógico utilizado para ejecutar el modelo. """
    LOCAL = "local"
    CLOUD = "cloud"

class ModelStatus(str, Enum):
    """ Estado técnico de una ejecución del modelo. """
    SUCCESS = "success"
    INVALID = "invalid"
    TIMEOUT = "timeout"
    ERROR = "error"

# ---------------------------------------------------------------------------
# Decisión de SIGNA
# ---------------------------------------------------------------------------

class Decision(str, Enum):
    """
    Decisión final de SIGNA.

    No representa una decisión de LLM, sino de SIGMA core.
    """
    AUTOMATIC = "automatic"
    HUMAN_REVIEW = "human_review"

class RiskLevel(str, Enum):
    """
    Riesgo asociado a automatizar una decisión.

    Es diferente de Urgency: Urgencia describe la incidencia,
    mientras que riesgo describe la automatización.
    """
    LOW  = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DecisionReason(str, Enum):
    """ Motivo principal de la decisión tomada por SIGMA. """
    MODELS_AGREE = "models_agree"
    LOW_CONFIDENCE = "low_confidence"
    MODEL_DISAGREEMENT = "model_disagreement"
    INVALID_MODEL_RESULT = "invalid_model_result"
    INSUFFICIENT_INFORMATION = "insufficient_information"
    CRITICAL_INCIDENT = "critical_incident"


# ---------------------------------------------------------------------------
# Revisión humana
# ---------------------------------------------------------------------------

class ReviewStatus(str, Enum):
    """Estado actual de una revisión humana."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    CORRECTED = "corrected"


# ---------------------------------------------------------------------------
# Comparación de modelos
# ---------------------------------------------------------------------------

class ClassificationField(str, Enum):
    """
    Campos utilizados para comparar las clasificaciones de los modelos.

    No se comparan summary, explanation ni confidence.
    """
    CATEGORY = "category"
    URGENCY = "urgency"
    DEPARTMENT = "department"