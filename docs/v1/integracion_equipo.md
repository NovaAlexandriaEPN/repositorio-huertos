# Integración del equipo en bryan

Revisión del 24 de octubre de 2026. Base: `56eb2d1` de Bryan. Referencias:
[alcance V1](01_Alcance_V1_Huertos_Medicinales.md),
[arquitectura](02_Arquitectura_V1_Django.md) y
[actividades del equipo](https://huertos-avance-equipo.cozyglobe1024.chatgpt.site/).
Se comprobó que la versión publicada 4 del tablero corresponde al commit
`0c0899bd077d5123ec244531a14d319e815f683b`, igual a la fuente local usada para leer
las descripciones de las tareas. Esta revisión no cambia sus casillas de progreso.

## Entregas reunidas

| Integrante | Entrega publicada incorporada | Resultado de la integración |
| --- | --- | --- |
| Fernando | `b2cb686`, actividades F1–F3 | Modelo, servicios, formularios, historial, huerto virtual y maestro corregidos contra el alcance. |
| Doménica | `0ec3f2a`, diseño D1 | Bocetos, Bootstrap 5.3.8 local, estilos y plantillas de acceso. Menú conectado a las rutas reales. Se conservan las pantallas posteriores de Bryan. |
| Juan | `4f07830`, seis fichas y fotografías | Fichas adaptadas a los 19 campos y cargadas por código. Observaciones convertidas de tuplas a texto; rutas de imagen relativas a static/. |
| Matthew | `8a1e353` | Ya estaba contenido en bryan; no hay una entrega nueva en esa rama. |
| Guillermo | Sin rama publicada identificada | No hay cambios de Git que incorporar. Los cálculos integrados siguen abiertos a su revisión. |

Solo se escriben y publican cambios en `bryan`. Las otras ramas y `main` conservan
sus entregas. Las fusiones conservan la procedencia de los commits.

## Correcciones de actividades

- Las tres generales son preparación, diseño y ritual. Las diez por planta son las del alcance; no se sustituyen por poda, abonado o control de plagas.
- La preparación es del huerto. Siembra exige al menos 15 días desde ella. Empaquetado exige al menos 10 días desde el inicio de secado. No son plazos máximos.
- Se registra fecha y hora, sin futuro ni retroceso respecto de la última actividad activa de la selección. Los empates se ordenan por ID.
- El servicio aplica los estados de los trece tipos. Señalética, baño, gratitud y limpieza conservan su estado.
- Cada envío conserva UUID y carga normalizada, incluida la nota. Un reenvío idéntico devuelve el registro, incluso anulado, antes de comprobar el nuevo estado. No reactiva ni duplica puntos.
- Solo cuidados y riego se repiten. El primer activo de cada uno recibe sus puntos y los siguientes cero. La base impide dos registros activos de los otros tipos por alcance.
- Se conservan puntos base y repetibilidad históricos. Anular recalcula las recompensas afectadas desde esos valores, sin cambiar el actor original.
- Solo el responsable anula con motivo. Se respeta el orden inverso por planta; preparación con siembras se protege, y diseño/ritual se anulan independientemente.
- Hay seis hitos iguales. Cuidado o riego cuenta como crecimiento; empaquetado es el sexto. El avance del huerto es el promedio, puede bajar al añadir una selección y es cero sin plantas.
- Los niveles son aprendiz, oficial y maestro. El maestro exige al menos 100 puntos y nombramiento con motivo; 300 no lo concede. La sustitución comprueba el maestro esperado y la anulación retira al que baja de 100 en la misma operación.
- Los servicios comprueban cuenta activa y comunidad. Se usa SQLite IMMEDIATE con operaciones atómicas cortas; no se atribuye a SQLite un bloqueo de filas mediante select_for_update.

## Catálogo y contenido pendiente

El comando `cargar_catalogo` reúne los datos Python y crea solo códigos nuevos en una
transacción. Repetirlo conserva fichas existentes, historial, pertenencias y maestro.
No se debe usar para reemplazar datos ya cargados: las correcciones internas requieren
una operación explícita sobre los registros afectados, con respaldo previo.

Están cargables las seis especies de Juan, los 13 tipos con sus reglas, las 23 opciones
del alcance y seis recomendaciones iniciales de materiales. Se añadieron las consultas
de catálogo, guía y calendario para conectar las pantallas.

**V1 todavía no está terminada:** faltan las doce fichas de Matthew y Guillermo con sus
fotos y fuentes; las instrucciones ampliadas, materiales, precauciones y recomendaciones
verificadas de las 13 guías; la revisión de la lista de materiales; los eventos USNO de
septiembre a diciembre y sus recomendaciones; la base ficticia de demo y las pruebas
formales del 1 al 9 de noviembre. No se han inventado fichas ni eventos para ocultar faltantes.

Se revisaron los créditos de fotografías de Wikimedia:
[Hierba buena.JPG](https://commons.wikimedia.org/wiki/File:Hierba_buena.JPG) y
[Kamille_01.jpg](https://commons.wikimedia.org/wiki/File:Kamille_01.jpg).
Se corrigieron autores y licencias a CC BY-SA 3.0 según sus páginas. La fotografía recibida
para toronjil y sus créditos se señalan como no verificados; se conserva el archivo y no
se presenta como identificación confirmada. El resto del contenido botánico conserva
las referencias entregadas y requiere la revisión de dominio prevista para el catálogo.

## Migraciones y bases que ya usaron la entrega anterior

Se conserva `actividades/0001_initial.py` de Fernando y se añade `0002`; no se cambia una
migración que otro integrante puede haber aplicado. La segunda se detiene si encuentra
actividades del esquema anterior: no existen equivalencias seguras para sus tipos,
fechas y recompensas. Ese caso requiere respaldar y revisar los registros antes de
convertirlos. No se borra la base ni se declara que una conversión fue verificada.

En una instalación nueva, `migrate` y después `cargar_catalogo` preparan las tablas y
los datos entregados. La base local de trabajo se respalda antes de aplicar la migración.

## Comprobaciones de desarrollo

`manage.py test` descubre y ejecuta **160 pruebas**, con resultado **OK**. Incluye el ciclo
de trece actividades mediante formularios y CSRF, plazos 14/15 y 9/10, UUID y notas,
permisos de otra comunidad, estados, puntos históricos, anulaciones, progreso promedio,
nombramiento/sustitución/retiro de maestro, protección real del historial de PlantaHuerto
y carga repetida del catálogo. Estos resultados no completan los casos manuales de noviembre.

Los cuatro módulos mantienen sus tests.py. No se añadieron cobertura, CI, servicios
externos ni dependencias de ejecución. La comprobación en otro computador sigue pendiente.

La comprobación adicional usó una copia temporal de las fuentes y una base vacía:
`check` y `migrate` terminaron correctamente, la primera carga creó 48 registros y la
segunda creó cero. Un servidor WSGI respondió HTTP 200 para acceso, registro, CSS,
Bootstrap y una fotografía local; la entrada privada redirigió al acceso. La copia
temporal se eliminó al terminar. Se migró y cargó también la instalación de trabajo,
con respaldo local previo en `copias/antes_integracion_equipo_2026-10-24.sqlite3`, fuera de Git.
