import secrets
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from catalogo.models import MetodoSiembra, OpcionHuerto


def generar_codigo_invitacion() -> str:
    """Genera 12 caracteres hexadecimales con aleatoriedad criptográfica."""
    return secrets.token_hex(6).upper()


class Comunidad(models.Model):
    """Grupo que comparte un huerto y tiene un único responsable."""

    class Tipo(models.TextChoices):
        PERSONA = "persona", "Persona"
        FAMILIA = "familia", "Familia"
        CONDOMINIO = "condominio", "Condominio"
        BARRIO = "barrio", "Barrio"

    nombre = models.CharField("nombre", max_length=150)
    tipo = models.CharField("tipo", max_length=15, choices=Tipo.choices)
    responsable = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comunidad_a_cargo",
        editable=False,
    )
    contacto_nombre = models.CharField("nombre de contacto", max_length=150)
    contacto_telefono = models.CharField(
        "teléfono de contacto",
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^\+?(?:[ ()-]*[0-9]){7,15}[ ()-]*$",
                message="Escribe un teléfono de 7 a 15 dígitos; admite + inicial, espacios, paréntesis y guiones.",
            ),
        ],
    )
    contacto_correo = models.EmailField("correo de contacto")
    codigo_invitacion = models.CharField(
        "código de invitación",
        max_length=12,
        unique=True,
        default=generar_codigo_invitacion,
        editable=False,
        validators=[RegexValidator(r"^[A-F0-9]{12}$", "El código debe tener 12 caracteres hexadecimales.")],
    )

    class Meta:
        verbose_name_plural = "comunidades"
        constraints = [
            models.CheckConstraint(
                name="comunidad_tipo_valido",
                condition=models.Q(tipo__in=["persona", "familia", "condominio", "barrio"]),
                violation_error_message="El tipo de comunidad no es válido.",
            ),
        ]

    def clean(self):
        super().clean()
        errores = {}
        if self.pk:
            anterior = Comunidad.objects.filter(pk=self.pk).values("responsable_id").first()
            if anterior and anterior["responsable_id"] != self.responsable_id:
                errores["responsable"] = "No se transfiere el responsable en esta versión."
        if self.responsable_id and Miembro.objects.filter(
            usuario_id=self.responsable_id
        ).exclude(comunidad_id=self.pk).exists():
            errores["responsable"] = "El responsable ya pertenece a otra comunidad."
        if errores:
            raise ValidationError(errores)

    def __str__(self) -> str:
        return self.nombre


