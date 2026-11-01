"""Operaciones atómicas y consultas del historial de una comunidad.

SQLite IMMEDIATE serializa estas escrituras cortas. Los permisos y los valores
históricos se resuelven aquí; la vista solo recibe formularios y muestra resultados.
"""
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone as zona_utc

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError, transaction
from django.db.models import Sum
from django.utils import timezone

from catalogo.models import TipoActividad
from comunidades.models import Huerto, Miembro, PlantaHuerto

from .models import Actividad
from .reglas import HITOS, UMBRAL_MAESTRO, calcular_nivel, calcular_progreso

Tipo = Actividad.Tipo
Estado = Actividad.Estado
ACTIVA = Estado.ACTIVA
ESTADOS_PERMITIDOS = {
    Tipo.SIEMBRA: {"planeada"},
    Tipo.SENALETICA: {"sembrada", "creciendo"},
    Tipo.CUIDADOS: {"sembrada", "creciendo"},
    Tipo.RIEGO: {"sembrada", "creciendo"},
    Tipo.BANO: {"creciendo"},
    Tipo.GRATITUD: {"creciendo"},
    Tipo.COSECHA: {"creciendo"},
    Tipo.LIMPIEZA: {"cosechada"},
    Tipo.SECADO: {"cosechada"},
    Tipo.EMPAQUETADO: {"secando"},
}
TRANSICIONES = {
    Tipo.SIEMBRA: "sembrada", Tipo.CUIDADOS: "creciendo", Tipo.RIEGO: "creciendo",
    Tipo.COSECHA: "cosechada", Tipo.SECADO: "secando", Tipo.EMPAQUETADO: "empacada",
}
SIGUIENTE = {
    "planeada": "Preparar la tierra y sembrar al menos 15 días después.",
    "sembrada": "Registrar cuidados de crecimiento o riego.",
    "creciendo": "Continuar cuidados; registrar la cosecha cuando corresponda.",
    "cosechada": "Limpiar las plantas e iniciar el secado a la sombra.",
    "secando": "Empaquetar y etiquetar al menos 10 días después del inicio del secado.",
    "empacada": "Ciclo de esta selección completo.",
}


# Actividad que la tarjeta propone registrar a continuación (solo preselecciona el
# formulario; las reglas de registro siguen decidiendo si se acepta).
TIPO_SUGERIDO = {
    "planeada": Tipo.SIEMBRA, "sembrada": Tipo.CUIDADOS, "secando": Tipo.EMPAQUETADO,
}
@contextmanager
def _escritura_atomica():
    try:
        with transaction.atomic():
            yield
    except IntegrityError as error:
        raise ValidationError("Los datos entraron en conflicto. Actualiza la página y revisa el historial.") from error
    except OperationalError as error:
        codigo = getattr(error.__cause__, "sqlite_errorcode", None)
        if codigo is not None and (codigo & 0xFF) in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
            raise ValidationError("La base está ocupada. Espera un momento e inténtalo de nuevo.") from error
        raise


def _exigir_cuenta_activa(usuario):
    if (not usuario.is_authenticated or not usuario.is_active or not usuario.pk
            or not get_user_model().objects.filter(pk=usuario.pk, is_active=True).exists()):
        raise PermissionDenied("Debes iniciar sesión con una cuenta activa.")


def miembro_del_huerto(usuario, huerto):
    _exigir_cuenta_activa(usuario)
    miembro = Miembro.objects.filter(usuario_id=usuario.pk, comunidad_id=huerto.comunidad_id).first()
    if miembro is None:
        raise PermissionDenied("Este huerto pertenece a otra comunidad.")
    return miembro


def _huerto_actual(huerto, usuario):
    actual = Huerto.objects.select_related("comunidad", "maestro__usuario", "maestro_nombrado_por").get(pk=huerto.pk)
    miembro_del_huerto(usuario, actual)
    return actual


def es_responsable(usuario, huerto):
    return huerto.comunidad.responsable_id == usuario.pk


def huerto_del_usuario(usuario):
    _exigir_cuenta_activa(usuario)
    return Huerto.objects.filter(comunidad__miembros__usuario_id=usuario.pk).select_related("comunidad").first()


def puntos_de_usuario(usuario, huerto):
    return Actividad.objects.filter(huerto=huerto, actor_original_id=usuario.pk, estado=ACTIVA).aggregate(total=Sum("puntos"))["total"] or 0


