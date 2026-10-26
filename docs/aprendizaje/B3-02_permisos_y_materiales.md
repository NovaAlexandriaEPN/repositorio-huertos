# B3-02: permisos del servidor y materiales compartidos

## 1. Qué se revisó

Las pantallas de cuentas, comunidad, huerto y selección obtienen la identidad de la sesión. El navegador no elige qué usuario está actuando ni a qué comunidad pertenece.

La distinción de permisos queda así:

| Operación | Responsable | Participante |
| --- | --- | --- |
| Consultar su comunidad, huerto y miembros | Sí | Sí |
| Editar comunidad o configuración | Sí | No |
| Elegir plantas, cambiar métodos o retirar sin historial | Sí | No |
| Consultar y marcar materiales compartidos | Sí | Sí |
| Consultar nacimiento o género de otra persona | No | No |

El maestro conserva los permisos que ya tenga como miembro o responsable; su reconocimiento no concede administración. Las operaciones del servidor comparan al responsable real de la comunidad, sin aceptar un rol enviado por un formulario.

## 2. Qué se añadió para los materiales

Desde **Mi comunidad → Mi huerto → Ver materiales compartidos** se presenta una lista de recomendaciones. Cada fila tiene una casilla y un botón para guardar su disponibilidad.

Todos los miembros pueden actualizarla. La marca pertenece al huerto de su comunidad, no a la persona que pulsa el botón.

```text
Material del catálogo: pala
             │
             ├── MarcaMaterial del huerto A: disponible
             └── MarcaMaterial del huerto B: no disponible
```

Las dos comunidades consultan el mismo tipo de material, pero cada una guarda su propia disponibilidad. El sistema no administra unidades, costos ni compras.

## 3. Las dos funciones públicas para integrar

En `comunidades/servicios.py`:

```python
listar_materiales(actor=usuario)
marcar_material(actor=usuario, material_id=identificador, disponible=True)
```

`actor` procede de `request.user` en la vista.

### listar_materiales

Devuelve filas con esta estructura:

```python
{
    "material": material_del_catalogo,
    "disponible": False,
}
```

La función:

1. Comprueba que la cuenta esté activa y tenga una comunidad con huerto configurado.
2. Obtiene los métodos de siembra de las selecciones de ese huerto.
3. Consulta las marcas exclusivamente de ese huerto.
4. Incluye materiales comunes y los que correspondan a alguno de sus métodos.

Si no hay marca guardada, se muestra no disponible. Consultar la lista no crea registros.

En el catálogo, `metodos_siembra=[]` significa que el material sirve para todos los métodos. Una lista como `["semillas"]` significa que se recomienda cuando el huerto incluye ese método. El filtro se realiza en Python para funcionar con SQLite sin depender de consultas JSON no compatibles.

Si no se han elegido plantas, se muestran únicamente los materiales comunes. Si cambia un método, una marca que deja de mostrarse no se borra: puede volver a ser relevante después.

### marcar_material

Recibe el identificador del material del catálogo y un booleano real: `True` o `False`. No recibe un ID de huerto, comunidad o marca para decidir dónde escribir.

Dentro de una transacción:

1. Obtiene el huerto del miembro de la sesión.
2. Comprueba que el material exista y corresponda a sus métodos.
3. Busca la marca por la combinación huerto y material.
4. Crea la marca si falta o actualiza la existente.
5. Valida el modelo y guarda solo la disponibilidad cuando ya existe.

Se guarda el valor solicitado. No se alterna automáticamente el anterior: reenviar `True` deja `True`, sin invertirlo ni crear otra fila. La restricción única del modelo mantiene una marca por material y huerto.

## 4. El recorrido del formulario

```text
GET /comunidades/huerto/materiales/
    ↓
listar_materiales → recomendaciones y marcas propias
    ↓
Plantilla con una casilla por material
    ↓
POST /comunidades/huerto/materiales/<material_id>/
    ↓
DisponibilidadMaterialForm → marcar_material
    ↓
MarcaMaterial → redirección al listado
```

