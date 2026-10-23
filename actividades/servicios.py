"""
Servicios del módulo actividades (tareas F2 y F3).

Aquí viven las reglas de registro, anulación, recompensas y Maestro del huerto. Las vistas
solo reciben la petición, llaman a estas funciones y muestran el resultado.

Decisiones sobre los modelos compartidos de comunidades (Bryan):
    - Administra la comunidad su responsable (`Comunidad.responsable`); no hay otro rol.
    - Los puntos no se guardan en `Miembro`. Los puntos de una persona son la suma de los
      puntos de sus actividades ACTIVAS en el huerto de su comunidad. Al anular, el total
      baja solo, sin una segunda copia que pueda quedar desfasada.
    - `Huerto.maestro` es un `Miembro` y su constancia es `maestro_motivo`,
      `maestro_nombrado_por` y `maestro_fecha`: los cuatro campos se guardan o se vacían
      juntos (restricción `huerto_maestro_constancia_completa`).
    - Ser Maestro no concede permisos (README de comunidades).

Todas las escrituras son atómicas y bloquean la fila del huerto mientras se decide, para que
dos registros o nombramientos simultáneos no calculen sobre datos viejos. En SQLite el modo
`IMMEDIATE` de settings ya serializa las escrituras; el bloqueo deja la intención explícita.
"""
import uuid as uuid_lib

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from comunidades.models import Huerto, Miembro

from .models import Actividad
from .reglas import (
    HITOS,
    UMBRAL_MAESTRO,
    calcular_nivel,
    calcular_progreso,
    porcentaje_en_nivel,
)

Tipo = Actividad.Tipo
Estado = Actividad.Estado

# Puntos base por tipo (RN de recompensas). Los seis hitos solo los dan la primera vez
# para cada planta del huerto; repetidos dan 0 (en riego y cuidado: 5 y luego 0).
PUNTOS_POR_TIPO = {
    Tipo.PREPARACION: 10,
    Tipo.SIEMBRA: 15,
    Tipo.RIEGO: 5,
    Tipo.CUIDADO: 5,
    Tipo.ABONO: 5,
    Tipo.ASOCIACION: 5,
    Tipo.PODA: 5,
    Tipo.CONTROL_PLAGAS: 5,
    Tipo.COSECHA: 20,
    Tipo.SECADO: 15,
    Tipo.PROCESAMIENTO: 10,
    Tipo.DISENO: 10,
    Tipo.RITUAL: 10,
}

# Plazos agrícolas (CP-05). Cada valor es el último día permitido.
PLAZO_MAX_SIEMBRA_TRAS_PREPARACION = 14   # el día 14 se acepta; el 15 se rechaza
PLAZO_MAX_SECADO_TRAS_COSECHA = 9         # el día 9 se acepta; el 10 se rechaza

# Etapa que muestra cada tarjeta del Huerto Virtual según el último hito cumplido.
ETAPAS = {
    None: "Sin iniciar",
    Tipo.PREPARACION: "Terreno preparado",
    Tipo.SIEMBRA: "Sembrada",
    Tipo.RIEGO: "En crecimiento",
    Tipo.CUIDADO: "En crecimiento",
    Tipo.COSECHA: "Cosechada",
    Tipo.SECADO: "Secada",
}

# Valor que indica "no comprobar si el formulario quedó desactualizado".
_SIN_VERIFICAR = object()


# ---------------------------------------------------------------------------
# Pertenencia, permisos y puntos
# ---------------------------------------------------------------------------

def miembro_del_huerto(usuario, huerto) -> Miembro:
    """Devuelve la pertenencia del usuario a la comunidad del huerto.

    Lanza PermissionDenied si la cuenta no pertenece a esa comunidad, para que nadie lea ni
    modifique datos de un huerto ajeno.
    """
    miembro = Miembro.objects.filter(
        usuario_id=usuario.pk, comunidad_id=huerto.comunidad_id
    ).select_related("usuario").first()
    if miembro is None:
        raise PermissionDenied("Solo los miembros de la comunidad pueden acceder a este huerto.")
    return miembro


