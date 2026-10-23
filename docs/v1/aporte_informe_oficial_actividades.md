# Aporte para el Informe Oficial de Calidad de Software (V1)
## Sección: Módulo de Actividades y Huerto Virtual (HU-08 a HU-11)

**Autor:** Fernando Alonso Carrera Zambrano (Programador 2 - P2)  
**Asignatura:** Calidad de Software (ISWD652 - 2026B), EPN  
**Destinatario:** Juan Chugá (Coordinador del informe oficial - `informe.docx`)

---

> **Instrucciones para Juan:** El siguiente texto puede ser copiado e integrado directamente en las secciones correspondientes del documento `informe.docx` (Capítulo de Diseño de Software, Implementación de Módulos, Reglas de Negocio y Resultados de Pruebas).

---

### 1. Descripción del Módulo y Responsabilidades del Programador 2

El módulo **`actividades/`** constituye el núcleo operativo y funcional del sistema "Huertos Medicinales Comunitarios". Su objetivo es registrar, supervisar y auditar la totalidad de las labores agronómicas y ceremonias ancestrales que los miembros ejecutan en los huertos de sus comunidades, vinculando la actividad física con la gamificación comunitaria (puntos, niveles y distinción de Maestro del Huerto) y la visualización en tiempo real del Huerto Virtual.

#### Historias de Usuario Asignadas e Implementadas:
* **HU-08 (Registro de actividades de cultivo y ancestrales):** Permite a los miembros registrar 13 tipos de labores con trazabilidad del actor original, coherencia de fechas, control de plazos agrícolas y otorgamiento atómico de recompensas.
* **HU-09 (Anulación de actividades y auditoría de ciclo):** Faculta a los autores o administradores a anular actividades erróneas bajo estricta auditoría (motivo, autor, fecha), respetando el principio de orden cronológico del ciclo (solo última activa por planta) y deduciendo atómicamente los puntos otorgados sin borrar al actor original.
* **HU-10 (Historial de actividades y Huerto Virtual):** Provee una vista de tablero consolidado con el porcentaje de avance sobre los 6 hitos agrícolas, plantas cultivadas, nivel del miembro y tabla histórica con filtrado dinámico.
* **HU-11 (Nombramiento, sustitución y revocación del Maestro del Huerto):** Gestiona la designación administrativa del líder tradicional del huerto bajo un umbral de elegibilidad ($\ge 100$ puntos) y contempla la revocación automática de la distinción en caso de que una anulación reduzca su puntaje por debajo del umbral mínimo.

---

### 2. Formulación Formal de las Reglas de Negocio

Para asegurar los atributos de calidad de **consistencia, integridad y no-repudio**, el módulo implementa las siguientes reglas de negocio en la capa de servicios (`actividades/servicios.py`) y reglas puras (`actividades/reglas.py`):

#### RN-ACT-01: Membresía y Autorización
Solo los usuarios registrados como miembros activos de la comunidad propietaria del huerto pueden registrar actividades, consultar el historial detallado o anular labores. Cualquier intento de acceso por parte de usuarios ajenos genera un rechazo con excepción `PermissionDenied`.

#### RN-ACT-02: Idempotencia Estricta por UUID
Para neutralizar la duplicación de actividades o de puntos ocasionada por reenvíos de formularios HTTP o reintentos de red:
1. Toda petición de creación porta un identificador `UUIDv4` único indexado en base de datos.
2. Si el sistema recibe una solicitud con un UUID preexistente y la carga de datos (`huerto`, `tipo`, `planta`, `fecha`) es idéntica, la operación retorna el registro existente sin duplicar registros ni volver a acreditar puntos.
3. Si el UUID ya fue utilizado con una carga de datos distinta, la operación se rechaza con `ValidationError`.
4. Si el UUID pertenece a una actividad previamente anulada, se rechaza la reactivación artificial.

#### RN-ACT-03: Temporalidad y Coherencia Agrícola
1. **Fechas no futuras:** No se admiten registros con `fecha > fecha_actual`.
2. **Siembra tras la preparación:** si la planta tiene una preparación activa, la siembra no puede tener fecha anterior a ella y debe registrarse hasta 14 días después (el día 14 se acepta y el 15 se rechaza). Si la planta no tiene preparación, la siembra no se bloquea por plazo.
3. **Secado tras la cosecha:** el secado exige una cosecha activa de la misma planta, no puede tener fecha anterior a ella y debe registrarse hasta 9 días después (el día 9 se acepta y el 10 se rechaza).
4. Los dos límites están en las constantes `PLAZO_MAX_SIEMBRA_TRAS_PREPARACION` y `PLAZO_MAX_SECADO_TRAS_COSECHA` de `actividades/servicios.py`. Las actividades anuladas no cuentan para los plazos.

#### RN-ACT-04: Recompensas sin duplicar hitos
* Puntos base: Preparación 10, Siembra 15, Riego 5, Cuidado 5, Cosecha 20, Secado 15, Procesamiento 10, Diseño 10, Ritual 10; Abono, Asociación, Poda y Control de plagas 5.
* Los seis hitos (preparación, siembra, riego, cuidado, cosecha y secado) dan sus puntos solo la primera vez para cada planta del huerto; repetirlos con otro UUID da **0 puntos**. Para riego y cuidado esto equivale a la regla 5/0.
* Si la actividad que cumplió el hito se anula, el hito vuelve a dar puntos cuando se registra de nuevo.
* Las labores que no son hito mantienen su puntaje cada vez que se registran.

