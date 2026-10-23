"""
Modelos de la aplicación actividades.
Define el modelo Actividad con todas las restricciones de base de datos,
estados, puntos, trazabilidad de actor original y auditoría de anulación.
"""
import uuid
from django.conf import settings
from django.db import models


class Actividad(models.Model):
    """
    Registra una actividad de cultivo o ancestral en el huerto comunitario.
    Soporta 13 tipos de actividades, cálculo de recompensas, trazabilidad
    del actor original y anulación controlada con auditoría (motivo, autor, fecha).
    """

    # 13 tipos de actividades del huerto medicinal comunitario
    TIPO_PREPARACION = 'preparacion'
    TIPO_SIEMBRA = 'siembra'
    TIPO_RIEGO = 'riego'
    TIPO_CUIDADO = 'cuidado'
    TIPO_ABONO = 'abono'
    TIPO_ASOCIACION = 'asociacion'
    TIPO_PODA = 'poda'
    TIPO_CONTROL_PLAGAS = 'control_plagas'
    TIPO_COSECHA = 'cosecha'
    TIPO_SECADO = 'secado'
    TIPO_PROCESAMIENTO = 'procesamiento'
    TIPO_DISENO = 'diseno'
    TIPO_RITUAL = 'ritual'

    TIPO_ACTIVIDAD_CHOICES = [
        (TIPO_PREPARACION, 'Preparación de terreno'),
        (TIPO_SIEMBRA, 'Siembra'),
        (TIPO_RIEGO, 'Riego'),
        (TIPO_CUIDADO, 'Cuidado cultural / Deshierbe'),
        (TIPO_ABONO, 'Fertilización / Abonado orgánico'),
        (TIPO_ASOCIACION, 'Asociación de cultivos'),
        (TIPO_PODA, 'Poda y mantenimiento'),
        (TIPO_CONTROL_PLAGAS, 'Control ecológico de plagas'),
        (TIPO_COSECHA, 'Cosecha / Recolección'),
        (TIPO_SECADO, 'Secado tradicional'),
        (TIPO_PROCESAMIENTO, 'Procesamiento / Almacenamiento'),
        (TIPO_DISENO, 'Diseño del huerto'),
        (TIPO_RITUAL, 'Ritual ancestral y agradecimiento'),
    ]

    ESTADO_ACTIVA = 'ACTIVA'
    ESTADO_ANULADA = 'ANULADA'

    ESTADO_CHOICES = [
        (ESTADO_ACTIVA, 'Activa'),
        (ESTADO_ANULADA, 'Anulada'),
    ]

    # Identificador único universal para evitar duplicados en reenvíos (idempotencia)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        db_index=True,
        verbose_name="UUID de idempotencia"
    )

    huerto = models.ForeignKey(
        'comunidades.Huerto',
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name="Huerto"
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_ACTIVIDAD_CHOICES,
        verbose_name="Tipo de actividad"
    )

    # Puede ser una de las 18 especies medicinales o vacío para actividades generales (diseño, ritual)
    planta = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="Planta medicinal",
        help_text="Especie medicinal asociada (o vacío para diseño y ritual)."
    )

    fecha = models.DateField(
        verbose_name="Fecha de realización"
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=ESTADO_ACTIVA,
        db_index=True,
        verbose_name="Estado"
    )

    puntos = models.PositiveIntegerField(
        default=0,
        verbose_name="Puntos otorgados"
    )

    # Actor original: el usuario que ejecutó la labor; se conserva intacto al anular
    actor_original = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='actividades_registradas',
        verbose_name="Actor original"
    )

    detalles = models.TextField(
        blank=True,
        default='',
        verbose_name="Detalles u observaciones"
    )

    # Auditoría de anulación
    motivo_anulacion = models.TextField(
        blank=True,
        default='',
        verbose_name="Motivo de anulación"
    )
    autor_anulacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actividades_anuladas',
        verbose_name="Autor de la anulación"
    )
    fecha_anulacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de anulación"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['-fecha', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['uuid'],
                name='unique_actividad_uuid'
            ),
            models.CheckConstraint(
                check=models.Q(puntos__gte=0),
                name='actividad_puntos_no_negativos'
            ),
            models.CheckConstraint(
                check=models.Q(estado__in=['ACTIVA', 'ANULADA']),
                name='actividad_estado_valido'
            ),
        ]

    def __str__(self):
        info = f"{self.get_tipo_display()}"
        if self.planta:
            info += f" en {self.planta}"
        info += f" ({self.fecha}) - {self.estado}"
        return info

    @property
    def es_activa(self):
        return self.estado == self.ESTADO_ACTIVA

    @property
    def es_anulada(self):
        return self.estado == self.ESTADO_ANULADA
