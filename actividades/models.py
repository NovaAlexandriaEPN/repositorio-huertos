"""
Modelo Actividad del módulo actividades.

Cada fila es una labor registrada en el huerto de una comunidad. Las actividades no se
borran: al anular se cambia el estado y se guarda la constancia (motivo, autor y fecha),
de modo que el historial y el actor original se conservan.

Contrato con comunidades (README, sección "Contrato con actividades"):
    - `planta` apunta a la selección `comunidades.PlantaHuerto`, no a la especie del
      catálogo, con `related_name="actividades"` y `on_delete=PROTECT`.
    - `PlantaHuerto.tiene_historial` usa esa relación inversa (activas y anuladas).
Los puntos y el nivel no se guardan en `Miembro`: se calculan sumando los puntos de las
actividades activas de cada persona (ver `actividades/servicios.py`).
"""
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Actividad(models.Model):
    """Una labor de cultivo o ancestral realizada en un huerto comunitario."""

    class Tipo(models.TextChoices):
        PREPARACION = "preparacion", "Preparación del terreno"
        SIEMBRA = "siembra", "Siembra"
        RIEGO = "riego", "Riego"
        CUIDADO = "cuidado", "Cuidado y deshierbe"
        ABONO = "abono", "Abonado orgánico"
        ASOCIACION = "asociacion", "Asociación de cultivos"
        PODA = "poda", "Poda y mantenimiento"
        CONTROL_PLAGAS = "control_plagas", "Control ecológico de plagas"
        COSECHA = "cosecha", "Cosecha"
        SECADO = "secado", "Secado"
        PROCESAMIENTO = "procesamiento", "Procesamiento y almacenamiento"
        DISENO = "diseno", "Diseño del huerto"
        RITUAL = "ritual", "Ritual ancestral"

    class Estado(models.TextChoices):
        ACTIVA = "activa", "Activa"
        ANULADA = "anulada", "Anulada"

    # Los seis hitos del ciclo de una planta (CP-05 a CP-07 y HU-10).
    HITOS = (
        Tipo.PREPARACION, Tipo.SIEMBRA, Tipo.RIEGO,
        Tipo.CUIDADO, Tipo.COSECHA, Tipo.SECADO,
    )
    # Actividades generales del huerto: no se asocian a una planta.
    TIPOS_GENERALES = (Tipo.DISENO, Tipo.RITUAL)

    uuid = models.UUIDField(
        "identificador de envío", default=uuid.uuid4, unique=True, editable=False,
        help_text="Evita duplicar la actividad o sus puntos si el formulario se reenvía.",
    )
    huerto = models.ForeignKey(
        "comunidades.Huerto", on_delete=models.PROTECT, related_name="actividades",
    )
    planta = models.ForeignKey(
        "comunidades.PlantaHuerto",
        on_delete=models.PROTECT,
        related_name="actividades",
        null=True,
        blank=True,
        verbose_name="planta del huerto",
    )
    tipo = models.CharField("tipo", max_length=20, choices=Tipo.choices)
    fecha = models.DateField("fecha de realización")
    estado = models.CharField(
        "estado", max_length=10, choices=Estado.choices, default=Estado.ACTIVA,
        editable=False,
    )
    puntos = models.PositiveSmallIntegerField("puntos otorgados", default=0, editable=False)
    actor_original = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actividades_realizadas",
        editable=False,
    )
    detalles = models.TextField("observaciones", blank=True)

    # Constancia de la anulación: los tres campos se guardan juntos.
    motivo_anulacion = models.TextField("motivo de la anulación", blank=True, editable=False)
    anulada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="actividades_anuladas",
        null=True, blank=True, editable=False,
    )
    fecha_anulacion = models.DateTimeField(
        "fecha de la anulación", null=True, blank=True, editable=False
    )
    fecha_registro = models.DateTimeField("fecha de registro", auto_now_add=True)

    class Meta:
        verbose_name = "actividad"
        verbose_name_plural = "actividades"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["huerto", "planta", "estado"], name="actividad_planta_estado"),
        ]
        constraints = [
            models.CheckConstraint(
                name="actividad_tipo_valido",
                condition=models.Q(tipo__in=[
                    "preparacion", "siembra", "riego", "cuidado", "abono", "asociacion", "poda",
                    "control_plagas", "cosecha", "secado", "procesamiento", "diseno", "ritual",
                ]),
                violation_error_message="El tipo de actividad no es válido.",
            ),
            models.CheckConstraint(
                name="actividad_estado_valido",
                condition=models.Q(estado__in=["activa", "anulada"]),
                violation_error_message="El estado de la actividad no es válido.",
            ),
            models.CheckConstraint(
                name="actividad_planta_segun_tipo",
                condition=(
                    models.Q(tipo__in=["diseno", "ritual"], planta__isnull=True)
                    | (~models.Q(tipo__in=["diseno", "ritual"]) & models.Q(planta__isnull=False))
                ),
                violation_error_message=(
                    "Diseño y ritual son actividades generales; las demás se registran sobre una planta."
                ),
            ),
            models.CheckConstraint(
                name="actividad_constancia_anulacion",
                condition=(
                    models.Q(
                        estado="activa",
                        motivo_anulacion="",
                        anulada_por__isnull=True,
                        fecha_anulacion__isnull=True,
                    )
                    | (
                        models.Q(
                            estado="anulada",
                            anulada_por__isnull=False,
                            fecha_anulacion__isnull=False,
                        )
                        & ~models.Q(motivo_anulacion="")
                    )
                ),
                violation_error_message="La anulación guarda motivo, autor y fecha juntos.",
            ),
        ]

    def clean(self):
        super().clean()
        if self.planta_id and self.huerto_id and self.planta.huerto_id != self.huerto_id:
            raise ValidationError({"planta": "La planta no pertenece a este huerto."})

    @property
    def es_activa(self) -> bool:
        return self.estado == self.Estado.ACTIVA

    @property
    def es_anulada(self) -> bool:
        return self.estado == self.Estado.ANULADA

    @property
    def es_hito(self) -> bool:
        return self.tipo in self.HITOS

    @property
    def nombre_planta(self) -> str:
        """Nombre común de la especie, o una etiqueta para las actividades generales."""
        if self.planta_id:
            return self.planta.planta.nombre_comun
        return "Todo el huerto"

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} · {self.nombre_planta} · {self.fecha} ({self.estado})"
