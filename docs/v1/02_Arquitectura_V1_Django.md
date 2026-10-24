# Arquitectura de la versión 1

Una aplicación Django con páginas HTML y SQLite

Documento 1.4 | 14 de octubre de 2026

## Organización y tecnologías

Una sola aplicación web en un repositorio. Django recibe los formularios, consulta o guarda en SQLite y devuelve HTML. Cuatro módulos separan cuentas, catálogo, comunidades y actividades. Las reglas se escriben en servicios.py de cada módulo; las vistas coordinan la petición y la respuesta.

Navegador -> Django -> SQLite

| Pieza | Selección |
| --- | --- |
| Lenguaje | Python 3.13 para todo el equipo. Al iniciar se acuerda el mismo parche 3.13.x y se indica en README; no se mezclan versiones menores. |
| Framework | Django 5.2 LTS. Un parche de mantenimiento vigente y compatible se fija exactamente en requirements.txt al iniciar el repositorio. |
| Interfaz | Plantillas Django, Bootstrap 5.3 local y CSS mínimo. JavaScript solo si una interacción lo necesita; formularios normales y recarga de página son suficientes. |
| Base de datos | SQLite, ORM y migraciones de Django; tzdata para America/Guayaquil en Windows. Cada cambio de modelo incluye su migración. |
| Comprobaciones | Django TestCase y su ejecutor incorporado; un tests.py por módulo. Casos funcionales y resultados reales en noviembre. |
| Ejecución | Desarrollo y demo local en un computador del equipo. README y una segunda instalación comprobada. Bootstrap, imágenes y datos disponibles sin internet. |

## Los cuatro módulos

| Módulo | Contenido | Depende de |
| --- | --- | --- |
| cuentas | Usuario, registro, sesión, perfil y consentimiento. | Django auth |
| catalogo | 18 plantas, 13 guías, opciones, materiales y eventos lunares. | Sin dependencia del dominio |
| comunidades | Comunidad, miembros, huerto, selección y materiales disponibles. | cuentas y catalogo |
| actividades | Registro, historial, anulación, puntos, progreso y maestro. | cuentas, catalogo y comunidades |

Los módulos inferiores no importan actividades. Los cálculos que necesitan su historial y el nombramiento del maestro se coordinan desde actividades. Las rutas globales incluyen las cuatro aplicaciones.

## Formularios, vistas y errores

cuentas, comunidades y actividades tienen formularios propios en forms.py y vistas propias en views.py, con campos y validaciones de su función. catalogo tiene vistas de consulta. Se mantiene servicios.py en las cuatro aplicaciones, aunque algunas funciones solo hagan consultas. No se impone usar formularios o vistas genéricas como atajo.

base.html comparte menú y estilos. componentes/errores.html muestra errores de campo y del formulario; componentes/mensajes.html muestra mensajes de resultado. Las pantallas pueden tener plantillas de formulario distintas. La autenticación, el hash de contraseñas, las sesiones y CSRF siguen a cargo de Django.

## Modelo de datos

Doce modelos del dominio. Django añade sus tablas de autenticación y las relaciones múltiples generan tablas intermedias.

| Módulo | Modelo | Contenido |
| --- | --- | --- |
| cuentas | Usuario | AbstractUser; nombre completo, nacimiento, género, talentos y consentimiento con fecha y versión. |
| catalogo | Planta | Código estable, ficha, ruta de foto, licencia y fuentes. |
| catalogo | TipoActividad | Código, alcance, guía, puntos, repetibilidad y recomendaciones. |
| catalogo | Material | Código, grupo, recomendación y métodos de siembra aplicables. |
| catalogo | OpcionHuerto | Código, categoría, nombre y explicación. |
| catalogo | EventoLunar | Tipo, instante UTC y fuente; tabla fija de septiembre a diciembre de 2026. |
| comunidades | Comunidad | Nombre, tipo, responsable, contacto y código de invitación. |
| comunidades | Miembro | Usuario único y comunidad; no se traslada ni tiene varias pertenencias. |
| comunidades | Huerto | Comunidad única, ubicación, área, opciones y maestro vigente con motivo, autor y fecha. |
| comunidades | PlantaHuerto | Huerto, especie y método; selección única por especie. Estado y progreso derivados. |
| comunidades | MarcaMaterial | Huerto y material disponible; combinación única. |
| actividades | Actividad | Huerto, planta opcional, tipo, actor, fecha/hora, nota, puntos históricos y otorgados, repetibilidad, UUID/carga y anulación. |

