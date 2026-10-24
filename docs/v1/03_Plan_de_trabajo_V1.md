# Plan de trabajo de la versión 1

Equipo de seis integrantes; producto y documentación base al 31 de octubre

Documento 1.4 | 14 de octubre de 2026

## Objetivo y dedicación estimada

Terminar producto y documentación base el 31 de octubre. Del 1 al 9 de noviembre: ejecución formal, correcciones, resultados e informe. Entrega antes de las 16:00 y demo en clase el 10 de noviembre de 2026. La construcción empieza el 14 de octubre; se mantienen todas las funciones de V1, 18 plantas y 13 actividades.

Las estimaciones incluyen aprender lo necesario para las tareas, programación, datos, conexión y documentación. Sirven para detectar sobrecarga, no son cuotas ni un registro de horas reales. Cada persona conserva su rol principal y aporta desarrollo. No se añaden actividades solo para igualar números.

| Integrante | 14-31 oct | 1-9 nov | Total previsto |
| --- | --- | --- | --- |
| Juan | 22 h | 6 h | 28 h |
| Matthew | 24 h | 4 h | 28 h |
| Doménica | 23 h | 5 h | 28 h |
| Bryan | 24 h | 5 h | 29 h |
| Fernando | 25 h | 7 h | 32 h |
| Guillermo | 22 h | 8 h | 30 h |

Total orientativo del equipo: 175 horas. En octubre son 140 horas: promedio de 1 h 18 min diarios por integrante si se trabaja los 18 días. En noviembre son 35 horas: unos 39 min diarios por integrante si se trabaja los nueve días. La dedicación real se concentra en entregas y errores; estos promedios no garantizan terminar. Si hay días sin trabajo, se redistribuye antes del siguiente hito.

## Hitos y tiempo de integración

| Fecha | Entrega comprobable |
| --- | --- |
| 16 oct | Configuración y Usuario; modelos/campos de catálogo; historias, bocetos, base HTML, errores comunes y README inicial. Instalación principal lista. |
| 19 oct | Modelos/migraciones de comunidad, miembro y huerto disponibles para actividades. Acordar firmas de servicios y variables de plantilla. |
| 23 oct | 18 fichas, 13 guías, opciones, materiales y calendario precargados. Cuentas/comunidad/configurador operativos; empezar a conectar consultas. |
| 28 oct | Registro y anulación integrados; primera conexión de tarjetas, puntos y maestro. Del 29 al 31 se reservan jornadas para integrar las últimas pantallas y terminar pendientes. |
| 31 oct | Todas las historias implementadas, README, diseño/arquitectura y borrador del informe. Casos preparados; ejecución formal todavía pendiente. |
| 1-4 nov | Ejecutar diez casos y pruebas automáticas; registrar resultados reales y fallos. |
| 5-7 nov | Corregir y repetir solo los casos afectados. Cerrar fallos que impidan uso o afecten datos, permisos o puntos. |
| 8-9 nov | Recorrido final, segunda instalación, copia de demo, informe final y ensayo. |
| 10 nov | Verificar enlace/repositorio y entregar informe antes de las 16:00; demostrar en clase. |

## Equipo y archivos que coordina

| Integrante y rol | Trabajo principal y apoyo |
| --- | --- |
| Juan Camilo Chugá Rosero<br>Gestor del proyecto | Coordina entregas, README, informe y demo. Programa la carga inicial y los materiales; prepara seis fichas. |
| Matthew Vladimir Redín Espinel<br>Analista | Cierra historias y reglas; organiza los datos del dominio. Programa modelos/consultas de catálogo y calendario; prepara seis fichas. |
| Doménica Anabell Astudillo Ayala<br>Diseñadora | Bocetos, plantillas, estilos y fotos con licencia. Conecta los formularios y pantallas; comparte mensajes y errores. |
| Bryan Steeven Ayala Pabón<br>Programador 1 | Configuración, cuentas, comunidades y configurador. Coordina los modelos compartidos y apoya materiales e instalación. |
| Fernando Alonso Carrera Zambrano<br>Programador 2 | Registro, estados, recompensas, anulación y maestro. Conecta historial y tarjetas; integra los cálculos de Guillermo. |
| Guillermo Javier Cevallos Herrera<br>Tester | Casos mínimos, pruebas de reglas y resultados. Programa nivel/progreso, prepara seis fichas y la base ficticia. |