def puntos_por_usuario(huerto):
    filas = Actividad.objects.filter(huerto=huerto, estado=ACTIVA).values("actor_original_id").annotate(total=Sum("puntos"))
    return {fila["actor_original_id"]: fila["total"] for fila in filas}


def _estado(actividades):
    estado = "planeada"
    for actividad in actividades:
        estado = TRANSICIONES.get(actividad.tipo_id, estado)
    return estado


def _normalizar_fecha(fecha):
    if not isinstance(fecha, datetime) or timezone.is_naive(fecha):
        raise ValidationError("Indica una fecha y hora válidas con zona horaria.")
    return fecha.astimezone(zona_utc.utc)


def registrar_actividad(huerto, usuario, tipo, fecha, planta=None, detalles="", request_uuid=None):
    """Devuelve (registro, creado). Un reenvío idéntico devuelve incluso un registro anulado."""
    fecha = _normalizar_fecha(fecha)
    if not isinstance(detalles, str):
        raise ValidationError("La nota debe ser un texto.")
    detalles = detalles.strip()
    tipo_codigo = tipo.codigo if isinstance(tipo, TipoActividad) else tipo
    try:
        envio = uuid.UUID(str(request_uuid)) if request_uuid is not None else uuid.uuid4()
    except (ValueError, TypeError, AttributeError) as error:
        raise ValidationError("El identificador del envío no es válido. Recarga el formulario.") from error
    with _escritura_atomica():
        huerto = _huerto_actual(huerto, usuario)
        carga = {"huerto": huerto.pk, "planta": planta.pk if planta is not None else None,
                 "tipo": tipo_codigo, "fecha": fecha.isoformat(), "nota": detalles}
        existente = Actividad.objects.filter(uuid=envio).first()
        if existente is not None:
            if existente.actor_original_id != usuario.pk or existente.huerto_id != huerto.pk or existente.carga != carga:
                raise ValidationError("Ese identificador ya se usó con otros datos. Abre un formulario nuevo.")
            return existente, False
        guia = TipoActividad.objects.filter(codigo=tipo_codigo).first()
        if guia is None:
            raise ValidationError("La actividad no está cargada en el catálogo.")
        if fecha > timezone.now():
            raise ValidationError("La fecha y hora no pueden ser futuras.")
        generales = tipo_codigo in Actividad.TIPOS_GENERALES
        if guia.alcance != ("huerto" if generales else "planta"):
            raise ValidationError("El alcance del tipo no coincide con las reglas. Revisa el catálogo.")
        activas = Actividad.objects.filter(huerto=huerto, estado=ACTIVA)
        if generales:
            if planta is not None:
                raise ValidationError("Esta actividad es de todo el huerto: deja vacía la planta.")
            if activas.filter(tipo_id=Tipo.SIEMBRA).exists():
                raise ValidationError("No se registran nuevas actividades generales mientras haya siembras activas.")
            previas = activas.filter(planta__isnull=True, tipo_id=tipo_codigo)
        else:
            seleccion = PlantaHuerto.objects.filter(pk=carga["planta"], huerto=huerto).first()
            if seleccion is None:
                raise ValidationError("Elige una planta de este huerto.")
            planta = seleccion
            historial = list(activas.filter(planta=planta).order_by("fecha", "id"))
            if historial and fecha < historial[-1].fecha:
                raise ValidationError("La fecha no puede ser anterior a la última actividad activa de esta planta.")
            estado = _estado(historial)
            if estado not in ESTADOS_PERMITIDOS[tipo_codigo]:
                raise ValidationError(f"No se puede registrar {guia.nombre.lower()} con la planta {estado}.")
            if tipo_codigo == Tipo.SIEMBRA:
                preparacion = activas.filter(tipo_id=Tipo.PREPARACION, planta__isnull=True).first()
                if preparacion is None or fecha < preparacion.fecha + timedelta(days=15):
                    raise ValidationError("La siembra requiere una preparación de la tierra al menos 15 días antes.")
            if tipo_codigo == Tipo.EMPAQUETADO:
                secado = next((a for a in reversed(historial) if a.tipo_id == Tipo.SECADO), None)
                if secado is None or fecha < secado.fecha + timedelta(days=10):
                    raise ValidationError("Deben pasar al menos 10 días desde el inicio del secado para empaquetar.")
            previas = activas.filter(planta=planta, tipo_id=tipo_codigo)
        repetible = guia.repetible
        if repetible != (tipo_codigo in (Tipo.CUIDADOS, Tipo.RIEGO)):
            raise ValidationError("La repetibilidad del catálogo no coincide con el alcance.")
        if not repetible and previas.exists():
            raise ValidationError("Ya existe una actividad activa de este tipo en ese alcance.")
        actividad = Actividad(uuid=envio, huerto=huerto, planta=planta, tipo=guia, fecha=fecha,
            actor_original=usuario, detalles=detalles, puntos_base=guia.puntos_base,
            repetible=repetible, puntos=0 if previas.exists() else guia.puntos_base, carga=carga)
        actividad.full_clean()
        actividad.save()
        return actividad, True


