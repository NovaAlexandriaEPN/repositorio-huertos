"""
Servicios de negocio del módulo de actividades.
Implementa transacciones atómicas, validación de permisos, idempotencia por UUID,
reglas de anulación, cálculo de recompensas y gestión del Maestro de huerto.
"""
import uuid
from datetime import timedelta
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from comunidades.models import Huerto, Miembro
from .models import Actividad
from .reglas import (
    calcular_puntos_actividad,
    calcular_progreso,
    calcular_nivel,
    determinar_hitos_cumplidos,
    UMBRAL_MINIMO_MAESTRO,
    HITOS_CULTIVO,
)

# Plazos agrícolas (CP-05). Cada valor es el ÚLTIMO día permitido:
#   - Siembra: hasta 14 días después de la preparación (el día 15 ya se rechaza).
#   - Secado: hasta 9 días después de la cosecha (el día 10 ya se rechaza).
# Si el alcance (Matthew) fija otro límite, basta con cambiar estas dos constantes.
PLAZO_MAX_SIEMBRA_TRAS_PREPARACION = 14
PLAZO_MAX_SECADO_TRAS_COSECHA = 9

# Valor centinela: "no comprobar si el formulario quedó desactualizado".
_SIN_VERIFICAR = object()


@transaction.atomic
def registrar_actividad(huerto, usuario, tipo, fecha, planta='', detalles='', request_uuid=None):
    """
    Registra una actividad de cultivo o ancestral en el huerto de forma atómica e idempotente.

    Qué recibe:
        - huerto (Huerto): Instancia del huerto comunitario donde se realiza la actividad.
        - usuario (Usuario): Usuario que ejecuta la actividad (actor original).
        - tipo (str): Uno de los 13 tipos de actividad válidos.
        - fecha (date): Fecha de ejecución de la labor.
        - planta (str, opcional): Especie medicinal asociada (o vacío para diseño/ritual).
        - detalles (str, opcional): Observaciones adicionales.
        - request_uuid (UUID o str, opcional): Identificador único de la petición para idempotencia.

    Qué valida:
        1. Permisos y pertenencia: El usuario debe ser miembro activo de la comunidad del huerto.
        2. Idempotencia y UUID:
           - Si ya existe una actividad con ese UUID y la carga (tipo, planta, fecha, huerto)
             coincide exactamente: devuelve la actividad existente sin duplicar ni alterar puntos.
           - Si ya existe con ese UUID pero con carga distinta: rechaza con ValidationError.
           - Si ya existe con ese UUID y se encuentra ANULADA: rechaza con ValidationError
             ("anulado no reactivado").
        3. Plazos y coherencia temporal:
           - No se permiten fechas futuras (fecha > hoy).
           - Siembra: no puede ser anterior a la preparación de la planta ni pasar de
             14 días después de ella (el día 15 se rechaza).
           - Secado: exige una cosecha activa de la planta; no puede ser anterior a ella
             ni pasar de 9 días después (el día 10 se rechaza).
        4. Recompensas:
           - Hitos (preparación, siembra, riego, cuidado, cosecha, secado): puntos completos
             la primera vez para la planta y 0 las siguientes (riego y cuidado: 5 y luego 0).
           - Otro UUID no duplica los puntos de un hito ya cumplido.
           - Las demás actividades otorgan su puntaje estándar.

    Qué guarda:
        - Crea la instancia de Actividad con estado='ACTIVA', actor_original=usuario, puntos calculados
          y el UUID de la petición.
        - Actualiza atómicamente los puntos acumulados del Miembro en la comunidad.

    Qué permisos exige:
        - Requiere que el usuario sea miembro registrado de la comunidad propietaria del huerto.
          Usuarios ajenos son rechazados con PermissionDenied.
    """
    # 1. Validación de permisos y pertenencia
    try:
        miembro = Miembro.objects.select_for_update().get(usuario=usuario, comunidad=huerto.comunidad)
    except Miembro.DoesNotExist:
        raise PermissionDenied("Solo los miembros de la comunidad pueden registrar actividades en este huerto.")

    # 2. Manejo de UUID e idempotencia (evitar duplicados en reenvíos)
    if request_uuid:
        try:
            uuid_obj = uuid.UUID(str(request_uuid))
        except (ValueError, TypeError):
            raise ValidationError("El formato del UUID proporcionado no es válido.")

        actividad_existente = Actividad.objects.filter(uuid=uuid_obj).first()
        if actividad_existente:
            # Comprobar si está anulada
            if actividad_existente.es_anulada:
                raise ValidationError("Una actividad anulada no puede ser reactivada mediante reenvío de UUID.")

            # Comprobar igualdad de carga
            misma_carga = (
                actividad_existente.huerto_id == huerto.id and
                actividad_existente.tipo == tipo and
                (actividad_existente.planta or '').strip().lower() == (planta or '').strip().lower() and
                actividad_existente.fecha == fecha
            )
            if misma_carga:
                # Idempotencia: devuelve la existente sin alterar nada
                return actividad_existente
            else:
                raise ValidationError("El UUID ya fue utilizado con una carga de datos distinta.")
    else:
        uuid_obj = uuid.uuid4()

    # 3. Validación de fecha
    hoy = timezone.localdate()
    if fecha > hoy:
        raise ValidationError("No se pueden registrar actividades con fecha futura.")

    planta_limpia = (planta or '').strip()

    # Validación de plazos y orden de fechas por planta (CP-05)
    if planta_limpia and tipo in ('siembra', 'secado'):
        actividades_planta = Actividad.objects.filter(
            huerto=huerto,
            planta__iexact=planta_limpia,
            estado=Actividad.ESTADO_ACTIVA
        )

        # Siembra: si la planta tiene preparación, la siembra no puede ser anterior
        # ni pasar de PLAZO_MAX_SIEMBRA_TRAS_PREPARACION días.
        if tipo == 'siembra':
            ult_prep = actividades_planta.filter(tipo='preparacion').order_by('fecha', 'id').last()
            if ult_prep:
                dias = (fecha - ult_prep.fecha).days
                if dias < 0:
                    raise ValidationError("La siembra no puede ser anterior a la preparación de esa planta.")
                if dias > PLAZO_MAX_SIEMBRA_TRAS_PREPARACION:
                    raise ValidationError(
                        f"La preparación de {planta_limpia} tiene {dias} días; la siembra debe hacerse "
                        f"hasta {PLAZO_MAX_SIEMBRA_TRAS_PREPARACION} días después. Registre una nueva preparación."
                    )

        # Secado: exige una cosecha activa de la planta, no puede ser anterior a ella
        # ni pasar de PLAZO_MAX_SECADO_TRAS_COSECHA días.
        if tipo == 'secado':
            ult_cosecha = actividades_planta.filter(tipo='cosecha').order_by('fecha', 'id').last()
            if not ult_cosecha:
                raise ValidationError(f"No hay una cosecha activa de {planta_limpia} para registrar su secado.")
            dias = (fecha - ult_cosecha.fecha).days
            if dias < 0:
                raise ValidationError("El secado no puede realizarse antes de la cosecha.")
            if dias > PLAZO_MAX_SECADO_TRAS_COSECHA:
                raise ValidationError(
                    f"La cosecha de {planta_limpia} tiene {dias} días; el secado debe registrarse "
                    f"hasta {PLAZO_MAX_SECADO_TRAS_COSECHA} días después."
                )

    # 4. Cálculo de puntos
    # Regla (CP-06): un hito (preparación, siembra, riego, cuidado, cosecha, secado) solo
    # da puntos la primera vez para esa planta; repetirlo con otro UUID da 0 puntos.
    # Si la actividad anterior se anula, el hito vuelve a dar puntos al registrarse de nuevo.
    es_primera = True
    if tipo in HITOS_CULTIVO:
        es_primera = not Actividad.objects.filter(
            huerto=huerto,
            planta__iexact=planta_limpia,
            tipo=tipo,
            estado=Actividad.ESTADO_ACTIVA
        ).exists()

    puntos_otorgados = calcular_puntos_actividad(tipo, es_primera_en_planta=es_primera)

    # 5. Creación atómica de la Actividad
    actividad = Actividad.objects.create(
        uuid=uuid_obj,
        huerto=huerto,
        tipo=tipo,
        planta=planta_limpia,
        fecha=fecha,
        estado=Actividad.ESTADO_ACTIVA,
        puntos=puntos_otorgados,
        actor_original=usuario,
        detalles=detalles or ''
    )

    # Actualizar puntos del miembro
    if puntos_otorgados > 0:
        miembro.puntos += puntos_otorgados
        miembro.save(update_fields=['puntos'])

    return actividad


