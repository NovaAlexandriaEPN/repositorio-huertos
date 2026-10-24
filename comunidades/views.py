from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from .forms import (
    ComunidadForm, ConfirmarRetiroForm, ElegirPlantaForm, HuertoForm,
    MetodoSiembraForm, UnirseComunidadForm,
)
from .models import PlantaHuerto
from .servicios import (
    cambiar_metodo_siembra,
    configurar_huerto,
    crear_comunidad,
    editar_comunidad,
    elegir_planta,
    listar_miembros,
    obtener_comunidad,
    obtener_comunidad_editable,
    obtener_huerto,
    obtener_seleccion_editable,
    retirar_planta,
    unirse_comunidad,
)


def _mostrar_errores(form, error):
    """Asociar errores del servicio a campos visibles o al formulario completo."""
    if hasattr(error, "error_dict"):
        for campo, errores in error.error_dict.items():
            form.add_error(campo if campo in form.fields else None, errores)
    else:
        form.add_error(None, error)


@never_cache
@require_GET
def mi_comunidad(request):
    comunidad = obtener_comunidad(actor=request.user)
    return render(request, "comunidades/mi_comunidad.html", {
        "comunidad": comunidad,
        "miembros": listar_miembros(actor=request.user) if comunidad else [],
        "puede_editar": comunidad is not None and comunidad.responsable_id == request.user.pk,
    })


@never_cache
@require_http_methods(["GET", "POST"])
def crear(request):
    if request.method == "GET" and obtener_comunidad(actor=request.user) is not None:
        return redirect("comunidades:mi_comunidad")
    form = ComunidadForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            crear_comunidad(actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            _mostrar_errores(form, error)
        else:
            messages.success(request, "Tu comunidad se ha creado. Eres su responsable.")
            return redirect("comunidades:mi_comunidad")
    return render(request, "comunidades/formulario.html", {
        "form": form,
        "titulo": "Crear comunidad",
        "descripcion": "Crea el grupo que compartirá el huerto. Tú serás su responsable.",
        "ruta_formulario": "comunidades:crear",
        "texto_boton": "Crear comunidad",
    })


@never_cache
@require_http_methods(["GET", "POST"])
def unirse(request):
    if request.method == "GET" and obtener_comunidad(actor=request.user) is not None:
        return redirect("comunidades:mi_comunidad")
    form = UnirseComunidadForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            unirse_comunidad(actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            _mostrar_errores(form, error)
        else:
            messages.success(request, "Ya formas parte de la comunidad.")
            return redirect("comunidades:mi_comunidad")
    return render(request, "comunidades/unirse.html", {"form": form})


@never_cache
@require_http_methods(["GET", "POST"])
def editar(request):
    comunidad = obtener_comunidad_editable(actor=request.user)
    form = ComunidadForm(
        request.POST if request.method == "POST" else None,
        instance=comunidad,
    )
    if request.method == "POST" and form.is_valid():
        try:
            editar_comunidad(actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            _mostrar_errores(form, error)
        else:
            messages.success(request, "Los datos de la comunidad se han actualizado.")
            return redirect("comunidades:mi_comunidad")
    return render(request, "comunidades/formulario.html", {
        "form": form,
        "titulo": "Editar comunidad",
        "descripcion": "Actualiza el nombre, el tipo y los datos de contacto de tu comunidad.",
        "ruta_formulario": "comunidades:editar",
        "texto_boton": "Guardar cambios",
    })


@never_cache
@require_GET
def mi_huerto(request):
    comunidad = obtener_comunidad(actor=request.user)
    if comunidad is None:
        return redirect("comunidades:mi_comunidad")
    huerto = obtener_huerto(actor=request.user)
    return render(request, "comunidades/mi_huerto.html", {
        "huerto": huerto,
        "comunidad": comunidad,
        "selecciones": huerto.plantas.all() if huerto else [],
        "puede_editar": comunidad.responsable_id == request.user.pk,
    })


@never_cache
@require_http_methods(["GET", "POST"])
def configurar(request):
    obtener_comunidad_editable(actor=request.user)
    huerto = obtener_huerto(actor=request.user)
    form = HuertoForm(
        request.POST if request.method == "POST" else None, instance=huerto,
    )
    if request.method == "POST" and form.is_valid():
        try:
            configurar_huerto(actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            _mostrar_errores(form, error)
        else:
            messages.success(request, "La configuración del huerto se ha guardado.")
            return redirect("comunidades:mi_huerto")
    return render(request, "comunidades/configurar_huerto.html", {"form": form})


@never_cache
@require_http_methods(["GET", "POST"])
def elegir(request):
    obtener_comunidad_editable(actor=request.user)
    huerto = obtener_huerto(actor=request.user)
    if huerto is None:
        messages.info(request, "Configura el huerto antes de elegir plantas.")
        return redirect("comunidades:configurar_huerto")
    form = ElegirPlantaForm(
        request.POST if request.method == "POST" else None, huerto=huerto,
    )
    if request.method == "POST" and form.is_valid():
        try:
            elegir_planta(actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            _mostrar_errores(form, error)
        else:
            messages.success(request, "La especie se ha añadido a tu huerto.")
            return redirect("comunidades:mi_huerto")
    return render(request, "comunidades/elegir_planta.html", {
        "form": form,
        "hay_disponibles": form.fields["planta"].queryset.exists(),
        "catalogo_vacio": form.catalogo_vacio,
    })


def _seleccion_de_la_sesion(request, seleccion_id):
    try:
        return obtener_seleccion_editable(actor=request.user, seleccion_id=seleccion_id)
    except (PlantaHuerto.DoesNotExist, ValidationError) as error:
        raise Http404("No se encontró esa selección en tu huerto.") from error


@never_cache
@require_http_methods(["GET", "POST"])
def cambiar_metodo(request, seleccion_id):
    seleccion = _seleccion_de_la_sesion(request, seleccion_id)
    form = MetodoSiembraForm(
        request.POST if request.method == "POST" else None,
        initial={"metodo_siembra": seleccion.metodo_siembra},
    )
    if request.method == "POST" and form.is_valid():
        try:
            cambiar_metodo_siembra(
                actor=request.user, seleccion_id=seleccion_id, **form.cleaned_data,
            )
        except ValidationError as error:
            _mostrar_errores(form, error)
        except PlantaHuerto.DoesNotExist as error:
            raise Http404("La selección ya no está disponible.") from error
        else:
            messages.success(request, "El método de siembra se ha actualizado.")
            return redirect("comunidades:mi_huerto")
    return render(request, "comunidades/cambiar_metodo.html", {
        "form": form, "seleccion": seleccion, "con_historial": seleccion.tiene_historial,
    })


@never_cache
@require_http_methods(["GET", "POST"])
def retirar(request, seleccion_id):
    seleccion = _seleccion_de_la_sesion(request, seleccion_id)
    form = ConfirmarRetiroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            retirar_planta(actor=request.user, seleccion_id=seleccion_id)
        except ValidationError as error:
            _mostrar_errores(form, error)
        except PlantaHuerto.DoesNotExist as error:
            raise Http404("La selección ya no está disponible.") from error
        else:
            messages.success(request, "La especie se ha retirado de tu huerto.")
            return redirect("comunidades:mi_huerto")
    return render(request, "comunidades/retirar_planta.html", {
        "form": form, "seleccion": seleccion, "con_historial": seleccion.tiene_historial,
    })
