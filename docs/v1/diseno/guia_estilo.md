# Guía de estilo V1

Autora: Doménica Astudillo. Actualizada el 1 de noviembre de 2026.

Referencia visual de la interfaz: colores, tipografía y qué clases CSS usar en cada tipo de pantalla. Para entender cómo se arma una pantalla y cómo llegan los datos, ver primero el [README de diseño](README.md).

Todos los valores viven en `static/css/estilos.css`, que se carga después de Bootstrap 5.3. Los colores se definen una sola vez en el bloque `:root`: si un color cambia, se cambia solo allí.

**Estilo:** botánico y sereno. Fondo marfil, verde bosque como color principal, salvia para destacar y terracota como acento pequeño (raya bajo los títulos, avisos y pendientes). Títulos con serifa y texto sin serifa.

## 1. Paleta

| Nombre | Variable CSS | Valor | Uso |
|---|---|---|---|
| Marfil | `--marfil` | `#f7f5ef` | Fondo de página |
| Superficie | `--superficie` | `#fbfaf6` | Tarjetas y formularios |
| Verde bosque | `--bosque` | `#244c3a` | Botón principal, enlaces, menú activo |
| Bosque oscuro | `--bosque-oscuro` | `#193e2d` | Botón principal al pasar el cursor |
| Tinta | `--tinta` | `#20382d` | Texto y títulos |
| Salvia | `--salvia` | `#dfe5d3` | Opción activa del menú, bloque destacado, mensaje de éxito |
| Salvia suave | `--salvia-suave` | `#ecefe4` | Fondo al pasar el cursor y fondo de iconos |
| Apagado | `--apagado` | `#5f6866` | Ayudas, subtítulos y etiquetas pequeñas |
| Línea | `--linea` | `#deded5` | Bordes y separadores |
| Borde de campo | `--borde-campo` | `#c8ccc3` | Campos de formulario |
| Terracota | `--terracota` | `#b94d26` | Raya bajo títulos, botón de acento, avisos |
| Durazno | `--durazno` | `#fbe6d6` | Fondo de etiquetas e iconos de acento |
| Error | `--error` | `#a8321f` | Campo con error y resumen de errores |

## 2. Tipografía

- **Títulos:** Playfair Display si está instalada; si no, Georgia.
- **Texto:** DM Sans si está instalada; si no, Segoe UI (Windows) o la fuente del sistema.
- No se cargan fuentes de internet. Si el equipo quiere las fuentes exactas, se pueden guardar en `static/fuentes/` (ambas tienen licencia OFL) y declarar con `@font-face`.

## 3. Iconos

Se usan con `<svg class="icono" aria-hidden="true"><use href="#i-NOMBRE"/></svg>`. Están definidos en `templates/componentes/iconos.html`.

Nombres disponibles: `hoja`, `inicio`, `brote`, `libro`, `calendario`, `comunidad`, `historial`, `persona`, `salir`, `flecha`, `gota`, `check`.

## 4. Clases por tipo de pantalla

### Estructura general

| Componente | Clases | Notas |
|---|---|---|
| Contenedor | `contenido` (760 px) o `contenido contenido-amplio` (1200 px) | Se elige con el bloque `ancho` |
| Título de página | `introduccion` (con `h1` y `p`) | El `h1` lleva una raya terracota debajo |
| Título con acción | `encabezado-pagina` (contiene `introduccion` y un botón) | Por ejemplo «Mi huerto» + «Registrar actividad» |
| Título de sección | `titulo-seccion`, `encabezado-seccion` | Raya terracota; el encabezado admite un enlace a la derecha |
| Bloques en rejilla | `bloques` (con `resumen` dentro), `vacio`, `tarjeta-opcion` | Contacto y código de comunidad, estados vacíos |
| Bloque destacado | `heroe`, `heroe-texto`, `heroe-imagen` (`heroe-imagen-hojas` sin foto) | Texto sobre salvia y foto con esquina curva |
| Enlace de regreso | `volver`, `enlace-flecha` | Flecha de icono |
| Avisos antes de confirmar | `lista-avisos` | Consecuencias o reglas (anular, nombrar Maestro) |

### Acceso (iniciar sesión y crear cuenta)

| Componente | Clases | Notas |
|---|---|---|
| Pantalla dividida | `acceso`, `acceso-foto` (`acceso-foto-hierbas`, `acceso-foto-siembra`), `acceso-panel`, `acceso-interior` | Plantilla `base_acceso.html` |
| Formulario de acceso | `formulario-acceso`, `campo-con-icono`, `boton-ancho`, `pie-acceso`, `lema` | Sin caja: el panel ya es el fondo |

Para usar una foto local en el panel, la pantalla redefine el bloque `foto_estilo`:

```django
{% block foto_estilo %}background-image: url('{% static "img/plantas/romero.jpg" %}'){% endblock %}
```

### Formularios, botones y mensajes

| Componente | Clases | Notas |
|---|---|---|
| Formulario | `formulario`, `campo`, `cuadricula` (`cuadricula-tres`), `ancho-completo`, `ayuda`, `opcional`, `acciones` | El campo con error se resalta solo (Django pone `aria-invalid`) |
| Casillas múltiples | `opciones-multiples` alrededor de un `CheckboxSelectMultiple` | Diseños y abonos como píldoras; la marcada se ve en salvia |
| Botones | `<button>` (principal), `boton-secundario`, `boton-acento`, `boton-enlace`, `boton-pequeno`; `boton` para un enlace con forma de botón | Un solo botón principal por pantalla |
| Mensajes | `alert-success`, `alert-info`, `alert-warning`, `alert-danger` | Los pone `componentes/mensajes.html`; borde izquierdo de color |
| Errores | `errores` | Lo pone `componentes/errores.html`; resumen arriba con enlace a cada campo |
| Filtros | `barra-filtros`, `barra-filtros-acciones` | Una fila de listas; «Quitar filtros» solo si hay alguno activo |