## Restricciones que se conservan

- AUTH_USER_MODEL se define antes de la primera migración; las referencias usan el modelo configurado. Miembro tiene usuario único; Huerto, comunidad única.
- PlantaHuerto es única por huerto y especie; MarcaMaterial por huerto y material. Código de invitación y UUID de envío son únicos. Área positiva y opciones de la categoría correcta se validan en el servidor.
- Los catálogos usan códigos estables. Las referencias del historial se protegen de eliminación. Método y especie no se cambian si la selección tiene historial, aun anulado.
- Actividad fija puntos_base y repetible desde el servidor al registrarse, además de puntos_otorgados. Así una anulación puede recomputar recompensas sin consultar valores cambiados del catálogo.
- Los tipos no repetibles tienen restricciones únicas condicionales para registros activos: (huerto, tipo) cuando planta está vacía y (planta, tipo) cuando está informada. La condición usa anulado=False y repetible=False; no consulta otra tabla. Esto evita depender del comportamiento de NULL en una única clave.
- Huerto guarda maestro opcional, motivo, autor y fecha vigentes. El servicio valida pertenencia y umbral; el nivel de maestro no es un permiso de administrador.

Puntos, estado, nivel y porcentaje se calculan a partir de las actividades activas, sin guardar copias del total en varias tablas. Para el progreso se usan los seis hitos del alcance. Para el estado se consideran solo actividades que producen una transición.

## Datos fijos en el código

catalogo/datos/ contiene listas y diccionarios Python: 18 fichas repartidas en tres archivos de seis; las 13 guías y sus puntos; opciones y materiales; eventos lunares y fuentes. __init__.py reúne esos datos para el comando de carga. Este es el único formato obligatorio del catálogo; no se mantienen CSV, JSON y hojas de fuentes paralelos.

```text
PLANTAS = [
    {
        'codigo': 'romero',
        'nombre_comun': 'Romero',
        'nombre_cientifico': 'dato verificado',
        # Resto de campos de la ficha, foto, licencia y fuentes.
    },
]
# Ejemplo de estructura, no una ficha lista para cargar.
```

cargar_catalogo crea los registros iniciales por código estable y no duplica los que existen. No borra ni modifica actividades, pertenencias o nombramientos. No es un sincronizador general: las correcciones del contenido se hacen internamente, mediante el código y una operación controlada sobre los registros afectados o una nueva base ficticia. No se implementan editor, auditoría de catálogo ni historial de versiones del contenido.

Cada ficha conserva sus fuentes y la licencia de la foto dentro de sus propios datos. La foto usa una ruta local bajo static/img/plantas/. No hay subida de archivos ni se necesita ImageField/Pillow para estas fotos. Los eventos lunares se verifican en la fuente antes de dejarlos precargados; no se ejecuta una API ni un cálculo astronómico en la demo.

## Servicios de cada módulo

| Archivo | Funciones que concentra |
| --- | --- |
| cuentas/servicios.py | Crear cuenta/perfil, guardar consentimiento y actualizar perfil propio; nacimiento válido y privacidad, sin umbral de edad. |
| catalogo/servicios.py | Consultar fichas/guías, recomendaciones y eventos por mes; convertir a hora local y gestionar ausencia de datos. |
| comunidades/servicios.py | Crear/unir/editar comunidad, configurar huerto, elegir plantas y marcar materiales, comprobando rol y comunidad. |
| actividades/servicios.py | Registrar, anular y nombrar maestro; consultas de historial, estado, puntos y progreso. |
| actividades/reglas.py | Cálculos de nivel y porcentaje sin acceso a base de datos; recibe puntos/nombramiento o indicadores de hitos. |

