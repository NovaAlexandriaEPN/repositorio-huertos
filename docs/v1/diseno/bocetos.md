# Bocetos V1 (D1-01)

Autora: Doménica Astudillo (diseñadora). Bocetos de referencia para construir las plantillas; no son un prototipo navegable ni una guía de marca.

## Pantallas

| Archivo | Pantalla | Plantilla que orienta |
|---|---|---|
| `01_iniciar_sesion.png` | Iniciar sesión: pantalla dividida con imagen y formulario | `cuentas/login.html` (sobre `base_acceso.html`) |
| `02_crear_cuenta.png` | Crear cuenta (formulario representativo) | `cuentas/registro.html` (sobre `base_acceso.html`) + `componentes/errores.html` |
| `03_mi_huerto.png` | Mi huerto: barra lateral, bloque destacado, resumen, tarjetas de plantas y lista lateral | `actividades/inicio_huerto_virtual.html` (sobre `base.html`) |

## Recorrido

1. **Iniciar sesión** → al entrar, **Mi huerto**. El enlace «Crear una cuenta» lleva a **Crear cuenta**.
2. **Crear cuenta** → *Crear cuenta*: si hay errores, se queda en la misma pantalla con lo escrito y los errores; si es válido, vuelve a **Iniciar sesión** con el mensaje «Tu cuenta se ha creado. Ya puedes iniciar sesión.». El enlace «¿Ya tienes una cuenta? Inicia sesión» vuelve a Iniciar sesión sin enviar.
3. **Mi huerto** → botón principal **Registrar actividad**; al guardar vuelve a Mi huerto con el mensaje de resultado.
4. **Mi huerto** → *Ver planta* en una tarjeta abre la ficha del catálogo, que tiene un enlace de regreso.
5. Sin sesión solo se ofrecen «Iniciar sesión» y «Crear cuenta». Con sesión, la barra lateral muestra Mi huerto, Catálogo, Guías, Calendario, Mi comunidad e Historial, y abajo el menú de la cuenta (perfil y cerrar sesión).

## Ajustes acordados para las plantillas reales

Los bocetos muestran la estructura visual. Al construir las plantillas se aplican estas reglas del alcance:

- **Acceso:** se entra con **usuario**, no con correo. No hay «Recordarme» ni «¿Olvidaste tu contraseña?» (la recuperación por correo está fuera de V1).
- **Mi huerto:**
  - El botón principal es **Registrar actividad**, no «Añadir planta» (las plantas se eligen en el configurador del responsable).
  - No hay buscador ni notificaciones.
  - El menú usa las secciones del proyecto: no hay «Mis plantas», «Bitácora» ni «Configuración». El historial ocupa el lugar de la bitácora.
  - Las tres cifras del resumen son las del alcance: **nivel**, **puntos** y **avance del huerto**, no «plantas», «cuidados para hoy» o «próximas cosechas».
  - La lista lateral muestra **actividades recientes** o **siguientes acciones** que entrega la vista; no es una lista de tareas para marcar con casillas.

- **Niveles:** el resumen usa los niveles del alcance: Aprendiz (0–99), Oficial (desde 100) y Maestro (nombrado por el responsable). Se muestra quién es el maestro vigente o «Sin maestro nombrado». No hay «Nivel 3 · Brote» ni una barra de puntos hacia el siguiente nivel.
- **Avance del huerto:** la barra muestra el **promedio de avance de las plantas** (seis hitos), con su número, por ejemplo «Avance del huerto: 58 %». Sin plantas, 0 %.
- **Tarjetas de planta:** cada una muestra foto, nombre, **método** (semillas, estacas, esquejes o plántulas), **estado** en texto (planeada, sembrada, creciendo, cosechada, secando o empacada), **porcentaje** con número y **siguiente acción** recomendada. Las etiquetas del boceto («Riego hoy», «Saludable») se reemplazan por esos estados. El uso medicinal se consulta en la ficha.
- **Fotos:** las ilustraciones del boceto se reemplazan por las fotos del catálogo con su autor, licencia y fuente.
- **Crear cuenta:**
  - Se usan los campos reales del formulario de Bryan (`RegistroForm`): usuario, nombre completo, contraseña y confirmación, fecha de nacimiento, género y talentos ancestrales.
  - Las ayudas de usuario y contraseña son las que entrega el formulario, no las del boceto.
  - **Género** no es obligatorio: incluye la opción «Prefiero no indicarlo».
  - «Participación recomendada desde los 14 años» es solo un aviso y aparece **una vez**. No se usa `min`, cálculo de edad ni JavaScript que rechace a un menor.
  - El **aviso de datos completo** se lee antes de aceptar, y la casilla de aceptación aparece **sin marcar**. Fecha y versión del consentimiento las guarda el servidor (la versión va en un campo oculto).
  - Si hay un error, el formulario conserva lo escrito; las contraseñas se vuelven a escribir.
- **Errores:** el resumen superior enumera los campos con problema y cada campo resalta su error, sin repetir el mismo texto dos veces. El boceto muestra el formulario sin errores; se aplican las mismas reglas que en el resto de formularios.
- **Menú:** se agregan Guías y Calendario. El menú de la cuenta (perfil y cerrar sesión con POST) se hace sin JavaScript.
- **Sin recursos externos:** Bootstrap local y fuentes del sistema; la demo funciona sin internet.
- Todo lo que se calcula (puntos, nivel, estado, porcentaje y permisos) lo entrega la vista; la plantilla solo lo muestra.

## Plantilla base y menú (D1-02)

`templates/base.html` carga Bootstrap 5.3 desde `static/vendor/bootstrap/` y después `static/css/estilos.css`. Con sesión iniciada, las pantallas usan una barra lateral (en celular pasa a ser una cabecera con el menú desplazable). Iniciar sesión y crear cuenta usan `templates/base_acceso.html`: pantalla dividida con imagen y formulario. Colores, tipografía y clases de tarjetas, fotos y formularios: ver [guia_estilo.md](guia_estilo.md). No usa JavaScript: el menú de la cuenta es un `<details>` y cerrar sesión es un formulario POST.

El menú común busca estas rutas. Mientras una ruta no exista, su opción aparece deshabilitada («Disponible próximamente») en lugar de romper la página; cuando el módulo la define con este nombre, se activa sola.

| Opción | Ruta que debe existir | También se marca activa en | Módulo |
|---|---|---|---|
| Mi huerto | `actividades:inicio` | `actividades:registrar` | Fernando |
| Catálogo | `catalogo:lista_plantas` | `catalogo:detalle_planta` | Matthew |
| Guías | `catalogo:guias` | — | Matthew |
| Calendario | `catalogo:calendario` | — | Matthew |
| Mi comunidad | `comunidades:mi_comunidad` | `comunidades:crear`, `unirse`, `editar` | Bryan |
| Historial | `actividades:historial` | — | Fernando |

Si un módulo prefiere otro nombre, se cambia en `base.html` (una línea por opción).

Componentes:

- `componentes/enlace_menu.html`: una opción del menú (recibe `ruta`, `texto`, `icono` y opcionalmente `tambien`).
- `componentes/iconos.html`: iconos de línea propios que se usan con `<svg class="icono"><use href="#i-hoja"/></svg>`.
- `componentes/mensajes.html`: mensajes de Django como alertas de Bootstrap (`success`, `info`, `warning`, `danger`).
- `componentes/errores.html`: resumen de errores del formulario como alerta `danger`, con enlace a cada campo.
