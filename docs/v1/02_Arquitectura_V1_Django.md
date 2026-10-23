# Arquitectura de Software V1 - Huertos Medicinales Comunitarios

**Proyecto:** Calidad de Software (ISWD652 - Período 2026B)  
**Institución:** Escuela Politécnica Nacional (EPN)  
**Grupo:** Nova Alexandria (GR1SW)  
**Coordina este documento:** Doménica Astudillo (arquitectura y diseño, con Bryan y Fernando).  
**Sección del módulo `actividades/`:** aporte de Fernando Alonso Carrera Zambrano (Programador 2).

---

## 1. Visión General de la Arquitectura del Sistema

La solución "Huertos Medicinales Comunitarios" está construida sobre **Django 5.2 LTS** y **Python 3.13**, adoptando un enfoque de **Arquitectura en Capas (Layered Architecture)** con desacoplamiento mediante **Service Layer** y componentes de **Lógica Pura de Dominio**.

```
+-------------------------------------------------------------------------+
|                       Capa de Presentación                             |
|  - Templates Django (HTML5, Bootstrap 5.3, Componentes Reutilizables)   |
|  - Formularios con validación y tokens UUID (forms.py)                 |
|  - Vistas controladoras delgadas (views.py)                             |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                       Capa de Servicios de Negocio                      |
|  - Transacciones atómicas (@transaction.atomic)                         |
|  - Concurrencia y bloqueos pesimistas (select_for_update)              |
|  - Idempotencia estricta, trazabilidad y no-repudio                    |
|  - Orquestación de casos de uso (servicios.py)                          |
+-------------------------------------------------------------------------+
                     /                               \
                    v                                 v
+---------------------------------------+   +-----------------------------+
|        Capa de Reglas Puras           |   |   Capa de Persistencia      |
|  - Funciones puras sin estado         |   |   - Modelos Django (ORM)    |
|  - Fórmulas de progreso e hitos       |   |   - Restricciones Check/Unique  |
|  - Niveles y rangos (reglas.py)       |   |   - FK con PROTECT / CASCADE|
+---------------------------------------+   +-----------------------------+
```

### 1.1 Dependencias Acíclicas entre Módulos
Para garantizar mantenibilidad y evitar dependencias circulares, el proyecto establece una jerarquía estricta:
1. **`cuentas`**: Gestión de usuarios, autenticación y credenciales de acceso.
2. **`catalogo`**: Fichas botánicas de las 18 plantas medicinales, saberes ancestrales y calendario lunar. No depende de ningún otro módulo.
3. **`comunidades`**: Comunidades, huertos físicos y membresías con acumulación de puntos. Depende de `cuentas` y `catalogo`.
4. **`actividades`**: Registro de labores, cálculo de recompensas, anulación auditada, Huerto Virtual y designación del Maestro. Consume los tres módulos anteriores.

> [!IMPORTANT]
> **Regla de oro de acoplamiento:** Los módulos inferiores (`cuentas`, `catalogo`, `comunidades`) **nunca importan ni dependen de `actividades`**. Toda interacción inversa se realiza mediante interfaces abstractas o claves foráneas desde el módulo superior.

---

## 2. Arquitectura Detallada del Módulo `actividades/`

El módulo `actividades/` coordina el registro de trabajo agrícola y ceremonial, la verificación de hitos, la gamificación comunitaria y el liderazgo del huerto. Responde directamente a las historias de usuario **HU-08**, **HU-09**, **HU-10** y **HU-11**.

### 2.1 Modelo de Datos y Restricciones de Persistencia (`actividades/models.py`)

El modelo `Actividad` encapsula la información de cada labor realizada en el huerto con las siguientes decisiones de ingeniería:

```python
class Actividad(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    huerto = models.ForeignKey('comunidades.Huerto', on_delete=models.CASCADE, related_name='actividades')
    tipo = models.CharField(max_length=30, choices=TIPO_ACTIVIDAD_CHOICES)
    planta = models.CharField(max_length=100, blank=True, default='')
    fecha = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='ACTIVA', db_index=True)
    puntos = models.PositiveIntegerField(default=0)
    actor_original = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='actividades_registradas')
    detalles = models.TextField(blank=True, default='')
    
    # Auditoría de anulación
    motivo_anulacion = models.TextField(blank=True, default='')
    autor_anulacion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
```