## Cambios en archivos compartidos

| Archivo o carpeta | Coordina | Contribución acordada |
| --- | --- | --- |
| huertos/; cuentas/; requirements.txt | Bryan | Guillermo aporta pruebas; Doménica, plantillas; Juan, instrucciones del README. |
| catalogo/ | Matthew | Cada autor tiene su archivo de seis fichas; Juan escribe cargar_catalogo; Doménica incorpora fotos. Matthew consolida. |
| comunidades/ | Bryan | Juan trabaja las funciones/formulario/rutas de materiales; acuerdan antes esos cambios para evitar conflictos. |
| actividades/ | Fernando | Guillermo escribe reglas.py y aporta pruebas; comparten tests.py con cambios coordinados. |
| templates/; static/; diseno/ | Doménica | Los autores de vistas acuerdan campos/variables y conectan la pantalla con ella. |
| resultados.md; demo.md | Guillermo / Juan | Guillermo reúne resultados; cada ejecutor entrega los suyos. Juan mantiene el guion; Guillermo prepara datos ficticios. |
| Tres documentos de trabajo; informe.docx | Juan | Matthew: alcance; Doménica: arquitectura/diseño con Bryan y Fernando; Guillermo: pruebas; Juan: plan y cierre. |

## Entregas que evitan bloqueos

El 16 se acuerdan campos de modelos, códigos de catálogo y variables principales de plantillas. Bryan entrega los modelos de comunidades el 19, antes de sus pantallas completas. Guillermo entrega firmas y primeros cálculos de reglas el 22. Juan y Guillermo entregan sus seis fichas el 22; Matthew consolida y carga con Juan el 23. Matthew conecta consultas del 24 al 29 y Doménica integra sus plantillas. Fernando entrega registro/anulación el 27 y maestro/tarjetas hasta el 31; la conexión se hace por partes desde el 28.

Cada entrega indica qué funciona, qué falta y cómo comprobarla. Los cambios de modelos y migraciones se coordinan con el responsable del módulo antes de integrarlos. No se exige instalar seis entornos el primer día: quienes programan usan Python 3.13 y verifican su parte localmente o junto al integrador; otra persona realiza después la instalación limpia del README.

## Juan Camilo Chugá Rosero

Gestor del proyecto. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| J1<br>14-16 oct<br>4 h estimadas | Repositorio compartido y README inicial: instalar, migrar, cargar datos y ejecutar. Acordar entregas y resolver bloqueos. | README.md; .gitignore |
| J2<br>17-23 oct<br>10 h estimadas | Seis fichas: menta, hierbabuena, toronjil, orégano, romero y manzanilla. Comando de carga inicial desde los datos Python; comprobar que un reenvío no duplica ni borra historial. | catalogo/datos/plantas_juan.py; catalogo/management/commands/cargar_catalogo.py |
| J3<br>24-31 oct<br>8 h estimadas | Materiales compartidos: formulario, permisos, guardado y rutas. Completar README, borrador del informe y guion corto de demo; coordinar la integración final. | comunidades/forms.py; comunidades/servicios.py; comunidades/views.py; comunidades/urls.py; README.md; docs/v1/informe.docx; docs/v1/demo.md |
| J4<br>1-9 nov<br>6 h estimadas | Ejecutar CP-09 y CP-10; probar una instalación en otro equipo. Preparar copia ficticia de demo; integrar resultados en el informe, verificar enlace y exportar el PDF; coordinar ensayo. | docs/v1/resultados.md; docs/v1/demo.md; docs/v1/informe.docx; docs/v1/Proyecto-Version1-nombreEquipo.pdf; README.md |

## Matthew Vladimir Redín Espinel

