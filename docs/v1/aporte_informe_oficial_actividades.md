# Aporte al informe V1: módulo de actividades y Huerto Virtual

**Autor:** Fernando Alonso Carrera Zambrano (Programador 2)
**Para:** Juan Chugá, que consolida `docs/v1/informe.docx`
**Historias:** HU-08, HU-09, HU-10 y HU-11 · **Casos que apoya:** CP-05 a CP-08
**Tareas del plan:** F1, F2 y F3 (14 al 31 de octubre)

Este texto describe lo que hace el código de `actividades/` sobre los modelos compartidos de
`comunidades/` (Bryan). Las pruebas automáticas mencionadas son comprobaciones de desarrollo;
los resultados formales de CP-05 a CP-08 los registra Guillermo del 1 al 4 de noviembre en
`docs/v1/resultados.md`.

## 1. Qué cubre el módulo

| Historia | Qué permite | Pantalla |
| --- | --- | --- |
| HU-08 | Registrar las 13 actividades con fecha, planta del huerto y observaciones, sin duplicarlas al reenviar el formulario. | Registrar actividad |
| HU-09 | Anular una actividad con motivo, sin borrarla ni cambiar a quien la realizó. | Anular actividad |
| HU-10 | Consultar el historial con filtros y el Huerto Virtual: progreso, tarjetas por planta, puntos, nivel y totales. | Historial y Huerto Virtual |
| HU-11 | Nombrar o sustituir al Maestro del huerto, con motivo, autor y fecha. | Maestro del huerto |

## 2. Reglas implementadas

**Pertenencia y permisos.** Solo los miembros de la comunidad registran, consultan el
historial o ven el Huerto Virtual; una persona ajena recibe un rechazo (403). Anula quien
realizó la actividad o el responsable de la comunidad. Nombra al Maestro solo el responsable.
Ser Maestro o tener muchos puntos no da permisos.

**Planta de cada actividad.** Diseño y ritual son actividades de todo el huerto, sin planta.
Las otras once se registran sobre una planta elegida en ese huerto (`PlantaHuerto`). La base de
datos rechaza una combinación distinta.

**Reenvíos (UUID).** Cada formulario lleva un identificador único oculto. Si llega dos veces
con los mismos datos, se devuelve la actividad ya guardada y no se suman puntos de nuevo. Si el
identificador llega con datos distintos, o pertenece a una actividad anulada, se rechaza.

**Fechas y plazos.** No se aceptan fechas futuras. La siembra no puede ser anterior a la
preparación activa de esa planta y se registra hasta 14 días después (el día 15 se rechaza).
El secado exige una cosecha activa, no puede ser anterior a ella y se registra hasta 9 días
después (el día 10 se rechaza). Las actividades anuladas no cuentan para los plazos.

**Puntos.** Preparación 10, siembra 15, riego 5, cuidado 5, cosecha 20, secado 15,
procesamiento 10, diseño 10, ritual 10; abono, asociación, poda y control de plagas 5. Los seis
hitos (preparación, siembra, riego, cuidado, cosecha y secado) dan puntos solo la primera vez
para cada planta del huerto; repetirlos da 0. Las demás labores puntúan siempre.

Los puntos de una persona son la suma de los puntos de sus actividades activas. No se guardan
en otra tabla: al anular, el total baja de inmediato y no puede quedar desfasado. Por eso, si
se anula la actividad que cumplió un hito, volver a registrarlo da puntos otra vez.

**Anulación.** Se anula solo la última actividad activa de una planta, ordenando por fecha y,
en la misma fecha, por número de registro. Diseño y ritual se anulan de forma independiente.
Una preparación no se anula si la planta ya tiene siembras activas. La anulación guarda
motivo, autor y fecha juntos; la base de datos impide una anulación sin esa constancia.

**Maestro del huerto.** El candidato debe pertenecer a la comunidad y tener al menos 100
puntos; el motivo es obligatorio. Hay como máximo un Maestro: un nuevo nombramiento sustituye
al anterior. Si el Maestro cambió mientras el responsable llenaba el formulario, el nombramiento
se rechaza y se pide revisar el estado actual. Si una anulación deja al Maestro con menos de 100
puntos, el nombramiento se retira y su constancia se vacía. Llegar a 300 puntos no nombra a
nadie.

**Niveles y progreso** (funciones de `reglas.py`, a cargo de Guillermo).

| Nivel | Puntos | Nombre |
| --- | --- | --- |
| 1 | 0–49 | Semilla |
| 2 | 50–99 | Brote |
| 3 | 100–199 | Guardián |
| 4 | 200–299 | Cosechador |
| 5 | 300 o más | Sabio del huerto |

El progreso es el porcentaje de los seis hitos cumplidos, con un decimal. Cada tarjeta muestra
el progreso de su planta y su etapa (sin iniciar, terreno preparado, sembrada, en crecimiento,
cosechada o secada); el progreso del huerto junta los hitos de todas sus plantas.

## 3. Diseño técnico

- `actividades/models.py`: modelo `Actividad`, con cuatro restricciones de base de datos (tipo
  válido, estado válido, planta según tipo y constancia de anulación completa).
- `actividades/servicios.py`: reglas de registro, anulación, puntos, Maestro, historial y
  resumen. Cada escritura es atómica y bloquea la fila del huerto mientras decide.
- `actividades/forms.py` y `views.py`: validan la forma de los datos y muestran el resultado;
  las escrituras usan POST con protección CSRF.
- Contrato con comunidades: `Actividad.planta` apunta a `PlantaHuerto` con
  `related_name="actividades"`. Así, el configurador de Bryan impide cambiar el método de
  siembra o borrar una planta que ya tiene historial.

## 4. Comprobaciones de desarrollo

`python manage.py test actividades` ejecuta 73 pruebas: reglas puras (6), CP-05 (18),
CP-06 (10), CP-07 (10), CP-08 (13), HU-10 (4), contrato con comunidades (2) y pantallas con
permisos (10). Con el resto del proyecto, `python manage.py test` ejecuta 136 pruebas.

## 5. Pendientes y coordinación

- Guillermo puede reemplazar `reglas.py` conservando sus tres firmas; las pruebas de reglas
  están separadas en `ReglasPurasTest`.
- Doménica da el estilo final a `templates/actividades/` (clases `tarjeta`, `etiqueta-estado`,
  `resumen`, `totales`, `detalle` y `tabla-desplazable`) y decide dónde va el enlace
  «Mi huerto» (`actividades:mi_huerto`) en el menú.
- Los plazos de 14 y 9 días y la tabla de puntos deben coincidir con el alcance de Matthew;
  si cambian, se ajustan las constantes de `servicios.py`.
