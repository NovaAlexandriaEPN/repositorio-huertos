"""
Formularios del módulo actividades (tareas F1 y F3).

Validan la forma de los datos (campos obligatorios, fecha no futura, planta del huerto).
Las reglas del dominio (plazos, puntos, permisos, Maestro) están en servicios.py.
"""
import uuid

from django import forms
from django.utils import timezone

from comunidades.models import Miembro

from .models import Actividad
from . import servicios


class RegistroActividadForm(forms.Form):
    """Registro de una actividad (HU-08).

    El campo oculto `uuid` identifica este envío: si el formulario se envía dos veces,
    el servicio reconoce el mismo UUID y no duplica la actividad ni sus puntos.
    """

    uuid = forms.UUIDField(widget=forms.HiddenInput)
    tipo = forms.ChoiceField(label="Actividad", choices=Actividad.Tipo.choices)
    planta = forms.ModelChoiceField(
        label="Planta del huerto",
        queryset=None,
        required=False,
        empty_label="Todo el huerto (preparación, diseño o ritual)",
        help_text="Preparación, diseño y ritual se registran para todo el huerto; las demás actividades, para una planta.",
    )
    fecha = forms.DateTimeField(
        label="Fecha y hora en que se realizó (Ecuador)",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )
    detalles = forms.CharField(
        label="Observaciones",
        required=False,
        max_length=1000,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, huerto, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["planta"].queryset = huerto.plantas.select_related("planta").order_by(
            "planta__nombre_comun", "pk"
        )
        self.fields["planta"].label_from_instance = (
            lambda seleccion: f"{seleccion.planta.nombre_comun} ({seleccion.get_metodo_siembra_display()})"
        )
        if not self.is_bound:
            self.fields["uuid"].initial = uuid.uuid4()
            self.fields["fecha"].initial = timezone.localtime().replace(second=0, microsecond=0)

    def clean_fecha(self):
        fecha = self.cleaned_data["fecha"]
        if fecha > timezone.now():
            raise forms.ValidationError("La fecha no puede ser futura.")
        return fecha

    def clean(self):
        datos = super().clean()
        tipo = datos.get("tipo")
        planta = datos.get("planta")
        if tipo in Actividad.TIPOS_GENERALES and planta is not None:
            self.add_error("planta", "Preparación, diseño y ritual se registran para todo el huerto: deja la planta vacía.")
        elif tipo and tipo not in Actividad.TIPOS_GENERALES and planta is None:
            self.add_error("planta", "Elige la planta sobre la que se hizo esta actividad.")
        return datos


class AnulacionActividadForm(forms.Form):
    """Motivo obligatorio para anular una actividad (HU-09)."""

    motivo = forms.CharField(
        label="Motivo de la anulación",
        min_length=1,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Queda guardado junto con tu usuario y la fecha.",
    )


class NombramientoMaestroForm(forms.Form):
    """Nombramiento o sustitución del Maestro del huerto (HU-11).

    Solo lista miembros con al menos 100 puntos. El campo oculto `maestro_esperado` guarda
    qué Maestro había al abrir el formulario, para detectar si otra persona lo cambió.
    """

    candidato = forms.ModelChoiceField(label="Nuevo Maestro", queryset=Miembro.objects.none())
    motivo = forms.CharField(
        label="Motivo del nombramiento",
        min_length=1,
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Explica por qué esta persona puede guiar la siembra y el cuidado del huerto.",
    )
    maestro_esperado = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, huerto, **kwargs):
        super().__init__(*args, **kwargs)
        elegibles = servicios.candidatos_a_maestro(huerto)
        puntos = {miembro.pk: total for miembro, total in elegibles}
        self.fields["candidato"].queryset = Miembro.objects.filter(
            pk__in=puntos.keys()
        ).select_related("usuario")
        self.fields["candidato"].label_from_instance = lambda miembro: (
            f"{miembro.usuario.get_full_name() or miembro.usuario.username} ({puntos[miembro.pk]} puntos)"
        )
        if not self.is_bound:
            self.fields["maestro_esperado"].initial = str(huerto.maestro_id or "")

    def clean_maestro_esperado(self):
        valor = (self.cleaned_data.get("maestro_esperado") or "").strip()
        if not valor:
            return None
        if not valor.isdigit():
            raise forms.ValidationError("El formulario está dañado; recárgalo e inténtalo de nuevo.")
        return int(valor)
