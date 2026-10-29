# Guía de estilo V1

Autora: Doménica Astudillo. Resume cómo se ven las pantallas y qué clases usar. Los valores viven en `static/css/estilos.css` (bloque `:root`); si un color cambia, se cambia solo allí.

Estilo: botánico y sereno. Fondo marfil, verde bosque como color principal, salvia para destacar y terracota como acento pequeño (rayas bajo los títulos, pendientes). Títulos con serifa, texto sans.

## Paleta

| Nombre | Variable CSS | Valor | Uso |
|---|---|---|---|
| Marfil | `--marfil` | `#f7f5ef` | Fondo de página |
| Superficie | `--superficie` | `#fbfaf6` | Tarjetas y formularios |
| Verde bosque | `--bosque` | `#244c3a` | Botón principal, enlaces, menú activo |
| Bosque oscuro | `--bosque-oscuro` | `#193e2d` | Hover del principal |
| Tinta | `--tinta` | `#20382d` | Texto y títulos |
| Salvia | `--salvia` | `#dfe5d3` | Opción activa del menú, bloque destacado, mensaje de éxito |
| Salvia suave | `--salvia-suave` | `#ecefe4` | Hover y fondo de iconos |
| Apagado | `--apagado` | `#5f6866` | Ayudas, subtítulos y etiquetas |
| Línea | `--linea` | `#deded5` | Bordes y separadores |
| Terracota | `--terracota` | `#b94d26` | Raya bajo títulos, pendientes, botón de acento |
| Durazno | `--durazno` | `#fbe6d6` | Fondo de etiquetas e iconos de acento |
| Error | `--error` | `#a8321f` | Campo con error y resumen de errores |

## Tipografía

- **Títulos:** Playfair Display si está instalada; si no, Georgia.
- **Texto:** DM Sans si está instalada; si no, Segoe UI (Windows) o la fuente del sistema.
- No se cargan fuentes de Google ni de otro sitio: la demo debe funcionar sin internet (D1-02). Si el equipo quiere las fuentes exactas, se pueden guardar en `static/fuentes/` (ambas tienen licencia OFL) y declarar con `@font-face`.

## Estructura de pantallas

| Pantalla | Plantilla base | Cómo se ve |
|---|---|---|
| Iniciar sesión, crear cuenta | `base_acceso.html` | Dividida: panel verde con frase grande a la izquierda y formulario centrado a la derecha. En celular el panel queda arriba como franja |
| Todas las demás (con sesión) | `base.html` | Barra lateral con marca, «Mi espacio», menú con iconos y la cuenta abajo. En celular la barra pasa a ser una cabecera y el menú se desplaza de lado |

Panel de imagen del acceso: mientras no haya fotos locales muestra una ilustración de hojas sobre verde bosque (`acceso-foto-hierbas` y `acceso-foto-siembra`). Para usar una foto del catálogo, la pantalla redefine el bloque `foto_estilo`:

```django
{% block foto_estilo %}background-image: url('{% static "img/plantas/romero.jpg" %}'){% endblock %}
```

La foto debe tener su autor, licencia y fuente como las del catálogo (D2-01).

## Componentes y clases

