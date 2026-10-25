from django.core.exceptions import ValidationError
from django.db import models


class OpcionHuerto(models.Model):
    """Una opción fija del configurador, compartida por todos los huertos."""

    class Categoria(models.TextChoices):
        DISENO = "diseno", "Diseño"
        CERCA = "cerca", "Cerca"
        SUELO = "suelo", "Suelo"
        AGUA = "agua", "Fuente de agua"
        ABONO = "abono", "Abono"

    codigo = models.SlugField("código", max_length=60, unique=True)
    categoria = models.CharField(
        "categoría", max_length=10, choices=Categoria.choices
    )
    nombre = models.CharField("nombre", max_length=100)
    explicacion = models.TextField("explicación", blank=True)

    class Meta:
        ordering = ["categoria", "nombre", "pk"]
        verbose_name = "opción de huerto"
        verbose_name_plural = "opciones de huerto"
        constraints = [
            models.CheckConstraint(
                name="catalogo_opcion_categoria_valida",
                condition=models.Q(
                    categoria__in=["diseno", "cerca", "suelo", "agua", "abono"]
                ),
                violation_error_message="La categoría de la opción no es válida.",
            ),
        ]

    def __str__(self) -> str:
        return self.nombre


class MetodoSiembra(models.TextChoices):
    """Códigos compartidos por las selecciones del huerto y los materiales."""

    SEMILLAS = "semillas", "Semillas"
    ESTACAS = "estacas", "Estacas"
    ESQUEJES = "esquejes", "Esquejes"
    PLANTULAS = "plantulas", "Plántulas"


class Planta(models.Model):
    """Una especie del catálogo con los 19 campos del formato de fichas."""

    class Ciclo(models.TextChoices):
        CORTO = "corto", "Corto"
        LARGO = "largo", "Largo"

    class Cualidad(models.TextChoices):
        CALIENTE = "caliente", "Caliente"
        FRIA = "fria", "Fría"

    codigo = models.SlugField("código", max_length=60, unique=True)
    nombre_comun = models.CharField("nombre común", max_length=150)
    # None representa información pendiente, según el contrato de las fichas.
    nombre_cientifico = models.CharField(
        "nombre científico", max_length=200, null=True, blank=True
    )
    otros_nombres = models.JSONField("otros nombres", default=list, blank=True)
    familia = models.CharField("familia", max_length=150, null=True, blank=True)
    altitud_msnm = models.TextField("altitud en msnm", null=True, blank=True)
    provincias_ecuador = models.JSONField("provincias", default=list, blank=True)
    ciclo = models.CharField(
        "ciclo", max_length=10, choices=Ciclo.choices, null=True, blank=True
    )
    cualidad_ancestral = models.CharField(
        "cualidad ancestral", max_length=10, choices=Cualidad.choices,
        null=True, blank=True,
    )
    parte_utilizada = models.JSONField("partes utilizadas", default=list, blank=True)
    usos_documentados = models.TextField("usos documentados", null=True, blank=True)
    contraindicaciones = models.TextField("contraindicaciones", null=True, blank=True)
    imagen_ruta = models.CharField("ruta de imagen", max_length=255, null=True, blank=True)
    imagen_autor = models.CharField("autor de imagen", max_length=255, null=True, blank=True)
    imagen_fuente = models.TextField("fuente de imagen", null=True, blank=True)
    imagen_licencia = models.TextField("licencia de imagen", null=True, blank=True)
    fuentes = models.JSONField("fuentes", default=list, blank=True)
    campos_no_verificados = models.JSONField(
        "campos no verificados", default=list, blank=True
    )
    observaciones = models.TextField("observaciones", blank=True)

    class Meta:
        ordering = ["nombre_comun", "pk"]

    def clean(self):
        super().clean()
        errores = {}
        for campo in (
            "otros_nombres", "provincias_ecuador", "parte_utilizada",
            "campos_no_verificados",
        ):
            valor = getattr(self, campo)
            if not isinstance(valor, list) or not all(isinstance(v, str) for v in valor):
                errores[campo] = "Este campo debe ser una lista de textos."
        if not isinstance(self.fuentes, list) or not all(
            isinstance(fuente, dict) for fuente in self.fuentes
        ):
            errores["fuentes"] = "Las fuentes deben ser una lista de referencias."
        if errores:
            raise ValidationError(errores)

    def __str__(self) -> str:
        return self.nombre_comun


