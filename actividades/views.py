"""
Vistas de la aplicación actividades.
Coordinan peticiones HTTP y respuestas, delegando la lógica de negocio en servicios.py.
"""
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from comunidades.models import Huerto, Miembro
from .forms import (
    AnulacionActividadForm,
    NombramientoMaestroForm,
    RegistroActividadForm,
    ESPECIES_MEDICINALES_18,
    obtener_opciones_plantas_medicinales,
)
from .models import Actividad
from . import servicios


@login_required
def registrar_actividad_view(request, huerto_id):
    """
    Vista para el registro de una nueva actividad en el huerto comunitario.

    Qué recibe:
        - request (HttpRequest): Petición HTTP (GET o POST).
        - huerto_id (int): Identificador del huerto.

    Qué valida:
        - Que el usuario esté autenticado y sea miembro de la comunidad del huerto.
        - Campos del formulario de registro y restricciones de negocio en el servicio.

    Qué guarda:
        - Llama a servicios.registrar_actividad() para persistir la Actividad y sumar puntos.

    Qué permisos exige:
        - Pertenecer a la comunidad del huerto como miembro activo.
    """
    huerto = get_object_or_404(Huerto, id=huerto_id)

    # Validar pertenencia del usuario
    if not Miembro.objects.filter(usuario=request.user, comunidad=huerto.comunidad).exists():
        messages.error(request, "No perteneces a la comunidad propietaria de este huerto.")
        return redirect('comunidades:mi_comunidad') if 'comunidades' in request.resolver_match.namespaces else redirect('/')

    if request.method == 'POST':
        form = RegistroActividadForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                actividad = servicios.registrar_actividad(
                    huerto=huerto,
                    usuario=request.user,
                    tipo=datos['tipo'],
                    fecha=datos['fecha'],
                    planta=datos['planta'],
                    detalles=datos['detalles'],
                    request_uuid=datos.get('uuid')
                )
                messages.success(
                    request,
                    f"¡Actividad de '{actividad.get_tipo_display()}' registrada con éxito! "
                    f"(+{actividad.puntos} puntos otorgados)."
                )
                return redirect('actividades:historial_actividades', huerto_id=huerto.id)
            except (ValidationError, PermissionDenied) as e:
                error_msg = e.message if hasattr(e, 'message') else str(e)
                messages.error(request, error_msg)
    else:
        # Generar un UUID único fresco para la sesión del formulario
        form = RegistroActividadForm(initial={'uuid': uuid.uuid4()})

    contexto = {
        'form': form,
        'huerto': huerto,
        'especies_sugeridas': obtener_opciones_plantas_medicinales(),
    }
    return render(request, 'actividades/registrar_actividad.html', contexto)


@login_required
def historial_actividades_view(request, huerto_id):
    """
    Vista para consultar el historial cronológico de actividades del huerto.

    Qué recibe:
        - request (HttpRequest): Petición GET con posibles filtros en query params.
        - huerto_id (int): Identificador del huerto.

    Qué valida:
        - Pertenencia del usuario a la comunidad.

    Qué guarda:
        - Ninguna escritura (consulta de historial).

    Qué permisos exige:
        - Miembro de la comunidad.
    """
    huerto = get_object_or_404(Huerto, id=huerto_id)

    filtro_planta = request.GET.get('planta', '').strip()
    filtro_tipo = request.GET.get('tipo', '').strip()
    filtro_estado = request.GET.get('estado', '').strip()

    try:
        actividades = servicios.obtener_historial_actividades(
            huerto=huerto,
            usuario=request.user,
            planta=filtro_planta,
            tipo=filtro_tipo,
            estado=filtro_estado
        )
    except PermissionDenied as e:
        messages.error(request, str(e))
        return redirect('/')

    # Verificar si el usuario actual es admin o creador para mostrar opciones de gestión
    miembro = Miembro.objects.filter(usuario=request.user, comunidad=huerto.comunidad).first()
    es_admin = miembro and (miembro.rol == 'ADMIN' or huerto.comunidad.creador == request.user)

    contexto = {
        'huerto': huerto,
        'actividades': actividades,
        'filtro_planta': filtro_planta,
        'filtro_tipo': filtro_tipo,
        'filtro_estado': filtro_estado,
        'tipos_choices': Actividad.TIPO_ACTIVIDAD_CHOICES,
        'es_admin': es_admin,
    }
    return render(request, 'actividades/historial.html', contexto)


