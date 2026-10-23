"""
Reglas puras de cálculo de progreso, nivel y recompensas para Huertos Medicinales.
Desarrollado en coordinación con Guillermo (Tester) según el plan de trabajo.
NO realiza consultas a la base de datos (funciones puras sin efectos secundarios).
"""
from typing import Iterable, Set, Dict, Any

# Los seis hitos fundamentales del ciclo de cultivo de plantas medicinales
HITOS_CULTIVO = (
    'preparacion',
    'siembra',
    'riego',
    'cuidado',
    'cosecha',
    'secado',
)

TOTAL_HITOS = len(HITOS_CULTIVO)  # 6 hitos

# Tabla base de puntos por tipo de actividad
PUNTOS_POR_ACTIVIDAD = {
    'diseno': 10,
    'preparacion': 10,
    'siembra': 15,
    'riego': 5,          # 5 la primera vez, 0 las siguientes
    'cuidado': 5,        # 5 la primera vez, 0 las siguientes
    'abono': 5,
    'asociacion': 5,
    'poda': 5,
    'control_plagas': 5,
    'cosecha': 20,
    'secado': 15,
    'procesamiento': 10,
    'ritual': 10,
}

UMBRAL_MINIMO_MAESTRO = 100


def calcular_puntos_actividad(tipo: str, es_primera_en_planta: bool = True) -> int:
    """
    Calcula los puntos que otorga una actividad según las reglas del dominio.

    Reglas:
    - Hitos (preparación, siembra, riego, cuidado, cosecha, secado): puntos base la primera
      vez en la planta y 0 las siguientes (riego y cuidado: 5 y luego 0). Así otro UUID
      no duplica los puntos de un hito ya cumplido.
    - Demás actividades: otorgan los puntos base definidos.
    """
    if tipo in HITOS_CULTIVO and not es_primera_en_planta:
        return 0
    return PUNTOS_POR_ACTIVIDAD.get(tipo, 5)


def determinar_hitos_cumplidos(tipos_actividades: Iterable[str]) -> Set[str]:
    """
    Determina qué hitos del ciclo de cultivo han sido completados
    a partir de una colección de tipos de actividades activas.
    """
    tipos_set = set(tipos_actividades)
    return tipos_set.intersection(set(HITOS_CULTIVO))


def calcular_progreso(hitos_cumplidos: Iterable[str]) -> float:
    """
    Calcula el porcentaje de progreso del huerto sobre los seis hitos (0.0 a 100.0%).
    
    Recibe:
        hitos_cumplidos: Colección de nombres de hitos alcanzados.
    Retorna:
        Porcentaje completado con un decimal de precisión (0.0% a 100.0%).
    """
    hitos_validos = set(hitos_cumplidos).intersection(set(HITOS_CULTIVO))
    porcentaje = (len(hitos_validos) / TOTAL_HITOS) * 100.0
    return round(porcentaje, 1)


def calcular_nivel(puntos: int) -> Dict[str, Any]:
    """
    Calcula el nivel y rango alcanzado por un miembro en función de sus puntos acumulados.

    Niveles:
    - Nivel 1 (0-49 pts): Semilla / Aprendiz
    - Nivel 2 (50-99 pts): Brote / Cultivador
    - Nivel 3 (100-199 pts): Guardián / Cuidador (Elegible para Maestro)
    - Nivel 4 (200-299 pts): Cosechador / Sabio
    - Nivel 5 (300+ pts): Maestro Ancestral (Nota: no confiere nombramiento ni admin automático)
    """
    puntos_normalizados = max(0, int(puntos or 0))

    if puntos_normalizados < 50:
        return {
            'nivel': 1,
            'nombre': 'Semilla (Aprendiz)',
            'siguiente_umbral': 50,
            'puntos_restantes': 50 - puntos_normalizados,
            'es_elegible_maestro': False,
        }
    elif puntos_normalizados < 100:
        return {
            'nivel': 2,
            'nombre': 'Brote (Cultivador)',
            'siguiente_umbral': 100,
            'puntos_restantes': 100 - puntos_normalizados,
            'es_elegible_maestro': False,
        }
    elif puntos_normalizados < 200:
        return {
            'nivel': 3,
            'nombre': 'Guardián (Cuidador)',
            'siguiente_umbral': 200,
            'puntos_restantes': 200 - puntos_normalizados,
            'es_elegible_maestro': True,
        }
    elif puntos_normalizados < 300:
        return {
            'nivel': 4,
            'nombre': 'Cosechador (Sabio)',
            'siguiente_umbral': 300,
            'puntos_restantes': 300 - puntos_normalizados,
            'es_elegible_maestro': True,
        }
    else:
        return {
            'nivel': 5,
            'nombre': 'Maestro Ancestral',
            'siguiente_umbral': None,
            'puntos_restantes': 0,
            'es_elegible_maestro': True,
        }
