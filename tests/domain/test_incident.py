from uuid import UUID

import pytest

from domain.schemas import Incident


def test_incident_creates_successfully():
    """ Un incidente válido debe crearse correctamente. """

    incident = Incident(
        text="Cliente sin conexión a internet"
    )

    assert incident.text == "Cliente sin conexión a internet"
    assert isinstance(incident.id, UUID)
    assert incident.created_at is not None


def test_incident_normalizes_whitespace():
    """ El texto debe normalizar espacios innecesarios. """

    incident = Incident(
        text="  Cliente   sin   conexión   a internet  "
    )

    assert incident.text == "Cliente sin conexión a internet"


def test_incident_rejects_empty_text():
    """ Un incidente no puede tener el texto vacío. """

    with pytest.raises(ValueError):
        Incident(text="")


def test_incident_rejects_whitespace_only_text():
    """ Un incidente no puede contener solo espacios. """

    with pytest.raises(ValueError):
        Incident(text="     ")