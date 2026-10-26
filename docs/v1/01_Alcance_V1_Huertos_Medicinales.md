# Alcance de la versión 1

Huertos medicinales comunitarios

Documento 1.4 | 14 de octubre de 2026

## Propósito y fechas

Aplicación web para configurar un huerto medicinal comunitario, consultar saberes ancestrales, registrar actividades y observar plantas, puntos y niveles. Se desarrolla con Python 3.13, Django, plantillas HTML, Bootstrap y SQLite. El huerto virtual usa tarjetas por planta; representa el historial registrado, sin sensores ni simulación del cultivo real.

Producto y documentación base completos el 31 de octubre de 2026. Pruebas formales, correcciones e informe final del 1 al 9 de noviembre. Entrega del informe antes de las 16:00 del martes 10 de noviembre de 2026 y demostración presencial durante la clase.

## 1 Cuentas y datos personales

- Registro, inicio y cierre de sesión con usuario y contraseña; usuario único, fijo en V1 y validado con las reglas de Django. El correo se usa como contacto de la comunidad. Las contraseñas se validan y almacenan mediante Django.
- Perfil propio: nombre completo, fecha de nacimiento válida, género con opción de no indicarlo y talentos ancestrales declarados. Nacimiento y género solo los consulta y edita su titular.
- Aviso de datos completo y legible en el registro, consultable después desde el perfil. Aceptación obligatoria con fecha y versión guardadas. Aviso de participación recomendada desde los 14 años: no impide registrar a una persona menor ni exige un cálculo de edad mínima.
- Todas las pantallas del producto requieren sesión, salvo registro e inicio de sesión. Las escrituras y el cierre de sesión usan POST con protección CSRF.

## 2 Comunidad y permisos

Una comunidad por cuenta y un huerto por comunidad. La comunidad puede representar a una persona, familia, condominio o barrio; guarda nombre, tipo y contacto del responsable: nombre, teléfono y correo. Quien la crea es su responsable. Las otras personas se unen con un código generado por el sistema. No hay transferencia del responsable ni traslado de miembros en V1.

| Rol o nivel | Permisos |
| --- | --- |
| Responsable | Edita comunidad y huerto, elige plantas, registra actividades propias, anula, nombra/sustituye maestro y marca materiales. |
| Participante | Consulta su comunidad, huerto, miembros e historial; registra actividades propias y marca materiales. |
| Maestro | Reconocimiento de aprendizaje. Mantiene los permisos de su rol; no concede administración. El responsable también puede ser maestro. |

Los miembros ven nombre, puntos y nivel de su comunidad. El responsable no recibe nacimiento ni género de otras personas. El servidor comprueba comunidad y permiso en lecturas y escrituras; el código de invitación solo permite unirse.

## 3 Configurador del huerto

Solo el responsable edita: provincia, parroquia y dirección manuales; área mayor que cero; uno o varios diseños y abonos; una cerca, un suelo y una fuente de agua. La orientación Este a Oeste se muestra como recomendación. Diseños: tierra, vertical, colgante o piso, con los ejemplos del material del curso. Cercas: viva, natural, reciclada, metálica o convencional. Suelos: arcilloso, limoso, arenoso, margoso, gredoso o pantanoso. Agua: río, canal, goteo u otro. Abonos: barbecho, restos vegetales, hojas o compost.

Se eligen especies del catálogo y un método por selección: semillas, estacas, esquejes o plántulas. Una selección por especie y huerto y un ciclo por selección en V1. Se puede retirar una selección o cambiar su método solo si no tiene historial, incluido historial anulado. No se elimina la comunidad durante V1.

## 4 Catálogo fijo de 18 plantas

Especies incluidas: menta, hierbabuena, toronjil, orégano, romero, manzanilla, matico, taraxaco (diente de león), marco, llantén, ortiga, violeta, paico, chilca, lavanda, salvia, cedrón, laurel.

Cada ficha contiene nombre común y científico, otros nombres, familia botánica, altitud y distribución en provincias del Ecuador, ciclo corto/largo, cualidad ancestral caliente/fría, parte utilizada, usos descritos, contraindicaciones, foto estática con licencia y fuentes. Un atributo sin respaldo se identifica como no verificado. La información es educativa y no reemplaza la atención médica.