Analista. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| M1<br>14-16 oct<br>6 h estimadas | Cerrar las 12 historias y reglas del alcance. Definir modelos y campos del catálogo, códigos y contratos de datos para que los demás puedan comenzar. | docs/v1/01_Alcance_V1_Huertos_Medicinales.md; catalogo/models.py; catalogo/migrations/; catalogo/datos/__init__.py |
| M2<br>17-23 oct<br>10 h estimadas | Seis fichas: matico, taraxaco, marco, llantén, ortiga y violeta. Preparar las 13 guías, opciones, materiales y eventos lunares; consolidar las 18 fichas y revisar fuentes. | catalogo/datos/plantas_matthew.py; catalogo/datos/actividades.py; catalogo/datos/huerto.py; catalogo/datos/luna.py; catalogo/datos/__init__.py |
| M3<br>24-29 oct<br>8 h estimadas | Consultas de catálogo, detalle, guía y calendario; lista mensual con eventos locales. Conectar plantillas y completar la sección de requisitos y fuentes del borrador. | catalogo/servicios.py; catalogo/views.py; catalogo/urls.py; docs/v1/informe.docx |
| M4<br>1-9 nov<br>4 h estimadas | Ejecutar CP-03 y CP-04, corregir contenido y comprobar criterios de las historias en el producto. Actualizar solo las secciones afectadas del alcance y el informe. | docs/v1/resultados.md; catalogo/datos/; docs/v1/01_Alcance_V1_Huertos_Medicinales.md; docs/v1/informe.docx |

## Doménica Anabell Astudillo Ayala

Diseñadora. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| D1<br>14-16 oct<br>4 h estimadas | Dos o tres bocetos representativos; base HTML, menú, estilos y fragmento común de errores/mensajes. Acordar variables de las plantillas con quienes hacen las vistas. | docs/v1/diseno/; templates/base.html; templates/componentes/errores.html; templates/componentes/mensajes.html; static/css/estilos.css; static/vendor/bootstrap/ |
| D2<br>17-25 oct<br>12 h estimadas | Preparar plantillas de cuentas, comunidad, configurador, materiales, catálogo y guía; conectar las vistas ya disponibles. Entregar 18 fotos con rutas/fuentes/licencias el 23. Formularios con campos y ayudas propios según la función. | templates/cuentas/registro.html; templates/cuentas/login.html; templates/cuentas/perfil.html; templates/comunidades/; templates/catalogo/lista_plantas.html; templates/catalogo/detalle_planta.html; templates/catalogo/guia.html; static/img/plantas/ |
| D3<br>26-31 oct<br>7 h estimadas | Calendario y pantallas de actividades/huerto virtual con tarjetas y etiquetas de estado. Terminar las conexiones pendientes con Juan, Matthew, Bryan y Fernando hasta el 31; documentar el diseño. | templates/catalogo/calendario.html; templates/actividades/; templates/comunidades/; templates/catalogo/; docs/v1/02_Arquitectura_V1_Django.md; docs/v1/informe.docx |
| D4<br>1-9 nov<br>5 h estimadas | Ejecutar CP-01; apoyar a Juan en CP-10 con celular y teclado. Corregir pantallas, tomar capturas representativas y cerrar la sección de diseño. | docs/v1/resultados.md; templates/; static/css/estilos.css; docs/v1/diseno/; docs/v1/informe.docx |

## Bryan Steeven Ayala Pabón

Programador 1. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| B1<br>14-16 oct<br>6 h estimadas | Proyecto Django y configuración compartida; Usuario personalizado antes de migrar. Registro, consentimiento, aviso de edad, sesión y perfil propio sin exponer datos privados. | manage.py; requirements.txt; huertos/settings.py; huertos/urls.py; cuentas/models.py; cuentas/migrations/; cuentas/forms.py; cuentas/servicios.py; cuentas/views.py; cuentas/urls.py |
| B2<br>17-22 oct<br>10 h estimadas | Modelos de comunidad, miembro, huerto, selección y marcas disponibles para Fernando el 19. Crear/unirse/editar comunidad; configurador, permisos y protección de selecciones con historial. | comunidades/models.py; comunidades/migrations/; comunidades/forms.py; comunidades/servicios.py; comunidades/views.py; comunidades/urls.py |
| B3<br>23-31 oct<br>8 h estimadas | Integrar cuentas/comunidades y apoyar la lista de materiales de Juan. Revisar permisos y modelos compartidos; aportar comprobaciones automáticas de reglas propias y documentar su implementación. | cuentas/tests.py; comunidades/tests.py; cuentas/; comunidades/; huertos/urls.py; docs/v1/informe.docx |
| B4<br>1-9 nov<br>5 h estimadas | Corregir defectos de cuentas/comunidades, apoyar la instalación limpia y verificar correcciones con el ejecutor del caso. Ajustar README y documentación afectada. | cuentas/; comunidades/; README.md; docs/v1/02_Arquitectura_V1_Django.md; docs/v1/informe.docx |