#### Decisiones de Diseño Críticas:
1. **Control de Idempotencia (`uuid`):** Campo `UUIDField` con restricción de unicidad (`unique=True`) e índice en base de datos (`db_index=True`). Evita duplicación de registros y de puntos ante reenvíos de formularios HTTP o problemas de conexión.
2. **Principio de No-Repudio e Inmutabilidad (`actor_original`):** Clave foránea con `on_delete=models.PROTECT`. Cuando una actividad es anulada, el registro físico se preserva y el `actor_original` permanece inalterado como evidencia de la ejecución histórica.
3. **Auditoría de Anulación:** `motivo_anulacion`, `autor_anulacion` y `fecha_anulacion` permiten determinar exactamente quién revocó la actividad, en qué fecha y bajo qué justificación.
4. **Integridad de Base de Datos:** Restricciones `CheckConstraint` para `puntos__gte=0` y validación de estados admitidos (`ACTIVA`, `ANULADA`).
5. **Ordenamiento Canónico:** `ordering = ['-fecha', '-id']`, garantizando consistencia determinística para desempate de registros realizados en la misma fecha.

---

### 2.2 Capa de Servicios de Negocio (`actividades/servicios.py`)

La capa de servicios aísla completamente la lógica del negocio de las vistas HTTP. Cada servicio opera bajo un contrato transaccional estricto:

#### A. `registrar_actividad(...)`
* **Transaccionalidad:** Ejecutado íntegramente bajo `@transaction.atomic`.
* **Validación de Membresía:** Solo miembros activos de la comunidad propietaria del huerto pueden registrar labores (`PermissionDenied` en caso contrario).
* **Manejo de Idempotencia:**
  * Si el `request_uuid` ya existe y la carga (`huerto`, `tipo`, `planta`, `fecha`) coincide exactamente: retorna la instancia existente sin duplicar filas ni recalcular puntos.
  * Si el `request_uuid` existe con datos diferentes: lanza `ValidationError("El UUID ya fue utilizado con una carga de datos distinta.")`.
  * Si el `request_uuid` pertenece a una actividad en estado `ANULADA`: rechaza con `ValidationError("Una actividad anulada no puede ser reactivada mediante reenvío de UUID.")`.
* **Validación Temporal:**
  * Rechazo inmediato de fechas futuras (`fecha > timezone.localdate()`).
  * Siembra: si la planta tiene preparación activa, no puede ser anterior a ella y debe registrarse hasta 14 días después (el día 15 se rechaza).
  * Secado: exige cosecha activa de la planta, no puede ser anterior a ella y debe registrarse hasta 9 días después (el día 10 se rechaza).
  * Los límites están en `PLAZO_MAX_SIEMBRA_TRAS_PREPARACION` y `PLAZO_MAX_SECADO_TRAS_COSECHA`; las actividades anuladas no cuentan.
* **Cálculo y Acreditación de Recompensas:**
  * Los seis hitos (`preparacion`, `siembra`, `riego`, `cuidado`, `cosecha`, `secado`) dan sus puntos base solo la primera vez para cada planta; repetirlos con otro UUID da **0 puntos** (en riego y cuidado: 5 y luego 0). Si la actividad del hito se anula, el hito vuelve a puntuar al registrarse de nuevo.
  * Las labores que no son hito (`abono`, `asociacion`, `poda`, `control_plagas`, `procesamiento`, `diseno`, `ritual`) dan su puntaje base cada vez.
  * La actualización de puntos del usuario en la comunidad se efectúa con `Miembro.objects.select_for_update()`, bloqueando el registro del miembro durante la transacción para prevenir condiciones de carrera.

#### B. `anular_actividad(...)`
* **Permisos:** Exclusivo para el `actor_original` de la actividad, administradores de la comunidad o el Maestro titular del huerto.
* **Motivo Obligatorio:** Requiere texto explicativo no vacío; rechaza si se envía en blanco.
* **Regla de Ciclo Agrícola (Última Activa):** Solo se permite anular la última actividad activa de esa planta en orden cronológico (`-fecha`, `-id`). Intentar anular una actividad intermedia lanza `ValidationError`.
* **Bloqueo de Preparación:** No se permite anular una preparación de terreno si ya existen siembras activas posteriores registradas para esa planta.
* **Deducción de Puntos:** Resta atómicamente los puntos originalmente otorgados al `actor_original`.
* **Revocación Automática del Maestro (CP-08):** Si la deducción de puntos ocasiona que el puntaje del Maestro actual caiga por debajo del umbral de **100 puntos**, el servicio remueve automáticamente su cargo en el modelo `Huerto`, garantizando el cumplimiento de la regla de elegibilidad.

