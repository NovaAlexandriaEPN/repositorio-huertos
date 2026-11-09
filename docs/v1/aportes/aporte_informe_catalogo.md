# Requisitos y fuentes del catálogo, guía ancestral y calendario lunar

Texto actualizado el 5 de noviembre de 2026 para incorporar al informe V1 (aporte M3-04 de Matthew).
Historias: HU-005, HU-006 y HU-007. Las pruebas formales CP-03 y CP-04 se ejecutaron el 5 de noviembre de 2026 y resultaron aprobadas.

## Funciones que cubre la versión

El módulo catalogo reúne la información fija que consultan todas las comunidades: las 18
fichas de plantas que exige V1 (seis de Juan, seis de Matthew y seis de Guillermo), 13 guías
de actividades, 23 opciones del configurador, 18 recomendaciones de materiales y 17 eventos
lunares. Las vistas del catálogo solo aceptan consultas (GET) y todas requieren sesión.

- **HU-005, fichas de plantas.** Lista y detalle con nombre común y científico, otros
  nombres, familia, altitud, provincias del Ecuador, ciclo corto/largo, cualidad ancestral
  caliente/fría, parte utilizada, usos, contraindicaciones, foto local con autor y licencia,
  y fuentes. Un atributo sin respaldo se muestra como «No verificado» en lugar de un valor
  supuesto; si faltan contraindicaciones, la ficha pide consultar a personal de salud. La
  información es educativa y no indica dosis.
- **HU-006, guía ancestral.** Cada uno de los 13 tipos muestra instrucciones, materiales,
  precauciones y su fuente; el MSP se cita con página. La hora y la fase lunar recomendadas
  aparecen cuando la fuente las indica; si no, la guía muestra «No indicada en la fuente».
  Las dos condiciones obligatorias (15 días entre preparación y siembra; 10 días entre
  inicio del secado y empaquetado) aparecen primero, marcadas como plazo obligatorio, y
  separadas de las recomendaciones. El módulo actividades es el que exige esos plazos al
  registrar; las recomendaciones no bloquean registros.
- **HU-007, calendario lunar.** Lista mensual de luna nueva, cuarto creciente, luna llena y
  cuarto menguante entre septiembre y diciembre de 2026, en hora de Guayaquil y con enlace
  a la fuente. Cada evento muestra el nombre ancestral de la fase (Yana Killa, Wiñak killa,
  Pura killa, Wañuk killa, según el MSP) y las actividades que la guía recomienda para esa
  fase. También muestra el evento anterior y el siguiente a una fecha de referencia, un
  mensaje cuando la fecha está fuera del período cargado y otro cuando el mes no tiene
  eventos. No se inventa una fase para cada día y registrar una actividad no exige un
  evento lunar.

## Organización de los datos fijos

Los datos se escriben como listas de diccionarios Python en `catalogo/datos/`: un archivo de
seis fichas por autor (Juan, Matthew y Guillermo), `actividades.py`,
`huerto.py` y `luna.py`. `catalogo/datos/__init__.py` los reúne y el comando
`cargar_catalogo` los crea en SQLite por un código estable, dentro de una sola transacción:
si una fila falla, no queda un catálogo parcial. Repetir la carga no duplica ni modifica
registros y no toca cuentas, comunidades, huertos, actividades ni nombramientos; además
informa qué códigos difieren del archivo Python y avisa si faltan fichas para llegar a 18.

Cada ficha guarda sus fuentes, indicando qué campos respalda cada una, y la lista
`campos_no_verificados`. Los eventos lunares se guardan en UTC y se convierten a
America/Guayaquil solo al mostrarlos; el mes se selecciona con los límites del mes local,
de modo que un evento del 9 de diciembre a las 00:52 UTC aparece el 8 de diciembre a las
19:52. En una base nueva la carga crea 89 registros (18 plantas, 13 tipos, 23 opciones,
18 materiales y 17 eventos) y repetirla no crea más. Las 188 pruebas de desarrollo de main incluyen las del catálogo: formato de las
fichas, carga repetida, guías, eventos en UTC y las pantallas de guía y calendario.

## Fuentes que respaldan el contenido

- Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural,
  *Implementación de huertos medicinales en los establecimientos de salud del primer nivel
  de atención. Lineamientos*, 1.ª ed. Quito, 2017. Cualidad caliente/fría, ciclo, las 13
  guías, nombres de las fases lunares, opciones del huerto y materiales, con número de página.
