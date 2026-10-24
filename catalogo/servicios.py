"""Consultas del catálogo local. No cambian datos del huerto ni del historial."""
from datetime import date, datetime, time, timedelta
from django.utils import timezone
from .models import EventoLunar, Planta, TipoActividad


def listar_plantas():
    return Planta.objects.all()


def listar_guias():
    return TipoActividad.objects.all()


def calendario_local(mes, fecha):
    inicio = timezone.make_aware(datetime(2026, mes, 1))
    siguiente = timezone.make_aware(datetime(2027, 1, 1) if mes == 12 else datetime(2026, mes + 1, 1))
    dentro = date(2026, 9, 1) <= fecha <= date(2026, 12, 31)
    instante = timezone.make_aware(datetime.combine(fecha, time.min))
    return {
        "eventos": EventoLunar.objects.filter(instante__gte=inicio, instante__lt=siguiente),
        "anterior": EventoLunar.objects.filter(instante__lt=instante).last() if dentro else None,
        "siguiente": EventoLunar.objects.filter(instante__gte=instante).first() if dentro else None,
        "dentro_periodo": dentro,
    }