## Recorrido de una solicitud

urls.py elige la vista; esta verifica sesión y lee forms.py cuando hay entrada. El formulario valida campos básicos y conserva el UUID al mostrar errores. El servicio resuelve permisos, reenvíos y reglas del dominio. La vista redirige tras un POST correcto o vuelve a mostrar su plantilla con los errores comunes. Puntos, estado y permisos no se deciden en HTML o JavaScript.

## Registro y corrección sin duplicaciones

registrar_actividad(usuario, datos, envio_id) obtiene actor, huerto, puntos y repetibilidad desde el servidor. El UUID se genera al abrir el formulario; se conserva en reintentos. Los campos normalizados de la carga incluyen huerto, planta, tipo, fecha/hora y nota.

- Dentro de la operación atómica, autorizar comunidad y comprobar si existe el UUID. Mismo actor, huerto y carga devuelve el registro existente, incluso anulado; otra carga se rechaza.
- Resolver el reenvío antes de rechazar por nuevo estado o hito duplicado. Solo un envío nuevo valida estado, alcance, fecha y los plazos locales de 15/10 días, además de la ausencia de siembras para las generales.
- Guardar actividad y recompensa; ordenar por fecha/hora e ID para localizar el primer cuidado/riego activo. Los posteriores dan 0. La base protege los tipos no repetibles aunque se envíe otro UUID.

## Anulación y nombramiento

anular_actividad(responsable, actividad, motivo) exige responsable, comunidad y motivo. Por planta, solo última activa; preparación, sin siembras activas; diseño y ritual, de forma independiente. Guarda motivo, autor y fecha de anulación sin cambiar el actor original. Recalcula recompensas con los valores históricos y retira al maestro si baja de 100 puntos.

nombrar_maestro(responsable, candidato, motivo, maestro_esperado) comprueba rol, comunidad, puntos actuales y motivo. Compara el maestro vigente con el que recibió el formulario para rechazar una sustitución desactualizada. En una operación guarda candidato, motivo, autor y fecha; como máximo queda uno. Una cuenta con 300 puntos continúa como oficial si no es nombrada.

## Escrituras y permisos

Las escrituras compuestas usan transaction.atomic(). Con SQLite se configura transaction_mode="IMMEDIATE" y un tiempo de espera breve para serializar escrituras cortas, incluida la comprobación del maestro. Si hay conflicto, se devuelve un mensaje para reintentar; no se mantiene una transacción abierta mientras se renderiza HTML. No se usa select_for_update() como si SQLite tuviera bloqueos de fila.

Todas las lecturas/escrituras filtran la comunidad autorizada. Registro y formularios incluyen validadores de Django y CSRF. Las vistas no envían nacimiento/género de otros miembros, tampoco al responsable. El aviso completo permanece consultable en el perfil. No se habilita un panel técnico para consultar o editar el catálogo en V1. Los niveles y los identificadores enviados por el navegador no determinan permisos.

## Pruebas pequeñas y útiles

Django TestCase y manage.py test bastan para comprobar nuestras reglas: límites de nivel/progreso, permisos propios, plazos, recompensas/reenvíos, anulación y maestro. No se escriben pruebas del funcionamiento interno de Django ni de cada variante visual. Un archivo tests.py por aplicación; no se exige cobertura, integración continua, herramientas de análisis, laboratorio de concurrencia o inyección de fallos.

El conjunto manual comprueba los doce requisitos con diez casos y un recorrido final, según el plan. Se revisan las 18 fichas, pero se usan pocas plantas representativas para el ciclo. Las pruebas formales y sus resultados se ejecutan en noviembre; cada autor comprueba su código al integrarlo en octubre.

## Estructura de ficheros