def verificar_puede_anular(actividad, usuario):
    huerto = _huerto_actual(actividad.huerto, usuario)
    if not es_responsable(usuario, huerto):
        raise PermissionDenied("Solo el responsable de la comunidad puede anular actividades.")


def _retirar_maestro_si_corresponde(huerto):
    if huerto.maestro_id and puntos_de_usuario(huerto.maestro.usuario, huerto) < UMBRAL_MAESTRO:
        huerto.maestro = None
        huerto.maestro_motivo = ""
        huerto.maestro_nombrado_por = None
        huerto.maestro_fecha = None
        huerto.save(update_fields=["maestro", "maestro_motivo", "maestro_nombrado_por", "maestro_fecha"])
        return True
    return False


def anular_actividad(actividad_id, usuario_autor, motivo):
    motivo = (motivo or "").strip()
    if not motivo:
        raise ValidationError("Escribe el motivo de la anulación.")
    with _escritura_atomica():
        actividad = Actividad.objects.select_related("huerto__comunidad", "planta").filter(pk=actividad_id).first()
        if actividad is None:
            raise ValidationError("La actividad no existe.")
        huerto = _huerto_actual(actividad.huerto, usuario_autor)
        verificar_puede_anular(actividad, usuario_autor)
        if actividad.es_anulada:
            raise ValidationError("Esta actividad ya está anulada.")
        activas = Actividad.objects.filter(huerto=huerto, estado=ACTIVA)
        if actividad.planta_id:
            ultima = activas.filter(planta_id=actividad.planta_id).order_by("fecha", "id").last()
            if ultima.pk != actividad.pk:
                raise ValidationError("Solo se anula la última actividad activa de esta planta.")
        elif actividad.tipo_id == Tipo.PREPARACION and activas.filter(tipo_id=Tipo.SIEMBRA).exists():
            raise ValidationError("No se anula la preparación mientras haya siembras activas.")
        actividad.estado = Estado.ANULADA
        actividad.motivo_anulacion = motivo
        actividad.anulada_por = usuario_autor
        actividad.fecha_anulacion = timezone.now()
        actividad.save(update_fields=["estado", "motivo_anulacion", "anulada_por", "fecha_anulacion"])
        if actividad.repetible:
            restantes = activas.filter(planta_id=actividad.planta_id, tipo_id=actividad.tipo_id).order_by("fecha", "id")
            for indice, restante in enumerate(restantes):
                nuevos = restante.puntos_base if indice == 0 else 0
                if restante.puntos != nuevos:
                    restante.puntos = nuevos
                    restante.save(update_fields=["puntos"])
        return actividad, _retirar_maestro_si_corresponde(huerto)


def nombrar_maestro(huerto, usuario_autor, candidato, motivo, *, maestro_esperado_id):
    with _escritura_atomica():
        huerto = _huerto_actual(huerto, usuario_autor)
        if not es_responsable(usuario_autor, huerto):
            raise PermissionDenied("Solo el responsable nombra al maestro.")
        if huerto.maestro_id != maestro_esperado_id:
            raise ValidationError("El maestro cambió mientras completabas el formulario. Revisa el nombramiento actual.")
        candidato = Miembro.objects.select_related("usuario").filter(pk=candidato.pk, comunidad_id=huerto.comunidad_id).first()
        if candidato is None:
            raise ValidationError("El candidato debe pertenecer a esta comunidad.")
        if puntos_de_usuario(candidato.usuario, huerto) < UMBRAL_MAESTRO:
            raise ValidationError("El candidato necesita al menos 100 puntos.")
        motivo = (motivo or "").strip()
        if not motivo:
            raise ValidationError("Explica por qué puede guiar una siembra.")
        if huerto.maestro_id == candidato.pk:
            raise ValidationError("Esa persona ya es el maestro.")
        huerto.maestro = candidato
        huerto.maestro_motivo = motivo
        huerto.maestro_nombrado_por = usuario_autor
        huerto.maestro_fecha = timezone.now()
        huerto.full_clean()
        huerto.save(update_fields=["maestro", "maestro_motivo", "maestro_nombrado_por", "maestro_fecha"])
        return huerto