@login_required
def anular_actividad_view(request, actividad_id):
    """
    Vista para solicitar la anulación justificada de una actividad activa.

    Qué recibe:
        - request (HttpRequest): GET (formulario) o POST (confirmación de anulación).
        - actividad_id (int): ID de la actividad a anular.

    Qué valida:
        - Que la actividad exista y esté ACTIVA.
        - Que el motivo esté presente y sea válido.
        - Permisos de anulación (autor original, admin o maestro) y restricciones de ciclo.

    Qué guarda:
        - Llama a servicios.anular_actividad() para marcarla ANULADA, deducir puntos y registrar autor y fecha.

    Qué permisos exige:
        - Ser el actor original, o el administrador/creador de la comunidad, o el Maestro de huerto.
    """
    actividad = get_object_or_404(Actividad, id=actividad_id)
    huerto = actividad.huerto

    if request.method == 'POST':
        form = AnulacionActividadForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            try:
                servicios.anular_actividad(
                    actividad_id=actividad.id,
                    usuario_autor=request.user,
                    motivo=motivo
                )
                messages.warning(
                    request,
                    f"La actividad #{actividad.id} ({actividad.get_tipo_display()}) ha sido anulada con éxito. "
                    f"Se dedujeron {actividad.puntos} puntos."
                )
                return redirect('actividades:historial_actividades', huerto_id=huerto.id)
            except (ValidationError, PermissionDenied) as e:
                error_msg = e.message if hasattr(e, 'message') else str(e)
                messages.error(request, error_msg)
    else:
        form = AnulacionActividadForm()

    contexto = {
        'actividad': actividad,
        'huerto': huerto,
        'form': form,
    }
    return render(request, 'actividades/anular.html', contexto)


@login_required
def nombrar_maestro_view(request, huerto_id):
    """
    Vista para nombrar o sustituir al Maestro de huerto.

    Qué recibe:
        - request (HttpRequest): Petición GET o POST.
        - huerto_id (int): Identificador del huerto.

    Qué valida:
        - Que el usuario autenticado sea Administrador de la comunidad o creador.
        - Que el candidato pertenezca a la comunidad y cumpla el umbral de 100 puntos.
        - Justificación obligatoria.
        - Que el Maestro no haya cambiado desde que se abrió el formulario (formulario desactualizado).

    Qué guarda:
        - Actualiza el Maestro, motivo, autor y fecha en el modelo Huerto.

    Qué permisos exige:
        - Rol Administrador o Creador de la comunidad.
    """
    huerto = get_object_or_404(Huerto, id=huerto_id)

    # Validar permisos administrativos
    miembro = Miembro.objects.filter(usuario=request.user, comunidad=huerto.comunidad).first()
    es_admin = miembro and (miembro.rol == 'ADMIN' or huerto.comunidad.creador == request.user)
    if not es_admin:
        messages.error(request, "Solo los administradores pueden nombrar o sustituir al Maestro de huerto.")
        return redirect('actividades:inicio_huerto_virtual', huerto_id=huerto.id)

    if request.method == 'POST':
        form = NombramientoMaestroForm(request.POST, huerto=huerto)
        if form.is_valid():
            candidato = form.cleaned_data['candidato']
            motivo = form.cleaned_data['motivo']
            try:
                servicios.nombrar_o_sustituir_maestro(
                    huerto=huerto,
                    usuario_autor=request.user,
                    nuevo_maestro_usuario=candidato,
                    motivo=motivo,
                    maestro_esperado_id=form.cleaned_data['maestro_esperado']
                )
                messages.success(
                    request,
                    f"¡Nombramiento exitoso! {candidato.get_full_name() or candidato.username} "
                    f"es el nuevo Maestro del huerto medicinal."
                )
                return redirect('actividades:inicio_huerto_virtual', huerto_id=huerto.id)
            except (ValidationError, PermissionDenied) as e:
                error_msg = e.message if hasattr(e, 'message') else str(e)
                messages.error(request, error_msg)
    else:
        form = NombramientoMaestroForm(huerto=huerto)

    contexto = {
        'form': form,
        'huerto': huerto,
        'maestro_actual': huerto.maestro,
    }
    return render(request, 'actividades/nombrar_maestro.html', contexto)


@login_required
def inicio_huerto_virtual_view(request, huerto_id):
    """
    Vista del Huerto Virtual: tarjetas de estado, hitos alcanzados,
    progreso del ciclo, puntos del usuario y panel del Maestro.

    Qué recibe:
        - request (HttpRequest): Petición GET.
        - huerto_id (int): Identificador del huerto.

    Qué valida:
        - Pertenencia del usuario a la comunidad.

    Qué guarda:
        - Ninguna escritura (pantalla de consulta interactiva).

    Qué permisos exige:
        - Miembro de la comunidad.
    """
    huerto = get_object_or_404(Huerto, id=huerto_id)

    try:
        resumen = servicios.obtener_resumen_huerto(huerto=huerto, usuario=request.user)
    except PermissionDenied as e:
        messages.error(request, str(e))
        return redirect('/')

    miembro = Miembro.objects.filter(usuario=request.user, comunidad=huerto.comunidad).first()
    es_admin = miembro and (miembro.rol == 'ADMIN' or huerto.comunidad.creador == request.user)

    contexto = {
        **resumen,
        'es_admin': es_admin,
        'huerto': huerto,
    }
    return render(request, 'actividades/inicio_huerto_virtual.html', contexto)