| Componente | Clases | Notas |
|---|---|---|
| Contenedor | `contenido` (760 px) o `contenido contenido-amplio` (1200 px) | Las pantallas con tarjetas redefinen `{% block ancho %}` |
| Título de página | `introduccion` (con `h1` y `p`) | El `h1` lleva una raya terracota debajo |
| Título con acción | `encabezado-pagina` > `introduccion` + botón | Por ejemplo «Mi huerto» + «Registrar actividad» |
| Bloque destacado | `heroe`, `heroe-texto`, `heroe-imagen` | Texto sobre salvia y foto con esquina curva |
| Iconos | `<svg class="icono"><use href="#i-NOMBRE"/></svg>` | hoja, inicio, brote, libro, calendario, comunidad, historial, persona, salir, flecha, gota, check |
| Formulario | `formulario`, `campo`, `cuadricula`, `ancho-completo`, `ayuda`, `opcional`, `acciones` | El campo con error se resalta solo (Django pone `aria-invalid`) |
| Formulario de acceso | `formulario-acceso`, `campo-con-icono`, `boton-ancho`, `pie-acceso`, `lema` | Sin caja: el panel ya es el fondo |
| Botones | `<button>` (principal), `boton-secundario`, `boton-acento`, `boton-enlace`; `boton` para un enlace con forma de botón | Un solo botón principal por pantalla |
| Mensajes | `componentes/mensajes.html` → `alert-success`, `alert-info`, `alert-warning`, `alert-danger` | Borde izquierdo de color |
| Errores | `componentes/errores.html` | Resumen arriba con enlace a cada campo |
| Tarjeta | `tarjeta`, `tarjeta-cuerpo`, `tarjeta-pie`, `nombre-cientifico` | Borde fino, esquinas de 8 px |
| Rejilla de tarjetas | `rejilla-tarjetas` | 1 columna en celular, 3-4 en computador |
| Foto de planta | `foto-planta` (tarjeta, 150 px de alto, recortada), `foto-planta-ficha` (ficha, sin recorte) + `atribucion` | Nunca se deforma la foto |
| Resumen | `rejilla-resumen`, `tarjeta tarjeta-resumen`, `resumen-icono` (`resumen-icono-acento`), `resumen-valor`, `resumen-etiqueta` | Icono redondo y número grande |
| Estado | `etiqueta` (salvia) o `etiqueta etiqueta-acento` (durazno) | Siempre con texto, no solo color |
| Avance | `avance`, `avance-barra`, `avance-relleno` (con `style="width: N%"`), `avance-texto` | El número siempre visible |
| Lista con bordes | `lista-filas`, `fila`, `fila-texto` | Actividades recientes, historial |
| Ficha de planta | `ficha` (foto + identificación), `ficha-secciones` (bloques), `ficha-ancha`, `datos-ficha` + `componentes/dato_ficha.html` | Un dato sin valor muestra «No verificado» |
| Precauciones | `precauciones` | Borde y fondo terracota; siempre con su título visible |
| Fuentes | `lista-fuentes` | Si la fuente no tiene URL (PDF del aula) se muestra el título sin enlace |
| Guía de actividad | `guia`, `guia-encabezado`, `guia-pasos`, `plazo-obligatorio`, `guia-detalles`, `lista-chips` | El plazo obligatorio va destacado; hora y fase se marcan como «no obligatorias» |
| Enlaces de regreso | `volver`, `enlace-flecha` | Flecha de icono, sin texto «←» |
| Bloques de página | `bloques` (rejilla de `resumen`), `encabezado-seccion`, `vacio`, `tarjeta-opcion` | Mi comunidad, huerto sin configurar |
| Casillas múltiples | `opciones-multiples` alrededor de un `CheckboxSelectMultiple` | Diseños y abonos como píldoras; la marcada se ve en salvia |
| Resumen de especie | `componentes/seleccion_resumen.html` | Foto pequeña, nombre y método actual (cambiar método, retirar) |
| Material | `lista-materiales`, `material`, `material-disponible`, `material-formulario`, `boton-pequeno`, `etiqueta-neutra` | Casilla + botón por material; la etiqueta repite el estado guardado |
| Calendario | `cabecera-mes` (`boton-mes`, `titulo-mes`), `formulario-fecha`, `tabla-calendario` (con `data-titulo` en cada celda), `fila-referencia`, `etiqueta-hora` | En celular cada fila de la tabla se lee como tarjeta |
| Fase lunar | `luna luna-nueva`, `luna-creciente`, `luna-llena`, `luna-menguante` + `nombre-ancestral` | Círculo dibujado con CSS; siempre acompañado del nombre de la fase |
| Eventos vecinos | `eventos-vecinos`, `evento-vecino` | Indican la fecha de referencia; no son la fase de cada día |
| Vista del mes | `cuadricula-mes`, `dia-con-evento`, `dia-referencia`, `dia-enlace`, `leyenda-fases` + filtro `cuadricula_mes` | Lunes a domingo; solo se marcan los días con un evento verificado, nunca la fase de los demás días |

Ejemplo de tarjeta de planta:

```html
<article class="tarjeta">
  <img src="{% static planta.imagen_ruta %}" alt="{{ planta.nombre_comun }}" class="foto-planta">
  <div class="tarjeta-cuerpo">
    <h3>{{ planta.nombre_comun }}</h3>
    <p class="nombre-cientifico">{{ planta.nombre_cientifico }}</p>
    <span class="etiqueta">{{ seleccion.estado }}</span>
    <div class="avance">
      <span class="avance-barra"><span class="avance-relleno" style="width: {{ seleccion.porcentaje }}%"></span></span>
      <span class="avance-texto">{{ seleccion.porcentaje }} %</span>
    </div>
  </div>
  <div class="tarjeta-pie"><a href="...">Ver planta</a></div>
</article>
```

Los nombres de variables del ejemplo son orientativos; se usan los que entregue la vista.

### Filtros de presentación del catálogo

`{% load presentacion %}` (archivo `catalogo/templatetags/presentacion.py`) solo separa textos guardados para mostrarlos:

- `texto|lineas`: una línea por paso de la guía.
- `texto|elementos`: materiales escritos como «a; b; c.» en una lista.
- `texto|licencia`: separa «CC BY-SA 4.0 - https://...» en nombre y enlace.
- `numero|nombre_mes`: nombre del mes en español (12 -> «Diciembre»).
- `filas|cuadricula_mes:mes`: semanas del mes con los eventos que entrega la vista, ubicados en su día de Guayaquil.

## Qué se tomó de la propuesta visual y qué se adaptó

La propuesta (generada aparte, sin el contexto del proyecto) se aplicó en colores, tipografía, pantalla dividida de acceso, barra lateral, tarjetas, etiquetas y resumen con iconos. Se adaptó para cumplir el alcance V1 y el plan:

- **Usuario en lugar de correo:** el acceso es con nombre de usuario, como el formulario de Bryan.
- **Sin «Recordarme», «¿Olvidaste tu contraseña?», buscador ni notificaciones:** no existen en V1 (la guía D2-02 pide no añadir recuperación por correo).
- **Crear cuenta conserva todos los campos reales:** perfil, datos para entrar, aviso de datos completo y casilla sin marcar; no solo nombre, correo y contraseña.
- **Menú con las secciones del proyecto:** Mi huerto, Catálogo, Guías, Calendario, Mi comunidad e Historial (no «Bitácora» ni «Configuración»).
- **Sin fotos ni fuentes de internet:** las fotos de Unsplash y Google Fonts se reemplazaron por una ilustración en línea y fuentes del sistema.
- **Sin JavaScript ni navegación simulada:** el prototipo usaba `:target` para cambiar de pantalla; aquí cada pantalla es una ruta de Django.
