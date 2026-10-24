"""Único punto de reunión de los datos fijos de cada integrante."""
from .actividades import ACTIVIDADES
from .huerto import MATERIALES, OPCIONES
from .luna import EVENTOS
from .plantas_juan import PLANTAS as PLANTAS_JUAN
# Agregar aquí las listas de Matthew y Guillermo cuando estén entregadas.
PLANTAS = [*PLANTAS_JUAN]
