"""Filtros de presentación para las plantillas del catálogo.

Solo separan o nombran datos ya guardados para mostrarlos; no calculan
reglas del dominio ni cambian los datos.
"""
import calendar

from django import template
from django.utils import timezone

register = template.Library()

# El período cargado del calendario lunar es de 2026 (datos de Matthew).
ANIO_CALENDARIO = 2026

MESES = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
         "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")


@register.filter
def lineas(texto):
    """Cada línea no vacía de un texto, sin espacios sobrantes."""
    return [linea.strip() for linea in (texto or "").splitlines() if linea.strip()]


@register.filter
def elementos(texto):
    """Elementos de una lista escrita como «a; b; c.»."""
    return [parte.strip().rstrip(".").strip() for parte in (texto or "").split(";") if parte.strip(" .")]


@register.filter
def licencia(texto):
    """Separa «CC BY-SA 4.0 - https://...» en nombre y enlace.

    Las bases cargadas antes de estandarizar los caracteres guardan una raya
    (U+2014) como separador; se acepta también para no romper sus fichas.
    """
    nombre, _, resto = (texto or "").replace(" \u2014 ", " - ").partition(" - ")
    url = resto.split()[0] if resto.startswith("http") else ""
    extra = resto[len(url):].strip(" .") if url else resto.strip()
    return {"nombre": nombre.strip(), "url": url, "extra": extra}


@register.filter
def nombre_mes(numero):
    """Nombre del mes (1 a 12) en español; vacío si el número no es un mes."""
    try:
        return MESES[int(numero) - 1] if 1 <= int(numero) <= 12 else ""
    except (TypeError, ValueError):
        return ""


@register.filter
def cuadricula_mes(filas, mes):
    """Semanas del mes (lunes a domingo) con los eventos que ya entregó la vista.

    Cada día es {"dia": número o None, "eventos": [filas de ese día]}. El día de
    cada evento se toma en la hora local (America/Guayaquil). Los días sin evento
    quedan vacíos: no se deduce la fase de ningún día.
    """
    try:
        mes = int(mes)
    except (TypeError, ValueError):
        return []
    if not 1 <= mes <= 12:
        return []
    por_dia = {}
    for fila in filas or []:
        local = timezone.localtime(fila["evento"].instante)
        if local.year == ANIO_CALENDARIO and local.month == mes:
            por_dia.setdefault(local.day, []).append(fila)
    semanas = calendar.Calendar(firstweekday=0).monthdayscalendar(ANIO_CALENDARIO, mes)
    return [[{"dia": dia or None, "eventos": por_dia.get(dia, [])} for dia in semana]
            for semana in semanas]
