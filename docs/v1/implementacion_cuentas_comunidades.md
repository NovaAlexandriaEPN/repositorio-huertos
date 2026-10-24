# Implementación de cuentas y comunidades

## Organización del código

La aplicación utiliza Python 3.13.14, Django 5.2.18 y SQLite. El servidor recibe solicitudes del navegador, aplica las reglas del producto y devuelve páginas HTML. La interfaz implementada usa plantillas Django y CSS local. Bootstrap 5.3 permanece previsto para la presentación.

Se conserva la arquitectura de una sola aplicación con cuatro módulos: `cuentas`, `catalogo`, `comunidades` y `actividades`. `cuentas` gestiona la identidad y el perfil. `comunidades` utiliza esa identidad y las referencias del catálogo para organizar los grupos y sus huertos. El registro de actividades se integra sobre los modelos compartidos de esos módulos.

Cada módulo separa los datos en `models.py`, los campos de entrada en `forms.py`, las operaciones en `servicios.py` y la atención de solicitudes en `views.py`. `urls.py` vincula las direcciones con sus vistas y las plantillas presentan los datos recibidos. Las reglas de autorización y guardado se ejecutan en el servidor.

## Cuentas, sesión y datos personales

`Usuario` extiende `AbstractUser` de Django e incorpora nombre completo, fecha de nacimiento, género opcional, talentos ancestrales y constancia del consentimiento. El registro público exige aceptar el aviso vigente. El servidor guarda su versión y la fecha de aceptación; los campos de constancia no se editan desde el perfil.

El formulario comprueba los campos recibidos y el servicio vuelve a validar las condiciones de registro. Django valida la contraseña y `set_password()` prepara su hash antes del guardado. Una fecha de nacimiento futura se rechaza. La recomendación de participar desde los 14 años se presenta como un aviso y no impide crear una cuenta de menor edad.

El inicio de sesión utiliza `authenticate()` y las sesiones de Django. Las vistas privadas identifican a la persona mediante `request.user`. El cierre de sesión se realiza por POST y elimina su acceso a esas vistas. Las escrituras incluyen protección CSRF y, después de un guardado correcto, redirigen a una página de consulta.

La pantalla de perfil consulta y modifica únicamente la cuenta de la sesión. Un identificador de otra persona añadido a GET o POST no cambia ese destino. El perfil permite editar nombre completo, nacimiento, género y talentos; conserva nombre de acceso, contraseña, permisos y constancia del aviso. El aviso de datos permanece consultable desde esa pantalla.

## Comunidad, huerto y selecciones

Los modelos compartidos de comunidades son:

| Modelo | Responsabilidad |
| --- | --- |
| `Comunidad` | Guarda nombre, tipo, contacto, responsable creador y código de invitación único. |
| `Miembro` | Relaciona una cuenta con su única comunidad. |
| `Huerto` | Relaciona una comunidad con su configuración y la constancia de maestro vigente, si existe. |
| `PlantaHuerto` | Relaciona un huerto con una especie del catálogo y un método de siembra. |
| `MarcaMaterial` | Conserva la disponibilidad de un material en un huerto concreto. |

Crear una comunidad guarda también la pertenencia de su responsable en la misma transacción. Las demás personas se unen mediante el código generado por el sistema. Los servicios rechazan una segunda pertenencia, el traslado a otro grupo y la transferencia del responsable. Las relaciones únicas de la base refuerzan esas restricciones.

El huerto se crea al completar su primera configuración válida. Guarda provincia, parroquia y dirección manuales, área positiva, uno o varios diseños y abonos y una cerca, un suelo y una fuente de agua. El formulario ofrece opciones de la categoría correspondiente y el servicio vuelve a comprobarlas. La configuración y sus relaciones múltiples se guardan juntas. Editar la configuración conserva la identidad del huerto, sus selecciones y el nombramiento que tenga registrado.

Una especie se puede elegir una sola vez por huerto y distintas comunidades pueden elegirla de manera independiente. La selección apunta a la ficha del catálogo y no la duplica. Su método de siembra puede cambiarse o la selección puede retirarse únicamente mientras no tenga historial. Retirar la selección conserva la ficha del catálogo.

