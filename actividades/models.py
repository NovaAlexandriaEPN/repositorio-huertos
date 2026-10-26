"""Historial de labores: actor original, recompensa histórica y constancia de anulación."""
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from catalogo.models import TipoActividad


class Actividad(models.Model):
    Tipo = TipoActividad.Codigo
    TIPOS_GENERALES = (Tipo.PREPARACION, Tipo.DISENO, Tipo.RITUAL)

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        ANULADA = "anulada", "Anulada"

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    huerto = models.ForeignKey("comunidades.Huerto", on_delete=models.PROTECT, related_name="actividades")
    planta = models.ForeignKey("comunidades.PlantaHuerto", on_delete=models.PROTECT,
                               related_name="actividades", null=True, blank=True)
    tipo = models.ForeignKey(TipoActividad, to_field="codigo", on_delete=models.PROTECT)
    fecha = models.DateTimeField("fecha y hora de realización")
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVA, editable=False)
    puntos_base = models.PositiveSmallIntegerField(default=0, editable=False)
    repetible = models.BooleanField(default=False, editable=False)
    puntos = models.PositiveSmallIntegerField("puntos otorgados", default=0, editable=False)
    carga = models.JSONField(default=dict, editable=False)
    actor_original = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="actividades_realizadas", editable=False)
    detalles = models.TextField("nota", max_length=1000, blank=True)
    motivo_anulacion = models.TextField(blank=True, editable=False)
    anulada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="actividades_anuladas", null=True, blank=True, editable=False)
    fecha_anulacion = models.DateTimeField(null=True, blank=True, editable=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["huerto", "planta", "estado"], name="actividad_planta_estado")]
        constraints = [
            models.CheckConstraint(name="actividad_estado_valido", condition=models.Q(estado__in=["activa", "anulada"])),
            models.CheckConstraint(name="actividad_planta_segun_tipo", condition=(
                models.Q(tipo__in=["preparacion", "diseno", "ritual"], planta__isnull=True)
                | (~models.Q(tipo__in=["preparacion", "diseno", "ritual"]) & models.Q(planta__isnull=False)))),
            models.UniqueConstraint(fields=["huerto", "tipo"],
                condition=models.Q(estado="activa", repetible=False, planta__isnull=True), name="actividad_general_activa_unica"),
            models.UniqueConstraint(fields=["planta", "tipo"],
                condition=models.Q(estado="activa", repetible=False, planta__isnull=False), name="actividad_planta_activa_unica"),
            models.CheckConstraint(name="actividad_constancia_anulacion", condition=(
                models.Q(estado="activa", motivo_anulacion="", anulada_por__isnull=True, fecha_anulacion__isnull=True)
                | (models.Q(estado="anulada", anulada_por__isnull=False, fecha_anulacion__isnull=False)
                   & ~models.Q(motivo_anulacion="")))),
        ]

    def clean(self):
        super().clean()
        if self.planta_id and self.huerto_id and self.planta.huerto_id != self.huerto_id:
            raise ValidationError({"planta": "La selección no pertenece a este huerto."})

    @property
    def es_activa(self):
        return self.estado == self.Estado.ACTIVA

    @property
    def es_anulada(self):
        return not self.es_activa

    @property
    def nombre_planta(self):
        return self.planta.planta.nombre_comun if self.planta_id else "Todo el huerto"

    def get_tipo_display(self):
        return self.tipo.nombre

    def __str__(self):
        return f"{self.tipo} · {self.nombre_planta} · {self.fecha}"
