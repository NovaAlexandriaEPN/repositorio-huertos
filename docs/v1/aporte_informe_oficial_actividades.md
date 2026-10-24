# Implementación integrada de actividades y huerto virtual

Texto actualizado el 24 de octubre de 2026 para incorporar al informe V1.
La entrega inicial de Fernando se integró y corrigió en bryan contra el alcance acordado.
Historias: HU-08 a HU-11. Las pruebas formales CP-05 a CP-08 quedan para noviembre.

El módulo actividades registra las tres labores generales del huerto y diez por planta.
Las vistas reciben formularios propios y llaman a servicios. Actividad referencia el
huerto, la selección opcional, el tipo del catálogo y la cuenta de la sesión. Conserva
fecha/hora, nota, UUID, carga normalizada, puntos base, repetibilidad y puntos otorgados.
Las referencias protegen el historial de eliminación y el autor no se recibe del navegador.

Los servicios comprueban comunidad, estado y fechas. Siembra exige una preparación general
al menos 15 días antes y empaquetado al menos 10 desde el inicio del secado. Las demás
horas/fases son recomendaciones. Las generales se registran sin siembras activas.
Los reenvíos idénticos devuelven el registro existente, incluso anulado; una carga distinta
con el mismo UUID se rechaza. Cuidados y riego premian solo el primer activo; los otros
tipos tienen un único activo por alcance, reforzado por restricciones de la base.

Solo el responsable anula, con motivo. Se guarda quién anuló y cuándo sin alterar al
actor original. Por planta se revierte la última activa; preparación queda protegida
por siembras y diseño/ritual son independientes. Las operaciones atómicas actualizan
anulación, recompensas afectadas y retiro del maestro si baja de 100 puntos.

Estado, puntos, nivel y avance se consultan desde el historial activo. Preparación,
siembra, crecimiento por cuidado o riego, cosecha, secado y empaquetado son seis hitos
iguales. El avance comunitario promedia las selecciones y puede disminuir al añadir otra.
Los niveles son aprendiz (0–99), oficial (desde 100) y maestro (desde 100 con nombramiento).
El responsable puede nombrarse si cumple el umbral. La sustitución exige motivo y compara
el maestro esperado para rechazar formularios antiguos. El reconocimiento no concede permisos.

El huerto virtual ofrece tarjetas con método, estado, progreso y siguiente acción,
puntos personales/comunitarios y constancia del maestro. El historial conserva activos y
anulados y permite filtrar. Todas estas rutas requieren sesión y comprueban pertenencia;
las escrituras usan POST y CSRF. Las 160 pruebas de desarrollo del conjunto incluyen el
ciclo completo en formularios. Véase `integracion_equipo.md` para los datos pendientes,
las migraciones y los commits de origen. Aún faltan contenido del catálogo y ejecución
formal antes de declarar terminada V1.