class Miembro(models.Model):
    """Pertenencia de una cuenta a su única comunidad."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="miembro",
    )
    comunidad = models.ForeignKey(
        Comunidad, on_delete=models.PROTECT, related_name="miembros"
    )

    class Meta:
        verbose_name = "miembro"

    @property
    def es_responsable(self) -> bool:
        return self.usuario_id == self.comunidad.responsable_id

    def clean(self):
        super().clean()
        errores = {}
        if self.pk:
            anterior = Miembro.objects.filter(pk=self.pk).values(
                "usuario_id", "comunidad_id"
            ).first()
            if anterior:
                if anterior["usuario_id"] != self.usuario_id:
                    errores["usuario"] = "La pertenencia no se reasigna a otra cuenta."
                if anterior["comunidad_id"] != self.comunidad_id:
                    errores["comunidad"] = "No se trasladan miembros entre comunidades en esta versión."
        if self.usuario_id and Comunidad.objects.filter(
            responsable_id=self.usuario_id
        ).exclude(pk=self.comunidad_id).exists():
            errores["comunidad"] = "El responsable debe pertenecer a la comunidad que tiene a cargo."
        if errores:
            raise ValidationError(errores)

    def __str__(self) -> str:
        return f"Miembro {self.usuario_id} de comunidad {self.comunidad_id}"


class Huerto(models.Model):
    """Configuración del huerto y constancia de su maestro vigente, si lo hay."""

    comunidad = models.OneToOneField(
        Comunidad, on_delete=models.PROTECT, related_name="huerto"
    )
    provincia = models.CharField("provincia", max_length=100)
    parroquia = models.CharField("parroquia", max_length=100)
    direccion = models.CharField("dirección", max_length=255)
    area_m2 = models.DecimalField(
        "área en m²",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    disenos = models.ManyToManyField(
        OpcionHuerto,
        related_name="huertos_con_diseno",
        limit_choices_to={"categoria": OpcionHuerto.Categoria.DISENO},
        verbose_name="diseños",
    )
    abonos = models.ManyToManyField(
        OpcionHuerto,
        related_name="huertos_con_abono",
        limit_choices_to={"categoria": OpcionHuerto.Categoria.ABONO},
        verbose_name="abonos",
    )
    cerca = models.ForeignKey(
        OpcionHuerto,
        on_delete=models.PROTECT,
        related_name="huertos_con_cerca",
        limit_choices_to={"categoria": OpcionHuerto.Categoria.CERCA},
    )
    suelo = models.ForeignKey(
        OpcionHuerto,
        on_delete=models.PROTECT,
        related_name="huertos_con_suelo",
        limit_choices_to={"categoria": OpcionHuerto.Categoria.SUELO},
    )
    fuente_agua = models.ForeignKey(
        OpcionHuerto,
        on_delete=models.PROTECT,
        related_name="huertos_con_agua",
        limit_choices_to={"categoria": OpcionHuerto.Categoria.AGUA},
        verbose_name="fuente de agua",
    )

    # El nombramiento se realiza desde actividades, con sus reglas y transacción.
    maestro = models.ForeignKey(
        Miembro, on_delete=models.PROTECT, related_name="huertos_como_maestro",
        null=True, blank=True, editable=False,
    )
    maestro_motivo = models.TextField("motivo del nombramiento", blank=True, editable=False)
    maestro_nombrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="nombramientos_de_maestro",
        null=True, blank=True, editable=False,
    )
    maestro_fecha = models.DateTimeField(
        "fecha del nombramiento", null=True, blank=True, editable=False
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="huerto_area_positiva",
                condition=models.Q(area_m2__gt=0),
                violation_error_message="El área debe ser mayor que cero.",
            ),
            models.CheckConstraint(
                name="huerto_maestro_constancia_completa",
                condition=(
                    models.Q(
                        maestro__isnull=True,
                        maestro_motivo="",
                        maestro_nombrado_por__isnull=True,
                        maestro_fecha__isnull=True,
                    )
                    | (
                        models.Q(
                            maestro__isnull=False,
                            maestro_nombrado_por__isnull=False,
                            maestro_fecha__isnull=False,
                        )
                        & ~models.Q(maestro_motivo="")
                    )
                ),
                violation_error_message="El maestro y la constancia de su nombramiento deben guardarse juntos.",
            ),
        ]

    def clean(self):
        super().clean()
        errores = {}
        for campo, categoria in (
            ("cerca", OpcionHuerto.Categoria.CERCA),
            ("suelo", OpcionHuerto.Categoria.SUELO),
            ("fuente_agua", OpcionHuerto.Categoria.AGUA),
        ):
            identificador = getattr(self, campo + "_id")
            if identificador and not OpcionHuerto.objects.filter(
                pk=identificador, categoria=categoria
            ).exists():
                errores[campo] = "Selecciona una opción de la categoría correspondiente."

        if self.pk:
            anterior = Huerto.objects.filter(pk=self.pk).values("comunidad_id").first()
            if anterior and anterior["comunidad_id"] != self.comunidad_id:
                errores["comunidad"] = "No se traslada un huerto a otra comunidad."
        if self.maestro_id:
            if not Miembro.objects.filter(
                pk=self.maestro_id, comunidad_id=self.comunidad_id
            ).exists():
                errores["maestro"] = "El maestro debe ser miembro de esta comunidad."
            if not self.maestro_motivo.strip():
                errores["maestro_motivo"] = "Explica la capacidad del maestro para guiar la siembra."
            if self.maestro_nombrado_por_id and not Comunidad.objects.filter(
                pk=self.comunidad_id, responsable_id=self.maestro_nombrado_por_id
            ).exists():
                errores["maestro_nombrado_por"] = "El nombramiento corresponde al responsable de la comunidad."
        if errores:
            raise ValidationError(errores)

    def __str__(self) -> str:
        return f"Huerto de comunidad {self.comunidad_id}"


class PlantaHuerto(models.Model):
    """Una especie elegida para un huerto, con un único ciclo en esta versión."""

    huerto = models.ForeignKey(
        Huerto, on_delete=models.PROTECT, related_name="plantas"
    )
    planta = models.ForeignKey(
        "catalogo.Planta", on_delete=models.PROTECT, related_name="selecciones_huerto"
    )
    metodo_siembra = models.CharField(
        "método de siembra", max_length=10, choices=MetodoSiembra.choices
    )

    class Meta:
        verbose_name = "planta del huerto"
        verbose_name_plural = "plantas del huerto"
        constraints = [
            models.UniqueConstraint(
                fields=["huerto", "planta"], name="planta_unica_por_huerto"
            ),
            models.CheckConstraint(
                name="planta_huerto_metodo_valido",
                condition=models.Q(metodo_siembra__in=MetodoSiembra.values),
                violation_error_message="El método de siembra no es válido.",
            ),
        ]

    @property
    def tiene_historial(self) -> bool:
        """Incluye actividades anuladas; el historial no se filtra por estado."""
        if not self.pk:
            return False
        # La relación inversa evita importar el módulo de actividades desde aquí.
        actividades = getattr(self, "actividades", None)
        if actividades is None:
            return False
        # El gestor base conserva también anuladas aunque el gestor habitual las filtre.
        return actividades.model._base_manager.filter(
            **{actividades.field.attname: self.pk}
        ).exists()

    def clean(self):
        super().clean()
        if not self.pk:
            return
        anterior = PlantaHuerto.objects.filter(pk=self.pk).values(
            "huerto_id", "planta_id", "metodo_siembra"
        ).first()
        if not anterior:
            return
        errores = {}
        for campo in ("huerto", "planta"):
            if anterior[campo + "_id"] != getattr(self, campo + "_id"):
                errores[campo] = "La selección conserva su huerto y su especie."
        if anterior["metodo_siembra"] != self.metodo_siembra and self.tiene_historial:
            errores["metodo_siembra"] = "No se cambia el método de una selección con historial."
        if errores:
            raise ValidationError(errores)

    def __str__(self) -> str:
        return f"Planta {self.planta_id} en huerto {self.huerto_id}"


class MarcaMaterial(models.Model):
    """Disponibilidad compartida de un material en un huerto concreto."""

    huerto = models.ForeignKey(
        Huerto, on_delete=models.PROTECT, related_name="marcas_materiales"
    )
    material = models.ForeignKey(
        "catalogo.Material", on_delete=models.PROTECT, related_name="marcas_huertos"
    )
    disponible = models.BooleanField("disponible", default=False)

    class Meta:
        verbose_name = "marca de material"
        verbose_name_plural = "marcas de materiales"
        constraints = [
            models.UniqueConstraint(
                fields=["huerto", "material"], name="material_unico_por_huerto"
            ),
        ]

    def clean(self):
        super().clean()
        if self.pk:
            anterior = MarcaMaterial.objects.filter(pk=self.pk).values(
                "huerto_id", "material_id"
            ).first()
            if anterior:
                errores = {}
                for campo in ("huerto", "material"):
                    if anterior[campo + "_id"] != getattr(self, campo + "_id"):
                        errores[campo] = "La marca conserva su huerto y su material."
                if errores:
                    raise ValidationError(errores)

    def __str__(self) -> str:
        return f"Material {self.material_id} en huerto {self.huerto_id}"
