import re
import sqlite3
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import F

from .models import Comunidad, Miembro


def _exigir_actor_activo(actor):
    """No confiar en un ID enviado por el formulario ni en una cuenta desactivada."""
    if (
        not actor.is_authenticated
        or not actor.is_active
        or actor.pk is None
        or not get_user_model().objects.filter(pk=actor.pk, is_active=True).exists()
    ):
        raise PermissionDenied("Debes iniciar sesión con una cuenta activa.")


def _exigir_sin_comunidad(actor):
    # También protege una cuenta responsable si sus datos antiguos no tienen Miembro.
    if (
        Miembro.objects.filter(usuario_id=actor.pk).exists()
        or Comunidad.objects.filter(responsable_id=actor.pk).exists()
    ):
        raise ValidationError("Ya perteneces a una comunidad. En esta versión no se cambia de comunidad.")


@contextmanager
def _escritura_atomica():
    """Confirmar la operación completa o revertirla antes de comunicar un conflicto."""
    try:
        with transaction.atomic():
            yield
    except IntegrityError as error:
        raise ValidationError(
            "No se pudo guardar la operación. Actualiza la página y comprueba "
            "si ya perteneces a una comunidad antes de intentarlo de nuevo."
        ) from error
    except OperationalError as error:
        codigo = getattr(error.__cause__, "sqlite_errorcode", None)
        if codigo is not None and (codigo & 0xFF) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            raise ValidationError(
                "La base de datos está ocupada. Espera un momento e inténtalo de nuevo."
            ) from error
        raise


def obtener_comunidad(*, actor) -> Comunidad | None:
    """Consultar únicamente la comunidad a la que pertenece la cuenta de la sesión."""
    _exigir_actor_activo(actor)
    return Comunidad.objects.filter(miembros__usuario_id=actor.pk).first()


def obtener_comunidad_editable(*, actor) -> Comunidad:
    comunidad = obtener_comunidad(actor=actor)
    if comunidad is None or comunidad.responsable_id != actor.pk:
        raise PermissionDenied("Solo el responsable puede editar su comunidad.")
    return comunidad


def listar_miembros(*, actor):
    """Proyección pública: no devuelve perfiles, nacimientos ni géneros ajenos."""
    comunidad = obtener_comunidad(actor=actor)
    if comunidad is None:
        return []
    return list(
        Miembro.objects.filter(comunidad=comunidad)
        .order_by("usuario__nombre_completo", "pk")
        .values("usuario_id", nombre=F("usuario__nombre_completo"))
    )


def crear_comunidad(
    *, actor, nombre: str, tipo: str, contacto_nombre: str,
    contacto_telefono: str, contacto_correo: str,
) -> Comunidad:
    """Crear la comunidad y la pertenencia de su responsable en una operación."""
    with _escritura_atomica():
        _exigir_actor_activo(actor)
        _exigir_sin_comunidad(actor)
        comunidad = Comunidad(
            responsable_id=actor.pk,
            nombre=nombre.strip(),
            tipo=tipo,
            contacto_nombre=contacto_nombre.strip(),
            contacto_telefono=contacto_telefono.strip(),
            contacto_correo=contacto_correo.strip(),
        )
        comunidad.full_clean()
        comunidad.save()
        miembro = Miembro(usuario_id=actor.pk, comunidad=comunidad)
        miembro.full_clean()
        miembro.save()
    # El huerto se creará al completar su configuración, en B2-03.
    return comunidad


def unirse_comunidad(*, actor, codigo_invitacion: str) -> Miembro:
    with _escritura_atomica():
        _exigir_actor_activo(actor)
        _exigir_sin_comunidad(actor)
        codigo = codigo_invitacion.strip().upper()
        if not re.fullmatch(r"[A-F0-9]{12}", codigo):
            raise ValidationError({"codigo_invitacion": "El código de invitación no es válido."})
        comunidad = Comunidad.objects.filter(codigo_invitacion=codigo).first()
        if comunidad is None:
            raise ValidationError({"codigo_invitacion": "No se encontró una comunidad con ese código."})
        miembro = Miembro(usuario_id=actor.pk, comunidad=comunidad)
        miembro.full_clean()
        miembro.save()
    return miembro


def editar_comunidad(
    *, actor, nombre: str, tipo: str, contacto_nombre: str,
    contacto_telefono: str, contacto_correo: str,
) -> Comunidad:
    with _escritura_atomica():
        # Se vuelve a consultar: no se guarda una instancia elegida por el navegador.
        comunidad = obtener_comunidad_editable(actor=actor)
        comunidad.nombre = nombre.strip()
        comunidad.tipo = tipo
        comunidad.contacto_nombre = contacto_nombre.strip()
        comunidad.contacto_telefono = contacto_telefono.strip()
        comunidad.contacto_correo = contacto_correo.strip()
        comunidad.full_clean()
        comunidad.save(update_fields=[
            "nombre", "tipo", "contacto_nombre", "contacto_telefono", "contacto_correo",
        ])
    return comunidad
