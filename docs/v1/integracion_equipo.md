# Revisión general e integración del equipo

Revisión del 25 de octubre de 2026. Se integran los aportes publicados hasta los commits
de esta tabla mediante un merge con commit en main. No se eliminan ramas ni se reescriben
commits. Las comprobaciones se hacen primero en una carpeta Git de integración separada;
la copia de Bryan y su base de datos permanecen intactas durante la revisión.

## Referencias y criterio de alcance

Se contrastaron la definición del proyecto, la presentación Huertos Medicinales Comunitarios,
los lineamientos MSP de 2017, el alcance V1 1.4, la arquitectura, el plan y las descripciones de
las tareas del [tablero del equipo](https://huertos-avance-equipo.cozyglobe1024.chatgpt.site/).
Los documentos del curso describen el producto general. Para esta entrega se mantienen las
reducciones de V1 ya acordadas: no se reintroducen GPS, evidencias subidas, foro, ranking,
insignias, certificaciones, cantidades de inventario ni servicios en la nube. Tampoco se
convierten recomendaciones de edad, hora o fase lunar en bloqueos nuevos.

Esta revisión comprueba lo publicado en Git. No atribuye como terminado trabajo que un
integrante tenga solamente en su equipo o fuera del repositorio.

## Ramas revisadas

| Rama | Commit revisado | Aporte conservado |
| --- | --- | --- |
| main | `73ba17d` | Estructura inicial del proyecto. Es la primera línea del merge. |
| bryan | `fae10db` | Cuentas, comunidades, configurador, selección, materiales, integración y correcciones de las reglas de actividades. |
| fernandoCarrera | `b2cb686` | Actividad, formularios, historial, huerto virtual, anulaciones y maestro; se conservan las correcciones de alcance ya integradas por Bryan. |
| domenicaAstudillo | `0ec3f2a` | Bocetos, Bootstrap 5.3.8 local, estilos y plantillas de acceso; menú conectado a rutas reales. |
| juanChuga | `4f07830` | Seis fichas y fotografías, con las correcciones de formato y créditos de la integración anterior. |
| matthewRedin | `c8f5096` | Seis fichas nuevas, 13 guías, explicaciones de opciones, 18 materiales, 17 eventos USNO y recomendaciones por fase. |
| Guillermo | Sin rama publicada identificada | No hay una entrega de Git que incorporar. Esto no demuestra ausencia de trabajo fuera del repositorio. |

Matthew ya incorpora fae10db, que contiene los merges de Fernando, Juan y Doménica.
Por eso un merge normal de ese historial contiene todos estos aportes; volver a copiar
carpetas o hacer squash perdería información útil para las próximas integraciones.

## Revisión de las doce historias

| Historia | Estado del progreso integrado | Lo que sigue pendiente |
| --- | --- | --- |
| HU-01 Registro y perfil | Registro con aviso/versionado del consentimiento; edad recomendada sin bloqueo; perfil propio y nacimiento válido. | Ejecución formal y revisión visual final. |
| HU-02 Sesión | Autenticación Django, acceso privado, salida por POST y CSRF. | Ejecución formal. |
| HU-03 Comunidad | Una pertenencia, código, responsable creador y permisos de edición en servidor. | Ejecución formal. |
| HU-04 Huerto y plantas | Ubicación manual, área positiva, categorías, selección única y protección de historial activo o anulado. | Ejecución formal. |
| HU-05 Fichas | 12 fichas con sus fuentes y pendientes visibles. | Seis fichas: paico, chilca, lavanda, salvia, cedrón y laurel. Faltan las seis fotos de Matthew y verificar foto/créditos de toronjil, además de los atributos marcados. |
| HU-06 Guía ancestral | 13 guías con instrucciones, materiales, precauciones y referencias al MSP. No se inventan horas/fases donde la fuente no las indica. | Revisión final de dominio y prueba formal. |
| HU-07 Calendario | 17 instantes USNO de septiembre a diciembre, hora de Guayaquil, anterior/siguiente y enlaces a recomendaciones. Funciona con datos locales. | Prueba formal de meses, extremos y conversión de día. |
| HU-08 Registro | Actor de la sesión, alcance, estados, fecha/hora, mínimos 15/10 días y UUID/carga. | Prueba formal con el equipo. |
| HU-09 Anulación | Solo responsable y con motivo; orden inverso por planta, preparación protegida y diseño/ritual independientes. Conserva autor y constancia. | Prueba formal. |
| HU-10 Progreso y puntos | Seis hitos; cuidado o riego forman uno; promedio de plantas; valores históricos, niveles aprendiz/oficial/maestro. | Prueba formal y datos ficticios de demo. |
| HU-11 Maestro | Umbral de 100, motivo, autor y fecha, sustitución con maestro esperado y retiro bajo 100. No añade permisos ni se concede por 300. | Prueba formal. |
| HU-12 Materiales | Lista por métodos y marcas compartidas con permisos en servidor, sin cantidades ni compras. | Revisar marcas de bases antiguas y ejecutar la prueba formal. |

La versión unifica el progreso disponible. No equivale a V1 terminada ni sustituye el
informe oficial, los resultados reales de noviembre o la revisión en otro computador.

## Correcciones al unificar

Se conserva la corrección previa de actividades: 3 generales y 10 por planta, plazos
mínimos, puntos históricos, reenvíos, autoría, anulaciones, seis hitos, niveles y maestro.
La relación Actividad.planta sigue apuntando a PlantaHuerto con PROTECT y toda su historia.

En esta revisión se corrigió el texto de registro para incluir preparación entre las
generales, se añadió un acceso directo a la guía y se aclaró que diseño y ritual no son
prerrequisitos para sembrar. Las explicaciones que Matthew añadió a las opciones se
pueden consultar en el configurador; permanecían guardadas sin mostrarse.

`cargar_catalogo` conserva su carga por códigos nuevos. Ahora avisa si una fila existente
tiene contenido distinto del archivo Python. No modifica sus datos silenciosamente.

Los 17 eventos se contrastaron de nuevo el 25 de octubre con la
[API anual de USNO](https://aa.usno.navy.mil/api/moon/phases/year?year=2026): los tipos,
días y minutos coinciden. La aplicación sigue consultando SQLite durante la demo.
Las fichas conservan las fuentes entregadas; esta revisión estructural no declara
independientemente verificados todos sus usos o contraindicaciones.

## Actualización de bases existentes

Git integra fuentes y migraciones. SQLite es local y no se publica en Git. No se
fusionan bases de personas distintas ni se sobrescribe la base de Bryan al integrar.

En una base nueva, `migrate` y `cargar_catalogo` preparan 83 registros de catálogo:
12 plantas, 13 tipos, 23 opciones, 18 materiales y 17 eventos. Repetir la carga no crea más.
En una base anterior, la carga añade códigos nuevos y conserva los existentes. Por eso
las antiguas guías abreviadas y las explicaciones vacías no cambian automáticamente.

Después de respaldar y revisar la base, se puede hacer esta corrección interna de
contenido en `manage.py shell`, usando los datos revisados del repositorio:

```python
from django.db import transaction
from catalogo.datos import ACTIVIDADES, OPCIONES
from catalogo.models import TipoActividad, OpcionHuerto

with transaction.atomic():
    for fila in ACTIVIDADES:
        campos = ("nombre", "instrucciones", "materiales", "precauciones",
                  "hora_recomendada", "fase_recomendada", "fuentes")
        TipoActividad.objects.filter(codigo=fila["codigo"]).update(
            **{campo: fila[campo] for campo in campos}
        )
    for fila in OPCIONES:
        OpcionHuerto.objects.filter(codigo=fila["codigo"]).update(
            explicacion=fila["explicacion"]
        )
```

La operación reemplaza únicamente ese contenido por la entrega revisada: no se debe
aplicar encima de otras correcciones locales sin compararlas antes. No toca código,
alcance, puntos, repetibilidad, actividades, miembros ni maestro. La carga normal sigue
sin ser un sincronizador general y no se añade un editor de catálogo.

Las primeras seis recomendaciones de materiales tenían códigos distintos de los 18
materiales detallados de Matthew. En bases antiguas se conservan esas filas y sus marcas.
Antes de la demo deben revisarse manualmente: una marca genérica de «herramientas» no
permite afirmar que cada herramienta está disponible. No se borra ni se redistribuye
esa información automáticamente. Esta diferencia no aparece en una instalación nueva.

Se conserva la migración inicial de Fernando. actividades/0002 se detiene si encuentra
actividades guardadas con el esquema anterior incompatible: respalda y revisa ese caso
antes de convertir sus tipos, fechas y recompensas. No se borran registros ni se inventan
equivalencias para conseguir que una migración pase.

## Comprobaciones de desarrollo

La suite final integrada ejecutó 167 pruebas con resultado OK. Incluye cuentas,
privacidad, pertenencia, configuración, selección, materiales, el ciclo de trece labores
con formularios/CSRF, límites 14/15 y 9/10, UUID, recompensas, anulación, progreso,
sustitución y retiro de maestro, datos de Matthew y calendario con cambio de día local.
También pasaron check, makemigrations --check --dry-run y la revisión del diff.
Una instalación temporal sobre base vacía cargó 83 registros y cero en el segundo intento.
Se recorrió el sistema por HTTP real con dos cuentas ficticias y CSRF: registro, acceso,
comunidad, configuración, selección, unión, materiales, las trece actividades, maestro,
las doce fichas, guía, calendario y anulación. El ciclo llegó a 100 % y 125 puntos,
y la anulación redujo el avance.

En una copia de la base anterior se añadió un escenario ficticio con historial,
material disponible y maestro. La carga y la corrección interna documentada conservaron
cuentas, comunidad, relaciones, marcas, actividades, recompensas y maestro sin cambios.
La base original se abrió solamente en modo lectura para obtener esa copia.
Las cuentas y bases usadas para comprobar no forman parte del producto ni se publican.

Los resultados de desarrollo no se anotan como casos formales ya ejecutados en
resultados.md. Se mantienen los tests.py de cada módulo, sin añadir cobertura ni CI.
