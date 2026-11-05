# Demostración del sistema de huertos medicinales

## 1. Objetivo

Este documento describe cómo preparar y presentar un escenario ficticio del sistema de huertos medicinales.

El escenario permite demostrar:

- Creación y gestión de comunidades.
- Registro de participantes.
- Configuración de huertos.
- Selección de plantas y disponibilidad de materiales.
- Registro e historial de actividades.
- Cálculo de puntos y progreso.
- Nombramiento de un Maestro.
- Anulación de actividades.
- Validación de las reglas de cultivo.
- Separación de permisos entre comunidades.

Los datos y las cuentas descritos son exclusivamente ficticios y se utilizan para pruebas y presentaciones.

## 2. Requisitos previos

Antes de generar el escenario, cada integrante debe contar con:

- El repositorio del proyecto clonado.
- Python instalado y compatible con el proyecto.
- Un entorno virtual.
- Las dependencias del proyecto instaladas.
- Una base de datos SQLite configurada.
- Las migraciones aplicadas.
- El catálogo cargado.

Desde la raíz del repositorio, ejecutar:

\`\`\`bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt

# Aplicar las migraciones
python manage.py migrate

# Cargar el catálogo
python manage.py cargar_catalogo
\`\`\`

Si el entorno virtual ya existe, no es necesario crearlo nuevamente.

## 3. Crear el escenario ficticio

El script encargado de crear los datos se encuentra en:

\`\`\`text
scripts/crear_demo.py
\`\`\`

Para ejecutarlo desde la raíz del proyecto:

En Windows (PowerShell):

```powershell
& .\.venv\Scripts\python.exe manage.py shell -c "import runpy; runpy.run_path('scripts/crear_demo.py', run_name='__main__')"
```

En Linux o macOS:

```bash
.venv/bin/python manage.py shell -c "import runpy; runpy.run_path('scripts/crear_demo.py', run_name='__main__')"
```

El script realiza las siguientes comprobaciones antes de crear información:

1. Verifica que la base de datos predeterminada utilice SQLite.
2. Comprueba que no existan migraciones pendientes.
3. Comprueba que estén disponibles las plantas, opciones y materiales requeridos.
4. Verifica que no existan previamente las cuentas y comunidades de la demostración.

La creación de los registros se realiza dentro de una transacción. Si ocurre un error durante este proceso, los cambios de esa ejecución se revierten.

Al finalizar, se genera una copia de la base de datos en:

\`\`\`text
copias/demo_huertos.sqlite3
\`\`\`

La copia se comprueba mediante la instrucción \`PRAGMA integrity_check\` antes de reemplazar una copia anterior.

**Importante:** el script no elimina ni modifica registros existentes. Si encuentra alguna de las cuentas o comunidades del escenario, se detiene para evitar duplicados.

Para volver a generar el escenario, se debe utilizar una base de datos de demostración limpia. No se debe eliminar una base de datos de trabajo que contenga información necesaria.

## 4. Cuentas de acceso

Todas las cuentas son ficticias y se crean mediante el servicio de registro de usuarios de la aplicación.

| Rol | Usuario | Contraseña |
|---|---|---|
| Responsable de Los Aromos | \`demo_responsable_a\` | \`R3fugio!Luna_Cedro#72\` |
| Participante de Los Aromos | \`demo_participante_a\` | \`M4nt4!Bosque_Romero#83\` |
| Responsable de La Esperanza | \`demo_responsable_b\` | \`V3rde!Huerto_Lavanda#94\` |
| Participante de La Esperanza | \`demo_participante_b\` | \`T1erra!Semilla_Menta#65\` |

Estas credenciales son únicamente para el entorno de demostración. No deben utilizarse en servicios reales ni reutilizarse para cuentas personales.

## 5. Comunidades y huertos

### 5.1. Comunidad A: Huerto Medicinal Los Aromos

| Elemento | Información |
|---|---|
| Comunidad | Huerto Medicinal Los Aromos |
| Tipo | Barrio |
| Responsable | Ana Responsable Los Aromos |
| Participante | Mateo Participante Los Aromos |
| Ubicación del huerto | Quito, Pichincha |
| Plantas seleccionadas | Romero y Menta |
| Material disponible | Pala |

Mateo es el participante que completa el ciclo histórico del Romero y recibe el nombramiento de Maestro.

### 5.2. Comunidad B: Huerto Medicinal La Esperanza

| Elemento | Información |
|---|---|
| Comunidad | Huerto Medicinal La Esperanza |
| Tipo | Barrio |
| Responsable | Lucia Responsable La Esperanza |
| Participante | Diego Participante La Esperanza |
| Ubicación del huerto | Quito, Pichincha |
| Planta seleccionada | Lavanda |
| Material disponible | Pala |

Esta segunda comunidad permite comprobar que sus integrantes no pueden acceder a la información privada del huerto de Los Aromos.

## 6. Historial del Romero y nombramiento del Maestro

El participante Mateo registra el historial completo del Romero. Las actividades se crean con fechas pasadas y en orden cronológico.

| Actividad | Puntos |
|---|---:|
| Preparación de la tierra | 10 |
| Elaboración del diseño | 10 |
| Ritual de siembra | 10 |
| Siembra | 15 |
| Señalética | 5 |
| Cuidados de crecimiento | 5 |
| Baño de la planta | 5 |
| Ritual de gratitud | 10 |
| Cosecha | 20 |
| Limpieza | 5 |
| Secado | 10 |
| Empaquetado y etiquetado | 15 |
| **Total** | **120** |

Al completar estas actividades, Mateo acumula 120 puntos.

El responsable de Los Aromos lo nombra Maestro porque ha completado el ciclo de cultivo y demuestra experiencia en preparación, siembra, cuidados, cosecha y procesamiento de plantas medicinales.

El nombramiento conserva:

- El participante nombrado.
- El motivo del nombramiento.
- El responsable que realizó el nombramiento.
- La fecha del nombramiento.

## 7. Demostración de las reglas de cultivo y anulación

La planta Menta se utiliza para demostrar la validación de la siembra y la anulación de una actividad.

### 7.1. Intento de siembra antes del plazo

El script intenta registrar una siembra de Menta cuando han transcurrido 14 días desde la preparación de la tierra.

El registro debe rechazarse con el mensaje:

> La siembra requiere una preparación de la tierra al menos 15 días antes.

Esta prueba se realiza durante la ejecución del script y no deja una actividad válida en el historial.

### 7.2. Siembra válida

Después, el script registra una siembra de Menta con la fecha y hora actuales.

Esta actividad suma 15 puntos al participante.

| Momento | Puntos de Mateo |
|---|---:|
| Después del ciclo del Romero | 120 |
| Después de la siembra de Menta | 135 |

### 7.3. Anulación de la siembra

El responsable de Los Aromos anula la última actividad de Menta e indica el motivo de la anulación.

La actividad no se elimina. Se conserva con estado anulado y mantiene el motivo, el autor de la anulación y la fecha correspondiente.

Los puntos de la actividad anulada dejan de contabilizarse.

| Momento | Puntos de Mateo |
|---|---:|
| Antes de la anulación | 135 |
| Después de la anulación | 120 |

Mateo conserva el nombramiento de Maestro porque mantiene los 120 puntos obtenidos con el ciclo activo del Romero.

## 8. Guion para presentar el sistema

### Paso 1. Iniciar sesión como responsable de Los Aromos

Ingresar con:

\`\`\`text
Usuario: demo_responsable_a
Contraseña: R3fugio!Luna_Cedro#72
\`\`\`

Mostrar:

- La comunidad Huerto Medicinal Los Aromos.
- Los miembros registrados.
- El huerto configurado.
- Las plantas seleccionadas.
- La disponibilidad de materiales.

### Paso 2. Revisar el huerto como participante

Cerrar la sesión e ingresar con:

\`\`\`text
Usuario: demo_participante_a
Contraseña: M4nt4!Bosque_Romero#83
\`\`\`

Mostrar:

- El historial de actividades del Romero.
- El avance del ciclo de cultivo.
- Los puntos acumulados.
- El nombramiento de Mateo como Maestro.

### Paso 3. Mostrar la anulación

Volver a ingresar como responsable de Los Aromos.

Abrir el historial de actividades de Menta y localizar la actividad anulada.

Mostrar que conserva el registro y el motivo de la anulación.

Después, ingresar nuevamente como participante y comprobar que los puntos contabilizados son 120 y que el nombramiento de Maestro continúa vigente.

### Paso 4. Comprobar la separación entre comunidades

Primero, obtener el identificador real del huerto de Los Aromos:

\`\`\`bash
.venv/bin/python manage.py shell -c '
from comunidades.models import Huerto

for huerto in Huerto.objects.select_related("comunidad"):
    print(huerto.pk, huerto.comunidad.nombre)
'
\`\`\`

Identificar el ID correspondiente a:

\`\`\`text
Huerto Medicinal Los Aromos
\`\`\`

Cerrar la sesión e ingresar con:

\`\`\`text
Usuario: demo_participante_b
Contraseña: T1erra!Semilla_Menta#65
\`\`\`

En el navegador, intentar acceder a:

\`\`\`text
/actividades/ID_DEL_HUERTO_A/
\`\`\`

Reemplazar \`ID_DEL_HUERTO_A\` por el identificador obtenido anteriormente.

El resultado esperado es una respuesta HTTP 403 o la pantalla de acceso denegado definida por la aplicación.

El participante de La Esperanza no debe poder consultar el huerto de Los Aromos.

Esta comprobación se realiza desde una sesión web. La creación del escenario no sustituye la prueba de autorización.

## 9. Rutas útiles

Las rutas declaradas por la aplicación incluyen:

| Funcionalidad | Ruta |
|---|---|
| Comunidad del usuario | \`/comunidades/\` |
| Huerto del usuario | \`/comunidades/huerto/\` |
| Materiales del huerto | \`/comunidades/huerto/materiales/\` |
| Módulo de actividades | \`/actividades/\` |
| Huerto virtual por identificador | \`/actividades/ID_DEL_HUERTO/\` |
| Historial de un huerto | \`/actividades/ID_DEL_HUERTO/historial/\` |

Las rutas privadas requieren iniciar sesión.

El identificador del huerto puede variar entre instalaciones, por lo que se debe consultar en cada base de datos.

## 10. Copia de seguridad y Git

Después de crear el escenario, el script genera la siguiente copia:

\`\`\`text
copias/demo_huertos.sqlite3
\`\`\`

La copia se valida antes de reemplazar una copia anterior.

La carpeta \`copias/\` está excluida de Git. No se deben subir al repositorio:

- \`db.sqlite3\`.
- \`copias/demo_huertos.sqlite3\`.
- Otras bases de datos locales que contengan información de trabajo.

Sí se deben versionar:

- \`scripts/crear_demo.py\`.
- \`docs/v1/demo.md\`.

Para comprobarlo:

\`\`\`bash
git check-ignore -v copias/demo_huertos.sqlite3
git status --short
\`\`\`

La copia de demostración debe permanecer en cada equipo local y no es necesaria para ejecutar el script en otras máquinas.

## 11. Restaurar la copia de demostración

La copia puede utilizarse para recuperar el escenario sin tener que crearlo nuevamente.

Para restaurarla:

1. Detener el servidor de desarrollo.
2. Cerrar cualquier proceso que esté utilizando la base de datos.
3. Conservar una copia de la base actual si contiene información que se desea mantener.
4. Identificar la ruta configurada en \`DATABASES["default"]["NAME"]\`.
5. Copiar \`copias/demo_huertos.sqlite3\` sobre la base de datos configurada.
6. Iniciar nuevamente el servidor.

Antes de reemplazar una base de datos, verificar la ruta configurada en la aplicación.

No reemplazar una base de datos de trabajo sin tener un respaldo.

## 12. Resultado esperado

Al finalizar la preparación, la base de datos contiene:

| Registro | Cantidad |
|---|---:|
| Usuarios ficticios | 4 |
| Comunidades | 2 |
| Miembros | 4 |
| Huertos | 2 |
| Actividades de Los Aromos | 13 |
| Actividades activas de Los Aromos | 12 |
| Actividades anuladas de Los Aromos | 1 |

El participante Mateo termina con 120 puntos y conserva el nombramiento de Maestro.

El escenario queda preparado para demostrar el historial de cultivo, las reglas de registro, la anulación de actividades y la separación de permisos entre comunidades.