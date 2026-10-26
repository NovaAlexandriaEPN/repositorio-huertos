from datetime import date
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET
from . import servicios
from .models import Planta


@require_GET
def lista_plantas(request):
    plantas = servicios.listar_plantas()
    return render(request, "catalogo/lista_plantas.html", {"plantas": plantas, "total": plantas.count()})


@require_GET
def detalle_planta(request, codigo):
    planta = get_object_or_404(Planta, codigo=codigo)
    campos = [(campo.verbose_name, (", ".join(getattr(planta, campo.name)) if isinstance(getattr(planta, campo.name), list) else getattr(planta, campo.name)), campo.name in planta.campos_no_verificados)
              for campo in Planta._meta.fields if campo.name not in
              {"id", "codigo", "nombre_comun", "imagen_ruta", "fuentes", "campos_no_verificados"}]
    return render(request, "catalogo/detalle_planta.html", {"planta": planta, "campos": campos})


@require_GET
def guia(request):
    return render(request, "catalogo/guia.html", {"guias": servicios.listar_guias()})


@require_GET
def calendario(request):
    try:
        mes = int(request.GET.get("mes", timezone.localdate().month))
        if not 1 <= mes <= 12:
            raise ValueError
        fecha = date.fromisoformat(request.GET.get("fecha", timezone.localdate().isoformat()))
    except ValueError:
        return render(request, "catalogo/calendario.html", {"error": "Indica un mes del 1 al 12 y una fecha válida."}, status=400)
    return render(request, "catalogo/calendario.html", {"mes": mes, "fecha": fecha, **servicios.calendario_local(mes, fecha)})
