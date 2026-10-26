"""Cálculos puros del alcance V1: no consultan tablas ni conceden permisos."""
UMBRAL_MAESTRO = 100
HITOS = ("preparacion", "siembra", "crecimiento", "cosecha", "secado", "empaquetado")


def calcular_progreso(hitos_cumplidos):
    hitos = set(hitos_cumplidos)
    if hitos.intersection({"cuidados", "riego"}):
        hitos.add("crecimiento")
    return len(hitos.intersection(HITOS)) * 100 / len(HITOS)


def calcular_nivel(puntos, nombrado=False):
    if puntos < UMBRAL_MAESTRO:
        return {"nombre": "Aprendiz", "es_elegible_maestro": False}
    return {"nombre": "Maestro" if nombrado else "Oficial", "es_elegible_maestro": True}