## Fernando Alonso Carrera Zambrano

Programador 2. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| F1<br>17-22 oct<br>6 h estimadas | Modelo Actividad y migración; formulario y rutas de registro, historial y anulación. Acordar las funciones de reglas con Guillermo; usar los modelos de comunidad desde el 19. | actividades/models.py; actividades/migrations/; actividades/forms.py; actividades/views.py; actividades/urls.py |
| F2<br>23-27 oct<br>11 h estimadas | Servicios para registrar y anular: permisos, UUID/carga, plazos, estados, recompensas y actor original. Restricciones de base y escrituras atómicas; integrar nivel/progreso de Guillermo. | actividades/servicios.py; actividades/models.py; actividades/migrations/; actividades/tests.py |
| F3<br>28-31 oct<br>8 h estimadas | Nombramiento/sustitución del maestro con motivo, autor y fecha. Conectar historial, totales y tarjetas del huerto; terminar funciones y explicar reglas en el borrador del informe. | actividades/servicios.py; actividades/forms.py; actividades/views.py; actividades/urls.py; actividades/tests.py; docs/v1/informe.docx |
| F4<br>1-9 nov<br>7 h estimadas | Resolver fallos de actividades, anulaciones, puntos y maestro; repetir con Guillermo los casos afectados. Ajustar reglas/documentación y comprobar el ciclo integrado para el ensayo. | actividades/; docs/v1/01_Alcance_V1_Huertos_Medicinales.md; docs/v1/02_Arquitectura_V1_Django.md; docs/v1/informe.docx |

## Guillermo Javier Cevallos Herrera

Tester. Las tareas de octubre terminan antes de la ejecución formal de noviembre.

| Tarea y fecha | Producto | Archivos |
| --- | --- | --- |
| G1<br>16-22 oct<br>10 h estimadas | Seis fichas: paico, chilca, lavanda, salvia, cedrón y laurel. Preparar los 10 casos mínimos con datos, pasos y esperado en una tabla única; no registrar ejecuciones todavía. | catalogo/datos/plantas_guillermo.py; docs/v1/resultados.md |
| G2<br>20-25 oct<br>6 h estimadas | Funciones puras de nivel y porcentaje sobre seis hitos; pruebas cortas de límites. Entregar firmas/primeros cálculos el 22 para Fernando y terminar el 25. | actividades/reglas.py; actividades/tests.py |
| G3<br>26-31 oct<br>6 h estimadas | Completar un conjunto pequeño de pruebas de reglas críticas con Fernando/Bryan; preparar una base ficticia para demo con un ciclo avanzado y dos comunidades. Describir cómo ejecutar y registrar pruebas. | actividades/tests.py; cuentas/tests.py; comunidades/tests.py; catalogo/tests.py; docs/v1/demo.md; docs/v1/resultados.md; README.md |
| G4<br>1-9 nov<br>8 h estimadas | Ejecutar CP-02 y CP-05 a CP-08; correr pruebas automáticas, reunir resultados de los demás y reportar fallos reproducibles. Repetir lo afectado y cerrar la sección de pruebas con resultados reales. | docs/v1/resultados.md; docs/v1/informe.docx; actividades/tests.py; cuentas/tests.py; comunidades/tests.py; catalogo/tests.py |

## Casos mínimos y ejecutor