@transaction.atomic
def anular_actividad(actividad_id, usuario_autor, motivo):
    """
    Anula una actividad previamente registrada, preservando al actor original,
    registrando auditoría completa y deduciendo los puntos de forma atómica.

    Qué recibe:
        - actividad_id (int): ID de la actividad a anular.
        - usuario_autor (Usuario): Usuario que solicita la anulación.
        - motivo (str): Razón explicativa de la anulación (obligatorio).

    Qué valida:
        1. Pertenencia: El usuario autor debe pertenecer a la comunidad del huerto.
        2. Estado: La actividad debe estar en estado 'ACTIVA'.
        3. Motivo: Debe proporcionarse un motivo no vacío.
        4. Última activa por planta (CP-07):
           - Si la actividad está asociada a una planta (excepto diseño y ritual),
             solo se puede anular si es la última actividad activa de esa planta en orden cronológico (fecha, id).
        5. Preparación con siembras bloqueada (CP-07):
           - Si la actividad es 'preparacion', no puede anularse si existen actividades
             de 'siembra' activas posteriores asociadas a esa planta.
        6. Regla de retiro de Maestro (CP-08):
           - Si al restar los puntos al actor original, su puntaje queda bajo 100 y actualmente
             es el Maestro del huerto, se retira automáticamente su nombramiento.

    Qué guarda:
        - Modifica la Actividad: estado='ANULADA', motivo_anulacion=motivo,
          autor_anulacion=usuario_autor, fecha_anulacion=timezone.now().
          El campo actor_original PERMANECE INTACTO.
        - Resta atómicamente los puntos de la actividad del registro del Miembro correspondiente.
        - Si aplica, retira al Maestro en el modelo Huerto.

    Qué permisos exige:
        - Debe ser miembro activo de la comunidad con rol de autorización
          (el actor original, administrador de comunidad o maestro).
    """
    if not motivo or not motivo.strip():
        raise ValidationError("Es obligatorio especificar el motivo de anulación.")

    try:
        actividad = Actividad.objects.select_for_update().get(id=actividad_id)
    except Actividad.DoesNotExist:
        raise ValidationError("La actividad especificada no existe.")

    huerto = actividad.huerto

    # 1. Pertenencia del autor
    try:
        miembro_autor = Miembro.objects.get(usuario=usuario_autor, comunidad=huerto.comunidad)
    except Miembro.DoesNotExist:
        raise PermissionDenied("No tiene permisos para anular actividades en este huerto.")

    # Permiso: actor original, admin o maestro actual
    es_actor_original = (actividad.actor_original == usuario_autor)
    es_admin = (miembro_autor.rol == 'ADMIN' or huerto.comunidad.creador == usuario_autor)
    es_maestro = (huerto.maestro == usuario_autor)

    if not (es_actor_original or es_admin or es_maestro):
        raise PermissionDenied("Solo el autor original, el administrador o el Maestro pueden anular una actividad.")

    # 2. Validación de estado
    if not actividad.es_activa:
        raise ValidationError("Esta actividad ya ha sido anulada previamente.")

    # 3. Reglas de coherencia de ciclo (CP-07)
    planta_limpia = (actividad.planta or '').strip()
    es_independiente = actividad.tipo in ('diseno', 'ritual') or not planta_limpia

    if not es_independiente:
        # Última activa por planta
        actividades_posteriores = Actividad.objects.filter(
            huerto=huerto,
            planta__iexact=planta_limpia,
            estado=Actividad.ESTADO_ACTIVA
        ).exclude(id=actividad.id).filter(
            models_q_posteriores(actividad)
        )

        if actividades_posteriores.exists():
            raise ValidationError(
                "Solo se puede anular la última actividad activa registrada para esta planta "
                "para preservar la secuencia del ciclo de cultivo."
            )

        # Preparación con siembras bloqueada
        if actividad.tipo == 'preparacion':
            siembras_asociadas = Actividad.objects.filter(
                huerto=huerto,
                planta__iexact=planta_limpia,
                tipo='siembra',
                estado=Actividad.ESTADO_ACTIVA
            ).exists()
            if siembras_asociadas:
                raise ValidationError(
                    "No se puede anular una actividad de preparación que ya cuenta con siembras activas registradas."
                )

    # 4. Anulación y preservación del actor original
    actividad.estado = Actividad.ESTADO_ANULADA
    actividad.motivo_anulacion = motivo.strip()
    actividad.autor_anulacion = usuario_autor
    actividad.fecha_anulacion = timezone.now()
    actividad.save(update_fields=['estado', 'motivo_anulacion', 'autor_anulacion', 'fecha_anulacion'])

    # 5. Deducción de puntos del Miembro original
    puntos_a_descontar = actividad.puntos
    if puntos_a_descontar > 0:
        miembro_original = Miembro.objects.select_for_update().filter(
            usuario=actividad.actor_original,
            comunidad=huerto.comunidad
        ).first()

        if miembro_original:
            miembro_original.puntos = max(0, miembro_original.puntos - puntos_a_descontar)
            miembro_original.save(update_fields=['puntos'])

            # 6. Regla de retiro del Maestro bajo 100 puntos (CP-08)
            if huerto.maestro == actividad.actor_original and miembro_original.puntos < UMBRAL_MINIMO_MAESTRO:
                huerto.maestro = None
                huerto.motivo_maestro = (
                    f"Retiro automático del cargo de Maestro: los puntos del miembro se redujeron a "
                    f"{miembro_original.puntos} (bajo el umbral de {UMBRAL_MINIMO_MAESTRO}) tras la anulación "
                    f"de la actividad #{actividad.id}."
                )
                huerto.fecha_maestro = timezone.now()
                huerto.autor_maestro = usuario_autor
                huerto.save(update_fields=['maestro', 'motivo_maestro', 'fecha_maestro', 'autor_maestro'])

    return actividad


