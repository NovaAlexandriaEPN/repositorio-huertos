"""Único punto de reunión de los datos fijos de cada integrante."""
from .actividades import ACTIVIDADES
from .huerto import MATERIALES, OPCIONES
from .luna import EVENTOS
from .plantas_juan import PLANTAS as PLANTAS_JUAN
from .plantas_matthew import PLANTAS as PLANTAS_MATTHEW
from .plantas_guillermo import PLANTAS as PLANTAS_GUILLERMO
PLANTAS = [*PLANTAS_JUAN, *PLANTAS_MATTHEW, *PLANTAS_GUILLERMO]
