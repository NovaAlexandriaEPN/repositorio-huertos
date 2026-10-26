import re
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import F, Prefetch
from django.db.models.deletion import ProtectedError

from catalogo.models import Material, OpcionHuerto, Planta

from .models import Comunidad, Huerto, MarcaMaterial, Miembro, PlantaHuerto


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
            "No se pudo guardar la operación porque los datos entraron en conflicto. "
            "Actualiza la página y comprueba el resultado antes de intentarlo de nuevo."
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


def obtener_huerto(*, actor) -> Huerto | None:
    """Consultar el huerto propio y sus selecciones sin aceptar IDs de otra comunidad."""
    comunidad = obtener_comunidad(actor=actor)
    if comunidad is None:
        return None
    return (
        Huerto.objects.filter(comunidad=comunidad)
        .select_related("cerca", "suelo", "fuente_agua")
        .prefetch_related(
            "disenos", "abonos",
            Prefetch(
                "plantas",
                queryset=PlantaHuerto.objects.select_related("planta").order_by(
                    "planta__nombre_comun", "pk"
                ),
            ),
        )
        .first()
    )


def _opciones_multiples_validas(
    opciones: Iterable[OpcionHuerto], *, categoria: str, campo: str,
) -> list[OpcionHuerto]:
    opciones = list(opciones)
    if not opciones or any(
        not isinstance(opcion, OpcionHuerto) or opcion.pk is None for opcion in opciones
    ):
        raise ValidationError({campo: "Selecciona al menos una opción válida."})
    identificadores = {opcion.pk for opcion in opciones}
    guardadas = list(OpcionHuerto.objects.filter(pk__in=identificadores, categoria=categoria))
    if len(guardadas) != len(identificadores):
        raise ValidationError({campo: "Todas las opciones deben ser de la categoría correspondiente."})
    return guardadas


def configurar_huerto(
    *, actor, provincia: str, parroquia: str, direccion: str, area_m2: Decimal,
    disenos: Iterable[OpcionHuerto], cerca: OpcionHuerto, suelo: OpcionHuerto,
    fuente_agua: OpcionHuerto, abonos: Iterable[OpcionHuerto],
) -> Huerto:
    """Crear o actualizar la configuración y sus relaciones como una sola operación."""
    with _escritura_atomica():
        comunidad = obtener_comunidad_editable(actor=actor)
        disenos_validos = _opciones_multiples_validas(
            disenos, categoria=OpcionHuerto.Categoria.DISENO, campo="disenos"
        )
        abonos_validos = _opciones_multiples_validas(
            abonos, categoria=OpcionHuerto.Categoria.ABONO, campo="abonos"
        )
        huerto = Huerto.objects.filter(comunidad=comunidad).first()
        if huerto is None:
            huerto = Huerto(comunidad=comunidad)
        huerto.provincia = provincia.strip()
        huerto.parroquia = parroquia.strip()
        huerto.direccion = direccion.strip()
        huerto.area_m2 = area_m2
        huerto.cerca = cerca
        huerto.suelo = suelo
        huerto.fuente_agua = fuente_agua
        huerto.full_clean()
        if huerto.pk:
            huerto.save(update_fields=[
                "provincia", "parroquia", "direccion", "area_m2",
                "cerca", "suelo", "fuente_agua",
            ])
        else:
            huerto.save()
        huerto.disenos.set(disenos_validos)
        huerto.abonos.set(abonos_validos)
    return huerto


def _huerto_editable(*, actor) -> Huerto:
    comunidad = obtener_comunidad_editable(actor=actor)
    huerto = Huerto.objects.filter(comunidad=comunidad).first()
    if huerto is None:
        raise ValidationError("Configura el huerto antes de elegir plantas.")
    return huerto