Plantas, guías, actividades, opciones, materiales y eventos lunares se definen como datos fijos en archivos Python del repositorio y se precargan en SQLite. Son de solo lectura en la aplicación. Las correcciones se hacen internamente en el código; no hay editor, registro de cambios ni sistema de versiones del catálogo dentro del producto. El historial de actividades y sus recompensas conserva sus valores originales.

## 5 Guía ancestral y actividades

Cada tipo muestra instrucciones, materiales, precauciones, hora y fase lunar recomendadas, con fuente. Se conservan las 13 actividades: 3 generales del huerto y 10 por planta. El formulario guarda tipo, planta cuando corresponda, fecha/hora y nota opcional. El autor se toma de la sesión; cada persona registra únicamente sus actividades.

| Actividad | Alcance | Puntos |
| --- | --- | --- |
| Preparación de la tierra | Huerto | 10 |
| Elaboración del diseño | Huerto | 10 |
| Ritual de siembra | Huerto | 10 |
| Siembra | Planta | 15 |
| Señalética | Planta | 5 |
| Cuidados de crecimiento | Planta | 5 |
| Riego | Planta | 5 |
| Baño de la planta | Planta | 5 |
| Ritual de gratitud | Planta | 10 |
| Cosecha | Planta | 20 |
| Limpieza de plantas | Planta | 5 |
| Secado | Planta | 10 |
| Empaquetado y etiquetado | Planta | 15 |

Cada tipo premia una vez por su alcance, entre los registros activos. Cuidados y riegos se pueden repetir: el primero activo recibe 5 puntos y los siguientes 0. Los otros tipos admiten un único registro activo por alcance, con posibilidad de registrarse de nuevo tras una anulación válida.

## Guía y restricciones

Las instrucciones incluyen preparación en luna oscura, ritual al amanecer, siembra desde las 08:00, señalética por cualidad, cuidados, riego, baño y gratitud antes de cosechar, cosecha según la parte usada, limpieza, secado a la sombra y empaquetado. Se respetan las fuentes de cada recomendación.

Son obligatorios 15 días entre preparación y siembra, y 10 entre inicio de secado y empaquetado. Las demás horas, fases y tiempos son recomendaciones; no bloquean ni dan bonos. Nuevas actividades generales solo se registran sin siembras activas. Diseño y ritual no son prerrequisitos obligatorios para sembrar.

## Estados y validación del registro

| Actividad | Condición | Resultado |
| --- | --- | --- |
| Preparación de la tierra | Sin siembras activas | No cambia la planta |
| Elaboración del diseño | Sin siembras activas | No cambia la planta |
| Ritual de siembra | Sin siembras activas | No cambia la planta |
| Siembra | Planeada; preparación al menos 15 días antes | Sembrada |
| Señalética | Sembrada o creciendo | Conserva el estado |
| Cuidados de crecimiento | Sembrada o creciendo | Creciendo |
| Riego | Sembrada o creciendo | Creciendo |
| Baño de la planta | Creciendo | Conserva creciendo |
| Ritual de gratitud | Creciendo | Conserva creciendo |
| Cosecha | Creciendo | Cosechada |
| Limpieza de plantas | Cosechada | Conserva cosechada |
| Secado | Cosechada | Secando |
| Empaquetado y etiquetado | Secando; inicio al menos 10 días antes | Empacada |

- La fecha no es futura. Para una planta no puede ser anterior a su última actividad activa. El historial se ordena por fecha/hora y después por ID; en un empate, el mayor ID es el último.
- Planta, huerto y actor pertenecen a la comunidad autorizada. Cambiar un identificador del formulario no permite leer ni modificar datos ajenos.
- La misma clave de envío y los mismos datos devuelven el registro existente. Con la misma clave y otra carga se rechaza el envío. Un registro anulado no se reactiva por reenvío.
- Solo las transiciones de la tabla cambian el estado. Una nota, señalética, baño, gratitud o limpieza no se interpreta como una nueva transición.

## Historial y anulaciones

Todos los miembros consultan el historial de su comunidad. Las actividades guardan actor, fecha, tipo, nota y recompensa originales. Para corregir, el responsable anula con motivo; se guardan quién anuló y cuándo. El autor original registra la actividad correcta desde su propia cuenta. Si se revierten otras actividades, cada autor vuelve a registrar las suyas. La corrección no atribuye al responsable las actividades ni los puntos de otra persona.

