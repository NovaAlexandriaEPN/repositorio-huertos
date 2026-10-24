from django import forms

from catalogo.models import MetodoSiembra, OpcionHuerto, Planta

from .models import Comunidad, Huerto, PlantaHuerto


class ComunidadForm(forms.ModelForm):
    """Campos que puede completar el responsable al crear o editar su comunidad."""

    class Meta:
        model = Comunidad
        fields = (
            "nombre",
            "tipo",
            "contacto_nombre",
            "contacto_telefono",
            "contacto_correo",
        )
        labels = {
            "nombre": "Nombre de la comunidad",
            "tipo": "Tipo de comunidad",
            "contacto_nombre": "Nombre de contacto",
            "contacto_telefono": "Teléfono de contacto",
            "contacto_correo": "Correo de contacto",
        }
        widgets = {
            "nombre": forms.TextInput(attrs={"autocomplete": "organization"}),
            "contacto_nombre": forms.TextInput(attrs={"autocomplete": "name"}),
            "contacto_telefono": forms.TextInput(
                attrs={"autocomplete": "tel", "inputmode": "tel"}
            ),
            "contacto_correo": forms.EmailInput(attrs={"autocomplete": "email"}),
        }


class UnirseComunidadForm(forms.Form):
    """El código permite solicitar una pertenencia; no elige qué datos consultar."""

    codigo_invitacion = forms.RegexField(
        label="Código de invitación",
        regex=r"^[A-Fa-f0-9]{12}$",
        min_length=12,
        max_length=12,
        help_text="Escribe los 12 caracteres del código que te compartieron.",
        error_messages={"invalid": "El código debe contener 12 caracteres de 0 a 9 y de A a F."},
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "autocapitalize": "characters", "spellcheck": "false"}
        ),
    )

    def clean_codigo_invitacion(self):
        return self.cleaned_data["codigo_invitacion"].upper()


class HuertoForm(forms.ModelForm):
    """Configuración editable; comunidad y nombramiento no son campos del cliente."""

    class Meta:
        model = Huerto
        fields = (
            "provincia", "parroquia", "direccion", "area_m2",
            "disenos", "cerca", "suelo", "fuente_agua", "abonos",
        )
        labels = {"area_m2": "Área en m²"}
        widgets = {
            "disenos": forms.CheckboxSelectMultiple,
            "abonos": forms.CheckboxSelectMultiple,
            "area_m2": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categorias_pendientes = []
        for campo, categoria in (
            ("disenos", OpcionHuerto.Categoria.DISENO),
            ("cerca", OpcionHuerto.Categoria.CERCA),
            ("suelo", OpcionHuerto.Categoria.SUELO),
            ("fuente_agua", OpcionHuerto.Categoria.AGUA),
            ("abonos", OpcionHuerto.Categoria.ABONO),
        ):
            self.fields[campo].queryset = OpcionHuerto.objects.filter(categoria=categoria)
            if not self.fields[campo].queryset.exists():
                self.categorias_pendientes.append(str(OpcionHuerto.Categoria(categoria).label))


class ElegirPlantaForm(forms.ModelForm):
    class Meta:
        model = PlantaHuerto
        fields = ("planta", "metodo_siembra")
        labels = {"planta": "Especie del catálogo"}

    def __init__(self, *args, huerto, **kwargs):
        super().__init__(*args, **kwargs)
        self.catalogo_vacio = not Planta.objects.exists()
        self.fields["planta"].queryset = Planta.objects.exclude(
            selecciones_huerto__huerto=huerto
        )


class MetodoSiembraForm(forms.Form):
    metodo_siembra = forms.ChoiceField(
        label="Método de siembra", choices=MetodoSiembra.choices
    )


class ConfirmarRetiroForm(forms.Form):
    """La confirmación solo envía POST y CSRF; la selección procede de la ruta."""


class DisponibilidadMaterialForm(forms.Form):
    disponible = forms.BooleanField(
        label="Disponible para la comunidad", required=False,
    )