def candidatos_a_maestro(huerto):
    puntos = puntos_por_usuario(huerto)
    miembros = Miembro.objects.filter(comunidad_id=huerto.comunidad_id).exclude(pk=huerto.maestro_id).select_related("usuario")
    return [(m, puntos.get(m.usuario_id, 0)) for m in miembros if puntos.get(m.usuario_id, 0) >= UMBRAL_MAESTRO]


def obtener_historial(huerto, usuario, planta_id=None, tipo=None, estado=None):
    miembro_del_huerto(usuario, huerto)
    registros = Actividad.objects.filter(huerto=huerto).select_related("tipo", "planta__planta", "actor_original", "anulada_por")
    if planta_id is not None:
        registros = registros.filter(planta_id=planta_id)
    if tipo:
        registros = registros.filter(tipo_id=tipo)
    if estado:
        registros = registros.filter(estado=estado)
    return registros.order_by("-fecha", "-id")


def obtener_resumen_huerto(huerto, usuario):
    huerto = _huerto_actual(huerto, usuario)
    registros = list(Actividad.objects.filter(huerto=huerto).select_related("tipo", "planta__planta").order_by("fecha", "id"))
    activas = [a for a in registros if a.es_activa]
    preparada = any(a.tipo_id == Tipo.PREPARACION for a in activas)
    tarjetas = []
    for seleccion in huerto.plantas.select_related("planta").order_by("planta__nombre_comun", "pk"):
        historial = [a for a in activas if a.planta_id == seleccion.pk]
        codigos = {a.tipo_id for a in historial}
        if preparada:
            codigos.add(Tipo.PREPARACION)
        if codigos.intersection({Tipo.RIEGO, Tipo.CUIDADOS}):
            codigos.add("crecimiento")
        hitos = [h for h in HITOS if h in codigos]
        estado = _estado(historial)
        tarjetas.append({"seleccion": seleccion, "nombre": seleccion.planta.nombre_comun,
            "metodo": seleccion.get_metodo_siembra_display(), "hitos": hitos,
            "etapa": estado.capitalize(), "estado": estado, "siguiente": SIGUIENTE[estado],
            "tipo_sugerido": TIPO_SUGERIDO.get(estado, ""),
            "progreso": calcular_progreso(hitos), "ultima_actividad": historial[-1] if historial else None})
    puntos = puntos_por_usuario(huerto)
    miembros = []
    for m in Miembro.objects.filter(comunidad_id=huerto.comunidad_id).select_related("usuario").order_by("usuario__nombre_completo", "pk"):
        total = puntos.get(m.usuario_id, 0)
        miembros.append({"nombre": m.usuario.get_full_name() or m.usuario.username,
            "puntos": total, "nivel": calcular_nivel(total, m.pk == huerto.maestro_id),
            "es_maestro": m.pk == huerto.maestro_id,
            "es_responsable": m.usuario_id == huerto.comunidad.responsable_id})
    miembro = miembro_del_huerto(usuario, huerto)
    return {"huerto": huerto, "tarjetas": tarjetas,
        "progreso_huerto": sum(t["progreso"] for t in tarjetas) / len(tarjetas) if tarjetas else 0,
        "plantas_cultivadas": sum(t["estado"] != "planeada" for t in tarjetas),
        "total_activas": len(activas), "total_anuladas": len(registros) - len(activas),
        "puntos_comunidad": sum(puntos.values()), "puntos_usuario": puntos.get(usuario.pk, 0),
        "nivel_usuario": calcular_nivel(puntos.get(usuario.pk, 0), miembro.pk == huerto.maestro_id),
        "miembros": miembros, "maestro": huerto.maestro, "maestro_motivo": huerto.maestro_motivo,
        "maestro_fecha": huerto.maestro_fecha, "maestro_nombrado_por": huerto.maestro_nombrado_por,
        "es_responsable": es_responsable(usuario, huerto)}
