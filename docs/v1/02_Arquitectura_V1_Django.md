# Arquitectura V1: Huertos medicinales comunitarios (Django)

Borrador de Fernando Carrera para la sección de arquitectura. Doménica coordina este
documento (D3) con Bryan y Fernando; esta versión describe en detalle el módulo
`actividades/` y su relación con los demás.

## 1. Visión general

La aplicación es un proyecto Django 5.2 con SQLite y plantillas del servidor. Cada módulo
separa tres capas:

- **Modelos** (`models.py`): datos y restricciones que la base de datos también protege.
- **Servicios** (`servicios.py`): reglas del dominio, permisos y escrituras atómicas.
- **Vistas y formularios** (`views.py`, `forms.py`): reciben la petición, validan la forma de
  los datos, llaman a los servicios y eligen la plantilla.

Las pantallas son privadas por defecto (`LoginRequiredMiddleware`); solo registro e inicio de
sesión son públicos. Las escrituras usan POST con CSRF. SQLite trabaja en modo de transacción
`IMMEDIATE`, que serializa las escrituras simultáneas.

### 1.1 Dependencias entre módulos

1. `cuentas`: usuario personalizado, registro con consentimiento, sesión y perfil.
2. `catalogo`: plantas, opciones del configurador, materiales y calendario. No depende de nadie.
3. `comunidades`: comunidad con un responsable, miembros, huerto, plantas elegidas y marcas de
   materiales. Usa `cuentas` y `catalogo`.
4. `actividades`: registro, anulación, puntos, Maestro, historial y Huerto Virtual. Usa los tres
   anteriores. Ningún módulo inferior importa `actividades`.

## 2. Módulo `actividades/`

### 2.1 Modelo `Actividad`

| Campo | Tipo | Uso |
| --- | --- | --- |
| `uuid` | UUID único | Identifica cada envío del formulario y evita duplicados. |
| `huerto` | FK a `Huerto` (`PROTECT`) | Huerto donde se hizo la labor. |
| `planta` | FK a `PlantaHuerto` (`PROTECT`, opcional, `related_name="actividades"`) | Planta elegida del huerto; vacía solo en diseño y ritual. |
| `tipo` | Texto con 13 opciones | Actividad realizada. |
| `fecha` | Fecha | Día en que se realizó; no puede ser futura. |
| `estado` | `activa` o `anulada` | Las actividades no se borran. |
| `puntos` | Entero positivo | Puntos otorgados al registrar (0 si repite un hito). |
| `actor_original` | FK a `Usuario` (`PROTECT`) | Quien realizó la labor; no cambia al anular. |
| `detalles` | Texto | Observaciones. |
| `motivo_anulacion`, `anulada_por`, `fecha_anulacion` | Texto, FK y fecha | Constancia de la anulación. |
| `fecha_registro` | Fecha y hora | Momento en que se guardó. |

Restricciones de base de datos:

- `actividad_tipo_valido` y `actividad_estado_valido`: solo valores admitidos.
- `actividad_planta_segun_tipo`: diseño y ritual sin planta; el resto, con planta.
- `actividad_constancia_anulacion`: una actividad activa no tiene datos de anulación y una
  anulada tiene motivo, autor y fecha.

`clean()` comprueba además que la planta pertenezca al mismo huerto.

### 2.2 Servicios (`actividades/servicios.py`)

| Función | Qué hace | Permiso |
| --- | --- | --- |
| `registrar_actividad` | Valida reenvío por UUID, fecha, planta y plazos; calcula puntos; guarda. Devuelve `(actividad, creada)`. | Miembro |
| `anular_actividad` | Valida orden del ciclo y preparación con siembras; guarda la constancia; retira al Maestro si queda bajo 100. Devuelve `(actividad, maestro_retirado)`. | Quien la realizó o el responsable |
| `nombrar_maestro` | Valida formulario desactualizado, pertenencia, 100 puntos y motivo; guarda Maestro y constancia. | Responsable |
| `obtener_historial` | Actividades activas y anuladas con filtros por planta, tipo y estado. | Miembro |
| `obtener_resumen_huerto` | Progreso, tarjetas por planta, totales, puntos, nivel, miembros y Maestro. | Miembro |
| `puntos_de_usuario`, `puntos_por_usuario`, `candidatos_a_maestro` | Consultas de puntos. | Uso interno |

Decisiones de diseño:

1. **Puntos calculados, no guardados.** El total de una persona es la suma de los puntos de sus
   actividades activas. `Miembro` no guarda puntos (contrato de Bryan), y así una anulación no
   puede dejar un saldo desfasado.
2. **Responsable como único administrador.** Se usa `Comunidad.responsable`; no hay un segundo
   rol que pueda contradecirlo. Ser Maestro no concede permisos.
3. **Bloqueo del huerto.** Cada escritura vuelve a leer el huerto con `select_for_update()`
   dentro de `transaction.atomic`, de modo que dos registros o nombramientos simultáneos no
   decidan sobre datos viejos. Si dos envíos con el mismo UUID llegan a la vez, la restricción
   única y el manejo de `IntegrityError` devuelven la misma actividad.
4. **Constancia completa del Maestro.** Los cuatro campos del Maestro en `Huerto` se guardan o se
   vacían juntos, como exige la restricción `huerto_maestro_constancia_completa`.

### 2.3 Reglas puras (`actividades/reglas.py`, Guillermo)

Funciones sin consultas: `calcular_progreso(hitos)`, `calcular_nivel(puntos)` y
`porcentaje_en_nivel(puntos)`. Cinco niveles con límites 0, 50, 100, 200 y 300 puntos; el
progreso es el porcentaje de los seis hitos cumplidos.

### 2.4 Pantallas

| Ruta | Nombre | Pantalla |
| --- | --- | --- |
| `/actividades/` | `mi_huerto` | Lleva al huerto de la comunidad del usuario. |
| `/actividades/<huerto>/` | `inicio_huerto_virtual` | Huerto Virtual. |
| `/actividades/<huerto>/registrar/` | `registrar_actividad` | Registro. |
| `/actividades/<huerto>/historial/` | `historial_actividades` | Historial con filtros. |
| `/actividades/<huerto>/maestro/` | `nombrar_maestro` | Nombramiento (solo responsable). |
| `/actividades/actividad/<id>/anular/` | `anular_actividad` | Confirmación de anulación. |

Una persona ajena a la comunidad recibe 403 en todas, también en las de consulta.

## 3. Coordinación con el equipo

- **Bryan:** `Actividad.planta` cumple el contrato de su README; con la relación inversa,
  `PlantaHuerto.tiene_historial` bloquea el cambio de método y `PROTECT` impide borrar plantas
  con historial (hay pruebas de ambos casos).
- **Guillermo:** dueño de `reglas.py` (puede reemplazarla manteniendo las firmas) y de la
  ejecución formal de CP-05 a CP-08. Comparte `actividades/tests.py`.
- **Matthew:** los plazos (14 y 9 días) y la tabla de puntos deben coincidir con el alcance.
- **Doménica:** estilo final de `templates/actividades/` y enlace «Mi huerto» en el menú.
- **Juan:** recibe `docs/v1/aporte_informe_oficial_actividades.md` para el informe.