def models_q_posteriores(actividad):
    """Auxiliar para verificar si existen actividades posteriores por fecha y por ID (empate por ID)."""
    from django.db.models import Q
    return Q(fecha__gt=actividad.fecha) | (Q(fecha=actividad.fecha) & Q(id__gt=actividad.id))


@transaction.atomic
def nombrar_o_sustituir_maestro(huerto, usuario_autor, nuevo_maestro_usuario, motivo,
                                maestro_esperado_id=_SIN_VERIFICAR):
    """
    Nombra o sustituye al Maestro del huerto con registro de motivo, autor y fecha.

    Qué recibe:
        - huerto (Huerto): Huerto donde se realiza el nombramiento.
        - usuario_autor (Usuario): Usuario que realiza el nombramiento (debe ser admin o creador).
        - nuevo_maestro_usuario (Usuario): Usuario candidato a Maestro.
        - motivo (str): Justificación del nombramiento o sustitución (obligatorio).

    Qué valida:
        1. Pertenencia: Tanto el autor como el candidato deben pertenecer a la comunidad del huerto.
        2. Permiso del autor: Debe ser Administrador de la comunidad o creador.
        3. Umbral de 100 puntos (CP-08): El candidato debe tener al menos 100 puntos acumulados.
           Si tiene < 100, se rechaza la solicitud.
        4. Motivo obligatorio: No se permite motivo vacío.
        5. Máximo uno: Solo existe un Maestro por huerto (la asignación sustituye al anterior).
        6. Formulario desactualizado: si el Maestro cambió desde que se abrió el formulario
           (maestro_esperado_id distinto del actual), rechaza y pide recargar. También rechaza
           si el candidato ya es el Maestro actual.
        7. Regla: 300 puntos no otorgan nombramiento automático ni derechos administrativos
           (el nombramiento siempre requiere pasar por este servicio explícito).

    Qué guarda:
        - Actualiza el Huerto: maestro=nuevo_maestro_usuario, motivo_maestro=motivo,
          autor_maestro=usuario_autor, fecha_maestro=timezone.now().

    Qué permisos exige:
        - Rol Administrador en la comunidad o ser el creador de la misma.
    """
    if not motivo or not motivo.strip():
        raise ValidationError("Debe proporcionar un motivo para el nombramiento o sustitución del Maestro.")
    # Bloquear la fila del huerto para que dos nombramientos simultáneos no se pisen
    huerto = Huerto.objects.select_for_update().get(pk=huerto.pk)
    if maestro_esperado_id is not _SIN_VERIFICAR and huerto.maestro_id != maestro_esperado_id:
        raise ValidationError(
            "El Maestro del huerto cambió mientras completaba el formulario. "
            "Revise el nombramiento actual y vuelva a intentarlo."
        )

    # 1. Validar autor
    try:
        miembro_autor = Miembro.objects.get(usuario=usuario_autor, comunidad=huerto.comunidad)
    except Miembro.DoesNotExist:
        raise PermissionDenied("El usuario autor no pertenece a la comunidad.")

    es_autorizado = (miembro_autor.rol == 'ADMIN' or huerto.comunidad.creador == usuario_autor)
    if not es_autorizado:
        raise PermissionDenied("Solo un administrador o el creador de la comunidad pueden nombrar al Maestro de huerto.")

    # 2. Validar candidato
    try:
        miembro_candidato = Miembro.objects.get(usuario=nuevo_maestro_usuario, comunidad=huerto.comunidad)
    except Miembro.DoesNotExist:
        raise ValidationError("El usuario candidato no es miembro de esta comunidad.")

    if huerto.maestro == nuevo_maestro_usuario:
        raise ValidationError("El usuario seleccionado ya es el Maestro actual de este huerto.")

    # 3. Umbral de 100 puntos
    if miembro_candidato.puntos < UMBRAL_MINIMO_MAESTRO:
        raise ValidationError(
            f"El miembro {nuevo_maestro_usuario.get_username()} tiene {miembro_candidato.puntos} puntos. "
            f"Se requiere un mínimo de {UMBRAL_MINIMO_MAESTRO} puntos para ser nombrado Maestro."
        )

    # 4. Guardar nombramiento / sustitución
    huerto.maestro = nuevo_maestro_usuario
    huerto.autor_maestro = usuario_autor
    huerto.motivo_maestro = motivo.strip()
    huerto.fecha_maestro = timezone.now()
    huerto.save(update_fields=['maestro', 'autor_maestro', 'motivo_maestro', 'fecha_maestro'])

    return huerto