class Material(models.Model):
    """Recomendación común; su disponibilidad se guarda en cada huerto."""

    class Grupo(models.TextChoices):
        HERRAMIENTAS = "herramientas", "Herramientas e implementos"
        SIEMBRA = "siembra", "Material de siembra"
        ABONOS = "abonos", "Abonos"

    codigo = models.SlugField("código", max_length=60, unique=True)
    nombre = models.CharField("nombre", max_length=150)
    grupo = models.CharField("grupo", max_length=15, choices=Grupo.choices)
    recomendacion = models.TextField("recomendación", blank=True)
    metodos_siembra = models.JSONField(
        "métodos de siembra", default=list, blank=True,
        help_text="Una lista vacía indica que sirve para todos los métodos.",
    )

    class Meta:
        ordering = ["grupo", "nombre", "pk"]
        constraints = [
            models.CheckConstraint(
                name="catalogo_material_grupo_valido",
                condition=models.Q(grupo__in=["herramientas", "siembra", "abonos"]),
                violation_error_message="El grupo del material no es válido.",
            ),
        ]

    def clean(self):
        super().clean()
        if not isinstance(self.metodos_siembra, list) or any(
            metodo not in MetodoSiembra.values for metodo in self.metodos_siembra
        ):
            raise ValidationError({
                "metodos_siembra": "Usa una lista de métodos de siembra admitidos."
            })

    def __str__(self) -> str:
        return self.nombre


class TipoActividad(models.Model):
    """Guía fija. Las recompensas históricas se copian a cada actividad."""

    class Codigo(models.TextChoices):
        PREPARACION = "preparacion", "Preparación de la tierra"
        DISENO = "diseno", "Elaboración del diseño"
        RITUAL = "ritual", "Ritual de siembra"
        SIEMBRA = "siembra", "Siembra"
        SENALETICA = "senaletica", "Señalética"
        CUIDADOS = "cuidados", "Cuidados de crecimiento"
        RIEGO = "riego", "Riego"
        BANO = "bano", "Baño de la planta"
        GRATITUD = "gratitud", "Ritual de gratitud"
        COSECHA = "cosecha", "Cosecha"
        LIMPIEZA = "limpieza", "Limpieza de plantas"
        SECADO = "secado", "Secado"
        EMPAQUETADO = "empaquetado", "Empaquetado y etiquetado"

    codigo = models.CharField(max_length=20, choices=Codigo.choices, unique=True)
    nombre = models.CharField(max_length=100)
    alcance = models.CharField(max_length=6, choices=[("huerto", "Huerto"), ("planta", "Planta")])
    puntos_base = models.PositiveSmallIntegerField()
    repetible = models.BooleanField(default=False)
    instrucciones = models.TextField(blank=True)
    materiales = models.TextField(blank=True)
    precauciones = models.TextField(blank=True)
    hora_recomendada = models.TextField(blank=True)
    fase_recomendada = models.TextField(blank=True)
    fuentes = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(codigo__in=[
                "preparacion", "diseno", "ritual", "siembra", "senaletica", "cuidados",
                "riego", "bano", "gratitud", "cosecha", "limpieza", "secado", "empaquetado",
            ]), name="tipo_actividad_codigo_valido"),
            models.CheckConstraint(condition=models.Q(alcance__in=["huerto", "planta"]), name="tipo_actividad_alcance_valido"),
        ]

    def __str__(self):
        return self.nombre


class EventoLunar(models.Model):
    """Instante UTC verificado; no representa una fase inventada para cada día."""

    codigo = models.SlugField(max_length=60, unique=True)
    tipo = models.CharField(max_length=20, choices=[
        ("nueva", "Luna nueva"), ("creciente", "Cuarto creciente"),
        ("llena", "Luna llena"), ("menguante", "Cuarto menguante"),
    ])
    instante = models.DateTimeField()
    fuente = models.URLField(max_length=500)

    class Meta:
        ordering = ["instante", "pk"]

    def __str__(self):
        return f"{self.get_tipo_display()} · {self.instante}"
