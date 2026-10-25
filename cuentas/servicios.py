from datetime import date

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .aviso import AVISO_DATOS_VERSION
from .models import Usuario


def registrar_usuario(
    *,
    username: str,
    password: str,
    nombre_completo: str,
    fecha_nacimiento: date,
    acepta_aviso: bool,
    aviso_version: str,
    genero: str = "",
    talentos_ancestrales: str = "",
) -> Usuario:
    """Valida y guarda una cuenta con la constancia del aviso aceptado."""
    if acepta_aviso is not True:
        raise ValidationError(
            {"acepta_aviso": "Para crear tu cuenta debes aceptar el aviso de datos."}
        )
    if aviso_version != AVISO_DATOS_VERSION:
        raise ValidationError(
            "El aviso de datos cambió. Vuelve a cargar la página y revísalo."
        )

    usuario = Usuario(
        username=username.strip(),
        nombre_completo=nombre_completo.strip(),
        fecha_nacimiento=fecha_nacimiento,
        genero=genero,
        talentos_ancestrales=talentos_ancestrales.strip(),
        consentimiento_fecha=timezone.now(),
        consentimiento_version=AVISO_DATOS_VERSION,
    )
    usuario.full_clean(exclude=["password"])

    try:
        validate_password(password, user=usuario)
    except ValidationError as error:
        raise ValidationError({"password1": error.messages}) from error

    # El hash se calcula antes de abrir la transacción de escritura.
    usuario.set_password(password)
    try:
        with transaction.atomic():
            usuario.save()
    except IntegrityError as error:
        # Otra solicitud pudo ocupar el usuario después de su validación.
        if Usuario.objects.filter(username=usuario.username).exists():
            raise ValidationError(
                {"username": "Ya existe una cuenta con este usuario."}
            ) from error
        raise

    return usuario


def actualizar_perfil(
    *,
    actor: Usuario,
    nombre_completo: str,
    fecha_nacimiento: date,
    genero: str = "",
    talentos_ancestrales: str = "",
) -> Usuario:
    """Actualiza únicamente el perfil de la persona que actúa desde la sesión."""
    if not actor.is_authenticated or not actor.is_active or actor.pk is None:
        raise PermissionDenied("Debes iniciar sesión para editar tu perfil.")

    with transaction.atomic():
        try:
            usuario = Usuario.objects.get(pk=actor.pk, is_active=True)
        except Usuario.DoesNotExist as error:
            raise PermissionDenied("La cuenta no está disponible.") from error

        usuario.nombre_completo = nombre_completo.strip()
        usuario.fecha_nacimiento = fecha_nacimiento
        usuario.genero = genero
        usuario.talentos_ancestrales = talentos_ancestrales.strip()
        usuario.full_clean()
        # No sobrescribir contraseña, permisos ni constancia de consentimiento.
        usuario.save(
            update_fields=[
                "nombre_completo",
                "fecha_nacimiento",
                "genero",
                "talentos_ancestrales",
            ]
        )

    return usuario