- Royal Botanic Gardens, Kew, *Plants of the World Online*. Nombres científicos y familias.
- European Medicines Agency (HMPC), monografías de hierbas medicinales. Usos tradicionales y
  contraindicaciones de menta, toronjil, romero, manzanilla, taraxaco y ortiga.
- F. Tinitana et al., «Medicinal plants sold at traditional markets in southern Ecuador»,
  *J. Ethnobiol. Ethnomed.*, vol. 12, art. 29, 2016. Nombres locales, partes usadas y usos.
- GBIF.org, ejemplares de herbario de Ecuador. Provincias y altitud cuando no hubo una
  fuente ecuatoriana; el criterio está descrito en cada ficha.
- U.S. Naval Observatory, *Phases of the Moon*, 2026. Instantes de los 17 eventos lunares,
  consultados el 19 de octubre de 2026 por año y por fecha, con resultados idénticos.
- Wikimedia Commons e iNaturalist. Fotos con autor y licencia comprobados en su página
  original (CC BY, CC BY-SA o CC0).
- Además, cada ficha cita sus fuentes específicas (artículos ecuatorianos, fichas «Hierbas
  del Ilaló» de la USFQ y otras), con página o sección cuando existe.

## Estado de las historias del catálogo

| Historia | Estado al 5 de noviembre | Prueba formal |
|---|---|---|
| HU-005 | 18 fichas integradas en main, cada una con foto local, autor, licencia y fuentes. | CP-03 aprobado (2026-11-05). |
| HU-006 | 13 guías completas con fuente. | CP-03 aprobado (2026-11-05). |
| HU-007 | Calendario con 17 eventos verificados, hora local y recomendaciones. | CP-04 aprobado (2026-11-05). |

Las otras historias (HU-001 a HU-004 y HU-008 a HU-012) se describen en los aportes de sus
módulos. Ninguna historia se declara aprobada antes de su caso de prueba formal.

## Resultados de CP-03 y CP-04

Ambos casos se ejecutaron el 5 de noviembre de 2026 en Windows, sobre una base nueva
(`migrate` y `cargar_catalogo`, 89 registros), con la cuenta `cp_rosa`. El detalle está en
`resultados.md`.

- **CP-03 (HU-005, HU-006): aprobado.** El catálogo muestra las 18 plantas con foto, autor y
  licencia; ninguna ficha muestra «None» ni campos en blanco; «No verificado» aparece en los
  campos marcados en los archivos de datos; la guía muestra los 13 tipos con fuente y separa
  los dos plazos obligatorios de las recomendaciones. Observaciones: en Menta, «otros
  nombres» se muestra como «No verificado» por estar vacío sin figurar en
  `campos_no_verificados` (comunicado a Juan); en Matico, Marco, Ortiga y Violeta se quitaron
  notas de trabajo ya resueltas sobre la elección de la foto.
- **CP-04 (HU-007, HU-008): aprobado.** Los eventos se muestran en hora de Guayaquil,
  incluidos los que cambian de día respecto a UTC (8 de diciembre a las 19:52; 23 de
  diciembre a las 20:28; 25 de octubre a las 23:12); los extremos del período muestran «No
  disponible»; las fechas fuera del período se informan y los datos inválidos responden con
  estado 400; y el registro de una actividad no exige fase lunar.

## Limitaciones reales

- **Datos sin respaldo**, mostrados como «No verificado»: otros nombres, ciclo y
  contraindicaciones de matico; ciclo de llantén, paico y chilca; contraindicaciones de
  marco; altitud de violeta; provincias de salvia; cualidad ancestral de lavanda, salvia y
  laurel (el MSP no las clasifica).
- **Identidad botánica:** «matico» y «ortiga» designan varias especies. Se eligieron
  *Aristeguietia glutinosa* y *Urtica dioica*, confirmadas con fotos verificadas.
- **Tabla lunar:** cubre solo septiembre a diciembre de 2026 y no permite deducir la fase
  de cualquier día. La aplicación no consulta USNO en ejecución.
- **Correcciones de contenido:** `cargar_catalogo` no sobrescribe registros ya cargados;
  solo informa cuáles difieren. Corregirlos en una base existente requiere la operación
  interna descrita en `integracion_equipo.md`, previo respaldo, o una base nueva. No hay
  un editor de catálogo en la aplicación.
- **Uso médico:** la información es educativa; no reemplaza la atención médica ni indica dosis.

Uso de IA: para la parte del catálogo se usó Claude (Anthropic) como asistente para localizar
fuentes y redactar y probar código. Los datos se contrastaron con las fuentes citadas.
