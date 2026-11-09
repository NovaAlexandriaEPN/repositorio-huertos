# B3-03: pruebas de privacidad, pertenencia e historial

Las pruebas de estas reglas están en `cuentas/tests.py` y `comunidades/tests.py`. Se ejecutan con el descubrimiento normal de Django y datos ficticios en una base temporal.

## Reglas y pruebas correspondientes

| Regla del producto | Comprobaciones |
| --- | --- |
| Nacimiento y género solo pertenecen al perfil de su titular | `cuentas.tests.PerfilTests`, `comunidades.tests.PantallasComunidadTests.test_consulta_no_expone_comunidad_ajena_ni_perfil_de_otro_miembro` y `test_responsable_no_lee_ni_edita_el_perfil_privado_de_otro_miembro` |
| Una cuenta pertenece a una sola comunidad | `comunidades.tests.ComunidadMiembroTests`, `OperacionesComunidadTests` y `PantallasComunidadTests.test_formulario_antiguo_no_traslada_a_quien_ya_creo_una_comunidad` |
| Una selección con historial conserva su método y no se retira | `comunidades.tests.SeleccionesMaterialesTests` y `ContratoHistorialSeleccionTests` |

`PerfilTests` comprueba que un ID ajeno en GET o POST no permita consultar o editar otra cuenta. La prueba de comunidad añade el caso de un responsable que intenta acceder al perfil de un participante de su propio grupo. Su condición de responsable no amplía ese permiso.

Las pruebas de pertenencia comprueban la restricción de base, la validación y los servicios. El caso de dos formularios abiertos comprueba un envío desactualizado: si una pestaña ya creó una comunidad para esa cuenta, el formulario de unión abierto antes no puede trasladarla a otro grupo.

La prueba de historial crea una relación temporal de actividades en la base de pruebas. Comprueba registros activos y anulados, incluso si el gestor habitual oculta las anuladas. Valida el modelo, los servicios y el rechazo de POST procedentes de formularios abiertos antes de que apareciera la actividad.

## Cómo ejecutar las comprobaciones

Desde el repositorio, con la clave local cargada según el README:

```powershell
# Privacidad del perfil
& .\.venv\Scripts\python.exe manage.py test cuentas.tests.PerfilTests

# Pertenencia, privacidad del grupo y formularios desactualizados
& .\.venv\Scripts\python.exe manage.py test comunidades.tests.ComunidadMiembroTests comunidades.tests.OperacionesComunidadTests comunidades.tests.PantallasComunidadTests

# Historial activo y anulado
& .\.venv\Scripts\python.exe manage.py test comunidades.tests.ContratoHistorialSeleccionTests

# Conjunto completo
& .\.venv\Scripts\python.exe manage.py test
```

La línea `OK` y el código de salida cero indican que pasaron los casos ejecutados. Una `AssertionError` muestra qué resultado esperado no se cumplió; un `ERROR` puede indicar un problema de ejecución o de preparación de los datos.

## Cómo leer una prueba

Cada caso prepara un escenario, ejecuta una acción y comprueba su efecto. Por ejemplo:

```text
Preparar: una cuenta sin comunidad abre dos formularios.
Actuar: crea una comunidad y después envía el formulario de unión antiguo.
Comprobar: conserva una única pertenencia a la comunidad que creó.
```

Las comprobaciones verifican respuestas y estado persistido. Rechazar un envío no basta si la base hubiera cambiado de todas formas.

## Integración con las pruebas del equipo

Guillermo puede ejecutar estas clases y comparar sus casos antes de añadir otros sobre las mismas reglas. La prueba temporal de historial valida el contrato previsto; el recorrido final con el modelo y los servicios de Fernando sigue pendiente de su integración.

Estas son comprobaciones de desarrollo. La ejecución formal de los casos del curso y sus resultados se registrarán cuando corresponda en noviembre. B3-03 no necesita cobertura, CI ni paquetes adicionales.
