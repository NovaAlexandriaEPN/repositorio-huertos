from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def inicio(request):
    """Entrada privada al recorrido; la comunidad se resuelve desde la sesión."""
    return redirect("comunidades:mi_comunidad")