Cada formulario tiene un prefijo, por ejemplo `material-7`. Eso permite que las casillas de varias filas tengan nombres e identificadores diferentes.

El nombre del campo de esa fila será `material-7-disponible`. La casilla marcada se convierte en `True`; si se desmarca, el formulario devuelve `False`. Ambos casos llaman al mismo servicio.

La vista usa POST y CSRF. Una visita por GET a la ruta de guardado no cambia nada y responde con método no permitido. Los IDs de huerto, comunidad o marca añadidos al envío no se usan para seleccionar el destino.

## 5. Puntos de integración para Juan y Doménica

En la revisión se encontró que la versión disponible de la rama de Juan aún no tenía funciones de materiales. Se añadió una base funcional en `bryan`, conservando el resto de las operaciones de los archivos compartidos.

Para incorporar trabajo posterior:

- Reutilizar `listar_materiales` y `marcar_material` o revisar sus cambios juntos antes de integrar otra implementación equivalente.
- Conservar el control de pertenencia en el servicio. Los participantes también pueden marcar materiales.
- Mantener `DisponibilidadMaterialForm` y su prefijo por material, o actualizar de forma coordinada vista y plantilla si cambia el contrato del formulario.
- La plantilla recibe `materiales`: cada fila contiene `material`, `disponible` y `form`. Puede cambiar su presentación manteniendo las rutas y el token CSRF.
- Revisar los cambios concretos de `forms.py`, `views.py` y `servicios.py`; no reemplazar esos archivos completos por versiones antiguas de otra rama.

Las rutas estables son `comunidades:materiales` y `comunidades:marcar_material`. La segunda requiere `material_id`.

Esta guía documenta la conexión técnica. No afirma que ya se haya realizado una coordinación personal ni que se haya incorporado el diseño definitivo de otra persona.

## 6. Qué comprobaciones se hicieron

Los casos nuevos verifican:

- Materiales comunes y específicos según los métodos elegidos.
- Lecturas sin crear marcas.
- Una disponibilidad compartida por los miembros de la misma comunidad.
- Reenvíos sin duplicar ni invertir la marca.
- Aislamiento de la disponibilidad de otra comunidad, incluso con IDs inyectados en el envío.
- Rechazo de cuentas anónimas, inactivas o sin pertenencia.
- Escrituras por POST con CSRF y tratamiento del catálogo vacío o de la ausencia de huerto.

El recorrido integrado de B3-01 también incluye que el participante marque un material después de unirse. Usa registro, sesión y formularios reales en la misma base temporal, con CSRF activo.

```powershell
python manage.py test comunidades.tests.MaterialesCompartidosTests
python manage.py test comunidades.tests.RecorridoInicialIntegradoTests
python manage.py test
```

Estas son comprobaciones de desarrollo. No se llenó `docs/v1/resultados.md` ni se dio por ejecutada la batería formal de noviembre.

## 7. Qué falta para verlo con el contenido definitivo

El catálogo y su comando de carga siguen pendientes en esta rama. Las pruebas emplean material ficticio y no lo insertan en tu base local.

Para la revisión del producto con el equipo deben integrarse las opciones, materiales y 18 fichas documentadas. La lista informa cuando no hay recomendaciones disponibles. No se han creado cantidades ni un inventario adicional para completar esta tarea.

## 8. Qué leer primero para aprender

Empieza por `marcar_material`: reconoce la cuenta que actúa, la búsqueda del huerto propio, la comprobación del material y la creación o actualización de la marca.

Después sigue `actualizar_material`, en `views.py`. La vista valida el formulario, llama al servicio y devuelve una redirección. No decide por su cuenta qué huerto editar.

Por último revisa `materiales.html`: muestra los datos y envía el formulario. La casilla representa el valor guardado; los permisos no dependen de que esa casilla esté visible.