`PlantaHuerto.tiene_historial` consulta todos los registros relacionados, incluidas actividades anuladas. El modelo rechaza cambiar el método con historial y los servicios bloquean tanto ese cambio como el retiro. El campo previsto `Actividad.planta` debe apuntar a `PlantaHuerto`, usar `PROTECT` y declarar `related_name="actividades"`. El contrato permite las actividades generales mediante una referencia opcional. Una comprobación registrada en Django informa `comunidades.E001` si el modelo de actividades, una vez incorporado, no cumple esa relación. Esta conexión utiliza el registro de aplicaciones y la relación inversa, sin importar `actividades.models` desde comunidades.

## Permisos y materiales compartidos

El responsable es el creador de la comunidad y también es miembro. Su rol se obtiene de `Comunidad.responsable`, sin almacenar una segunda copia del mismo permiso.

| Operación | Responsable | Participante |
| --- | --- | --- |
| Consultar comunidad, huerto y miembros propios | Permitido | Permitido |
| Editar comunidad y configurar huerto | Permitido | Denegado |
| Elegir especies, cambiar métodos o retirar sin historial | Permitido | Denegado |
| Consultar y marcar materiales del huerto propio | Permitido | Permitido |
| Consultar o editar nacimiento y género de otro miembro | Denegado | Denegado |

Las consultas de miembros seleccionan los nombres e identificadores necesarios para la presentación. El responsable conserva acceso únicamente a su propio perfil privado. La condición de maestro es un reconocimiento y no añade permisos administrativos.

Los servicios obtienen la comunidad y el huerto desde la pertenencia de la cuenta activa. Los identificadores de selección se buscan dentro de ese huerto; un ID de otra comunidad no permite consultarla o modificarla. Ocultar un enlace en una plantilla se acompaña de la comprobación del permiso al recibir la solicitud y ejecutar el servicio.

Los materiales incluyen recomendaciones comunes y otras relacionadas con los métodos de siembra elegidos. `listar_materiales()` consulta la disponibilidad del huerto propio sin crear marcas al leer. `marcar_material()` guarda un valor booleano explícito mediante una transacción. El reenvío de la misma disponibilidad conserva una única marca y las marcas de otras comunidades permanecen independientes. Esta función no administra cantidades ni compras.

## Arranque y comprobaciones

El [README](../../README.md) contiene los pasos de clonación de `bryan`, creación del entorno virtual e instalación de `requirements.txt`. Cada integrante utiliza su propia variable `DJANGO_SECRET_KEY`. Con el entorno y la clave configurados, los comandos de desarrollo en PowerShell son:

```powershell
& .\.venv\Scripts\python.exe manage.py check
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py runserver
```

La dirección `http://127.0.0.1:8000/` exige sesión y lleva a la comunidad de la persona conectada. El menú vincula perfil, comunidad y huerto. Desde el huerto se accede a la selección de especies y los materiales compartidos.

Las pruebas de `cuentas/tests.py` y `comunidades/tests.py` comprueban privacidad, pertenencia única, autorización, configuración, selección y disponibilidad compartida. El recorrido integrado registra dos cuentas, inicia sus sesiones y conecta comunidad, huerto, plantas y materiales en una misma base temporal con CSRF activo. Las comprobaciones de desarrollo no registran una ejecución formal de los casos del curso.

El 24 de octubre de 2026 se verificó una copia temporal de las fuentes `c9e7747` en el mismo computador de desarrollo. Un entorno virtual nuevo instaló las dependencias fijadas y completó las migraciones sobre una base vacía. Las 122 pruebas descubiertas por `manage.py test` terminaron con resultado `OK`. Un servidor WSGI local respondió correctamente para acceso, registro y CSS y redirigió al acceso cuando se solicitó la entrada privada. La revisión de instalación en otro computador permanece pendiente.

La protección de historial se verifica con una tabla temporal que contiene registros activos y anulados. La comprobación incluye el modelo, los servicios y los envíos de formularios abiertos antes de que se registrara la actividad. La integración final con el modelo y los servicios de actividades de Fernando sigue pendiente.

## Estado de integración

La implementación de cuentas y comunidades está disponible en `bryan`. El catálogo definitivo, su carga y las funciones de actividades siguen siendo entregas pendientes de integración. El producto conserva el requisito de las 18 especies. Las pruebas emplean contenido ficticio en su base temporal y no completan las fichas ni preparan la base de demo.

La estructura de módulos, los modelos compartidos y los contratos de formulario y plantilla se mantienen según la arquitectura acordada. La incorporación de estas pruebas y de las instrucciones de arranque no requiere modificar esa arquitectura. El informe final deberá incorporar los resultados formales y el recorrido completo cuando estén disponibles las entregas del equipo.
