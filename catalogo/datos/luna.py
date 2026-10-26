"""Eventos lunares principales de septiembre a diciembre de 2026 (entrega M2-08).

Fuente: U.S. Naval Observatory (USNO), Astronomical Applications Department,
«Phases of the Moon» 2026, consultado el 19 de octubre de 2026 en
https://aa.usno.navy.mil/api/moon/phases/year?year=2026 y contrastado con la
consulta por fecha (date=2026-09-01&nump=20): ambas dieron los mismos instantes.

USNO publica los instantes en Tiempo Universal. Aquí se guardan en UTC y la
pantalla los convierte a America/Guayaquil una sola vez. Esta tabla no permite
deducir la fase de cualquier día. La aplicación no consulta USNO en ejecución.

Eventos que cambian de día al convertir a Guayaquil (útiles para CP-04):
- 2026-12-09 00:52 UTC (luna nueva)  ->  8 de diciembre de 2026, 19:52
- 2026-12-24 01:28 UTC (luna llena)  -> 23 de diciembre de 2026, 20:28
"""
from datetime import datetime, timezone

FUENTE_USNO = "https://aa.usno.navy.mil/data/MoonPhases"

# año, mes, día, hora y minuto en UTC, tipo
_UTC = [
    (2026, 9, 4, 7, 51, 'menguante'),
    (2026, 9, 11, 3, 27, 'nueva'),
    (2026, 9, 18, 20, 44, 'creciente'),
    (2026, 9, 26, 16, 49, 'llena'),
    (2026, 10, 3, 13, 25, 'menguante'),
    (2026, 10, 10, 15, 50, 'nueva'),
    (2026, 10, 18, 16, 12, 'creciente'),
    (2026, 10, 26, 4, 12, 'llena'),
    (2026, 11, 1, 20, 28, 'menguante'),
    (2026, 11, 9, 7, 2, 'nueva'),
    (2026, 11, 17, 11, 48, 'creciente'),
    (2026, 11, 24, 14, 53, 'llena'),
    (2026, 12, 1, 6, 8, 'menguante'),
    (2026, 12, 9, 0, 52, 'nueva'),
    (2026, 12, 17, 5, 42, 'creciente'),
    (2026, 12, 24, 1, 28, 'llena'),
    (2026, 12, 30, 18, 59, 'menguante'),
]

EVENTOS = [
    dict(
        codigo=f"{anio}-{mes:02d}-{dia:02d}-{tipo}",
        tipo=tipo,
        instante=datetime(anio, mes, dia, hora, minuto, tzinfo=timezone.utc),
        fuente=FUENTE_USNO,
    )
    for anio, mes, dia, hora, minuto, tipo in _UTC
]

# Nombres de las fases según el MSP (2017), Anexo 4 «El conteo del tiempo lunar»
# (p. 69). La luna oscura del MSP se relaciona con la luna nueva de USNO.
NOMBRES_ANCESTRALES = {
    "nueva": "Luna oscura (Yana Killa)",
    "creciente": "Wiñak killa",
    "llena": "Pura killa",
    "menguante": "Wañuk killa",
}