### Tarjetas, resumen y estados

| Componente | Clases | Notas |
|---|---|---|
| Tarjeta | `tarjeta`, `tarjeta-cuerpo`, `tarjeta-pie`, `nombre-cientifico` | La foto ocupa todo el borde superior |
| Rejilla de tarjetas | `rejilla-tarjetas` (`rejilla-plantas`) | 1 columna en celular, 3 o 4 en computador |
| Foto de planta | `foto-planta`, `foto-planta-ficha`, `foto-pendiente`, `foto-miniatura`, `atribucion` | Nunca se deforma la foto |
| Resumen con número | `rejilla-resumen`, `tarjeta tarjeta-resumen`, `resumen-icono` (`resumen-icono-acento`), `resumen-valor`, `resumen-etiqueta` | Icono redondo y número grande |
| Estado | `etiqueta`, `etiqueta-acento`, `etiqueta-neutra`, `etiquetas` | Siempre con texto, no solo color |
| Avance | `avance`, `avance-barra`, `avance-relleno` (con `style="width: N%"`), `avance-texto` | El número siempre visible |
| Lista con bordes | `lista-filas`, `fila`, `fila-texto`, `avatar`, `avatar-pequeno` | Miembros, siguientes acciones |
| Lista de etiquetas | `lista-chips` | Materiales, recomendaciones |

### Catálogo

| Componente | Clases | Notas |
|---|---|---|
| Ficha de planta | `ficha` (foto e identificación), `ficha-secciones`, `ficha-ancha`, `datos-ficha`, `dato` | Un dato sin valor muestra «No verificado» (`componentes/dato_ficha.html`) |
| Precauciones | `precauciones` | Borde y fondo terracota; siempre con su título |
| Fuentes | `lista-fuentes` | Si la fuente no tiene URL (PDF del aula) se muestra el título sin enlace |
| Guía de actividad | `guia`, `guia-encabezado`, `guia-pasos`, `plazo-obligatorio`, `guia-detalles`, `indice-guias` | El plazo obligatorio va destacado; hora y fase son «no obligatorias» |

### Calendario lunar

| Componente | Clases | Notas |
|---|---|---|
| Cabecera del mes | `cabecera-mes`, `boton-mes`, `titulo-mes`, `etiqueta-hora` | Mes anterior y siguiente a cada lado del nombre del mes |
| Vista del mes | `cuadricula-mes`, `dia-con-evento`, `dia-referencia`, `dia-enlace`, `leyenda-fases` | Lunes a domingo; solo se marcan los días con un evento verificado |
| Fase lunar | `luna` + `luna-nueva`, `luna-creciente`, `luna-llena` o `luna-menguante`; `nombre-ancestral` | Círculo dibujado con CSS, siempre con el nombre de la fase |
| Tabla de fases | `tabla-calendario` (con `data-titulo` en cada celda), `fila-referencia` | En celular cada fila se lee como tarjeta |
| Fases cercanas | `formulario-fecha`, `eventos-vecinos`, `evento-vecino` | Indican la fecha de referencia; no son la fase de cada día |

### Comunidad, huerto y materiales

| Componente | Clases | Notas |
|---|---|---|
| Datos de la comunidad | `codigo-invitacion`, `datos-dos-columnas` | Código de invitación destacado |
| Explicación de opciones | `explicacion-opciones` | Desplegable en el configurador |
| Resumen de especie | `seleccion-resumen`, `seleccion-nombre` | Cambiar método y retirar especie |
| Materiales | `grupo-materiales`, `lista-materiales`, `material`, `material-disponible`, `material-formulario` | Casilla y botón por material; la etiqueta repite el estado guardado |
| Acciones en tarjeta | `acciones-tarjeta`, `enlace-acento` | «Retirar» en terracota |

### Actividades y Mi huerto

| Componente | Clases | Notas |
|---|---|---|
| Registro de actividad | `guia-actividades`, `enlace-derecha` | Desplegable con las 13 guías |
| Historial | `tabla-calendario tabla-historial`, `nota-actividad`, `puntos`, `fila-anulada`, `fila-anulacion`, `detalle-anulacion`, `celda-sin-accion` | La anulada se atenúa, con puntos tachados y su motivo, autor y fecha |
| Maestro vigente | `maestro-actual`, `motivo-maestro` | Avatar, nombre, quién lo nombró, fecha y motivo |
| Mi huerto | `accesos-huerto`, `contenido-dividido`, `columna-lateral`, `fila-siguiente`, `resumen-icono-pequeno` | Plantas a la izquierda y siguientes acciones a la derecha; en celular, una debajo de la otra |

## 5. Ejemplo: tarjeta de planta

```django
<article class="tarjeta">
  <img class="foto-planta" src="{% static planta.imagen_ruta %}" alt="{{ planta.nombre_comun }}">
  <div class="tarjeta-cuerpo">
    <h3>{{ planta.nombre_comun }}</h3>
    <p class="nombre-cientifico">{{ planta.nombre_cientifico }}</p>
    <p class="etiquetas"><span class="etiqueta">{{ tarjeta.etapa }}</span></p>
    <div class="avance">
      <span class="avance-barra"><span class="avance-relleno" style="width: {{ tarjeta.progreso }}%"></span></span>
      <span class="avance-texto">{{ tarjeta.progreso }} %</span>
    </div>
  </div>
  <div class="tarjeta-pie"><a href="...">Ver planta</a></div>
</article>
```

Los nombres de variables son los que entrega cada vista; el ejemplo usa los de Mi huerto.
