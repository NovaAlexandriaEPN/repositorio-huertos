"""
Cálculos puros del alcance V1: no consultan tablas ni conceden permisos.
Reciben datos simples (sin ORM); servicios.py consulta la base y se los pasa.
"""
UMBRAL_MAESTRO = 100
HITOS = ("preparacion", "siembra", "crecimiento", "cosecha", "secado", "empaquetado")

"""
Recibe nombres de hitos cumplidos; devuelve el avance de 0 a 100, "cuidados" y "riego" cuentan como un solo hito: "crecimiento".
Los repetidos o desconocidos no suman.
"""
def calcular_progreso(hitos_cumplidos):
    hitos = set(hitos_cumplidos)
    if hitos.intersection({"cuidados", "riego"}):
        hitos.add("crecimiento")
    return len(hitos.intersection(HITOS)) * 100 / len(HITOS)


"""
Recibe puntos y si el responsable lo nombró; devuelve el nivel.
0-99 Aprendiz; desde 100 Oficial; Maestro solo si hay nombramiento
y al menos 100 puntos (los puntos solos nunca lo nombran).
 """
def calcular_nivel(puntos, nombrado=False):
    if puntos < UMBRAL_MAESTRO:
        return {"nombre": "Aprendiz", "es_elegible_maestro": False}
    return {"nombre": "Maestro" if nombrado else "Oficial", "es_elegible_maestro": True}