def es_responsable(usuario, huerto) -> bool:
    """True si la cuenta es la responsable de la comunidad del huerto."""
    return huerto.comunidad.responsable_id == usuario.pk


def huerto_del_usuario(usuario):
    """Huerto de la comunidad del usuario, o None si aún no tiene comunidad o huerto."""
    return Huerto.objects.filter(comunidad__miembros__usuario_id=usuario.pk).first()


def puntos_de_usuario(usuario, huerto) -> int:
    """Suma de los puntos de las actividades activas del usuario en el huerto."""
    total = Actividad.objects.filter(
        huerto=huerto, actor_original_id=usuario.pk, estado=Estado.ACTIVA
    ).aggregate(total=Sum("puntos"))["total"]
    return total or 0


def puntos_por_usuario(huerto) -> dict:
    """Puntos de cada persona del huerto, como {id de usuario: puntos}."""
    filas = (
        Actividad.objects.filter(huerto=huerto, estado=Estado.ACTIVA)
        .values("actor_original_id")
        .annotate(total=Sum("puntos"))
    )
    return {fila["actor_original_id"]: fila["total"] or 0 for fila in filas}


def _bloquear_huerto(huerto) -> Huerto:
    """Vuelve a leer el huerto bloqueando su fila hasta el final de la transacción."""
    return Huerto.objects.select_for_update().select_related("comunidad").get(pk=huerto.pk)


def _posteriores(actividad):
    """Condición de las actividades posteriores: fecha mayor, o misma fecha e id mayor."""
    return Q(fecha__gt=actividad.fecha) | Q(fecha=actividad.fecha, id__gt=actividad.id)


# ---------------------------------------------------------------------------
# HU-08: registro
# ---------------------------------------------------------------------------

@transaction.atomic
def registrar_actividad(huerto, usuario, tipo, fecha, planta=None, detalles="", request_uuid=None):
    """Registra una actividad sin duplicarla aunque el formulario se reenvíe.

    Qué recibe:
        huerto (Huerto), usuario (Usuario que realiza la labor), tipo (código de
        Actividad.Tipo), fecha (date), planta (PlantaHuerto del mismo huerto; None en
        diseño y ritual), detalles (texto) y request_uuid (UUID del formulario).

    Qué valida:
        1. Pertenencia: el usuario es miembro de la comunidad del huerto.
        2. Reenvío por UUID: mismo UUID y misma carga (tipo, planta, fecha y autor)
           devuelve la actividad existente; carga distinta se rechaza; un UUID de una
           actividad anulada no la reactiva.
        3. Fecha no futura. Diseño y ritual sin planta; el resto, con una planta de
           este huerto.
        4. Plazos: la siembra no es anterior a la preparación activa de la planta ni pasa
           de 14 días; el secado exige una cosecha activa, no es anterior a ella ni pasa
           de 9 días. Las actividades anuladas no cuentan.
        5. Recompensa: un hito da sus puntos solo la primera vez para esa planta mientras
           esa actividad siga activa; repetirlo da 0. Las demás labores siempre puntúan.

    Qué guarda:
        Una Actividad ACTIVA con actor_original=usuario, los puntos calculados y el UUID.
        No modifica Miembro: los puntos se obtienen sumando actividades activas.

    Qué permisos exige:
        Pertenecer a la comunidad del huerto. Cualquier miembro puede registrar.

    Devuelve:
        (actividad, creada): creada es False si fue un reenvío del mismo envío.
    """
    huerto = _bloquear_huerto(huerto)
    miembro_del_huerto(usuario, huerto)

    if tipo not in Tipo.values:
        raise ValidationError("El tipo de actividad no es válido.")

    if request_uuid:
        try:
            uuid_envio = uuid_lib.UUID(str(request_uuid))
        except (TypeError, ValueError):
            raise ValidationError("El identificador del formulario no es válido; recarga la página.")
        existente = Actividad.objects.filter(uuid=uuid_envio).first()
        if existente is not None:
            return _resolver_reenvio(existente, huerto, usuario, tipo, fecha, planta), False
    else:
        uuid_envio = uuid_lib.uuid4()

    if fecha > timezone.localdate():
        raise ValidationError("La fecha no puede ser futura.")

    if tipo in Actividad.TIPOS_GENERALES:
        if planta is not None:
            raise ValidationError("Diseño y ritual se registran para todo el huerto, sin planta.")
    else:
        if planta is None:
            raise ValidationError("Elige la planta del huerto sobre la que se hizo la labor.")
        if planta.huerto_id != huerto.pk:
            raise ValidationError("La planta elegida no pertenece a este huerto.")

    activas_planta = Actividad.objects.none()
    if planta is not None:
        activas_planta = Actividad.objects.filter(planta=planta, estado=Estado.ACTIVA)
        _validar_plazos(tipo, fecha, planta, activas_planta)

    puntos = PUNTOS_POR_TIPO[tipo]
    if tipo in HITOS and activas_planta.filter(tipo=tipo).exists():
        puntos = 0

    actividad = Actividad(
        uuid=uuid_envio,
        huerto=huerto,
        planta=planta,
        tipo=tipo,
        fecha=fecha,
        puntos=puntos,
        actor_original=usuario,
        detalles=(detalles or "").strip(),
    )
    actividad.full_clean(exclude=["uuid"])
    try:
        with transaction.atomic():
            actividad.save()
    except IntegrityError:
        # Otro envío con el mismo UUID se guardó entre la consulta y el guardado.
        existente = Actividad.objects.get(uuid=uuid_envio)
        return _resolver_reenvio(existente, huerto, usuario, tipo, fecha, planta), False
    return actividad, True