#### RN-ACT-05: Anulación Controlada y Trazabilidad del Actor Original
1. **Inmutabilidad del Actor:** El campo `actor_original` está protegido con `models.PROTECT`. La anulación no elimina el registro de la base de datos ni altera al autor original; únicamente conmuta el estado a `'ANULADA'`.
2. **Auditoría obligatoria:** La anulación exige registrar de manera atómica el `motivo_anulacion` (texto no vacío), el `autor_anulacion` (usuario autenticado) y la `fecha_anulacion` (marca de tiempo del sistema).
3. **Regla de Ciclo Agrícola:** Solo se permite anular la última actividad activa registrada cronológicamente para una planta medicinal. En caso de que existan múltiples labores en la misma fecha, el desempate se resuelve de forma determinística por el identificador descendente (`-id`).
4. **Bloqueo de Preparación:** No se puede anular la preparación de terreno si ya existen siembras activas posteriores registradas para esa especie.

#### RN-ACT-06: Gestión del Maestro del Huerto (Nombramiento y Retiro Automático)
1. **Designación administrativa:** Exclusiva de usuarios con rol `ADMIN` en la comunidad.
2. **Umbral de mérito:** El candidato debe contar con al menos **100 puntos** acumulados en la comunidad (equivalente a Nivel 3 o superior).
3. **Unicidad:** Solo puede existir un único Maestro activo por huerto. La designación de un nuevo Maestro sustituye al anterior con auditoría de fecha, autor y motivo.
4. **Retiro Automático:** Si una actividad registrada por el Maestro titular es anulada y la deducción de puntos reduce su saldo total a menos de 100 puntos, el sistema retira automáticamente su designación de Maestro en el modelo `Huerto`.
5. **Formulario desactualizado:** el formulario guarda en un campo oculto qué Maestro había al abrirse. Si otro administrador cambió al Maestro mientras tanto, el nombramiento se rechaza y se pide revisar el estado actual.
6. **Sin nombramiento automático:** alcanzar 300 puntos no nombra Maestro ni da permisos de administración.

---

### 3. Fórmulas de Cálculo de Progreso y Rangos

#### A. Porcentaje de Progreso del Huerto (6 Hitos)
El avance del ciclo agronómico en el Huerto Virtual no depende de la cantidad bruta de labores, sino del cumplimiento de los **6 hitos esenciales de cultivo**:
$$\text{Hitos} = \{\text{preparacion}, \text{siembra}, \text{riego}, \text{cuidado}, \text{cosecha}, \text{secado}\}$$
$$\text{Progreso} = \left( \frac{\text{Número de hitos completados}}{6} \right) \times 100\%$$
*Rango:* $0.0\%$ a $100.0\%$, redondeado a un decimal.

#### B. Escala de Niveles Comunitarios
| Nivel | Rango de Puntos | Denominación Ancestral | Condición Especial |
| :---: | :---: | :--- | :--- |
| **1** | 0 – 49 pts | Semilla (Aprendiz) | En etapa de iniciación. |
| **2** | 50 – 99 pts | Brote (Cultivador) | Participación activa continua. |
| **3** | 100 – 199 pts | Guardián (Cuidador) | **Elegible para nombramiento como Maestro.** |
| **4** | 200 – 299 pts | Cosechador (Sabio) | Dominio integral de labores y saberes. |
| **5** | 300+ pts | Maestro Ancestral | Máximo reconocimiento honorífico; no nombra Maestro por sí solo. |

---

### 4. Comprobaciones de desarrollo (pruebas automáticas)

Durante octubre se escribieron **45 pruebas automáticas** en `actividades/tests.py`. Son comprobaciones de desarrollo: la ejecución formal de los casos CP-05 a CP-08 la realiza Guillermo del 1 al 4 de noviembre y sus resultados reales se registran en `docs/v1/resultados.md`.

Se ejecutan con:

```
python manage.py test actividades
```

Qué cubren, según el caso al que apoyan:

* **CP-05 (Actividades y fechas):** los 13 tipos, fecha futura, siembra 14/15 días tras la preparación, secado 9/10 días tras la cosecha, siembra o secado con fecha anterior, empate por `id` y cuidado después de la cosecha.
* **CP-06 (Reenvíos y puntos):** mismo UUID y misma carga, carga distinta, anulado no reactivado, otro UUID no duplica hito, regla 5/0 en riego y cuidado, y usuarios ajenos bloqueados.
* **CP-07 (Anulaciones):** última activa por planta, preparación con siembras bloqueada, diseño y ritual independientes, auditoría de motivo, autor y fecha, actor original intacto, y puntos correctos al anular y volver a registrar.
* **CP-08 (Maestro):** umbral de 100 puntos, motivo, permiso de administrador, sustitución, formulario desactualizado, retiro bajo 100 y 300 puntos sin nombramiento automático.
* **HU-10 (Huerto Virtual):** plantas sin repetir, avance dentro del nivel y barra de progreso con punto decimal.
