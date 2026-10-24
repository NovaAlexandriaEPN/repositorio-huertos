from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods

from .forms import ComunidadForm, UnirseComunidadForm
from .servicios import (
    crear_comunidad,
    editar_comunidad,
    listar_miembros,
    obtener_comunidad,
    obtener_comunidad_editable,
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
