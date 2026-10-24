# B2-02: crear, unirse y editar una comunidad

Esta tarea convierte los modelos de B2-01 en operaciones que ya se pueden usar desde el navegador.

## 1. Qué puedes hacer ahora

Entra con tu cuenta y abre **Mi comunidad**, en el menú, o esta dirección con el servidor iniciado:

<http://127.0.0.1:8000/comunidades/>

- Si todavía no perteneces a una comunidad, puedes crear una o unirte con un código.
- Al crearla, te conviertes en su responsable y también en uno de sus miembros.
- Si te unes con un código, entras como participante.
- Todos los miembros pueden consultar su comunidad y la lista de nombres.
- Solo el responsable puede editar nombre, tipo y datos de contacto.
- Nadie puede usar estas operaciones para trasladarse a otra comunidad o transferir al responsable.

El huerto se configurará en B2-03. Crear ahora una comunidad no inventa una ubicación, un área o unas opciones de huerto para completar campos obligatorios.

## 2. El ejemplo que conecta todo

Ana crea «Huerto del barrio». El servicio guarda dos registros juntos:

```text
Comunidad
  nombre: Huerto del barrio
  responsable: cuenta de Ana
  código: generado por el servidor

Miembro
  usuario: cuenta de Ana
  comunidad: Huerto del barrio
```

Luis usa el código. No se copia la comunidad: se añade otra pertenencia que señala a la misma comunidad.

```text
Cuenta de Ana  → Miembro → Huerto del barrio ← Miembro ← Cuenta de Luis
                                  ↑
                         responsable: Ana
```

«Responsable» se deduce de `Comunidad.responsable`. No hay otro campo de rol que debamos mantener sincronizado. Por eso Luis no puede convertirse en responsable enviando un campo adicional desde su navegador.

## 3. Qué hace cada archivo nuevo

| Archivo | Qué debes buscar | Para qué sirve |
| --- | --- | --- |
| `comunidades/forms.py` | `ComunidadForm` y `UnirseComunidadForm` | Recibir y validar los campos de los formularios. |
| `comunidades/servicios.py` | `crear_comunidad`, `unirse_comunidad`, `editar_comunidad` | Ejecutar las operaciones y comprobar sus reglas. |
| `comunidades/views.py` | `crear`, `unirse`, `editar`, `mi_comunidad` | Coordinar la solicitud y devolver una página o una redirección. |
| `comunidades/urls.py` | Los cuatro `path(...)` | Relacionar una dirección con la vista correspondiente. |
| `templates/comunidades/` | `formulario.html`, `unirse.html`, `mi_comunidad.html` | Presentar campos, nombres, contactos y resultados. |
| `comunidades/tests.py` | `OperacionesComunidadTests` y `PantallasComunidadTests` | Comprobar las operaciones y sus permisos. |

También se añadió **Mi comunidad** a `templates/base.html` y unas reglas de presentación a `static/css/estilos.css`.

## 4. Sigue primero una sola operación: crear

### Paso A. La dirección elige una vista

En `comunidades/urls.py`:

```python
path("crear/", views.crear, name="crear")
```

La ruta global ya añade el prefijo `comunidades/`. Juntas producen `/comunidades/crear/`.

`views.crear` indica la función que debe atender la solicitud. `name="crear"` permite enlazar a ella mediante su nombre, `comunidades:crear`.

### Paso B. GET muestra; POST envía

En la vista:

```python
form = ComunidadForm(request.POST if request.method == "POST" else None)
```

Si abriste la página, el método es GET y se prepara un formulario sin datos enviados. Si pulsaste **Crear comunidad**, el método es POST y el formulario recibe los campos enviados.

```python
if request.method == "POST" and form.is_valid():
```

`and` exige ambas condiciones. No se crea una comunidad por visitar la dirección ni por enviar campos que el formulario rechaza.

### Paso C. El formulario limita qué se puede enviar

`ComunidadForm.Meta.fields` contiene solo:

```python
fields = (
    "nombre",
    "tipo",
    "contacto_nombre",
    "contacto_telefono",
    "contacto_correo",
)
```

Es una tupla: una colección ordenada de nombres. No incluye `responsable`, `codigo_invitacion`, identificadores de otras comunidades ni permisos.

Este formulario utiliza los campos del modelo para validar textos, tipo, teléfono y correo. La vista no llama a `form.save()`: entrega los datos válidos al servicio, que también crea la pertenencia y aplica las reglas de la operación completa.

### Paso D. La sesión decide quién crea

```python
crear_comunidad(actor=request.user, **form.cleaned_data)
```

- `request.user` es la cuenta identificada por la sesión.
- `actor=` le da un nombre explícito a ese argumento.
- `form.cleaned_data` es el diccionario de campos que pasó la validación.
- `**` entrega las claves del diccionario como argumentos con nombre.

Por ejemplo, si el diccionario contiene `{"nombre": "Huerto del barrio"}`, `**` permite pasarlo como `nombre="Huerto del barrio"`. Los otros campos se pasan del mismo modo.

La persona que usa la aplicación no puede elegir otra cuenta como `actor` mediante un campo del formulario.

### Paso E. El servicio valida y guarda

El servicio de creación:

1. Comprueba que la cuenta siga activa.
2. Comprueba que todavía no tenga comunidad ni una comunidad a su cargo.
3. Construye `Comunidad` con el responsable obtenido del actor.
4. Ejecuta `full_clean()` y guarda la comunidad.
5. Construye y valida `Miembro` para el creador y lo guarda.
6. Confirma ambos cambios juntos.

`full_clean()` comprueba los datos del modelo. `save()` los escribe. No son la misma operación y `save()` no ejecuta automáticamente `full_clean()`.

La creación utiliza:

```python
with _escritura_atomica():
    # Crear comunidad y pertenencia.
```

El nombre que empieza por `_` indica una ayuda interna del módulo. Esa ayuda usa `transaction.atomic()` de Django: si una parte falla, la operación se revierte y no queda una comunidad creada a medias.

La función auxiliar tiene `@contextmanager` y `yield`. Por ahora basta con leerlo así: abre la operación protegida, deja ejecutar lo que está dentro del `with` y, al terminar, confirma o revierte. Cuando estudiemos esa función línea por línea veremos la sintaxis. El mismo bloque atiende conflictos esperados de escritura para que la página pueda mostrar un mensaje de reintento.

### Paso F. La vista devuelve el resultado

Si el servicio termina correctamente, se muestra un mensaje y se redirige a **Mi comunidad**. La siguiente página se obtiene por GET: actualizar esa página no repite el POST anterior.

Si el servicio lanza `ValidationError`, `_mostrar_errores` lo conecta con el formulario. Los errores de un campo aparecen asociados a ese campo; los generales se muestran en el resumen compartido.

## 5. Qué cambia al unirse

El formulario recibe únicamente `codigo_invitacion`. Acepta los 12 caracteres hexadecimales del código, en mayúsculas o minúsculas, y normaliza las minúsculas a mayúsculas.

El servicio también normaliza y valida el código. Es importante que la regla exista ahí: una llamada desde Python no debe depender de haber usado antes el formulario.

Con un código existente y una cuenta sin comunidad, el servicio crea un `Miembro`. No cambia al responsable. Si la cuenta ya pertenece a una comunidad, rechaza la operación, incluso si vuelve a enviar el mismo código.

El código permite unirse. No sirve como contraseña, no inicia sesión y no permite editar directamente otra comunidad.

## 6. Qué cambia al editar

La dirección es `/comunidades/editar/`, sin un ID que permita elegir otra comunidad.

El servicio consulta la pertenencia de `request.user` y obtiene su comunidad. Después compara:

```python
comunidad.responsable_id != actor.pk
```

Lee esa expresión como «el identificador del responsable es distinto del identificador de la persona que intenta actuar». Si es distinto, la operación se rechaza con `PermissionDenied`.

El enlace de edición solo aparece al responsable, pero el permiso también se comprueba al entrar a la dirección y al ejecutar el servicio. Ocultar un enlace en HTML no es una autorización suficiente.

Al guardar, `update_fields` enumera los cinco campos permitidos. El código de invitación y el responsable se conservan.

## 7. Cómo probarlo tú, paso a paso

Con el servidor iniciado según el README:

1. Entra con una cuenta de prueba sin comunidad y abre **Mi comunidad**.
2. Pulsa **Crear una comunidad** y completa nombre, tipo y contacto con datos ficticios válidos.
3. Comprueba que apareces como responsable y que puedes ver el código generado.
4. Pulsa **Editar los datos de la comunidad**, cambia su nombre y guarda. El código debe seguir siendo el mismo.
5. Cierra sesión y entra con otra cuenta de prueba sin comunidad. Usa **Unirse con un código**.
6. Introduce el código anterior. Ahora debes ver la misma comunidad y ambos nombres.
7. Comprueba que esta segunda cuenta figura como participante y no tiene enlace de edición.
8. Desde esa cuenta, visita directamente `/comunidades/editar/`. Debe responder con acceso denegado (HTTP 403).
9. Comprueba que no se muestra nacimiento ni género de otros miembros.
10. Con una tercera cuenta sin comunidad, prueba un código inexistente: debe aparecer un error y no debe crearse una pertenencia.

Puedes usar dos navegadores o una ventana privada para mantener abiertas dos sesiones distintas. Dos pestañas normales del mismo navegador comparten la sesión.

Las pruebas automatizadas usan una base temporal y no crean estas cuentas en tu base local:

```powershell
python manage.py test comunidades
python manage.py test
```

## 8. Buenas prácticas que estás aplicando

- **Responsabilidades separadas:** el formulario valida campos; el servicio ejecuta reglas; la vista coordina; la plantilla presenta.
- **Autorización en el servidor:** comunidad y responsable proceden de la cuenta de la sesión, no de identificadores enviados por el cliente.
- **Lista explícita de campos:** creación y edición no aceptan cambios de permisos o de identidad.
- **Transacción:** crear comunidad y pertenencia es una operación indivisible.
- **Reglas también fuera del formulario:** llamar al servicio directamente no elimina las comprobaciones de pertenencia y autorización.
- **Privacidad al consultar:** la lista de miembros selecciona solo identificador de cuenta y nombre, en lugar de entregar perfiles completos.
- **POST, CSRF y redirección:** las escrituras están protegidas y el resultado correcto lleva a una página de consulta.

No añadimos un repositorio genérico, una API o una jerarquía de clases adicional: la separación actual permite entender las operaciones con pocas piezas.

## 9. Qué está terminado y qué sigue

- **B2-01:** están los cinco modelos y sus migraciones. Fernando puede referenciar `Huerto`, `Miembro` y `PlantaHuerto` al construir `Actividad`.
- **B2-02:** crear, unirse, consultar y editar comunidad están implementados y comprobados.
- **B2-03:** implementado el configurador con ubicación manual, área y opciones de las categorías correctas, solo por el responsable.
- **B2-04:** implementada la selección de plantas, el cambio de método y el retiro sin historial. Su contrato con actividades se comprueba con registros temporales de prueba.

Consulta [la guía de B2-03 y B2-04](B2-03_B2-04_huerto_y_plantas.md) para entender y probar esas operaciones. La comprobación final con el modelo y los servicios de Fernando se ejecutará cuando estén integrados. El contenido definitivo del catálogo y su carga siguen siendo entregas separadas.