def _resolver_reenvio(existente, huerto, usuario, tipo, fecha, planta):
    """Aplica las reglas de reenvío (CP-06) a una actividad que ya tiene ese UUID."""
    if existente.es_anulada:
        raise ValidationError("Ese envío corresponde a una actividad anulada y no se reactiva.")
    misma_carga = (
        existente.huerto_id == huerto.pk
        and existente.tipo == tipo
        and existente.fecha == fecha
        and existente.planta_id == (planta.pk if planta is not None else None)
        and existente.actor_original_id == usuario.pk
    )
    if not misma_carga:
        raise ValidationError("Ese envío ya se usó con otros datos. Recarga el formulario.")
    return existente


def _validar_plazos(tipo, fecha, planta, activas_planta):
    """Plazos de siembra y secado (CP-05) frente a las actividades activas de la planta."""
    nombre = planta.planta.nombre_comun
    if tipo == Tipo.SIEMBRA:
        preparacion = activas_planta.filter(tipo=Tipo.PREPARACION).order_by("fecha", "id").last()
        if preparacion is not None:
            dias = (fecha - preparacion.fecha).days
            if dias < 0:
                raise ValidationError("La siembra no puede ser anterior a la preparación del terreno.")
            if dias > PLAZO_MAX_SIEMBRA_TRAS_PREPARACION:
                raise ValidationError(
                    f"La preparación de {nombre} tiene {dias} días; la siembra se registra hasta "
                    f"{PLAZO_MAX_SIEMBRA_TRAS_PREPARACION} días después. Registra una nueva preparación."
                )
    elif tipo == Tipo.SECADO:
        cosecha = activas_planta.filter(tipo=Tipo.COSECHA).order_by("fecha", "id").last()
        if cosecha is None:
            raise ValidationError(f"{nombre} no tiene una cosecha activa para registrar su secado.")
        dias = (fecha - cosecha.fecha).days
        if dias < 0:
            raise ValidationError("El secado no puede ser anterior a la cosecha.")
        if dias > PLAZO_MAX_SECADO_TRAS_COSECHA:
            raise ValidationError(
                f"La cosecha de {nombre} tiene {dias} días; el secado se registra hasta "
                f"{PLAZO_MAX_SECADO_TRAS_COSECHA} días después."
            )


# ---------------------------------------------------------------------------
# HU-09: anulación
# ---------------------------------------------------------------------------