Cada aplicación incluye __init__.py, apps.py y migrations/. En el árbol, models/forms/servicios/views/urls/tests significan archivos .py. Los archivos generados sin uso no requieren desarrollo. No se crea un paquete tests/ además de tests.py.

```text
repositorio-huertos/
|-- manage.py; requirements.txt; README.md; .gitignore
|-- huertos/                 # settings.py, urls.py, wsgi.py, asgi.py
|-- cuentas/                 # models, forms, servicios, views, urls, tests
|-- catalogo/                # models, servicios, views, urls, tests
|   |-- datos/
|   |   |-- __init__.py
|   |   |-- plantas_juan.py
|   |   |-- plantas_matthew.py
|   |   |-- plantas_guillermo.py
|   |   |-- actividades.py
|   |   |-- huerto.py         # opciones y materiales
|   |   `-- luna.py          # eventos UTC y fuentes
|   `-- management/commands/cargar_catalogo.py
|-- comunidades/             # models, forms, servicios, views, urls, tests
|-- actividades/             # models, forms, servicios, views, urls, tests
|   `-- reglas.py            # nivel y porcentaje sin consultas
|-- templates/
|   |-- base.html
|   |-- componentes/errores.html; componentes/mensajes.html
|   |-- cuentas/registro.html; login.html; perfil.html
|   |-- catalogo/lista_plantas.html; detalle_planta.html
|   |             guia.html; calendario.html
|   |-- comunidades/crear.html; unirse.html; mi_comunidad.html
|   |                 configurar_huerto.html; materiales.html
|   `-- actividades/inicio_huerto_virtual.html
|                     registrar_actividad.html; historial.html
|                     anular.html; nombrar_maestro.html
|-- static/vendor/bootstrap/; css/estilos.css; img/plantas/
`-- docs/v1/
    |-- 01_Alcance_V1_Huertos_Medicinales.md
    |-- 02_Arquitectura_V1_Django.md
    |-- 03_Plan_de_trabajo_V1.md
    |-- diseno/              # pocos bocetos y capturas finales
    |-- resultados.md        # casos, ejecución y fallos
    |-- demo.md              # datos ficticios y recorrido
    |-- informe.docx         # plantilla oficial, un archivo
    `-- Proyecto-Version1-nombreEquipo.pdf
```

## Puesta en marcha local

Instalar el Python 3.13.x acordado. README explica entorno, dependencias y puesta en marcha. settings.py lee SECRET_KEY de DJANGO_SECRET_KEY; README indica generar/configurar una clave local sin subirla a Git y conservarla para reinicios. db.sqlite3, entornos, claves y copias de demo quedan fuera de Git. La base ficticia se prepara con el producto o shell y se copia para el ensayo.

```text
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Definir DJANGO_SECRET_KEY como indica README, antes de migrate.
python manage.py migrate
python manage.py cargar_catalogo
python manage.py runserver
# Comprobaciones automatizadas, durante la fase de pruebas:
python manage.py test
```

## Referencias técnicas

- Django: https://docs.djangoproject.com/en/5.2/faq/install/
- Autenticación y pruebas: https://docs.djangoproject.com/en/5.2/topics/auth/default/ ; https://docs.djangoproject.com/en/5.2/topics/testing/overview/
- Transacciones y SQLite: https://docs.djangoproject.com/en/5.2/topics/db/transactions/ ; https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes
- Eventos lunares: USNO: https://aa.usno.navy.mil/data/MoonPhases

## Correspondencia con la integración en bryan (24 de octubre de 2026)

La implementación conserva esta organización. En `Actividad`, el campo `puntos` contiene
los puntos otorgados, junto a `puntos_base`, `repetible` y `carga`. Se conserva el campo
`estado` de la entrega integrada: `activa` equivale a `anulado=False` para las restricciones
únicas condicionales. `tipo` referencia `TipoActividad` mediante su código estable.
La situación de las entregas y las comprobaciones figura en `integracion_equipo.md`.
