from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_not_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST

from .aviso import AVISO_DATOS_SECCIONES, AVISO_DATOS_VERSION
from .forms import InicioSesionForm, PerfilForm, RegistroForm
from .servicios import actualizar_perfil, registrar_usuario


@login_not_required
@sensitive_post_parameters("password1", "password2")
@never_cache
@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = RegistroForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        try:
            registrar_usuario(
                username=datos["username"],
                password=datos["password1"],
                nombre_completo=datos["nombre_completo"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                genero=datos["genero"],
                talentos_ancestrales=datos["talentos_ancestrales"],
                acepta_aviso=datos["acepta_aviso"],
                aviso_version=datos["aviso_version"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Tu cuenta se ha creado. Ya puedes iniciar sesión.")
            return redirect(settings.LOGIN_URL)

    return render(
        request,
        "cuentas/registro.html",
        {
            "form": form,
            "aviso_secciones": AVISO_DATOS_SECCIONES,
            "aviso_version": AVISO_DATOS_VERSION,
        },
    )


@login_not_required
@sensitive_post_parameters("password")
@never_cache
@require_http_methods(["GET", "POST"])
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    form = InicioSesionForm(request.POST if request.method == "POST" else None)
    siguiente = request.POST.get("next", request.GET.get("next", ""))
    if not url_has_allowed_host_and_scheme(
        siguiente,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        siguiente = ""

    if request.method == "POST" and form.is_valid():
        usuario = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if usuario is None:
            # Mismo mensaje para cuenta inexistente, inactiva o clave incorrecta.
            form.add_error(None, "Usuario o contraseña incorrectos.")
        else:
            auth_login(request, usuario)
            return redirect(siguiente or settings.LOGIN_REDIRECT_URL)

    return render(request, "cuentas/login.html", {"form": form, "next": siguiente})


@never_cache
@require_POST
def cerrar_sesion(request):
    auth_logout(request)
    messages.success(request, "Has cerrado sesión.")
    return redirect(settings.LOGOUT_REDIRECT_URL)


@never_cache
@require_http_methods(["GET", "POST"])
def perfil(request):
    # LoginRequiredMiddleware exige sesión antes de ejecutar esta vista.
    # El titular procede de la sesión, nunca de un ID enviado por el navegador.
    form = PerfilForm(
        request.POST if request.method == "POST" else None,
        instance=request.user,
    )
    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        try:
            actualizar_perfil(
                actor=request.user,
                nombre_completo=datos["nombre_completo"],
                fecha_nacimiento=datos["fecha_nacimiento"],
                genero=datos["genero"],
                talentos_ancestrales=datos["talentos_ancestrales"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Tu perfil se ha actualizado.")
            return redirect("cuentas:perfil")

    return render(
        request,
        "cuentas/perfil.html",
        {
            "form": form,
            "aviso_secciones": AVISO_DATOS_SECCIONES,
            "aviso_version": AVISO_DATOS_VERSION,
        },
    )
