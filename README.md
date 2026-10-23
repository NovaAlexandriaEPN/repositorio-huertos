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

En esta rama están disponibles el modelo `Usuario`, su primera migración, el registro con
consentimiento, el inicio/cierre de sesión y la consulta/edición del perfil propio.
Funcionan `migrate`, `runserver` y las pruebas automatizadas.

Los cinco modelos compartidos de B2-01 están definidos: `Comunidad`, `Miembro`, `Huerto`,
`PlantaHuerto` y `MarcaMaterial`, con sus migraciones. El catálogo aporta `OpcionHuerto`,
`Planta` y `Material` como dependencias.
Los formularios, servicios y pantallas de comunidades/huertos, selección de plantas y
materiales siguen pendientes. También faltan el modelo y las funciones de actividades.
El comando `cargar_catalogo` todavía no está implementado.

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
| Interfaz | Plantillas Django + Bootstrap 5.3 (local) + CSS mínimo | Sin CDN: la demo funciona sin internet. |
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

### 3.1 Clonar el repositorio

```powershell
git clone https://github.com/NovaAlexandriaEPN/repositorio-huertos.git repositorio-huertos
cd repositorio-huertos
```

Para revisar el avance de Bryan después de clonar:

```powershell
git switch --track origin/bryan
```

Bryan mantiene su trabajo en `bryan`. Los demás integrantes usan sus propias ramas para
sus cambios; revisar esta rama no requiere integrarla en `main`.

### 3.2 Crear y activar el entorno virtual

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

El prompt debe empezar con `(.venv)`. Comprueba:

```powershell
python --version   # Python 3.13.14
```

> Si PowerShell bloquea la activación ("la ejecución de scripts está deshabilitada"),
> habilítala solo para la terminal actual y vuelve a activar:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> .\.venv\Scripts\Activate.ps1
> ```

### 3.3 Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3.4 Clave secreta (`DJANGO_SECRET_KEY`)

`huertos/settings.py` lee la clave de la variable de entorno `DJANGO_SECRET_KEY`.
**Cada integrante genera su propia clave local, la conserva y nunca la sube a Git.**
Esto se hace **una sola vez** por computador y **antes de `migrate`**.

```powershell
# 1. Generar la clave
$clave = python -c "import secrets; print(secrets.token_urlsafe(50))"

# 2. Guardarla de forma permanente para tu usuario de Windows (sobrevive reinicios)
setx DJANGO_SECRET_KEY $clave

# 3. Cargarla también en la terminal actual (setx solo afecta a terminales nuevas)
$env:DJANGO_SECRET_KEY = $clave
```

Comprueba que está definida (en una terminal nueva):

```powershell
[bool]$env:DJANGO_SECRET_KEY  # Debe mostrar True, sin imprimir la clave.
```

> No cambies la clave después de crear datos: las sesiones iniciadas dejarían de ser válidas.

### 3.5 Crear la base de datos y cargar el catálogo

```powershell
python manage.py migrate
```

Esto crea la base local con las tablas de Django y los modelos disponibles de cuentas,
catálogo y comunidades.
`python manage.py cargar_catalogo` se ejecutará cuando esté implementado: deberá cargar las
18 plantas, 13 guías, opciones, materiales y eventos lunares sin duplicar datos ni borrar historial.

### 3.6 Levantar el servidor

```powershell
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/cuentas/login/> en el navegador. Si todavía no tienes cuenta,
usa el enlace «Crear una cuenta». Después de entrar se muestra tu perfil en
<http://127.0.0.1:8000/cuentas/perfil/>. Detener el servidor con `Ctrl + C`.

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

Los modelos `TipoActividad` y `EventoLunar`, y la carga de los datos, siguen pendientes.
Estos modelos no completan ni verifican el contenido de las 18 fichas.

La creación de comunidad deberá guardar comunidad y pertenencia del creador en una
transacción. El huerto se guardará al completar su primera configuración válida;
antes puede no existir. No se generan filas relacionadas mediante señales automáticas.

Los modelos validan los cambios de responsable/pertenencia, las categorías de las
opciones únicas y la pertenencia/autoría del nombramiento. Para ejecutar esa validación,
los servicios deben llamar a `full_clean()` antes de guardar: `save()` y `objects.create()`
no la ejecutan por sí solos. Las claves únicas y las restricciones de área/constancia
también están protegidas en SQLite.

El configurador pendiente deberá validar las listas recibidas de diseños y abonos:
al menos una opción de cada categoría, antes de guardarlas en la misma transacción.
`limit_choices_to` filtra los formularios, pero no protege una escritura directa en esas
relaciones múltiples. Los permisos y el código de invitación se comprobarán en los servicios;
el código se genera automáticamente, es único y no es una credencial de inicio de sesión.
Las reglas de puntos y el mínimo de 100 para nombrar maestro se implementarán en actividades.

### Contrato con actividades para proteger el historial

`Actividad.planta` debe apuntar a la selección `PlantaHuerto`, no a la especie del catálogo:

```python
# Dentro del futuro modelo Actividad:
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
relación y `clean()` rechaza cambiar el método si ya hay actividades. `PROTECT` impedirá
borrar una selección referenciada por actividades.

Hasta incorporar `Actividad`, aún no existe historial de actividades. La regla de cambio
de método tiene una prueba unitaria; la comprobación integrada con registros activos y
anulados, los permisos y la retirada de selecciones se completarán en B2-04. Comunidades
no importa el módulo actividades: usa la relación inversa que Django añadirá.

## 4. Uso diario

Cada vez que abras una terminal nueva para trabajar:

```powershell
cd repositorio-huertos
.\.venv\Scripts\Activate.ps1
git pull
python -m pip install -r requirements.txt   # solo si cambió requirements.txt
python manage.py migrate                    # solo si alguien subió migraciones nuevas
python manage.py runserver
```

### Variables de entorno disponibles

| Variable | Obligatoria | Valor por defecto | Uso |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Sí | — | Clave secreta local (sección 3.4). |
| `DJANGO_DEBUG` | No | `1` | `0` desactiva el modo depuración. |
| `DJANGO_ALLOWED_HOSTS` | No | vacío | Hosts extra separados por comas (por ejemplo, tu IP local). |

## 5. Pruebas

```powershell
python manage.py test                 # todas las aplicaciones
python manage.py test cuentas         # una sola aplicación
python manage.py test -v 2            # salida detallada
```

Las pruebas usan una base temporal; no modifican `db.sqlite3`.
Los casos manuales (CP-01 a CP-10) y sus resultados reales se registran en
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

Bootstrap 5.3 se guarda en el repositorio para que la demo funcione sin internet. Se agrega una
sola vez (Doménica) y el resto lo recibe con `git pull`:

1. Descargar *Compiled CSS and JS* de <https://getbootstrap.com/docs/5.3/getting-started/download/>.
2. Copiar `css/bootstrap.min.css` y `js/bootstrap.bundle.min.js` a `static/vendor/bootstrap/`.

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
  `python -m pip install <paquete>` y luego `python -m pip freeze > requirements.txt`.

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

La base ficticia (ciclo avanzado y dos comunidades) se prepara con el producto o con
`python manage.py shell` y se guarda **fuera de Git**. Para usarla en el ensayo o la demo:

```powershell
# Respaldar tu base de trabajo
Copy-Item db.sqlite3 db_trabajo.sqlite3

# Usar la copia de demo
Copy-Item <ruta>\db_demo.sqlite3 db.sqlite3 -Force
python manage.py runserver
```

El guion de la demo está en [`docs/v1/demo.md`](docs/v1/demo.md).