def obtener_seleccion_editable(*, actor, seleccion_id: int) -> PlantaHuerto:
    huerto = _huerto_editable(actor=actor)
    # Un ID válido de otra comunidad tampoco permite consultar ni modificar la selección.
    return PlantaHuerto.objects.select_related("planta").get(pk=seleccion_id, huerto=huerto)


def elegir_planta(*, actor, planta: Planta, metodo_siembra: str) -> PlantaHuerto:
    with _escritura_atomica():
        huerto = _huerto_editable(actor=actor)
        seleccion = PlantaHuerto(huerto=huerto, planta=planta, metodo_siembra=metodo_siembra)
        seleccion.full_clean()
        seleccion.save()
    return seleccion


def cambiar_metodo_siembra(*, actor, seleccion_id: int, metodo_siembra: str) -> PlantaHuerto:
    with _escritura_atomica():
        seleccion = obtener_seleccion_editable(actor=actor, seleccion_id=seleccion_id)
        if seleccion.tiene_historial:
            raise ValidationError("No se cambia el método de una selección con historial, incluso anulado.")
        seleccion.metodo_siembra = metodo_siembra
        seleccion.full_clean()
        seleccion.save(update_fields=["metodo_siembra"])
    return seleccion


def retirar_planta(*, actor, seleccion_id: int) -> None:
    with _escritura_atomica():
        seleccion = obtener_seleccion_editable(actor=actor, seleccion_id=seleccion_id)
        if seleccion.tiene_historial:
            raise ValidationError("No se retira una selección con historial, incluso anulado.")
        try:
            seleccion.delete()
        except ProtectedError as error:
            raise ValidationError("No se retira una selección que conserva registros relacionados.") from error


def _huerto_del_miembro(*, actor) -> Huerto:
    """Los materiales permiten actuar a todos los miembros, no solo al responsable."""
    huerto = obtener_huerto(actor=actor)
    if huerto is None:
        if obtener_comunidad(actor=actor) is None:
            raise PermissionDenied("Debes pertenecer a una comunidad para consultar sus materiales.")
        raise ValidationError("El responsable debe configurar el huerto antes de usar sus materiales.")
    return huerto


def _metodos_del_huerto(huerto: Huerto) -> set[str]:
    return {seleccion.metodo_siembra for seleccion in huerto.plantas.all()}


def _material_corresponde(material: Material, metodos: set[str]) -> bool:
    return not material.metodos_siembra or bool(set(material.metodos_siembra) & metodos)


def listar_materiales(*, actor) -> list[dict]:
    """Recomendaciones y disponibilidad del huerto propio, sin crear marcas al leer."""
    huerto = _huerto_del_miembro(actor=actor)
    metodos = _metodos_del_huerto(huerto)
    marcas = dict(
        MarcaMaterial.objects.filter(huerto=huerto).values_list("material_id", "disponible")
    )
    # El catálogo es pequeño; se filtra en Python para mantener compatibilidad con SQLite.
    return [
        {"material": material, "disponible": marcas.get(material.pk, False)}
        for material in Material.objects.all()
        if _material_corresponde(material, metodos)
    ]


def marcar_material(*, actor, material_id: int, disponible: bool) -> MarcaMaterial:
    """Guardar un valor explícito compartido; reenviar no invierte ni duplica la marca."""
    with _escritura_atomica():
        huerto = _huerto_del_miembro(actor=actor)
        if not isinstance(disponible, bool):
            raise ValidationError({"disponible": "Indica si el material está disponible."})
        material = Material.objects.get(pk=material_id)
        if not _material_corresponde(material, _metodos_del_huerto(huerto)):
            raise Material.DoesNotExist("El material no corresponde a los métodos del huerto.")
        marca = MarcaMaterial.objects.filter(huerto=huerto, material=material).first()
        if marca is None:
            marca = MarcaMaterial(huerto=huerto, material=material)
        marca.disponible = disponible
        marca.full_clean()
        if marca.pk:
            marca.save(update_fields=["disponible"])
        else:
            marca.save()
    return marca
