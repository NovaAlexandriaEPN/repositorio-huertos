from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Cuenta de acceso y datos personales del participante."""

    class Genero(models.TextChoices):
        NO_INDICA = "", "Prefiero no indicarlo"
        FEMENINO = "femenino", "Femenino"
        MASCULINO = "masculino", "Masculino"
        NO_BINARIO = "no_binario", "No binario"
        OTRO = "otro", "Otro"

    nombre_completo = models.CharField("nombre completo", max_length=150)
    fecha_nacimiento = models.DateField(
        "fecha de nacimiento",
        validators=[
            MaxValueValidator(
                timezone.localdate,
                message="La fecha de nacimiento no puede estar en el futuro.",
            ),
        ],
    )
    genero = models.CharField(
        "género",
        max_length=20,
        choices=Genero.choices,
        default=Genero.NO_INDICA,
        blank=True,
    )
    talentos_ancestrales = models.TextField("talentos ancestrales", blank=True)

    # El servicio de registro completa ambos datos después de la aceptación.
    consentimiento_fecha = models.DateTimeField(
        "fecha de consentimiento", null=True, blank=True, editable=False
    )
    consentimiento_version = models.CharField(
        "versión del aviso aceptado", max_length=30, blank=True, editable=False
    )

    REQUIRED_FIELDS = ["nombre_completo", "fecha_nacimiento"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="cuentas_usuario_consentimiento_completo",
                condition=(
                    models.Q(
                        consentimiento_fecha__isnull=True,
                        consentimiento_version="",
                    )
                    | (
                        models.Q(consentimiento_fecha__isnull=False)
                        & ~models.Q(consentimiento_version="")
                    )
                ),
                violation_error_message=(
                    "La fecha y la versión del consentimiento deben registrarse juntas."
                ),
            ),
        ]

    def get_full_name(self) -> str:
        """Usa el nombre completo del perfil en las consultas de Django."""
        return self.nombre_completo
