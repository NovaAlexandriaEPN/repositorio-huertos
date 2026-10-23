"""
Reglas puras de nivel y progreso (tarea G2 de Guillermo).

Funciones sin consultas a la base de datos: reciben números o listas y devuelven el
resultado, para poder probarlas en sus límites sin preparar datos.

Versión inicial dejada por Fernando para integrar el Huerto Virtual. Guillermo puede
reemplazar la implementación conservando estas firmas:
    calcular_progreso(hitos_cumplidos) -> float
    calcular_nivel(puntos) -> dict
    porcentaje_en_nivel(puntos) -> float
Los puntos de cada actividad no están aquí: son una regla de registro y viven en
actividades/servicios.py (tarea F2).
"""
from typing import Iterable

# Los seis hitos del ciclo de cultivo, con los mismos códigos de Actividad.Tipo.
HITOS = ("preparacion", "siembra", "riego", "cuidado", "cosecha", "secado")

# Límite inferior de cada nivel y su nombre. El nivel 5 no tiene límite superior.
NIVELES = (
    (0, "Semilla"),
    (50, "Brote"),
    (100, "Guardián"),
    (200, "Cosechador"),
    (300, "Sabio del huerto"),
)

# Puntos desde los que una persona puede ser nombrada Maestro (CP-08).
# Es una condición para el nombramiento, no lo concede por sí sola.
UMBRAL_MAESTRO = 100


def calcular_progreso(hitos_cumplidos: Iterable[str]) -> float:
    """Porcentaje de los seis hitos cumplidos, de 0.0 a 100.0 con un decimal.

    Ignora códigos que no son hitos y cuenta cada hito una sola vez.
    """
    cumplidos = set(hitos_cumplidos).intersection(HITOS)
    return round(len(cumplidos) * 100 / len(HITOS), 1)


def calcular_nivel(puntos: int) -> dict:
    """Nivel alcanzado con unos puntos.

    Devuelve: nivel (1 a 5), nombre, minimo (puntos donde empieza el nivel),
    siguiente_umbral (None en el nivel 5), puntos_restantes y es_elegible_maestro.
    """
    puntos = max(0, int(puntos or 0))
    indice = 0
    for posicion, (minimo, _nombre) in enumerate(NIVELES):
        if puntos >= minimo:
            indice = posicion
    minimo, nombre = NIVELES[indice]
    siguiente = NIVELES[indice + 1][0] if indice + 1 < len(NIVELES) else None
    return {
        "nivel": indice + 1,
        "nombre": nombre,
        "minimo": minimo,
        "siguiente_umbral": siguiente,
        "puntos_restantes": (siguiente - puntos) if siguiente is not None else 0,
        "es_elegible_maestro": puntos >= UMBRAL_MAESTRO,
    }


def porcentaje_en_nivel(puntos: int) -> float:
    """Avance dentro del nivel actual, de 0.0 a 100.0 con un decimal.

    En el nivel 5, que no tiene límite superior, devuelve 100.0.
    """
    nivel = calcular_nivel(puntos)
    if nivel["siguiente_umbral"] is None:
        return 100.0
    puntos = max(0, int(puntos or 0))
    tramo = nivel["siguiente_umbral"] - nivel["minimo"]
    return round((puntos - nivel["minimo"]) * 100 / tramo, 1)
