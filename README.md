# Huertos medicinales comunitarios - Nova Alexandria - Versión 1

Aplicación web para configurar un huerto medicinal comunitario, consultar saberes ancestrales,
registrar actividades y observar plantas, puntos y niveles.

Proyecto de **Calidad de Software (ISWD652, período 2026B)**.

- EPN - 2026B
- GR1SW
- Integrantes: Domenica Astudillo, Bryan Ayala, Fernando Carrera, Guillermo Cevallos, Juan Chugá, Matthew Redin

[Enlace de la carpeta compartida de la documentación](https://epnecuador-my.sharepoint.com/:f:/r/personal/juan_chuga_epn_edu_ec/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fjuan%5Fchuga%5Fepn%5Fedu%5Fec%2FDocuments%2FCalidad%20de%20Software&share=cgpAPIBlWcTlRoYB2Hgn%2DozUEgUC0pr97Omw7s%5F5ECGaECVdCA)

---

## Estado actual del proyecto

`main` reúne el progreso publicado del equipo hasta el 25 de octubre de 2026,
con un merge que conserva los commits y las ramas personales. Incluye cuentas y
comunidades de Bryan, actividades de Fernando corregidas contra el alcance,
seis fichas/fotos de Juan, el diseño de Doménica y las entregas de catálogo de Matthew.

Funcionan registro y consentimiento, sesión y perfil privado, comunidad por código,
configuración, selección protegida por historial, materiales, registro y anulación de
actividades, puntos, progreso, maestro, fichas, guía ancestral y calendario local.

La carga nueva contiene **las 18 fichas**, **13 guías**, **23 opciones**,
**18 materiales** y **17 eventos lunares**. Faltan la consolidación de las fichas,
fotos y datos expresamente señalados como no verificados, la base ficticia de demo,
los resultados formales y la comprobación en otro computador. La revisión de código
no sustituye la revisión de dominio de las fichas ni declara terminada V1.

Consulta [la revisión general y de ramas](docs/v1/integracion_equipo.md) para ver
las doce historias, las correcciones y los pendientes. Las comprobaciones automáticas
son de desarrollo; los casos formales siguen previstos para el 1 al 9 de noviembre.

Las guías de Bryan conservan la explicación de cada etapa:
[comunidades](docs/aprendizaje/B2-02_comunidades.md),
[huerto y plantas](docs/aprendizaje/B2-03_B2-04_huerto_y_plantas.md),
[recorrido inicial](docs/aprendizaje/B3-01_recorrido_integrado.md),
[materiales](docs/aprendizaje/B3-02_permisos_y_materiales.md) y
[pruebas propias](docs/aprendizaje/B3-03_pruebas_reglas_propias.md).

---

## Contenido

1. [Tecnologías y versiones](#1-tecnologías-y-versiones)
2. [Requisitos previos](#2-requisitos-previos)
3. [Instalación paso a paso](#3-instalación-paso-a-paso)
4. [Uso diario](#4-uso-diario)
5. [Pruebas](#5-pruebas)
6. [Estructura del proyecto](#6-estructura-del-proyecto)
7. [Reglas de trabajo con Git](#7-reglas-de-trabajo-con-git)
8. [Base de datos de demostración](#8-base-de-datos-de-demostración)

---

## 1. Tecnologías y versiones

| Pieza | Versión | Notas |
|---|---|---|
| Python | **3.13.14** | Todo el equipo usa el mismo parche. No se mezclan versiones menores. |
| Django | **5.2.18 (LTS)** | Fijado exactamente en `requirements.txt`. |
| Base de datos | SQLite | Incluida en Python. Transacciones `IMMEDIATE`, espera de 5 s. |
| tzdata | 2026.5 | Zona horaria `America/Guayaquil` en Windows. |
| Interfaz | Plantillas Django + Bootstrap 5.3.8 + CSS local | Recursos incorporados; no necesita CDN. |
| Pruebas | Django `TestCase` + `manage.py test` | Un `tests.py` por aplicación. |

## 2. Requisitos previos

- Windows 10/11 con PowerShell.
- **Git** instalado (`git --version`).
- **Python 3.13.14**. Comprueba que el lanzador `py` lo encuentra:

  ```powershell
  py -0p
  py -3.13 --version
  ```

  Debe aparecer `Python 3.13.14`. Si no está instalado, descárgalo desde
  <https://www.python.org/downloads/windows/> (marca *Add python.exe to PATH*) o usa
  el administrador de instalaciones de Python con `py install 3.13`.

> Si tienes otra versión (por ejemplo 3.14) instalada, no importa: el entorno virtual se crea
> explícitamente con `py -3.13`.

## 3. Instalación paso a paso

Todos los comandos se ejecutan en **PowerShell**, dentro de la carpeta del repositorio.

### 3.1 Clonar la base compartida

Para obtener la base compartida, crear una copia nueva en el escritorio:

```powershell
Set-Location -LiteralPath ([Environment]::GetFolderPath('Desktop'))
git clone --branch main https://github.com/NovaAlexandriaEPN/repositorio-huertos.git repositorio-huertos
Set-Location -LiteralPath .\repositorio-huertos
```

Si el repositorio ya está clonado, entrar en su carpeta y usar:

```powershell
git fetch origin
git switch bryan
git merge origin/main
```

Bryan continúa desarrollando en `bryan`; cada compañero usa su propia rama. El ejemplo
anterior trae la base compartida a bryan mediante merge y conserva el historial. Si hay
cambios locales sin guardar, revísalos antes de cambiar de rama o integrar. Las nuevas
funcionalidades no se desarrollan directamente en main.

### 3.2 Crear el entorno virtual

```powershell
py -3.13 -m venv .venv
& .\.venv\Scripts\python.exe --version
```

Debe mostrar `Python 3.13.14`. Los comandos de esta guía llaman directamente al Python de
`.venv`; no necesitan activar el entorno ni cambiar la política de ejecución de PowerShell.

### 3.3 Instalar dependencias

```powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pip check
```

### 3.4 Clave secreta (`DJANGO_SECRET_KEY`)

`huertos/settings.py` lee la clave de la variable de entorno `DJANGO_SECRET_KEY`.
**Cada integrante genera su propia clave local, la conserva y nunca la sube a Git.**
Esto se hace **una sola vez** por computador y **antes de `migrate`**.

```powershell
# Reutilizar la clave del usuario de Windows si ya existe.
$claveHuertosLocal = [Environment]::GetEnvironmentVariable('DJANGO_SECRET_KEY', 'User')
if ([string]::IsNullOrWhiteSpace($claveHuertosLocal)) {
    $claveHuertosLocal = & .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar la clave local.' }
    [Environment]::SetEnvironmentVariable('DJANGO_SECRET_KEY', $claveHuertosLocal, 'User')
}
$env:DJANGO_SECRET_KEY = $claveHuertosLocal
Remove-Variable claveHuertosLocal
```

Comprueba que está cargada en esta terminal:

```powershell
[bool]$env:DJANGO_SECRET_KEY  # Debe mostrar True, sin imprimir la clave.
```

> No cambies la clave después de crear datos: las sesiones iniciadas dejarían de ser válidas.

### 3.5 Crear la base de datos y cargar el catálogo

```powershell
& .\.venv\Scripts\python.exe manage.py check
& .\.venv\Scripts\python.exe manage.py migrate
& .\.venv\Scripts\python.exe manage.py cargar_catalogo
```

Esto crea las tablas de los cuatro módulos y carga el contenido entregado. Las advertencias
del comando identifican contenido pendiente o distinto. Repetirlo no reemplaza datos anteriores.

`cargar_catalogo` muestra una línea por modelo, por ejemplo
`Planta: entregados 12, nuevos 0, ya existían 12 (0 con contenido distinto), en la base 12.`

- **nuevos**: códigos que no existían y se crearon ahora.
- **ya existían**: códigos que se conservaron sin modificar.
- **con contenido distinto**: códigos existentes cuyo contenido no coincide con el archivo
  Python. No se sobrescriben; para ver cuáles son, ejecuta
  `& .\.venv\Scripts\python.exe manage.py cargar_catalogo -v 2`.

Si una ficha trae un campo que el modelo no tiene, el comando se detiene sin guardar nada
e indica la ficha y el campo.
Si tu base ya tenía las guías abreviadas, consulta la sección de actualización de bases
en el informe de integración: git merge actualiza archivos, no el contenido de SQLite.
Si ya usaste las actividades de la entrega original de Fernando y guardaste registros,
la migración se detiene para no convertirlos con reglas equivocadas. Conserva esa base y
consulta [la nota de migración](docs/v1/integracion_equipo.md#migraciones-y-bases-que-ya-usaron-la-entrega-anterior).

### 3.6 Levantar el servidor

```powershell
& .\.venv\Scripts\python.exe manage.py runserver
```

Abrir <http://127.0.0.1:8000/>. Sin sesión lleva al inicio de sesión y, después del acceso,
a la comunidad. Si se entra directamente por `/cuentas/login/` sin un destino solicitado,
se muestra el perfil. El enlace «Crear cuenta» permite registrarse; el menú conecta perfil,
comunidad y huerto. Detener el servidor con `Ctrl + C`.

### 3.7 Verificación de instalación

El 24 de octubre de 2026 se comprobó una copia temporal de las fuentes de `c9e7747` en
este mismo PC. Se creó un `.venv` nuevo, se instalaron las versiones de `requirements.txt`,
`pip check` terminó sin conflictos y las migraciones se aplicaron sobre una base vacía.
La suite completa descubrió y ejecutó 122 pruebas con resultado `OK`.

Un servidor WSGI local devolvió 200 para acceso, registro y CSS, y 302 al solicitar `/`
sin sesión. Se utilizó una clave temporal del proceso. La base de trabajo del repositorio
no participó en esta comprobación. La revisión en un segundo computador sigue pendiente.

### Acceso y privacidad

`LoginRequiredMiddleware` exige sesión en todas las vistas por defecto. Solo registro e
inicio de sesión llevan `@login_not_required`; las nuevas pantallas del producto permanecen
privadas sin añadir excepciones. El cierre de sesión y la edición usan POST con CSRF.

El perfil siempre se obtiene de `request.user`, sin recibir el ID de otra cuenta. Solo se
editan nombre completo, nacimiento, género y talentos. Usuario, contraseña, permisos y
constancia de consentimiento no se modifican desde ese formulario. Las respuestas de cuentas
llevan cabeceras para evitar almacenar las páginas personales en caché.

### Modelos de comunidad y huerto (B2)

`comunidades/models.py` define estas relaciones:

- `Comunidad.responsable`: una cuenta puede ser responsable de una sola comunidad.
- `Miembro.usuario`: una cuenta tiene una sola pertenencia. `Miembro.comunidad` permite
  que muchas cuentas pertenezcan a la misma comunidad. `es_responsable` se obtiene de
  `Comunidad.responsable`, sin guardar un segundo rol que pueda contradecirlo.
- `Huerto.comunidad`: cada comunidad puede tener un solo huerto. El área se guarda con
  dos decimales en `area_m2` y debe ser positiva; la ubicación es manual.
- `Huerto.disenos` y `Huerto.abonos`: elecciones múltiples. `cerca`, `suelo` y
  `fuente_agua`: elecciones únicas de `catalogo.OpcionHuerto`.
- `Huerto.maestro` apunta a un `Miembro`. `maestro_motivo`, `maestro_nombrado_por`
  (cuenta responsable) y `maestro_fecha` guardan la constancia vigente. Estos campos no
  conceden permisos ni guardan puntos o niveles.
- `PlantaHuerto.huerto` y `planta`: combinación única. `metodo_siembra` admite
  `semillas`, `estacas`, `esquejes` o `plantulas`, definidos en `catalogo.models.MetodoSiembra`.
  La selección conserva su huerto y especie. El método puede cambiar antes del historial.
- `MarcaMaterial.huerto` y `material`: combinación única. `disponible` es una casilla
  compartida, inicialmente falsa; cada huerto mantiene su propia marca.

`catalogo/models.py` contiene:

- `OpcionHuerto`: `codigo` único, `categoria`, `nombre` y `explicacion`.
  Categorías: `diseno`, `cerca`, `suelo`, `agua`, `abono`.
- `Planta`: las 19 claves de las fichas acordadas. Los textos desconocidos aceptan `None`;
  las listas y fuentes se guardan en `JSONField` con listas independientes por registro.
  La ruta de foto es relativa a `static/`, por ejemplo `img/plantas/romero.jpg`.
- `Material`: `codigo`, `nombre`, `grupo`, `recomendacion` y `metodos_siembra`.
  Grupos: `herramientas`, `siembra`, `abonos`. Una lista de métodos vacía indica que es
  común a todos los métodos; una lista no vacía usa los códigos de `MetodoSiembra`.

`TipoActividad` contiene las 13 reglas y sus guías de consulta; `EventoLunar` admite los
eventos verificados. Sus migraciones y el comando de carga están implementados. El
contenido de las fichas y las guías conserva los pendientes de integración indicados arriba.

La creación de comunidad guarda comunidad y pertenencia del creador en una
transacción. El huerto se guarda al completar su primera configuración válida;
antes puede no existir. No se generan filas relacionadas mediante señales automáticas.

Los modelos validan los cambios de responsable/pertenencia, las categorías de las
opciones únicas y la pertenencia/autoría del nombramiento. Para ejecutar esa validación,
los servicios deben llamar a `full_clean()` antes de guardar: `save()` y `objects.create()`
no la ejecutan por sí solos. Las claves únicas y las restricciones de área/constancia
también están protegidas en SQLite.

El configurador valida las listas recibidas de diseños y abonos:
al menos una opción de cada categoría, antes de guardarlas en la misma transacción.
`limit_choices_to` filtra los formularios, pero no protege una escritura directa en esas
relaciones múltiples. Los permisos y el código de invitación se comprueban en los servicios de comunidad;
el código se genera automáticamente, es único y no es una credencial de inicio de sesión.
Las reglas de puntos y el mínimo de 100 para nombrar maestro se aplican en actividades.

### Crear, unirse y editar comunidad (B2-02)

Con una sesión iniciada, abrir <http://127.0.0.1:8000/comunidades/> o usar **Mi comunidad**
en el menú. Si aún no hay pertenencia, la pantalla ofrece crear una comunidad o unirse
con el código de 12 caracteres generado por el sistema.

| Ruta | Operación |
|---|---|
| `/comunidades/` | Consultar la propia comunidad y sus miembros. |
| `/comunidades/crear/` | Mostrar el formulario o crear comunidad y pertenencia del responsable. |
| `/comunidades/unirse/` | Mostrar el formulario o unirse mediante un código válido. |
| `/comunidades/editar/` | Mostrar o guardar los datos de la comunidad propia, solo para su responsable. |

GET muestra las páginas; POST con CSRF realiza las escrituras. Las rutas no reciben un ID
de comunidad para elegir qué consultar o editar: los servicios la obtienen de la pertenencia
de la cuenta de la sesión. El código de invitación no concede permisos de edición.
No se aceptan responsable ni código como campos editables del formulario.

`ComunidadForm` valida los cinco campos públicos de creación/edición. Los servicios vuelven
a comprobar cuenta activa, pertenencia y permisos, validan el modelo y guardan en una
transacción. Crear o unirse por segunda vez se rechaza sin duplicar registros ni trasladar
al miembro. Los conflictos de integridad o de escritura ocupada en SQLite muestran un
mensaje para revisar o reintentar; otros errores de base no se ocultan como validaciones.

Las pruebas de comunidades incluyen los modelos B2-01, creación/unión/edición, aislamiento
entre comunidades, privacidad, métodos HTTP y CSRF. Se ejecutan con
`& .\.venv\Scripts\python.exe manage.py test comunidades`.

### Configurador y selección de plantas (B2-03/B2-04)

Desde **Mi comunidad**, abrir **Ver el huerto de la comunidad**. El responsable puede guardar
provincia, parroquia, dirección manual, área positiva, varios diseños y abonos y una opción
de cerca, suelo y agua. Las opciones se filtran por categoría en el formulario y se vuelven
a validar en el servicio. Configuración y relaciones múltiples se guardan juntas; al reabrir
el formulario se conservan las selecciones. Actualizar no reemplaza el huerto ni su maestro.

| Ruta | Función |
|---|---|
| `/comunidades/huerto/` | Consultar configuración y plantas de la comunidad propia. |
| `/comunidades/huerto/configurar/` | Crear o actualizar la configuración, solo por el responsable. |
| `/comunidades/huerto/plantas/elegir/` | Añadir una especie disponible con un método de siembra. |
| `/comunidades/huerto/plantas/<id>/metodo/` | Cambiar únicamente el método de una selección propia sin historial. |
| `/comunidades/huerto/plantas/<id>/retirar/` | Mostrar confirmación por GET y retirar por POST si no tiene historial. |

La consulta no acepta un ID de huerto externo. Los IDs de selección se buscan dentro del huerto
del responsable; un ID ajeno responde 404. La especie no se repite en un mismo huerto y otra
comunidad puede elegirla de forma independiente. Retirar no elimina la ficha del catálogo.
Las operaciones de escritura incluyen POST y CSRF.

No se añaden datos definitivos del catálogo como parte de estas tareas de Bryan: las opciones,
las fichas y su carga pertenecen a las entregas de Matthew, Guillermo y Juan. El producto sigue
requiriendo las 18 especies; usar unas pocas especies en pruebas no recorta ese requisito.

### Materiales compartidos (B3-02)

Desde el huerto, **Ver materiales compartidos** abre `/comunidades/huerto/materiales/`.
Responsable y participantes pueden consultar las recomendaciones y guardar la disponibilidad
con una casilla por material. `metodos_siembra=[]` identifica los materiales comunes;
los demás se muestran cuando coincide alguno de los métodos elegidos en el huerto.

`listar_materiales(actor=...)` consulta exclusivamente las marcas del huerto propio y no
crea registros al leer. `marcar_material(actor=..., material_id=..., disponible=...)` valida
la pertenencia y guarda un valor booleano explícito en una transacción. Los reenvíos conservan
una sola marca y no invierten su valor. Cambiar los métodos no borra las marcas que dejen
de mostrarse temporalmente.

El guardado usa POST con CSRF en `/comunidades/huerto/materiales/<material_id>/` y no acepta
IDs de comunidad o huerto para cambiar el destino. No se administran cantidades ni compras.
La guía B3-02 documenta los contratos de formulario y plantilla para la integración posterior.

Contrato de la pantalla (J3) con el diseño de `templates/comunidades/materiales.html`:

- `materiales`: filas de `listar_materiales` con `material`, `disponible` y `form`, ordenadas
  por los grupos del catálogo (herramientas e implementos, material de siembra y abonos).
- `recomendacion_bodega`: texto de `catalogo/datos/huerto.py` con su fuente (MSP p. 24).
- Cada formulario envía POST con CSRF a `comunidades:marcar_material` con el campo
  `material-<id>-disponible`. Al guardar se vuelve a la lista con el mensaje «La disponibilidad
  del material se ha guardado para tu comunidad.»; los errores usan `componentes/errores.html`.

### Contrato con actividades para proteger el historial

`Actividad.planta` debe apuntar a la selección `PlantaHuerto`, no a la especie del catálogo:

```python
# Relación implementada en Actividad:
planta = models.ForeignKey(
    "comunidades.PlantaHuerto",
    on_delete=models.PROTECT,
    related_name="actividades",
    null=True,
    blank=True,
)
```

`null=True` permite las actividades generales. La relación inversa debe incluir todo el
historial, también los registros anulados. `PlantaHuerto.tiene_historial` consulta esa
relación mediante el gestor base, sin excluir anuladas, y `clean()` rechaza cambiar el método
si ya hay actividades. Los servicios también bloquean el retiro. `PROTECT` impedirá
borrar una selección referenciada por actividades.

`comunidades/checks.py` usa el registro de aplicaciones de Django para verificar, cuando exista
`Actividad`, que su campo `planta` tenga esta relación, sea opcional y proteja el borrado.
Si no cumple, `manage.py check` informa `comunidades.E001`. No se importa el modelo de actividades.

`Actividad` ya está incorporada. Además de la prueba de contrato con una tabla temporal,
las pruebas de integración registran y anulan una siembra mediante los servicios reales
y comprueban que su historial sigue bloqueando el cambio de método y el retiro.

## 4. Uso diario

Cada vez que abras una terminal nueva para trabajar:

```powershell
$rutaProyectoHuertos = Join-Path ([Environment]::GetFolderPath('Desktop')) 'repositorio-huertos'
Set-Location -LiteralPath $rutaProyectoHuertos
git branch --show-current
git pull --ff-only
$env:DJANGO_SECRET_KEY = [Environment]::GetEnvironmentVariable('DJANGO_SECRET_KEY', 'User')
if (-not $env:DJANGO_SECRET_KEY) { throw 'Configura la clave siguiendo la sección 3.4.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt   # si cambiaron las dependencias
& .\.venv\Scripts\python.exe manage.py migrate                  # si hay migraciones nuevas
& .\.venv\Scripts\python.exe manage.py runserver
```

En la copia de Bryan, la rama debe ser `bryan`. `--ff-only` detiene la actualización si
las ramas han divergido y necesitan una integración.

### Variables de entorno disponibles

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Sí | - | Clave secreta local (sección 3.4). |
| `DJANGO_DEBUG` | No | `1` | `0` desactiva el modo depuración. |
| `DJANGO_ALLOWED_HOSTS` | No | vacío | Hosts extra separados por comas (por ejemplo, tu IP local). |

## 5. Pruebas

```powershell
& .\.venv\Scripts\python.exe manage.py test                 # todas las aplicaciones
& .\.venv\Scripts\python.exe manage.py test cuentas         # una sola aplicación
& .\.venv\Scripts\python.exe manage.py test -v 2            # salida detallada
```

Las pruebas usan una base temporal; no modifican `db.sqlite3`.
La guía B3-03 identifica las clases que comprueban privacidad, pertenencia e historial.
Los casos manuales (CP-01 a CP-10) y sus resultados reales de noviembre se registrarán en
[`docs/v1/resultados.md`](docs/v1/resultados.md).

## 6. Estructura del proyecto

```
repositorio-huertos/
|-- manage.py; requirements.txt; README.md; .gitignore
|-- huertos/                 # settings.py, urls.py, wsgi.py, asgi.py
|-- cuentas/                 # models, forms, servicios, views, urls, tests
|-- catalogo/                # models, servicios, views, urls, tests
|   |-- datos/               # fichas, guías, opciones, materiales y luna (Python)
|   `-- management/commands/cargar_catalogo.py
|-- comunidades/             # models, forms, servicios, views, urls, tests
|-- actividades/             # models, forms, servicios, views, urls, tests
|   `-- reglas.py            # nivel y porcentaje sin consultas
|-- templates/               # base.html, componentes/ y una carpeta por módulo
|-- static/                  # vendor/bootstrap/, css/estilos.css, img/plantas/
`-- docs/v1/                 # alcance, arquitectura, plan, diseño, resultados, demo, informe
```

Dependencias entre módulos: `catalogo` no depende de nadie; `comunidades` usa `cuentas` y
`catalogo`; `actividades` usa los tres anteriores. **Los módulos inferiores no importan
`actividades`.** Las reglas del dominio van en `servicios.py`; las vistas solo coordinan
petición y respuesta.

### Bootstrap local

Se incluye Bootstrap 5.3.8 en `static/vendor/bootstrap/`, con su cabecera de licencia.
`base.html` carga su CSS y después `static/css/estilos.css`. El menú y las pantallas
no dependen de una CDN. Los formularios y los menús de cuenta funcionan sin JavaScript.

## 7. Reglas de trabajo con Git

- Cada integrante trabaja en su rama. Bryan usa **`bryan`** y publica únicamente ahí;
  los cambios a `main` requieren la integración acordada por el equipo.
- Antes de guardar o publicar trabajo, comprobar `git branch --show-current`. En la
  instalación de Bryan debe mostrar `bryan`; `git push` publica a `origin/bryan`.
- **Nunca** se suben: `.venv/`, `db.sqlite3`, copias de la base de demo, claves ni archivos `.env`
  (ya están en `.gitignore`).
- Cada cambio de modelo incluye **su migración**. Los cambios de modelos y migraciones se
  coordinan con el responsable del módulo antes de integrarlos.
- `AUTH_USER_MODEL = 'cuentas.Usuario'` debe existir **antes de la primera migración**. No
  ejecutes `migrate` hasta que `cuentas/models.py` defina `Usuario`.
- Para cambios que afecten modelos compartidos, servicios, permisos o contratos entre módulos,
  se pide una revisión breve antes de integrar.
- Si `requirements.txt` cambia, avisa al grupo. Para fijar una dependencia nueva:
  `& .\.venv\Scripts\python.exe -m pip install <paquete>` y luego
  `& .\.venv\Scripts\python.exe -m pip freeze > requirements.txt`.

| Archivo o carpeta | Coordina |
|---|---|
| `huertos/`, `cuentas/`, `requirements.txt` | Bryan |
| `catalogo/` | Matthew |
| `comunidades/` | Bryan (materiales: Juan) |
| `actividades/` | Fernando (`reglas.py`: Guillermo) |
| `templates/`, `static/`, `docs/v1/diseno/` | Doménica |
| `docs/v1/resultados.md`, `docs/v1/demo.md` | Guillermo / Juan |
| `README.md`, `docs/v1/informe.docx` | Juan |

## 8. Base de datos de demostración

La base ficticia de demo con ciclo avanzado y dos comunidades está pendiente de preparación
e integración con actividades. Se guardará fuera de Git. Las pruebas automatizadas crean
sus propios datos temporales y no preparan esa base de demo.

Para respaldar la base de trabajo existente, detener el servidor y ejecutar desde el repositorio:

```powershell
# Respaldar tu base de trabajo
$respaldoHuertos = 'db_trabajo_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.sqlite3'
Copy-Item -LiteralPath db.sqlite3 -Destination $respaldoHuertos
```

El archivo [`docs/v1/demo.md`](docs/v1/demo.md) está reservado para el guion de la demo;
todavía no contiene un guion completo.

## Comprobación de la base compartida

Las pruebas comprueban el ciclo de las trece actividades, privacidad, permisos, comunidad,
plazos, UUID, anulaciones, progreso y maestro. La revisión vigente y la fecha de ejecución
se recogen en [integracion_equipo.md](docs/v1/integracion_equipo.md).

Para una instalación nueva: cargar la clave local, ejecutar `migrate`, `cargar_catalogo`
y `runserver`. En una base ya usada, la carga conserva los registros existentes y avisa
si difieren del código. No borres SQLite ni su historial para resolver un cambio de catálogo.

### Carga inicial y segunda carga (J2-08 y J2-09)

Comprobación de desarrollo del 25 de octubre de 2026; no es un resultado formal de pruebas.

- `catalogo/tests.py` (`CargaInicialTests`) comprueba que una base nueva recibe todas las
  listas de `catalogo/datos/`, que un campo desconocido detiene la carga sin guardar nada y
  que `-v 2` lista los códigos con diferencias sin corregirlos.
- `catalogo/tests.py` (`SegundaCargaTests`) prepara una base ficticia con dos cuentas,
  comunidad, huerto, planta seleccionada, material marcado, el ciclo de las trece
  actividades, una anulación y un maestro nombrado. Repite la carga sin cambios y con datos
  Python modificados (una ficha nueva y otros puntos para una guía): solo se crea la ficha
  nueva, la guía guardada conserva sus puntos y los datos de trabajo quedan idénticos.
- A mano, sobre una base temporal: `migrate`, `cargar_catalogo`, datos de trabajo creados
  con los servicios, conteo de filas, segunda carga y nuevo conteo. Las cantidades y el
  contenido de cuentas, comunidad, huerto, selección, marca y actividades no cambiaron.

Una base cargada antes del 25 de octubre de 2026 mostrará fichas y guías «con contenido
distinto»: los créditos de fotos se revisaron y los textos se estandarizaron (guion en lugar
de raya, «x» en nombres de híbridos, «...» en lugar de elipsis). La aplicación sigue
mostrando bien esas fichas. Para actualizar los créditos de fotos usa
`docs/v1/diseno/actualizar_fotos_base.py`, con una copia de respaldo de la base.
