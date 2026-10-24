"""
Vistas del módulo actividades (tareas F1 y F3).

Solo coordinan la petición y la respuesta: leen el formulario, llaman a servicios.py y
muestran el resultado. Las pantallas son privadas gracias a LoginRequiredMiddleware.
Un usuario ajeno a la comunidad recibe 403 (PermissionDenied), también en las consultas.
Las escrituras usan POST con CSRF.
"""
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from comunidades.models import Huerto

from . import servicios
from .forms import AnulacionActividadForm, NombramientoMaestroForm, RegistroActividadForm
from .models import Actividad


def _texto_error(error: ValidationError) -> str:
    return " ".join(error.messages)


def mi_huerto(request):
    """Lleva al Huerto Virtual de la comunidad del usuario.

    Si todavía no pertenece a una comunidad con huerto configurado, lo indica y vuelve al perfil.
    """
    huerto = servicios.huerto_del_usuario(request.user)
    if huerto is None:
        messages.info(request, "Tu comunidad todavía no tiene un huerto configurado.")
        return redirect("cuentas:perfil")
    return redirect("actividades:inicio_huerto_virtual", huerto_id=huerto.pk)


def huerto_virtual(request, huerto_id):
    """Huerto Virtual (HU-10): progreso, tarjetas por planta, totales, puntos y Maestro.

    Recibe: GET con huerto_id. Valida: pertenencia a la comunidad. No guarda nada.
    Permiso: ser miembro de la comunidad.
    """
    huerto = get_object_or_404(Huerto.objects.select_related("comunidad"), pk=huerto_id)
    resumen = servicios.obtener_resumen_huerto(huerto, request.user)
    return render(request, "actividades/inicio_huerto_virtual.html", resumen)


def registrar_actividad(request, huerto_id):
    """Registro de actividades (HU-08).

    Recibe: GET (formulario) o POST con uuid, tipo, planta, fecha y detalles.
    Valida: formulario y reglas del servicio (pertenencia, reenvío, plazos, puntos).
    Guarda: una Actividad mediante servicios.registrar_actividad.
    Permiso: ser miembro de la comunidad.
    """
    huerto = get_object_or_404(Huerto.objects.select_related("comunidad"), pk=huerto_id)
    servicios.miembro_del_huerto(request.user, huerto)

    if request.method == "POST":
        form = RegistroActividadForm(request.POST, huerto=huerto)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                actividad, creada = servicios.registrar_actividad(
                    huerto=huerto,
                    usuario=request.user,
                    tipo=datos["tipo"],
                    fecha=datos["fecha"],
                    planta=datos["planta"],
                    detalles=datos["detalles"],
                    request_uuid=datos["uuid"],
                )
            except ValidationError as error:
                form.add_error(None, _texto_error(error))
            else:
                if creada:
                    messages.success(
                        request,
                        f"Actividad registrada: {actividad.get_tipo_display()} "
                        f"({actividad.nombre_planta}). Puntos: {actividad.puntos}.",
                    )
                else:
                    messages.info(request, "Esta actividad ya estaba registrada; no se duplicó.")
                return redirect("actividades:historial_actividades", huerto_id=huerto.pk)
    else:
        form = RegistroActividadForm(huerto=huerto)

    return render(request, "actividades/registrar_actividad.html", {
        "form": form,
        "huerto": huerto,
        "tipos_generales": list(Actividad.TIPOS_GENERALES),
    })