#### C. `nombrar_o_sustituir_maestro(...)`
* **Permisos:** Reservado para el administrador de la comunidad o su creador.
* **Umbral Mínimo:** El candidato debe poseer un acumulado de $\ge 100$ puntos en la comunidad.
* **Motivo y Auditoría:** Exige justificación y registra autor, fecha y motivo en el modelo `Huerto`.
* **Exclusividad:** Máximo un único Maestro titular simultáneo por huerto.
* **Formulario desactualizado:** el formulario envía en un campo oculto el Maestro que había al abrirse; si otro administrador lo cambió mientras tanto, el servicio rechaza el nombramiento. La fila del huerto se bloquea con `select_for_update()` durante el cambio.

#### D. `obtener_historial_actividades(...)` y `obtener_resumen_huerto(...)`
* Consultas optimizadas con `.select_related('actor_original', 'autor_anulacion')` para prevenir el antipatrón de consultas $N+1$.
* Agregación de hitos cumplidos, cálculo del porcentaje de avance del huerto (0.0% a 100.0%), especies en cultivo sin repetir y nivel del usuario consultante con su avance dentro del nivel.

---

### 2.3 Capa de Reglas Puras (`actividades/reglas.py`)

Diseñada en coordinación técnica con Guillermo Cevallos (Tester). Se trata de un módulo libre de efectos secundarios (*side-effect free*), sin llamadas al ORM ni interacción con base de datos:

#### A. Cálculo de Progreso del Huerto
El ciclo de cultivo medicinal se fundamenta en **6 hitos agrícolas**:
$$\text{Hitos} = \{\text{preparacion}, \text{siembra}, \text{riego}, \text{cuidado}, \text{cosecha}, \text{secado}\}$$
$$\text{Progreso (\%)} = \left( \frac{|\text{Hitos cumplidos} \cap \text{Hitos validos}|}{6} \right) \times 100$$
Retorna un flotante redondeado a un decimal (0.0% a 100.0%).

#### B. Sistema de 5 Niveles del Cultivador
| Rango de Puntos | Nivel | Denominación | Elegible para Maestro |
| :---: | :---: | :--- | :---: |
| 0 – 49 | 1 | Semilla (Aprendiz) | No |
| 50 – 99 | 2 | Brote (Cultivador) | No |
| 100 – 199 | 3 | Guardián (Cuidador) | **Sí** ($\ge 100$) |
| 200 – 299 | 4 | Cosechador (Sabio) | **Sí** |
| 300+ | 5 | Maestro Ancestral | **Sí** |

> [!NOTE]
> Alcanzar 100 puntos o Nivel 5 otorga elegibilidad, pero **no asigna la titularidad de Maestro automáticamente**: el nombramiento requiere decisión administrativa formal.

---

### 2.4 Capa de Presentación (`forms.py`, `views.py`, `templates/`)

* **Controlador Delgado (*Skinny Views*):** Las vistas verifican la autenticación (`@login_required`), reciben la petición HTTP, delegan la lógica a `servicios.py` y retornan respuestas con mensajes flash de éxito o error (`django.contrib.messages`).
* **Protección de Formularios:** `RegistroActividadForm` inyecta en su inicialización un `UUID4` único en un campo oculto (`uuid`), el cual viaja con el formulario para garantizar idempotencia en la persistencia.
* **Componentes Visuales:**
  * `inicio_huerto_virtual.html`: Muestra barra de progreso, tarjetas de estado, métricas de cultivo y estado del Maestro.
  * `registrar_actividad.html`: Formulario estructurado con datalist de especies sugeridas.
  * `historial.html`: Tabla cronológica con filtrado por tipo, especie y estado, indicando badges de `ACTIVA` o `ANULADA`.
  * `anular.html` y `nombrar_maestro.html`: Formularios con confirmación de motivo.

