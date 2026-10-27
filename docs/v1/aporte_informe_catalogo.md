# Requisitos y fuentes del catálogo, guía ancestral y calendario lunar

Texto actualizado el 26 de octubre de 2026 para incorporar al informe V1 (aporte M3-04 de Matthew).
Historias: HU-05, HU-06 y HU-07. Las pruebas formales CP-03 y CP-04 quedan para noviembre.

## Funciones que cubre la versión

El módulo catalogo reúne la información fija que consultan todas las comunidades: fichas
de plantas, 13 guías de actividades, 23 opciones del configurador, 18 recomendaciones de
materiales y 17 eventos lunares. En main hay 12 fichas cargadas (Juan y Matthew); las seis
de Guillermo están en revisión en el PR #2 para completar las 18 que exige V1. Las vistas
del catálogo solo aceptan consultas (GET) y todas requieren sesión.

- **HU-05, fichas de plantas.** Lista y detalle con nombre común y científico, otros
  nombres, familia, altitud, provincias del Ecuador, ciclo corto/largo, cualidad ancestral
  caliente/fría, parte utilizada, usos, contraindicaciones, foto local con autor y licencia,
  y fuentes. Un atributo sin respaldo se muestra como «No verificado» en lugar de un valor
  supuesto; si faltan contraindicaciones, la ficha pide consultar a personal de salud. La
  información es educativa y no indica dosis.
- **HU-06, guía ancestral.** Cada uno de los 13 tipos muestra instrucciones, materiales,
  precauciones y su fuente; el MSP se cita con página. La hora y la fase lunar recomendadas
  aparecen cuando la fuente las indica; si no, la guía muestra «No indicada en la fuente».
  Las dos condiciones obligatorias (15 días entre preparación y siembra; 10 días entre
  inicio del secado y empaquetado) aparecen primero, marcadas como plazo obligatorio, y
  separadas de las recomendaciones. El módulo actividades es el que exige esos plazos al
  registrar; las recomendaciones no bloquean registros.
- **HU-07, calendario lunar.** Lista mensual de luna nueva, cuarto creciente, luna llena y
  cuarto menguante entre septiembre y diciembre de 2026, en hora de Guayaquil y con enlace
  a la fuente. Cada evento muestra el nombre ancestral de la fase (Yana Killa, Wiñak killa,
  Pura killa, Wañuk killa, según el MSP) y las actividades que la guía recomienda para esa
  fase. También muestra el evento anterior y el siguiente a una fecha de referencia, un
  mensaje cuando la fecha está fuera del período cargado y otro cuando el mes no tiene
  eventos. No se inventa una fase para cada día y registrar una actividad no exige un
  evento lunar.

## Organización de los datos fijos

Los datos se escriben como listas de diccionarios Python en `catalogo/datos/`: un archivo de
seis fichas por autor (Juan y Matthew en main; Guillermo en el PR #2), `actividades.py`,
`huerto.py` y `luna.py`. `catalogo/datos/__init__.py` los reúne y el comando
`cargar_catalogo` los crea en SQLite por un código estable, dentro de una sola transacción:
si una fila falla, no queda un catálogo parcial. Repetir la carga no duplica ni modifica
registros y no toca cuentas, comunidades, huertos, actividades ni nombramientos; además
informa qué códigos difieren del archivo Python y avisa si faltan fichas para llegar a 18.

Cada ficha guarda sus fuentes, indicando qué campos respalda cada una, y la lista
`campos_no_verificados`. Los eventos lunares se guardan en UTC y se convierten a
America/Guayaquil solo al mostrarlos; el mes se selecciona con los límites del mes local,
de modo que un evento del 9 de diciembre a las 00:52 UTC aparece el 8 de diciembre a las
19:52. Las 175 pruebas de desarrollo de main incluyen las del catálogo: formato de las
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

| Historia | Estado al 26 de octubre | Pendiente |
|---|---|---|
| HU-05 | 12 fichas integradas en main con foto y crédito. Las fotos de las 18 especies ya están en main; las seis fichas de Guillermo están revisadas en el PR #2 y cargan con su corrección. | Actualizar el PR #2 y ejecutar CP-03. |
| HU-06 | 13 guías completas con fuente. | Ejecutar CP-03. |
| HU-07 | Calendario con 17 eventos verificados, hora local y recomendaciones. | Ejecutar CP-04. |

Las otras historias (HU-01 a HU-04 y HU-08 a HU-12) se describen en los aportes de sus
módulos. Ninguna historia se declara aprobada antes de su caso de prueba formal.

## Limitaciones reales

- **Datos sin respaldo**, mostrados como «No verificado». En main: otros nombres, ciclo y
  contraindicaciones de matico; ciclo de llantén; contraindicaciones de marco; altitud de
  violeta. En las fichas de Guillermo (PR #2): ciclo de paico y chilca; cualidad ancestral
  de lavanda, salvia y laurel (el MSP no las clasifica); provincias de salvia.
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