- Por planta se anula únicamente la última actividad activa; para corregir una anterior se revierten primero las posteriores en orden inverso.
- Preparación no se anula si hay siembras activas. Diseño y ritual se anulan independientemente: no exigen revertir otras generales ni actividades de las plantas. Volver a registrar una general sigue requiriendo ausencia de siembras activas.
- La operación actualiza juntas la anulación, las recompensas afectadas y el nombramiento de maestro cuando corresponda. Estado, puntos y progreso se recalculan desde el historial activo. Si quedan cuidados/riegos, el primero activo de cada tipo recibe su recompensa histórica.
- Si el maestro baja de 100 puntos, se retira el nombramiento en esa operación. El registro anulado permanece visible con motivo, autor y fecha de anulación.

## 6 Calendario lunar

Tabla local de eventos principales verificados de USNO, del 1 de septiembre al 31 de diciembre de 2026: luna nueva, cuarto creciente, luna llena y cuarto menguante. Los instantes se guardan en UTC y se muestran en America/Guayaquil. Se presenta una lista o tabla por mes con las recomendaciones relacionadas.

Entre eventos se muestran el anterior y el siguiente disponibles, sin inventar una fase principal diaria. En los extremos puede faltar uno; fuera del período se indica que no hay datos cargados. Registrar una actividad no requiere que ese día tenga un evento lunar. La demo usa datos locales y funciona sin consultar servicios externos.

## 7 Huerto virtual y progreso

Una tarjeta por especie elegida muestra foto, nombre, método, estado y siguiente acción recomendada. Estados: planeada, sembrada, creciendo, cosechada, secando y empacada. Estado y progreso se derivan del historial activo.

Seis hitos de igual peso: preparación del huerto, siembra, crecimiento por cuidado o riego, cosecha, secado y empaquetado. Cada uno suma una sexta parte. Preparación y siembra dan 2 de 6, aproximadamente 33 %. Varios cuidados/riegos cuentan como un solo hito. El avance del huerto es el promedio de sus plantas; sin plantas es 0 %. Añadir una selección puede reducirlo: una planta al 100 % y otra planeada con preparación activa dan 58,3 %. Una anulación también puede reducir el avance.

## 8 Puntos y niveles

Los totales personales y comunitarios suman los puntos otorgados de actividades activas. Cambiar internamente los valores del catálogo no reescribe recompensas pasadas. Los niveles se calculan así:

| Nivel | Regla |
| --- | --- |
| Aprendiz | 0 a 99 puntos. Toda cuenta comienza sin puntos ni nombramiento. |
| Oficial | Desde 100 puntos, sin nombramiento vigente de maestro. |
| Maestro | Miembro de la comunidad con al menos 100 puntos, nombrado por el responsable con justificación de su capacidad para guiar una siembra. Llegar a 300 no lo nombra automáticamente. |

Como máximo un maestro vigente por huerto; puede no haber ninguno. Se conservan motivo, autor y fecha del nombramiento vigente. Sustituirlo retira el anterior y asigna el nuevo en una sola operación. El anterior vuelve al nivel que corresponde a sus puntos. El formulario desactualizado se rechaza si ya cambió el maestro.

## 9 Materiales compartidos

Recomendaciones de herramientas e implementos, material de siembra y abonos según los métodos elegidos. Se incluye la orientación para una bodega seca, ventilada y con luz natural. Cada material tiene una casilla compartida de disponible que cualquier miembro de la comunidad puede marcar/desmarcar. No se administran cantidades, costos ni compras.

## Fuera de V1

Fotos o videos de actividades; GPS y mapas; foro, ranking, misiones, insignias y certificaciones; inventario con cantidades, cosechas parciales, varios ciclos por especie, traslados de miembros y delegación del responsable. La ubicación se registra manualmente. No se requieren publicación en internet ni panel de administración técnico para la entrega de V1.

## Referencias del curso

