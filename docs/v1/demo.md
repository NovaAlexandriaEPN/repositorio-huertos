# Guion de la demo V1

**Huertos medicinales comunitarios · Nova Alexandria · Calidad de Software (ISWD652, 2026B)**

Demo presencial del martes 10 de noviembre de 2026. Este guion es una guía, no un libreto: se
puede cambiar el orden o saltar pasos según el tiempo y las preguntas de la clase.

> **Estado: borrador.** La base ficticia todavía no existe. Los textos entre `{{ }}` son
> marcadores que se reemplazan cuando esté lista (ver [Marcadores](#marcadores-por-completar)).
> Todos los datos de la demo son ficticios.

---

## Marcadores por completar

Guillermo los completa al preparar la base. Juan revisa que el recorrido siga funcionando.

| Marcador | Qué poner |
|---|---|
| `{{RUTA_BASE_DEMO}}` | Ubicación de la copia de la base (fuera de Git) |
| `{{CONTRASENA_DEMO}}` | Contraseña ficticia de las cuentas de la demo |
| `{{COMUNIDAD_A}}` | Comunidad principal de la demo |
| `{{USUARIO_RESPONSABLE}}` | Responsable de la comunidad A |
| `{{USUARIO_PARTICIPANTE}}` | Participante de la comunidad A |
| `{{COMUNIDAD_B}}` | Segunda comunidad |
| `{{USUARIO_AJENO}}` | Responsable de la comunidad B |
| `{{ID_HUERTO_A}}` | Número del huerto A, visible en la dirección de Mi huerto |
| `{{PLANTA_AVANZADA}}` | Planta con el ciclo avanzado |
| `{{PLANTA_PLANEADA}}` | Planta sin actividades, para registrar en vivo |
| `{{FECHA_PREPARACION}}` | Fecha de la preparación de la tierra del huerto A |
| `{{FECHA_RECHAZADA}}` | Fecha para el error: 14 días después de `{{FECHA_PREPARACION}}` |
| `{{PUNTOS_PARTICIPANTE}}` | Puntos del participante al iniciar |
| `{{AVANCE_INICIAL}}` | Avance del huerto A al iniciar |
| `{{MATERIAL_DEMO}}` | Material sin marcar que se usará en vivo |
| `{{PRESENTA_1}}` a `{{PRESENTA_6}}` | Quién presenta cada parte |
| `{{DURACION_TOTAL}}` | Tiempo disponible en clase |
| `{{EQUIPO_RESPALDO}}` | Quién lleva el computador de respaldo |

## Qué debe tener la base ficticia

El recorrido necesita estos datos. Se identifican como ficticios en sus nombres.

**Comunidad A**

- Un responsable y un participante, con el huerto configurado.
- `{{PLANTA_AVANZADA}}` con su ciclo registrado por el participante, de modo que este tenga
  **al menos 100 puntos**. El ciclo completo de una planta con las tres actividades generales
  suma 125 puntos.
- La preparación de la tierra activa, con **15 días o más** de antigüedad.
- `{{PLANTA_PLANEADA}}` elegida, sin ninguna actividad.
- **Sin maestro nombrado**, para hacerlo en vivo.
- `{{MATERIAL_DEMO}}` sin marcar como disponible.

**Comunidad B**

- Un responsable con su huerto configurado, para mostrar que no ve los datos de la comunidad A.

## Antes de empezar

1. Respaldar la base de trabajo y restaurar la copia de demo (README, sección 9), desde
   `{{RUTA_BASE_DEMO}}`.
2. Levantar el servidor y dejar abierto <http://127.0.0.1:8000/>:

   ```powershell
   & .\.venv\Scripts\python.exe manage.py runserver
   ```

3. Abrir dos ventanas: una normal con `{{USUARIO_RESPONSABLE}}` y una de incógnito con
   `{{USUARIO_PARTICIPANTE}}`.
4. Dejar a mano una tercera ventana para `{{USUARIO_AJENO}}`.

El sistema funciona sin internet. Tiempo disponible: `{{DURACION_TOTAL}}`.

## Recorrido

### 1. Presentación del producto · `{{PRESENTA_1}}`

Explicar en una frase qué hace la aplicación: configurar un huerto medicinal comunitario,
consultar saberes ancestrales, registrar actividades y observar plantas, puntos y niveles.

### 2. Cuenta y comunidad · `{{PRESENTA_2}}` · HU-01 a HU-03

1. En la tercera ventana, todavía sin sesión, abrir **Crear cuenta** y señalar el aviso de datos
   y su aceptación.
2. Con `{{USUARIO_RESPONSABLE}}`, entrar a **Mi comunidad** y mostrar el rol, los miembros y el
   código de invitación.
3. Abrir el perfil y explicar que nacimiento y género solo los ve su titular.

### 3. Huerto y materiales · `{{PRESENTA_3}}` · HU-04 y HU-12

1. Con el responsable, abrir **Plantas del huerto** y mostrar la configuración y las especies elegidas.
2. Con `{{USUARIO_PARTICIPANTE}}`, abrir **Materiales** y marcar `{{MATERIAL_DEMO}}` como disponible.
3. Con el responsable, recargar **Materiales** y comprobar que aparece **Disponible**.

### 4. Catálogo, guía y calendario · `{{PRESENTA_4}}` · HU-05 a HU-07

1. Abrir **Catálogo** y la ficha de lavanda. Señalar la foto con su crédito, las fuentes y el
   dato **No verificado** en la cualidad ancestral.
2. Abrir **Guías** y mostrar un plazo obligatorio frente a una recomendación.
3. Abrir **Calendario**, ir a diciembre con la fecha de referencia 2026-12-08 y mostrar que la
   luna nueva de las 00:52 UTC del día 9 aparece el 8 a las 19:52 en Guayaquil.

### 5. Actividades y reglas · `{{PRESENTA_5}}` · HU-08 y HU-10

Con `{{USUARIO_PARTICIPANTE}}`:

1. Abrir **Mi huerto** y mostrar las tarjetas, `{{AVANCE_INICIAL}}` de avance y
   `{{PUNTOS_PARTICIPANTE}}` puntos.
2. Pulsar **Registrar actividad**: siembra de `{{PLANTA_PLANEADA}}` con fecha `{{FECHA_RECHAZADA}}`.
   Debe aparecer: *«La siembra requiere una preparación de la tierra al menos 15 días antes.»*
3. Registrar la misma siembra con la fecha y hora actuales.
4. Volver a **Mi huerto**: la planta pasa a **Sembrada**, el avance sube y el participante gana
   15 puntos.

### 6. Anulación y maestro · `{{PRESENTA_6}}` · HU-09 y HU-11

Con `{{USUARIO_RESPONSABLE}}`:

1. Abrir **Historial**, pulsar **Anular** en la siembra anterior y escribir el motivo.
2. Mostrar que el registro sigue visible con motivo, autor y fecha, y que el estado y los puntos
   vuelven a sus valores anteriores.
3. Abrir **Mi huerto**, pulsar **Nombrar Maestro**, elegir al participante y escribir el motivo.
4. Explicar que maestro es un reconocimiento: no da permisos de administración.

### 7. Protección de datos · HU-08

Con `{{USUARIO_AJENO}}`, abrir `http://127.0.0.1:8000/actividades/{{ID_HUERTO_A}}/`. El sistema
responde **403**: un huerto de otra comunidad no se puede consultar cambiando la dirección.

## Si algo falla

- **Datos alterados por un ensayo:** detener el servidor y restaurar de nuevo la copia de demo.
- **El servidor no arranca:** revisar que `DJANGO_SECRET_KEY` esté cargada (README, sección 3.4).
- **Falta tiempo:** priorizar las partes 5 y 6, que muestran las reglas principales.
- **Falla el computador:** `{{EQUIPO_RESPALDO}}` lleva otra copia del proyecto y de la base.

## Después de cada ensayo

Restaurar la copia de demo: el recorrido deja una anulación, un maestro y un material marcado.