Diez casos cubren las doce historias. Cada uno tiene pasos y datos concretos; las variantes indicadas se registran en la misma tabla. Un ejecutor por caso; quien programó corrige o reproduce cuando haga falta. No se repite la misma comprobación entre todos los integrantes.

| Caso e historias | Comprobación y ejecutor |
| --- | --- |
| CP-01<br>HU-01, HU-02 | Registro, aviso y sesiones. Cuenta válida/duplicada, entradas inválidas, consentimiento ausente y acceso privado. Una fecha de nacimiento de menor de 14 es aceptada. Nacimiento/género solo del titular; cierre de sesión.<br>Ejecuta: Doménica |
| CP-02<br>HU-03, HU-04 | Comunidad y configurador. Código válido/inválido, pertenencia única, área/opciones válidas y selección repetida. Rechazar edición ajena y cambio de método/especie con historial; comprobar el promedio al añadir una planta.<br>Ejecuta: Guillermo |
| CP-03<br>HU-05, HU-06 | Catálogo y guía. 18 fichas/fotos y 13 actividades; campos, saberes, materiales, advertencias, fuentes/licencias y datos no verificados. No repetir el ciclo completo para cada especie.<br>Ejecuta: Matthew |
| CP-04<br>HU-07 | Calendario. Evento UTC mostrado en Guayaquil, incluyendo cambio de día; listado mensual, anterior/siguiente cuando existan y mensaje fuera del período. Registrar sin exigir fase lunar.<br>Ejecuta: Matthew |
| CP-05<br>HU-08, HU-10 | Actividades y fechas. Recorrer los 13 tipos con datos ficticios: estado y resultado. Preparación 14/15 días y secado 9/10; fecha futura/anterior, empate por ID y cuidado después de cosecha.<br>Ejecuta: Guillermo |
| CP-06<br>HU-08, HU-10 | Reenvíos y puntos. UUID/carga iguales devuelve el existente; carga distinta rechazada y anulado no reactivado. Otro UUID no duplica hito; cuidado/riego primero 5 y siguientes 0; actor y objetos ajenos protegidos.<br>Ejecuta: Guillermo |
| CP-07<br>HU-09, HU-10 | Anulaciones. Última activa por planta, preparación con siembras bloqueada, diseño/ritual independientes. Motivo/autor/fecha; conservar actor original; puntos/estado/progreso correctos tras anular y volver a registrar.<br>Ejecuta: Guillermo |
| CP-08<br>HU-11 | Maestro. Permiso, pertenencia, umbral 100 y motivo. Como máximo uno; sustitución, formulario desactualizado y retiro bajo 100; 300 no concede nombramiento ni administración.<br>Ejecuta: Guillermo |
| CP-09<br>HU-12 | Materiales. Recomendaciones por método y marcas compartidas al recargar. Miembro autorizado puede marcar/desmarcar; otro huerto no puede leer ni alterar las marcas; POST protegido.<br>Ejecuta: Juan |
| CP-10<br>HU-01 a HU-12 | Recorrido y entrega. Instalación desde README en otro equipo, carga inicial repetida, reinicio y persistencia. Un flujo final integrado; celular, computador y teclado, errores claros; respaldo de la base ficticia y demo local.<br>Ejecuta: Juan |

## Resultados y correcciones

docs/v1/resultados.md reúne caso/historia, pasos y datos, resultado esperado, observado, aprobado/fallido, fecha y ejecutor. Se añade una captura cuando ayuda a demostrar el resultado; no una por cada variante. Un fallo incluye cómo reproducirlo y quién lo corrige. Se identifican la revisión de código probada y las repeticiones tras correcciones. La misma tabla se incorpora al informe, sin otra transcripción manual en CSV o Word.

Las pruebas automáticas se ejecutan con manage.py test. Cubren nuestras reglas más delicadas y evitan repetir manualmente cada combinación. Tras corregir se repiten los casos afectados y, al final, un flujo completo. No se pide porcentaje de cobertura, CI, pruebas de carga o un laboratorio de dos conexiones.

## Reglas de trabajo

