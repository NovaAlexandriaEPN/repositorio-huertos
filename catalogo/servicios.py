"""Consultas del catálogo local. No cambian datos del huerto ni del historial."""
from datetime import date, datetime, time, timedelta
from django.utils import timezone
from .datos.actividades import FASES_RECOMENDADAS
from .datos.luna import NOMBRES_ANCESTRALES
from .models import EventoLunar, Planta, TipoActividad


def listar_plantas():
    return Planta.objects.all()


def listar_guias():
    return TipoActividad.objects.all()


def recomendaciones_por_fase():
    """{tipo de evento lunar: [guías que recomiendan esa fase]}. Solo informativo."""
    por_fase = {}
    for guia in TipoActividad.objects.filter(codigo__in=FASES_RECOMENDADAS).order_by("pk"):
        for fase in FASES_RECOMENDADAS[guia.codigo]:
            por_fase.setdefault(fase, []).append(guia)
    return por_fase


def filas_calendario(eventos):
    """Cada evento con su nombre ancestral y las actividades recomendadas."""
    por_fase = recomendaciones_por_fase()
    return [{"evento": evento, "nombre_ancestral": NOMBRES_ANCESTRALES.get(evento.tipo, ""),
             "recomendaciones": por_fase.get(evento.tipo, [])} for evento in eventos]


def calendario_local(mes, fecha):
    inicio = timezone.make_aware(datetime(2026, mes, 1))
    siguiente = timezone.make_aware(datetime(2027, 1, 1) if mes == 12 else datetime(2026, mes + 1, 1))
    dentro = date(2026, 9, 1) <= fecha <= date(2026, 12, 31)
    instante = timezone.make_aware(datetime.combine(fecha, time.min))
    eventos = EventoLunar.objects.filter(instante__gte=inicio, instante__lt=siguiente)
    return {
        "eventos": eventos,
        "filas": filas_calendario(eventos),
        "anterior": EventoLunar.objects.filter(instante__lt=instante).last() if dentro else None,
        "siguiente": EventoLunar.objects.filter(instante__gte=instante).first() if dentro else None,
        "dentro_periodo": dentro,
    }