def obtener_historial_actividades(huerto, usuario, planta=None, tipo=None, estado=None):
    """
    Obtiene el listado cronológico de actividades del huerto con filtros opcionales.

    Qué recibe:
        - huerto (Huerto): Huerto a consultar.
        - usuario (Usuario): Usuario que consulta.
        - planta (str, opcional): Filtrar por especie medicinal.
        - tipo (str, opcional): Filtrar por tipo de actividad.
        - estado (str, opcional): Filtrar por estado ('ACTIVA' o 'ANULADA').

    Qué valida:
        - Valida que el usuario sea miembro de la comunidad (protección de datos ajenos).

    Qué guarda:
        - No realiza escrituras (solo lectura).

    Qué permisos exige:
        - Miembro de la comunidad.
    """
    if not Miembro.objects.filter(usuario=usuario, comunidad=huerto.comunidad).exists():
        raise PermissionDenied("No tiene permiso para ver las actividades de este huerto.")

    qs = Actividad.objects.filter(huerto=huerto).select_related('actor_original', 'autor_anulacion')

    if planta and planta.strip():
        qs = qs.filter(planta__iexact=planta.strip())
    if tipo and tipo.strip():
        qs = qs.filter(tipo=tipo.strip())
    if estado and estado.strip():
        qs = qs.filter(estado=estado.strip())

    return qs.order_by('-fecha', '-id')