- Cada integrante comunica el estado de sus tareas y los bloqueos en el medio que ya use el equipo. Juan coordina cambios de fechas y entregas; no se mantiene otro tablero ni un registro diario de horas obligatorio.
- Ramas por funcionalidad o cambio coherente. Se revisan brevemente cambios que afecten modelos compartidos, servicios, permisos o contratos entre módulos. Para cambios pequeños, el autor comprueba su parte antes de integrar; no se exigen revisores múltiples ni reunión por cada hito.
- Si una tarea se retrasa, se reparte una parte concreta a quien tenga menor carga: datos, pantalla, función o documentación. Se simplifica la presentación y el proceso antes de quitar una función del alcance.
- El 31 de octubre el producto ya funciona y la documentación corresponde al código. En octubre se hacen comprobaciones de desarrollo y se preparan casos; no se presentan como resultados formales pruebas que aún no se han ejecutado.

## Informe sin documentos duplicados

Los tres documentos de trabajo contienen alcance, arquitectura/tecnologías y reparto. Los bocetos y capturas se guardan en diseno/. El informe oficial reúne ese contenido y la tabla de resultados usando la plantilla de Word; no se redactan informes de gestión, planes extensos de calidad, matrices de trazabilidad o hojas de horas adicionales.

Cada integrante entrega a Juan su sección inicial antes del 31 de octubre. Para evitar que varios sobrescriban informe.docx, Juan consolida los aportes y el resto revisa su sección. En noviembre se actualiza solo lo que cambió y se incorporan los resultados reales. Un párrafo del informe indica herramientas de IA utilizadas, para qué y cómo se verificaron; no se archiva cada conversación o prompt.

## Uso de IA y aprendizaje

La IA puede ayudar con código, consultas, pruebas y redacción. Quien entrega código debe explicar qué recibe, qué valida, qué guarda y qué permiso exige, además de comprobar su ejecución. Los datos del dominio se contrastan con fuentes y las pruebas se ejecutan; la salida de una IA no sustituye esas comprobaciones.

## Condiciones para la entrega

- Doce historias implementadas, catálogo completo, trece actividades, saberes, calendario, materiales, historial, puntos, maestro y huerto virtual operativos.
- Diez casos con resultados reales; correcciones comprobadas; ningún fallo conocido que impida el recorrido, altere puntos/estado o exponga datos ajenos. Una limitación no resuelta se indica, sin inventar un aprobado.
- Repositorio con código, migraciones, datos Python, imágenes/licencias, documentación V1 y README. Una instalación limpia en otro equipo y un reinicio comprueban ejecución y persistencia.
- Base de demo ficticia separada de los datos de trabajo, con ciclo avanzado y dos comunidades. Una copia comprobada, archivos estáticos locales y guion corto bastan; no se desarrolla una herramienta general de preparación/restauración.
- Informe con plantilla oficial y nombre Proyecto-Version1-nombreEquipo.pdf, enlace accesible al repositorio y resultados. Juan prepara entrega; los seis ensayan su parte el 9 de noviembre.

Si una parte no está completa el 31 de octubre, se identifica como pendiente y se ajusta la secuencia de pruebas. Las estimaciones se revisan con el avance real, sin crear trabajo para igualar horas ni marcar tareas incompletas como terminadas. Un cambio funcional del alcance se consulta con la profesora.

## Referencias del curso

- Proyecto: Definición del proyecto y consigna Desarrollo del producto versión 1, aula virtual de Calidad de Software, ISWD652, período 2026B.
- Dominio: Huertos Medicinales Comunitarios y MSP: Lineamientos para la implementación de huertos medicinales en establecimientos del primer nivel de atención, 2017. Material del aula virtual.
- Clases: 5 de octubre de 2026, 01:15:54 a 01:16:36: selección de actividades de calidad y revisión de defectos en la demo. 6 de octubre: maestro único, 00:47:12; entregables, 01:23:09; plantillas sugeridas, 01:25:24; saberes y huerto virtual, 01:33:19 a 01:34:36; edad recomendada, 01:35:44 a 01:36:48. Tiempos desde el inicio de las grabaciones.