def historial(request, huerto_id):
    """Historial de actividades (HU-10), con filtros por planta, tipo y estado.

    Recibe: GET con filtros opcionales. Valida: pertenencia. No guarda nada.
    Permiso: ser miembro de la comunidad.
    """
    huerto = get_object_or_404(Huerto.objects.select_related("comunidad"), pk=huerto_id)
    filtros = {
        "planta": request.GET.get("planta", "").strip(),
        "tipo": request.GET.get("tipo", "").strip(),
        "estado": request.GET.get("estado", "").strip(),
    }
    actividades = servicios.obtener_historial(
        huerto,
        request.user,
        planta_id=int(filtros["planta"]) if filtros["planta"].isdigit() else None,
        tipo=filtros["tipo"] if filtros["tipo"] in Actividad.Tipo.values else None,
        estado=filtros["estado"] if filtros["estado"] in Actividad.Estado.values else None,
    )
    return render(request, "actividades/historial.html", {
        "huerto": huerto,
        "actividades": actividades,
        "filtros": filtros,
        "plantas": huerto.plantas.select_related("planta").order_by("planta__nombre_comun"),
        "tipos": Actividad.Tipo.choices,
        "estados": Actividad.Estado.choices,
        "es_responsable": servicios.es_responsable(request.user, huerto),
    })


def anular_actividad(request, actividad_id):
    """Anulación con motivo (HU-09).

    Recibe: GET (confirmación) o POST con el motivo.
    Valida: permiso (quien la realizó o el responsable), estado y orden del ciclo.
    Guarda: estado ANULADA con motivo, autor y fecha; puede retirar al Maestro.
    Permiso: ser quien realizó la actividad o el responsable de la comunidad.
    """
    actividad = get_object_or_404(
        Actividad.objects.select_related("huerto__comunidad", "planta__planta", "actor_original"),
        pk=actividad_id,
    )
    servicios.verificar_puede_anular(actividad, request.user)

    if request.method == "POST":
        form = AnulacionActividadForm(request.POST)
        if form.is_valid():
            try:
                actividad, maestro_retirado = servicios.anular_actividad(
                    actividad.pk, request.user, form.cleaned_data["motivo"]
                )
            except ValidationError as error:
                form.add_error(None, _texto_error(error))
            else:
                messages.success(
                    request,
                    f"Actividad anulada. Sus {actividad.puntos} puntos dejaron de contar.",
                )
                if maestro_retirado:
                    messages.warning(
                        request,
                        "El Maestro del huerto quedó con menos de 100 puntos y se retiró su nombramiento.",
                    )
                return redirect("actividades:historial_actividades", huerto_id=actividad.huerto_id)
    else:
        form = AnulacionActividadForm()

    return render(request, "actividades/anular.html", {
        "actividad": actividad,
        "huerto": actividad.huerto,
        "form": form,
    })


def nombrar_maestro(request, huerto_id):
    """Nombramiento o sustitución del Maestro del huerto (HU-11).

    Recibe: GET (formulario) o POST con candidato, motivo y maestro_esperado.
    Valida: responsable, formulario desactualizado, pertenencia, 100 puntos y motivo.
    Guarda: Maestro con motivo, autor y fecha en el Huerto.
    Permiso: ser el responsable de la comunidad (otros miembros reciben 403).
    """
    huerto = get_object_or_404(Huerto.objects.select_related("comunidad"), pk=huerto_id)
    servicios.miembro_del_huerto(request.user, huerto)
    if not servicios.es_responsable(request.user, huerto):
        raise PermissionDenied("Solo el responsable de la comunidad nombra al Maestro del huerto.")

    if request.method == "POST":
        form = NombramientoMaestroForm(request.POST, huerto=huerto)
        if form.is_valid():
            try:
                servicios.nombrar_maestro(
                    huerto,
                    request.user,
                    form.cleaned_data["candidato"],
                    form.cleaned_data["motivo"],
                    maestro_esperado_id=form.cleaned_data["maestro_esperado"],
                )
            except ValidationError as error:
                form.add_error(None, _texto_error(error))
            else:
                candidato = form.cleaned_data["candidato"].usuario
                messages.success(
                    request,
                    f"{candidato.get_full_name() or candidato.username} es ahora el Maestro del huerto.",
                )
                return redirect("actividades:inicio_huerto_virtual", huerto_id=huerto.pk)
    else:
        form = NombramientoMaestroForm(huerto=huerto)

    return render(request, "actividades/nombrar_maestro.html", {
        "form": form,
        "huerto": huerto,
        "maestro": huerto.maestro,
    })
