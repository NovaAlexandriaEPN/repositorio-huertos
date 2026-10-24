from django.apps import apps
from django.core.checks import Error, Tags, register
from django.core.exceptions import FieldDoesNotExist
from django.db import models

from .models import PlantaHuerto


@register(Tags.models)
def comprobar_contrato_actividades(app_configs, **kwargs):
    """Detectar una integración que deje el historial fuera de sus protecciones."""
    try:
        actividad = apps.get_model("actividades", "Actividad")
    except LookupError:
        # El módulo de actividades todavía puede estar en desarrollo.
        return []
    try:
        campo = actividad._meta.get_field("planta")
    except FieldDoesNotExist:
        campo = None
    if (
        not isinstance(campo, models.ForeignKey)
        or not campo.many_to_one
        or campo.remote_field.model is not PlantaHuerto
        or campo.remote_field.related_name != "actividades"
        or campo.remote_field.on_delete is not models.PROTECT
        or not campo.null
        or not campo.blank
    ):
        return [Error(
            "Actividad.planta debe conservar la relación protegida con PlantaHuerto.",
            hint='Usa ForeignKey("comunidades.PlantaHuerto", on_delete=PROTECT, '
                 'related_name="actividades", null=True, blank=True).',
            id="comunidades.E001",
        )]
    return []
