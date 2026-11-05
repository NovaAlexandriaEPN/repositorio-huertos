from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def inicio(request):
    """Entrada privada al huerto de la cuenta autenticada."""
    return redirect(settings.LOGIN_REDIRECT_URL)