def verificar_puede_anular(actividad, usuario):
    """Comprueba el permiso para anular sin modificar nada (lo usa la pantalla de confirmación).

    Puede anular quien realizó la actividad o el responsable de la comunidad. Ser Maestro no
    da este permiso. Lanza PermissionDenied si no corresponde.
    """
    huerto = actividad.huerto
    miembro_del_huerto(usuario, huerto)
    if actividad.actor_original_id != usuario.pk and not es_responsable(usuario, huerto):
        raise PermissionDenied(
            "Solo quien realizó la actividad o el responsable de la comunidad pueden anularla."
        )


@transaction.atomic
def anular_actividad(actividad_id, usuario_autor, motivo):
    """Anula una actividad conservando el registro, el actor original y la constancia.

    Qué recibe:
        actividad_id (int), usuario_autor (Usuario que anula) y motivo (texto obligatorio).

    Qué valida:
        1. Permiso: quien realizó la actividad o el responsable de la comunidad.
        2. La actividad está activa y el motivo no está vacío.
        3. Ciclo: solo se anula la última actividad activa de esa planta, por fecha y,
           en la misma fecha, por id. Diseño y ritual no tienen planta y se anulan
           de forma independiente.
        4. Una preparación no se anula si la planta tiene siembras activas.

    Qué guarda:
        estado=ANULADA, motivo_anulacion, anulada_por y fecha_anulacion. No cambia
        actor_original ni borra la fila. Los puntos de esa actividad dejan de contar.
        Si la persona era Maestro y queda bajo 100 puntos, se retira el nombramiento y
        se vacía su constancia.

    Qué permisos exige:
        Ser quien realizó la actividad o el responsable de la comunidad.

    Devuelve:
        (actividad, maestro_retirado).
    """
    motivo = (motivo or "").strip()
    if not motivo:
        raise ValidationError("Escribe el motivo de la anulación.")

    actividad = (
        Actividad.objects.select_related("huerto__comunidad", "planta__planta")
        .filter(pk=actividad_id).first()
    )
    if actividad is None:
        raise ValidationError("La actividad no existe.")
    huerto = _bloquear_huerto(actividad.huerto)
    actividad = Actividad.objects.select_for_update().get(pk=actividad.pk)

    verificar_puede_anular(actividad, usuario_autor)
    if actividad.es_anulada:
        raise ValidationError("Esta actividad ya estaba anulada.")

    if actividad.planta_id is not None:
        activas_planta = Actividad.objects.filter(
            planta_id=actividad.planta_id, estado=Estado.ACTIVA
        ).exclude(pk=actividad.pk)
        if activas_planta.filter(_posteriores(actividad)).exists():
            raise ValidationError(
                "Solo se anula la última actividad activa de esta planta, para conservar el orden del ciclo."
            )
        if actividad.tipo == Tipo.PREPARACION and activas_planta.filter(tipo=Tipo.SIEMBRA).exists():
            raise ValidationError("No se anula la preparación de una planta que ya tiene siembras activas.")

    actividad.estado = Estado.ANULADA
    actividad.motivo_anulacion = motivo
    actividad.anulada_por = usuario_autor
    actividad.fecha_anulacion = timezone.now()
    actividad.full_clean(exclude=["uuid"])
    actividad.save(update_fields=["estado", "motivo_anulacion", "anulada_por", "fecha_anulacion"])

    maestro_retirado = False
    if huerto.maestro_id is not None:
        maestro = Miembro.objects.get(pk=huerto.maestro_id)
        if (
            maestro.usuario_id == actividad.actor_original_id
            and puntos_de_usuario(maestro.usuario, huerto) < UMBRAL_MAESTRO
        ):
            huerto.maestro = None
            huerto.maestro_motivo = ""
            huerto.maestro_nombrado_por = None
            huerto.maestro_fecha = None
            huerto.save(update_fields=["maestro", "maestro_motivo", "maestro_nombrado_por", "maestro_fecha"])
            maestro_retirado = True
    return actividad, maestro_retirado


# ---------------------------------------------------------------------------
# HU-11: Maestro del huerto
# ---------------------------------------------------------------------------

