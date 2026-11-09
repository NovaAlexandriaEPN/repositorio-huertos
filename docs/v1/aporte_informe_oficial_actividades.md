# Implementación integrada de actividades y huerto virtual

Texto actualizado el 8 de noviembre de 2026 para incorporar al informe V1 (aporte F4 de Fernando Carrera).
Historias: HU-008 a HU-011. La entrega inicial de Fernando se integró y corrigió en la rama bryan contra el alcance acordado. Las pruebas formales CP-05 a CP-08 las ejecutó Guillermo Cevallos el 5 y 6 de noviembre de 2026 y resultaron aprobadas; el detalle está en `resultados.md`.

## Registro de actividades

El módulo actividades registra las tres labores generales del huerto (preparación de la tierra, elaboración del diseño y ritual de siembra) y diez por planta. Las vistas reciben formularios propios y llaman a servicios. Cada Actividad referencia el huerto, la selección opcional, el tipo del catálogo y la cuenta de la sesión, y conserva fecha/hora, nota, UUID, carga normalizada, puntos base, repetibilidad y puntos otorgados. Las referencias protegen el historial de eliminación y el autor no se recibe del navegador.

Los servicios comprueban comunidad, estado y fechas. La siembra exige una preparación general al menos 15 días antes, y el empaquetado, al menos 10 días desde el inicio del secado. Las demás horas y fases lunares son recomendaciones y no bloquean el registro. Las actividades generales se registran sin siembras activas.

Los reenvíos idénticos devuelven el registro existente, incluso anulado; una carga distinta con el mismo UUID se rechaza. Cuidados y riego premian solo el primer registro activo; los demás tipos tienen un único activo por alcance, reforzado por restricciones de la base.

## Anulación

Solo el responsable de la comunidad anula, y siempre con motivo. Se guarda quién anuló y cuándo, sin alterar al autor original. Por planta se revierte la última actividad activa; la preparación queda protegida mientras haya siembras activas, y diseño y ritual se anulan de forma independiente. Las operaciones atómicas actualizan la anulación, las recompensas afectadas y el retiro del Maestro si baja de 100 puntos.

## Progreso, puntos y Maestro

Estado, puntos, nivel y avance se calculan desde el historial activo. Preparación, siembra, crecimiento (cuidados o riego), cosecha, secado y empaquetado son seis hitos de igual peso. El avance comunitario promedia las plantas seleccionadas y puede disminuir al añadir otra. Los niveles son Aprendiz (0 a 99 puntos), Oficial (desde 100) y Maestro (desde 100 y con nombramiento); el cálculo vive en `actividades/reglas.py`, a cargo de Guillermo.

El responsable puede nombrar Maestro a quien cumpla el umbral, incluido él mismo. La sustitución exige motivo y compara el Maestro esperado para rechazar formularios antiguos. El reconocimiento no concede permisos.

## Huerto virtual e historial

«Mi huerto» ofrece una tarjeta por planta con método, estado, progreso y siguiente acción. Cada tarjeta abre el registro con esa planta y la actividad sugerida ya elegidas, y su historial filtrado. También muestra los puntos personales y comunitarios y la constancia del Maestro. El historial conserva actividades activas y anuladas y permite filtrar. Todas estas rutas requieren sesión y comprueban pertenencia; las escrituras usan POST y CSRF.

## Comprobación

Comprobación de desarrollo del 8 de noviembre de 2026 sobre main: `manage.py check` sin problemas, `makemigrations --check` sin migraciones pendientes y 188 pruebas automáticas correctas, de las cuales 42 son del módulo actividades e incluyen el ciclo completo en formularios. Los casos formales CP-05 (registro, plazos y progreso), CP-06 (reenvíos e integridad), CP-07 (anulación e historial) y CP-08 (nombramiento y retiro del Maestro) resultaron aprobados, sin fallos que corregir en el módulo.

El escenario de demostración se prepara con `scripts/crear_demo.py`, según `demo.md`. Véase `integracion_equipo.md` para las migraciones y los commits de origen.
