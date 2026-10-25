"""Copia a una base SQLite ya usada los datos de foto revisados de las fichas.

cargar_catalogo no modifica plantas que ya existen. Si tu base se cargó antes de
la revisión de fotos (24-25 de octubre de 2026), puede conservar rutas o créditos
antiguos, por ejemplo una ruta «static/img/...» que deja la foto rota.

Respalda la base y ejecuta desde la raíz del proyecto:

    python manage.py shell -c "exec(open('docs/v1/diseno/actualizar_fotos_base.py', encoding='utf-8').read())"

Solo cambia la foto, sus créditos, las fuentes, los pendientes y las observaciones
de cada ficha. No toca huertos, selecciones, actividades ni cuentas.
"""
from django.db import transaction

from catalogo.datos import PLANTAS
from catalogo.models import Planta

CAMPOS = ("imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia",
          "fuentes", "campos_no_verificados", "observaciones")

with transaction.atomic():
    for fila in PLANTAS:
        n = Planta.objects.filter(codigo=fila["codigo"]).update(**{c: fila[c] for c in CAMPOS})
        print(fila["codigo"], "actualizada" if n else "no existe en esta base")