@transaction.atomic
def nombrar_maestro(huerto, usuario_autor, candidato, motivo, maestro_esperado_id=_SIN_VERIFICAR):
    """Nombra o sustituye al Maestro del huerto con motivo, autor y fecha.

    Qué recibe:
        huerto (Huerto), usuario_autor (Usuario que nombra), candidato (Miembro),
        motivo (texto) y maestro_esperado_id (id del Miembro Maestro que había al abrir
        el formulario, o None si no había).

    Qué valida:
        1. Permiso: solo el responsable de la comunidad.
        2. Formulario desactualizado: si el Maestro cambió desde que se abrió el
           formulario, se rechaza y se pide revisar el estado actual.
        3. El candidato pertenece a la comunidad y no es ya el Maestro.
        4. El candidato tiene al menos 100 puntos y hay un motivo.
        5. Como máximo un Maestro: el nuevo nombramiento sustituye al anterior.
        Llegar a 300 puntos no nombra a nadie: el nombramiento siempre pasa por aquí.

    Qué guarda:
        En Huerto: maestro, maestro_motivo, maestro_nombrado_por y maestro_fecha.

    Qué permisos exige:
        Ser el responsable de la comunidad del huerto.
    """
    motivo = (motivo or "").strip()
    huerto = _bloquear_huerto(huerto)

    if not es_responsable(usuario_autor, huerto):
        raise PermissionDenied("Solo el responsable de la comunidad nombra al Maestro del huerto.")
    if maestro_esperado_id is not _SIN_VERIFICAR and maestro_esperado_id != huerto.maestro_id:
        raise ValidationError(
            "El Maestro del huerto cambió mientras completabas el formulario. "
            "Revisa el nombramiento actual y vuelve a intentarlo."
        )
    if candidato.comunidad_id != huerto.comunidad_id:
        raise ValidationError("La persona elegida no pertenece a esta comunidad.")
    if candidato.pk == huerto.maestro_id:
        raise ValidationError("Esa persona ya es el Maestro del huerto.")
    puntos = puntos_de_usuario(candidato.usuario, huerto)
    if puntos < UMBRAL_MAESTRO:
        raise ValidationError(
            f"{candidato.usuario.get_full_name()} tiene {puntos} puntos; "
            f"se necesitan al menos {UMBRAL_MAESTRO} para ser Maestro."
        )
    if not motivo:
        raise ValidationError("Explica por qué esta persona puede guiar el huerto.")

    huerto.maestro = candidato
    huerto.maestro_motivo = motivo
    huerto.maestro_nombrado_por = usuario_autor
    huerto.maestro_fecha = timezone.now()
    huerto.full_clean()
    huerto.save(update_fields=["maestro", "maestro_motivo", "maestro_nombrado_por", "maestro_fecha"])
    return huerto


def candidatos_a_maestro(huerto):
    """Miembros de la comunidad con al menos 100 puntos, sin el Maestro actual.

    Devuelve una lista de (miembro, puntos) ordenada de mayor a menor puntaje.
    """
    puntos = puntos_por_usuario(huerto)
    miembros = Miembro.objects.filter(comunidad_id=huerto.comunidad_id).select_related("usuario")
    if huerto.maestro_id:
        miembros = miembros.exclude(pk=huerto.maestro_id)
    elegibles = [(m, puntos.get(m.usuario_id, 0)) for m in miembros]
    elegibles = [(m, p) for m, p in elegibles if p >= UMBRAL_MAESTRO]
    return sorted(elegibles, key=lambda par: (-par[1], par[0].usuario.username))


# ---------------------------------------------------------------------------
# HU-10: historial, totales y Huerto Virtual
# ---------------------------------------------------------------------------

def obtener_historial(huerto, usuario, planta_id=None, tipo=None, estado=None):
    """Actividades del huerto, de la más reciente a la más antigua, con filtros opcionales.

    Incluye las anuladas con su constancia. Solo pueden consultarlo los miembros.
    """
    miembro_del_huerto(usuario, huerto)
    actividades = Actividad.objects.filter(huerto=huerto).select_related(
        "planta__planta", "actor_original", "anulada_por"
    )
    if planta_id:
        actividades = actividades.filter(planta_id=planta_id)
    if tipo:
        actividades = actividades.filter(tipo=tipo)
    if estado:
        actividades = actividades.filter(estado=estado)
    return actividades.order_by("-fecha", "-id")


