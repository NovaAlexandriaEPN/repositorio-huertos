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