- Proyecto: Definición del proyecto y consigna Desarrollo del producto versión 1, aula virtual de Calidad de Software, ISWD652, período 2026B.
- Dominio: Huertos Medicinales Comunitarios y MSP: Lineamientos para la implementación de huertos medicinales en establecimientos del primer nivel de atención, 2017. Material del aula virtual.
- Clases: 5 de octubre de 2026, 01:15:54 a 01:16:36: selección de actividades de calidad y revisión de defectos en la demo. 6 de octubre: maestro único, 00:47:12; entregables, 01:23:09; plantillas sugeridas, 01:25:24; saberes y huerto virtual, 01:33:19 a 01:34:36; edad recomendada, 01:35:44 a 01:36:48. Tiempos desde el inicio de las grabaciones.

## Historias de usuario y aceptación

Estas doce historias y sus criterios constituyen la base de requisitos. No se exige repetirlas en otra matriz, en el código ni en cada tarea. Los resultados de pruebas identifican las historias que comprueban.

| ID e historia | Criterios de aceptación |
| --- | --- |
| HU-01<br>Como persona usuaria, quiero registrarme y editar mi perfil para participar con mis datos. | Cuenta única, contraseña validada, consentimiento guardado; nacimiento válido y género visibles solo al titular. Los 14 años son un aviso, sin bloqueo. |
| HU-02<br>Como miembro, quiero iniciar y cerrar sesión para acceder a mi comunidad. | Acceso con usuario y contraseña; páginas privadas protegidas y cierre por POST. |
| HU-03<br>Como miembro, quiero crear una comunidad o unirme con código para trabajar con otras personas. | Una pertenencia por cuenta; creador responsable. Solo este edita nombre, tipo y contacto; no se transfiere el rol. |
| HU-04<br>Como responsable, quiero configurar el huerto y elegir plantas para representar el cultivo. | Ubicación manual, área positiva, opciones válidas y una selección por especie; método e identidad protegidos si existe historial. |
| HU-05<br>Como miembro, quiero consultar las plantas para conocer sus características y precauciones. | Las 18 fichas tienen los campos acordados, foto, licencia y fuentes; los datos no verificados se identifican. |
| HU-06<br>Como miembro, quiero consultar la guía ancestral para realizar las actividades. | Los 13 tipos contienen instrucciones, materiales, precauciones y recomendaciones con fuente; se distinguen las restricciones obligatorias. |
| HU-07<br>Como miembro, quiero consultar eventos lunares para organizar las actividades. | Tabla mensual local, hora de Guayaquil y fuente; sin fases diarias inventadas ni datos fuera del período cargado. |
| HU-08<br>Como miembro, quiero registrar mis actividades para conservar lo realizado. | Actor de la sesión; fecha, estado y comunidad válidos. Se cumplen los plazos de 15 y 10 días y se controlan reenvíos. |
| HU-09<br>Como responsable, quiero anular registros erróneos para corregir el historial. | Motivo, autor y fecha de anulación; orden inverso por planta, preparación protegida, diseño y ritual independientes; no se transfiere autoría. |
| HU-10<br>Como miembro, quiero ver puntos, nivel y progreso para conocer el avance. | Recompensas sin duplicación, seis hitos, estado derivado y promedio de las plantas; anulaciones recalculan los valores afectados. |
| HU-11<br>Como responsable, quiero nombrar a un maestro para reconocer quién puede guiar la siembra. | Como máximo uno, de la comunidad y con al menos 100 puntos; motivo, autor y fecha. Sustitución y retiro si baja de 100; 300 no nombra automáticamente. |
| HU-12<br>Como miembro, quiero marcar los materiales disponibles para coordinar su uso. | Lista recomendada y marcas compartidas persistentes, limitadas a la comunidad; sin cantidades ni compras. |

## Entregables de la versión 1

Producto operativo; historias de usuario; arquitectura y diseño; listado de herramientas y tecnologías; código fuente; casos de prueba con resultados reales; README. El informe usa la plantilla oficial de Word, se entrega como Proyecto-Version1-nombreEquipo.pdf e incluye el enlace al repositorio con documentación V1 y código. Las plantillas de historias y casos del aula son una referencia, no un trabajo duplicado obligatorio.

Antes de la demo se comprueba el recorrido integrado y se corrigen los defectos que impidan el uso, alteren puntos/estados o expongan datos ajenos. Los datos ficticios de demostración se identifican y permiten mostrar un ciclo avanzado sin esperar los tiempos del cultivo.
