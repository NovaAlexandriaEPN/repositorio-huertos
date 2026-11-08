# Diseño de la interfaz V1

Autora: Doménica Astudillo (diseñadora). Actualizado el 1 de noviembre de 2026.

Este documento explica **cómo está construida la interfaz** de Huertos medicinales comunitarios: qué archivos la forman, cómo llegan los datos a cada pantalla, qué pantallas existen y qué se comprobó. Es el punto de entrada de todo lo que corresponde al diseño (tareas D1 a D3 del plan).

## Contenido de esta carpeta

| Archivo | Para qué sirve |
|---|---|
| `README.md` | Este documento: estructura, pantallas, recorrido, bocetos y comprobación |
| [guia_estilo.md](guia_estilo.md) | Referencia visual: colores, tipografía y clases CSS por tipo de pantalla |
| [fotos_plantas.md](fotos_plantas.md) | Las 18 fotos del catálogo: autor, licencia, fuente y cómo se muestra el crédito |
| `01_iniciar_sesion.png`, `02_crear_cuenta.png`, `03_mi_huerto.png` | Bocetos que guiaron el diseño (sección 6) |
| `mi_huerto_aplicacion.png`, `ficha_planta_aplicacion.png` | Capturas finales de las pantallas, usadas en el README y el informe (sección 8) |
| `actualizar_fotos_base.py` | Corrige los datos de foto en una base SQLite cargada antes del 25 de octubre |

Índice:

1. [Principios](#1-principios)
2. [Cómo está armada una pantalla](#2-cómo-está-armada-una-pantalla)
3. [Menú y rutas](#3-menú-y-rutas)
4. [Mapa de pantallas](#4-mapa-de-pantallas)
5. [Recorrido del usuario](#5-recorrido-del-usuario)
6. [Bocetos y ajustes al alcance](#6-bocetos-y-ajustes-al-alcance)
7. [Fotos de las plantas](#7-fotos-de-las-plantas)
8. [Comprobación](#8-comprobación)
9. [Cómo hacer cambios frecuentes](#9-cómo-hacer-cambios-frecuentes)

## 1. Principios

- **Funciona sin internet.** Bootstrap 5.3.8 está guardado en `static/vendor/bootstrap/`; las fuentes son del sistema y las fotos están en `static/img/plantas/`. No se carga nada de otros sitios.
- **Sin JavaScript.** Todo funciona con enlaces y formularios normales. El menú de la cuenta se abre con `<details>` y cerrar sesión es un formulario POST con CSRF.
- **La plantilla solo muestra.** Puntos, nivel, estado, porcentajes y permisos los calculan las vistas y servicios de cada módulo. La plantilla no repite esos cálculos ni oculta un permiso como única protección: el servidor también rechaza lo que no corresponde.
- **Texto antes que color.** Los estados, niveles y avisos siempre tienen texto; el color solo acompaña.
- **Celular incluido.** Cada pantalla se lee a 375 px de ancho sin desplazamiento lateral.
- **Caracteres estándar.** Se usa guion `-`, tres puntos `...` y `x` (no raya, elipsis ni signo de multiplicación), como se acordó en el equipo.

## 2. Cómo está armada una pantalla

### Dos plantillas base

| Plantilla | Se usa en | Cómo se ve |
|---|---|---|
| `templates/base.html` | Todas las pantallas con sesión iniciada | Barra lateral a la izquierda (marca, menú con iconos y la cuenta abajo) y contenido a la derecha. En celular la barra pasa a ser una cabecera con el menú desplazable |
| `templates/base_acceso.html` | Iniciar sesión y crear cuenta | Pantalla dividida: panel verde con una frase grande a la izquierda y el formulario a la derecha. En celular el panel queda arriba |

`base_acceso.html` hereda de `base.html` y reemplaza solo el cuerpo de la página, así que ambas comparten los estilos, los iconos y los mensajes.

### Bloques que define cada pantalla

| Bloque | Plantilla | Para qué |
|---|---|---|
| `titulo` | `base.html` | Texto de la pestaña del navegador |
| `contenido` | ambas | El contenido propio de la pantalla |
| `ancho` | `base.html` | `contenido` (760 px, formularios) o `contenido contenido-amplio` (1200 px, pantallas con tarjetas o tablas) |
| `foto_clase`, `foto_titulo`, `foto_texto`, `foto_estilo` | `base_acceso.html` | Imagen y frase del panel izquierdo |
| `encabezado`, `pie` | `base_acceso.html` | Título sobre el formulario y enlaces debajo |

### Cómo llegan los datos a la pantalla

```text
Navegador -> urls.py -> vista (views.py) -> servicio (servicios.py) -> base de datos
                             |
                             v
              render(plantilla, contexto) -> HTML que ve el usuario
```

1. La **vista** del módulo (Bryan, Juan, Matthew o Fernando) recibe la petición, comprueba la sesión y los permisos, y llama a su servicio.
2. La vista entrega a la plantilla un **contexto**: un diccionario con los datos ya calculados (por ejemplo `planta`, `tarjetas`, `form`).
3. La **plantilla** recorre esos datos y los muestra con el diseño. No consulta la base ni decide reglas.
4. Si hay un formulario, la vista lo entrega con el nombre `form`. Si el envío es inválido, la vista vuelve a mostrar la misma plantilla con lo escrito y los errores; si es válido, redirige y deja un mensaje de resultado.

### Componentes compartidos (`templates/componentes/`)

| Archivo | Qué hace | Dónde se usa |
|---|---|---|
| `mensajes.html` | Muestra los mensajes de Django («Actividad registrada...») como alertas de color | En las dos plantillas base, una sola vez |
| `errores.html` | Resumen de errores del formulario, con enlace a cada campo; el campo con error se resalta solo | Todas las pantallas con formulario |
| `iconos.html` | Iconos de línea propios, dibujados en SVG, sin descargas | En las dos plantillas base |
| `enlace_menu.html` | Una opción del menú; se marca activa en su pantalla y se desactiva si la ruta no existe | `base.html` |
| `aviso_datos.html` | Texto completo del aviso de uso de datos | Crear cuenta y perfil |
| `dato_ficha.html` | Un dato de la ficha de planta; sin valor muestra «No verificado» | Ficha de planta |
| `opciones_huerto.html` | Explicación desplegable de cada opción del configurador | Configurar huerto |
| `seleccion_resumen.html` | Foto, nombre y método actual de una especie del huerto | Cambiar método y retirar especie |

### Filtros de presentación

`catalogo/templatetags/presentacion.py` (se carga con `{% load presentacion %}`) solo separa o nombra textos ya guardados para mostrarlos; no calcula reglas:

| Filtro | Ejemplo | Uso |
|---|---|---|
| `lineas` | instrucciones -> un paso por línea | Guía de actividades |
| `elementos` | «a; b; c.» -> lista | Materiales de la guía |
| `licencia` | «CC BY-SA 4.0 - https://...» -> nombre y enlace | Crédito de la foto en la ficha |
| `nombre_mes` | `12` -> «Diciembre» | Calendario |
| `cuadricula_mes` | eventos del mes -> semanas de lunes a domingo | Vista del mes del calendario |

### Estilos

`static/css/estilos.css` se carga después de Bootstrap. Los colores se definen una sola vez al inicio (bloque `:root`) y el resto del archivo está ordenado por secciones: acceso, menú, formularios, tarjetas, catálogo, calendario, actividades, Mi huerto, comunidad y celular. El detalle está en [guia_estilo.md](guia_estilo.md).

## 3. Menú y rutas

El menú está en `templates/base.html`. Cada opción es una línea con el nombre de la ruta de Django; se marca activa en su pantalla y en las rutas que se indican en «también activa en».

| Opción | Ruta | También activa en | Autor de la vista |
|---|---|---|---|
| Mi huerto | `actividades:mi_huerto` | `actividades:inicio_huerto_virtual`, `actividades:registrar_actividad` | Fernando |
| Plantas del huerto | `comunidades:mi_huerto` | configurar huerto, elegir, cambiar método, retirar | Bryan |
| Materiales | `comunidades:materiales` | - | Juan |
| Catálogo | `catalogo:lista_plantas` | `catalogo:detalle_planta` | Matthew |
| Guías | `catalogo:guia` | - | Matthew |
| Calendario | `catalogo:calendario` | - | Matthew |
| Mi comunidad | `comunidades:mi_comunidad` | crear, unirse, editar | Bryan |
| Historial | `actividades:mi_historial` | - | Fernando |

Abajo, el menú de la cuenta tiene «Mi perfil» (`cuentas:perfil`) y «Cerrar sesión» (`cuentas:logout`, por POST). Sin sesión solo se ofrecen «Iniciar sesión» y «Crear cuenta».

## 4. Mapa de pantallas

| Pantalla | Dirección | Plantilla | Vista (autor) | Qué muestra |
|---|---|---|---|---|
| Iniciar sesión | `/cuentas/login/` | `cuentas/login.html` | Bryan | Usuario y contraseña; enlace a crear cuenta |
| Crear cuenta | `/cuentas/registro/` | `cuentas/registro.html` | Bryan | Perfil, datos para entrar, aviso de datos completo y casilla sin marcar |
| Mi perfil | `/cuentas/perfil/` | `cuentas/perfil.html` | Bryan | Datos propios editables y consentimiento registrado |
| Mi comunidad | `/comunidades/` | `comunidades/mi_comunidad.html` | Bryan | Contacto, código de invitación y miembros; sin comunidad, crear o unirse |
| Crear y editar comunidad | `/comunidades/crear/`, `/comunidades/editar/` | `comunidades/formulario.html` | Bryan | Nombre, tipo y contacto del responsable |
| Unirse | `/comunidades/unirse/` | `comunidades/unirse.html` | Bryan | Código de invitación |
| Plantas del huerto | `/comunidades/huerto/` | `comunidades/mi_huerto.html` | Bryan | Configuración del huerto y especies elegidas |
| Configurar huerto | `/comunidades/huerto/configurar/` | `comunidades/configurar_huerto.html` | Bryan | Ubicación, área, diseños, cerca, suelo, agua y abonos |
| Elegir, cambiar método, retirar | `/comunidades/huerto/plantas/...` | `elegir_planta.html`, `cambiar_metodo.html`, `retirar_planta.html` | Bryan | Especie y método; aviso si tiene historial |
| Materiales | `/comunidades/huerto/materiales/` | `comunidades/materiales.html` | Juan | Materiales por grupo con su casilla «Disponible» y la recomendación de bodega |
| Catálogo | `/catalogo/plantas/` | `catalogo/lista_plantas.html` | Matthew | Tarjetas con foto, nombres, cualidad y ciclo |
| Ficha de planta | `/catalogo/plantas/<codigo>/` | `catalogo/detalle_planta.html` | Matthew | Foto con crédito, identificación, distribución, usos, precauciones y fuentes |
| Guía de actividades | `/catalogo/guia/` | `catalogo/guia.html` | Matthew | Las 13 actividades con plazo obligatorio, pasos, materiales y recomendaciones |
| Calendario lunar | `/catalogo/calendario/` | `catalogo/calendario.html` | Matthew | Vista del mes, tabla de fases en hora de Guayaquil y fases cercanas a una fecha |
| Mi huerto | `/actividades/<huerto>/` | `actividades/inicio_huerto_virtual.html` | Fernando | Avance, puntos, plantas con su estado, siguientes acciones, Maestro y puntos por miembro |
| Registrar actividad | `/actividades/<huerto>/registrar/` | `actividades/registrar_actividad.html` | Fernando | Actividad, planta cuando corresponde, fecha y hora, observaciones y UUID oculto |
| Historial | `/actividades/<huerto>/historial/` | `actividades/historial.html` | Fernando | Filtros y tabla; las anuladas con motivo, autor y fecha |
| Anular actividad | `/actividades/actividad/<id>/anular/` | `actividades/anular.html` | Fernando | Registro a anular, consecuencias y motivo |
| Maestro del huerto | `/actividades/<huerto>/maestro/` | `actividades/nombrar_maestro.html` | Fernando | Reglas, Maestro vigente, candidatos con 100 puntos o más y motivo |

## 5. Recorrido del usuario

1. **Iniciar sesión** -> el sistema abre **Mi perfil**, que tiene el enlace «Continuar a mi comunidad». Desde iniciar sesión, «Crear una cuenta» lleva al registro, y al registrarse se vuelve a iniciar sesión con el mensaje «Tu cuenta se ha creado. Ya puedes iniciar sesión.».
2. **Sin comunidad**, Mi comunidad ofrece crear una o unirse con un código. Quien crea la comunidad es su responsable.
3. **El responsable** configura el huerto y elige las especies en «Plantas del huerto».
4. **Mi huerto** muestra cada planta con su estado y siguiente acción. «Registrar actividad» abre el formulario; al guardar, el sistema muestra el resultado en el historial.
5. **Historial** lista todo lo registrado; el responsable puede **anular** con motivo y nombrar al **Maestro** desde Mi huerto.
6. **Catálogo, guía y calendario** son de consulta: cada ficha tiene enlace de regreso y la guía se abre desde el registro de actividad.
7. **Materiales** se marcan como disponibles para toda la comunidad.

## 6. Bocetos y ajustes al alcance

| Boceto | Pantalla | Plantilla que orientó |
|---|---|---|
| `01_iniciar_sesion.png` | Iniciar sesión, pantalla dividida | `cuentas/login.html` sobre `base_acceso.html` |
| `02_crear_cuenta.png` | Crear cuenta (formulario representativo) | `cuentas/registro.html` + `componentes/errores.html` |
| `03_mi_huerto.png` | Mi huerto con barra lateral, bloque destacado, resumen, plantas y columna lateral | `actividades/inicio_huerto_virtual.html` |

Los bocetos muestran la estructura visual. Al construir las pantallas reales se ajustaron a las reglas del alcance V1:

- **Acceso con usuario, no con correo.** No hay «Recordarme» ni «¿Olvidaste tu contraseña?»: la recuperación por correo está fuera de V1.
- **Crear cuenta usa los campos reales** del formulario de Bryan. El género no es obligatorio («Prefiero no indicarlo»); «Participación recomendada desde los 14 años» es solo un aviso y no bloquea a un menor; el aviso de datos se lee completo y la casilla aparece sin marcar.
- **Mi huerto:**
  - el botón principal es «Registrar actividad» (las especies las elige el responsable en el configurador);
  - no hay buscador, notificaciones, «Bitácora» ni «Configuración»: el menú usa las secciones del proyecto;
  - el resumen muestra avance del huerto, puntos y nivel, plantas en cultivo y actividades;
  - la columna lateral muestra **siguientes acciones** que entrega la vista, no una lista de tareas para marcar;
  - las etiquetas del boceto («Riego hoy», «Saludable») se reemplazan por los estados del alcance: planeada, sembrada, creciendo, cosechada, secando y empacada.
- **Niveles del alcance:** Aprendiz (0-99), Oficial (desde 100) y Maestro (nombrado por el responsable). Sin Maestro se lee «Sin maestro nombrado».
- **Avance del huerto:** promedio de las plantas sobre seis hitos, con su número; sin plantas, 0 %.
- **Fotos:** las ilustraciones del boceto se reemplazaron por las fotos del catálogo con su autor, licencia y fuente.
- **Sin recursos de internet:** la propuesta visual original usaba fotos de Unsplash y fuentes de Google; se reemplazaron por fotos locales, una ilustración en línea y fuentes del sistema.

## 7. Fotos de las plantas

Las 18 especies tienen foto en `static/img/plantas/<codigo>.jpg`, reducida a 1200 px de lado mayor. Cada ficha guarda `imagen_ruta`, `imagen_autor`, `imagen_fuente` e `imagen_licencia`, y la ficha muestra debajo de la foto el autor, la licencia con su enlace, la fuente y la nota «copia reducida». El detalle de cada foto está en [fotos_plantas.md](fotos_plantas.md).

## 8. Comprobación

Comprobación de desarrollo del 1 de noviembre de 2026 (no es un resultado formal; los casos CP-01 a CP-10 se registran en `docs/v1/resultados.md`):

1. **Pruebas automáticas:** `python manage.py test` -> 188 pruebas correctas.
2. **Enlaces:** un script temporal entró con una cuenta responsable y otra participante y siguió todos los enlaces internos: 59 y 35 páginas, ninguna con error.
3. **Formularios en el navegador**, con datos ficticios: crear cuenta (con errores y válida), iniciar y cerrar sesión, crear comunidad, configurar huerto, elegir y retirar especie, marcar material, registrar actividad (inválida y válida), anular y nombrar Maestro.
4. **Celular:** cada pantalla a 375 px, sin desplazamiento lateral.

| Pantallas | Autor de la vista | Conectadas | Observación |
|---|---|---|---|
| Cuentas | Bryan | Sí | Cierre de sesión por POST |
| Comunidad y configurador | Bryan | Sí | Los puntos de cada miembro se ven en Mi huerto: el módulo de comunidades no consulta actividades |
| Materiales | Juan | Sí | Marca compartida por la comunidad |
| Catálogo, ficha, guía y calendario | Matthew | Sí | 18 fichas con foto y crédito |
| Actividades y Mi huerto | Fernando | Sí | UUID conservado ante error; anuladas visibles |

**Capturas finales (D4-03):** `mi_huerto_aplicacion.png` y `ficha_planta_aplicacion.png`, tomadas el 7 de noviembre de 2026 con la base de demostración. Se muestran en el README del proyecto y en el informe.

## 9. Cómo hacer cambios frecuentes

| Quiero... | Dónde |
|---|---|
| Cambiar un color | Bloque `:root` al inicio de `static/css/estilos.css` |
| Agregar una opción al menú | Una línea `{% include "componentes/enlace_menu.html" with ruta="..." texto="..." icono="..." %}` en `templates/base.html` |
| Crear una pantalla nueva | Una plantilla que empiece con `{% extends "base.html" %}` y defina los bloques `titulo` y `contenido`; para tarjetas o tablas, `{% block ancho %}contenido contenido-amplio{% endblock %}` |
| Mostrar los errores de un formulario | `{% include "componentes/errores.html" with form=form %}` antes del `<form>` |
| Usar un icono | `<svg class="icono" aria-hidden="true"><use href="#i-hoja"/></svg>` (nombres en [guia_estilo.md](guia_estilo.md)) |
| Cambiar la foto de una planta | Reemplazar `static/img/plantas/<codigo>.jpg` y actualizar las cuatro claves de imagen en su ficha de `catalogo/datos/` |