def obtener_resumen_huerto(huerto, usuario):
    """Datos del Huerto Virtual: progreso, tarjetas por planta, totales, puntos y Maestro.

    Qué devuelve (diccionario para la plantilla):
        progreso_huerto: % de los seis hitos cumplidos en el huerto (cualquier planta).
        hitos_huerto: códigos de hitos cumplidos en el huerto.
        tarjetas: una por planta elegida, con su etapa, hitos, progreso y última actividad.
        plantas_cultivadas: plantas con siembra activa (cada selección cuenta una vez).
        total_activas, total_anuladas, puntos_usuario, nivel_usuario, porcentaje_nivel.
        miembros: puntos y nivel de cada miembro, de mayor a menor.
        maestro, maestro_motivo, maestro_fecha, maestro_nombrado_por, es_responsable.
    """
    miembro_del_huerto(usuario, huerto)
    actividades = Actividad.objects.filter(huerto=huerto)
    activas = actividades.filter(estado=Estado.ACTIVA)

    hitos_por_planta = {}
    ultima_por_planta = {}
    for actividad in activas.filter(planta__isnull=False).order_by("fecha", "id"):
        if actividad.tipo in HITOS:
            hitos_por_planta.setdefault(actividad.planta_id, set()).add(actividad.tipo)
        ultima_por_planta[actividad.planta_id] = actividad

    tarjetas = []
    for seleccion in huerto.plantas.select_related("planta").order_by("planta__nombre_comun", "pk"):
        hitos = hitos_por_planta.get(seleccion.pk, set())
        ultimo_hito = next((h for h in reversed(HITOS) if h in hitos), None)
        tarjetas.append({
            "seleccion": seleccion,
            "nombre": seleccion.planta.nombre_comun,
            "metodo": seleccion.get_metodo_siembra_display(),
            "hitos": [h for h in HITOS if h in hitos],
            "etapa": ETAPAS[ultimo_hito],
            "progreso": calcular_progreso(hitos),
            "ultima_actividad": ultima_por_planta.get(seleccion.pk),
        })

    hitos_huerto = set().union(*hitos_por_planta.values()) if hitos_por_planta else set()
    puntos = puntos_por_usuario(huerto)
    puntos_usuario = puntos.get(usuario.pk, 0)

    miembros = []
    for miembro in Miembro.objects.filter(comunidad_id=huerto.comunidad_id).select_related("usuario"):
        total = puntos.get(miembro.usuario_id, 0)
        miembros.append({
            "miembro": miembro,
            "nombre": miembro.usuario.get_full_name() or miembro.usuario.username,
            "puntos": total,
            "nivel": calcular_nivel(total),
            "es_maestro": miembro.pk == huerto.maestro_id,
            "es_responsable": miembro.usuario_id == huerto.comunidad.responsable_id,
        })
    miembros.sort(key=lambda fila: (-fila["puntos"], fila["nombre"]))

    return {
        "huerto": huerto,
        "progreso_huerto": calcular_progreso(hitos_huerto),
        "hitos_huerto": [h for h in HITOS if h in hitos_huerto],
        "tarjetas": tarjetas,
        "plantas_cultivadas": sum(1 for t in tarjetas if Tipo.SIEMBRA in t["hitos"]),
        "total_activas": activas.count(),
        "total_anuladas": actividades.filter(estado=Estado.ANULADA).count(),
        "puntos_usuario": puntos_usuario,
        "nivel_usuario": calcular_nivel(puntos_usuario),
        "porcentaje_nivel": porcentaje_en_nivel(puntos_usuario),
        "miembros": miembros,
        "maestro": huerto.maestro,
        "maestro_motivo": huerto.maestro_motivo,
        "maestro_fecha": huerto.maestro_fecha,
        "maestro_nombrado_por": huerto.maestro_nombrado_por,
        "es_responsable": es_responsable(usuario, huerto),
    }