---

## 3. Puntos de Integración y Coordinación con los Integrantes del Equipo

Para dar cumplimiento a los estándares de trabajo colaborativo de la cátedra de Calidad de Software, el módulo de `actividades/` establece interfaces y acuerdos explícitos con cada uno de los integrantes:

### 3.1 Juan Chugá (Coordinador General y Responsable del Informe Oficial)
* **Canal / Documento:** [`docs/v1/aporte_informe_oficial_actividades.md`](aporte_informe_oficial_actividades.md).
* **Entregable aportado:** Redacción académica completa que formaliza las 6 reglas de negocio (`RN-ACT-01` a `RN-ACT-06`), las fórmulas matemáticas de avance sobre los 6 hitos agrícolas, la escala de los 5 niveles del cultivador y el reporte de aseguramiento de calidad para su inclusión en `informe.docx`.

### 3.2 Guillermo Cevallos (Tester / Responsable de Calidad y Pruebas)
* **Canal / Código:** [`actividades/reglas.py`](../../actividades/reglas.py) y `actividades/tests.py` (compartido, con cambios coordinados).
* **Acuerdo y Entregables:**
  * `reglas.py` es de Guillermo (G2). Fernando dejó una versión inicial y le agregó que un hito repetido da 0 puntos; Guillermo revisa y conserva o reemplaza esa versión.
  * `actividades/tests.py` tiene 45 pruebas automáticas de desarrollo. La ejecución formal de CP-05 a CP-08 y la descripción de cómo ejecutar y registrar las pruebas (G3) son de Guillermo.

### 3.3 Matthew Redin (Analista / Responsable del Catálogo de Plantas)
* **Canal / Código:** Función [`obtener_opciones_plantas_medicinales()`](../../actividades/forms.py) en `actividades/forms.py` y `actividades/views.py`.
* **Acuerdo de Integración:** 
  * Se implementó un patrón de diseño **Adaptador con Fallback Seguro**: el formulario de actividades consulta dinámicamente `catalogo.models.Planta` si el modelo y los registros existen en la base de datos.
  * Mientras Matthew completa la consolidación de las 18 fichas botánicas, el sistema opera con la lista estática `ESPECIES_MEDICINALES_18` sin bloquear la funcionalidad. La transición a catálogo dinámico será transparente y automática.

### 3.4 Doménica Astudillo (Diseñadora / Responsable de Interfaz y UX/UI)
* **Canal / Código:** [`static/css/estilos.css`](../../static/css/estilos.css) y [`templates/base.html`](../../templates/base.html).
* **Acuerdo de Integración:**
  * Se configuraron tokens CSS reutilizables con paleta agroecológica (`--primary-green`, `--accent-green`, `--earth-brown`), badges de estado (`.badge-estado-activa`, `.badge-estado-anulada`) y barra de progreso.
  * Bootstrap 5.3.3 y Bootstrap Icons 1.11.3 se sirven desde `static/vendor/` (sin CDN), para que la demo funcione sin internet.
  * Toda la estructura HTML se basó en Bootstrap 5 estándar y componentes modulares (`templates/componentes/errores.html`, `mensajes.html`), permitiendo a Doménica incorporar ajustes de diseño, imágenes o fuentes sin alterar la lógica de las vistas.

### 3.5 Bryan Ayala (Programador 1 / Responsable de Cuentas y Comunidades)
* **Canal / Código:** [`comunidades/models.py`](../../comunidades/models.py) y [`cuentas/models.py`](../../cuentas/models.py).
* **Acuerdo de Integración:**
  * **Pendiente de confirmar con Bryan:** Fernando dejó versiones iniciales de `cuentas/models.py` y `comunidades/models.py` para poder probar su módulo. Si Bryan entrega los suyos, se usan los de Bryan y se ajusta `actividades/`. Se propone mantener en `comunidades.Huerto` los campos para la auditoría y nombramiento del Maestro (`maestro`, `motivo_maestro`, `autor_maestro`, `fecha_maestro`).
  * Los puntos acumulados se vinculan directamente al modelo `comunidades.Miembro`, actualizados atómicamente por `actividades.servicios` con bloqueo `select_for_update()`.

