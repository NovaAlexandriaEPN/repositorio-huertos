from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html

from .aviso import AVISO_DATOS_VERSION
from .models import Usuario


class RegistroForm(forms.ModelForm):
    """Datos del perfil y confirmaciones necesarias para solicitar una cuenta."""

    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Repite la contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    acepta_aviso = forms.BooleanField(
        label="He leído el aviso y acepto el uso de mis datos para este proyecto.",
        error_messages={
            "required": "Para crear tu cuenta debes aceptar el aviso de datos.",
        },
    )
    aviso_version = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Usuario
        fields = (
            "username",
            "nombre_completo",
            "fecha_nacimiento",
            "genero",
            "talentos_ancestrales",
        )
        labels = {"username": "Usuario"}
        help_texts = {
            "username": "Hasta 150 caracteres. Letras, números y @ . + - _.",
            "talentos_ancestrales": "Opcional. Puedes describir los conocimientos que deseas compartir.",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={"autocomplete": "username", "autocapitalize": "none", "spellcheck": "false"}
            ),
            "nombre_completo": forms.TextInput(attrs={"autocomplete": "name"}),
            "fecha_nacimiento": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "autocomplete": "bday"}
            ),
            "talentos_ancestrales": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["aviso_version"].initial = AVISO_DATOS_VERSION

    def clean(self):
        datos = super().clean()
        password1 = datos.get("password1")
        password2 = datos.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        if datos.get("aviso_version") not in (None, AVISO_DATOS_VERSION):
            self.add_error(
                None,
                "El aviso de datos cambió. Vuelve a cargar la página, "
                "revísalo y acepta la versión actual.",
            )

        return datos


class InicioSesionForm(forms.Form):
    """Credenciales de acceso; Django comprueba la contraseña en la vista."""

    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autocapitalize": "none",
                "spellcheck": "false",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean_username(self):
        # Usa la misma normalización de caracteres que el modelo al registrarse.
        return Usuario.normalize_username(self.cleaned_data["username"])


class PerfilForm(forms.ModelForm):
    """Solo admite los datos personales que el titular puede editar."""

    class Meta:
        model = Usuario
        fields = (
            "nombre_completo",
            "fecha_nacimiento",
            "genero",
            "talentos_ancestrales",
        )
        help_texts = {
            "talentos_ancestrales": "Opcional. Puedes describir los conocimientos que deseas compartir.",
        }
        widgets = {
            "nombre_completo": forms.TextInput(attrs={"autocomplete": "name"}),
            "fecha_nacimiento": forms.DateInput(
                format="%Y-%m-%d", attrs={"type": "date", "autocomplete": "bday"}
            ),
            "talentos_ancestrales": forms.Textarea(attrs={"rows": 3}),
        }
