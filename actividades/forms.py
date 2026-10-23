"""
Formularios para el módulo de actividades de Huertos Medicinales Comunitarios.
Incluye validaciones de negocio, widgets HTML5 y protección contra reenvíos por UUID.
"""
import uuid
from django import forms
from django.utils import timezone
from .models import Actividad

# Las 18 plantas medicinales acordadas en el catálogo V1
ESPECIES_MEDICINALES_18 = [
    ('Menta', 'Menta'),
    ('Hierbabuena', 'Hierbabuena'),
    ('Toronjil', 'Toronjil'),
    ('Orégano', 'Orégano'),
    ('Romero', 'Romero'),
    ('Manzanilla', 'Manzanilla'),
    ('Matico', 'Matico'),
    ('Taraxaco', 'Taraxaco'),
    ('Marco', 'Marco'),
    ('Llantén', 'Llantén'),
    ('Ortiga', 'Ortiga'),
    ('Violeta', 'Violeta'),
    ('Paico', 'Paico'),
    ('Chilca', 'Chilca'),
    ('Lavanda', 'Lavanda'),
    ('Salvia', 'Salvia'),
    ('Cedrón', 'Cedrón'),
    ('Laurel', 'Laurel'),
]


def obtener_opciones_plantas_medicinales():
    """
    Retorna la lista de plantas medicinales disponibles.
    Si el catálogo dinámico de Matthew (catalogo.models.Planta) ya fue
    creado y tiene registros, los utiliza dinámicamente; de lo contrario,
    hace fallback seguro a las 18 especies medicinales acordadas para V1.
    """
    try:
        from django.apps import apps
        PlantaModel = apps.get_model('catalogo', 'Planta')
        if PlantaModel and PlantaModel.objects.exists():
            return [(p.nombre, p.nombre) for p in PlantaModel.objects.all().order_by('nombre')]
    except Exception:
        pass
    return list(ESPECIES_MEDICINALES_18)


class RegistroActividadForm(forms.Form):
    """
    Formulario para registrar una actividad en el huerto medicinal.
    Incluye un UUID oculto generado para evitar duplicados en reenvíos.
    """
    uuid = forms.UUIDField(
        widget=forms.HiddenInput(),
        required=False,
        help_text="Identificador único para evitar duplicados en caso de reenvío."
    )

    tipo = forms.ChoiceField(
        choices=Actividad.TIPO_ACTIVIDAD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
        label="Tipo de actividad"
    )

    planta = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_planta',
            'placeholder': 'Ej. Menta, Manzanilla (o dejar en blanco para diseño/ritual)',
            'list': 'plantas_sugeridas'
        }),
        label="Planta medicinal asociada"
    )

    fecha = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'id': 'id_fecha',
            'type': 'date'
        }),
        initial=timezone.localdate,
        label="Fecha de realización"
    )

    detalles = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_detalles',
            'rows': 3,
            'placeholder': 'Observaciones de la labor, saberes ancestrales o estado del cultivo...'
        }),
        required=False,
        label="Detalles u observaciones"
    )

    def clean_uuid(self):
        val = self.cleaned_data.get('uuid')
        if not val:
            return uuid.uuid4()
        return val

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError("No se puede registrar una actividad con fecha futura.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        planta = cleaned_data.get('planta', '').strip()

        # Diseño y ritual son actividades independientes del huerto en general
        if tipo not in (Actividad.TIPO_DISENO, Actividad.TIPO_RITUAL) and not planta:
            # Si no es diseño o ritual, sugerir la planta
            self.add_error('planta', "Debe indicar la planta medicinal sobre la cual se realiza esta labor.")

        return cleaned_data


class AnulacionActividadForm(forms.Form):
    """
    Formulario para anular una actividad con motivo obligatorio.
    """
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_motivo',
            'rows': 4,
            'placeholder': 'Explique claramente la razón por la cual se anula este registro (error en datos, planta incorrecta, etc.)...'
        }),
        min_length=5,
        required=True,
        label="Motivo de anulación",
        help_text="El motivo quedará registrado en la auditoría junto con su usuario y fecha."
    )


class NombramientoMaestroForm(forms.Form):
    """
    Formulario para nombrar o sustituir al Maestro de Huerto.
    Solo lista a miembros con al menos 100 puntos acumulados.
    """
    candidato = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_candidato'}),
        label="Seleccionar nuevo Maestro",
        help_text="Solo los miembros con 100 o más puntos son elegibles para este reconocimiento."
    )

    motivo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'id': 'id_motivo_maestro',
            'rows': 4,
            'placeholder': 'Justifique el nombramiento o sustitución (saberes tradicionales demostrados, dedicación, etc.)...'
        }),
        min_length=5,
        required=True,
        label="Motivo del nombramiento o sustitución"
    )

    # Maestro que había al abrir el formulario; sirve para detectar un formulario
    # desactualizado si otro administrador cambia al Maestro mientras tanto (CP-08).
    maestro_esperado = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, huerto=None, **kwargs):
        super().__init__(*args, **kwargs)
        if huerto:
            self.fields['maestro_esperado'].initial = str(huerto.maestro_id or '')
            from comunidades.models import Miembro
            # Filtrar miembros de la comunidad con al menos 100 puntos y excluir al maestro actual
            qs_miembros = Miembro.objects.filter(
                comunidad=huerto.comunidad,
                puntos__gte=100
            ).select_related('usuario')

            if huerto.maestro_id:
                qs_miembros = qs_miembros.exclude(usuario_id=huerto.maestro_id)

            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.fields['candidato'].queryset = User.objects.filter(
                id__in=qs_miembros.values_list('usuario_id', flat=True)
            )

    def clean_maestro_esperado(self):
        """Convierte el id oculto del Maestro esperado en int, o None si no había Maestro."""
        valor = (self.cleaned_data.get('maestro_esperado') or '').strip()
        if not valor:
            return None
        if not valor.isdigit():
            raise forms.ValidationError("El formulario está dañado; recárguelo e intente de nuevo.")
        return int(valor)