def obtener_resumen_huerto(huerto, usuario):
    """
    Calcula el estado consolidado del huerto virtual: progreso de hitos,
    actividades activas, plantas registradas y estado del Maestro.

    Qué recibe:
        - huerto (Huerto): Huerto a consultar.
        - usuario (Usuario): Usuario que consulta.

    Qué valida:
        - Valida pertenencia a la comunidad.

    Qué guarda:
        - Ninguna escritura.

    Qué permisos exige:
        - Miembro de la comunidad.
    """
    if not Miembro.objects.filter(usuario=usuario, comunidad=huerto.comunidad).exists():
        raise PermissionDenied("No tiene permiso para acceder al huerto virtual de esta comunidad.")

    actividades_activas = Actividad.objects.filter(huerto=huerto, estado=Actividad.ESTADO_ACTIVA)
    tipos_activos = actividades_activas.values_list('tipo', flat=True)
    hitos_cumplidos = determinar_hitos_cumplidos(tipos_activos)
    progreso_porcentaje = calcular_progreso(hitos_cumplidos)

    # order_by() vacío: sin él, el orden por defecto (-fecha, -id) hace que distinct() repita plantas.
    # Además se agrupan las mayúsculas/minúsculas ("toronjil" y "Toronjil" son la misma planta).
    plantas_cultivadas = {}
    for nombre in actividades_activas.exclude(planta='').order_by('planta').values_list('planta', flat=True):
        plantas_cultivadas.setdefault(nombre.strip().lower(), nombre.strip())

    # Puntos del usuario actual en esta comunidad
    miembro = Miembro.objects.filter(usuario=usuario, comunidad=huerto.comunidad).first()
    puntos_usuario = miembro.puntos if miembro else 0
    nivel_usuario = calcular_nivel(puntos_usuario)

    # Avance dentro del nivel actual para la barra del usuario (0 a 100).
    # Umbral inferior de cada nivel: 1→0, 2→50, 3→100, 4→200, 5→300.
    inferior = (0, 50, 100, 200, 300)[nivel_usuario['nivel'] - 1]
    siguiente = nivel_usuario['siguiente_umbral']
    if siguiente:
        porcentaje_nivel = round((puntos_usuario - inferior) * 100 / (siguiente - inferior), 1)
    else:
        porcentaje_nivel = 100.0

    return {
        'huerto': huerto,
        'maestro': huerto.maestro,
        'fecha_maestro': huerto.fecha_maestro,
        'motivo_maestro': huerto.motivo_maestro,
        'total_actividades': actividades_activas.count(),
        'hitos_cumplidos': list(hitos_cumplidos),
        'progreso_porcentaje': progreso_porcentaje,
        'plantas_cultivadas': list(plantas_cultivadas.values()),
        'puntos_usuario': puntos_usuario,
        'nivel_usuario': nivel_usuario,
        'porcentaje_nivel': porcentaje_nivel,
    }
