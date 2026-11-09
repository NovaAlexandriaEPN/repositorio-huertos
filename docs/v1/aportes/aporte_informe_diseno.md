# Diseño de la interfaz

Texto del 1 de noviembre de 2026 para incorporar al informe V1 (aporte D3-04 de Doménica Astudillo, diseñadora). Lo consolida Juan en el único `informe.docx`. El detalle técnico está en `docs/v1/diseno/README.md`.

## Enfoque

La interfaz se construyó con plantillas de Django, Bootstrap 5.3.8 guardado en el repositorio y una hoja de estilos propia (`static/css/estilos.css`). No usa JavaScript ni recursos de internet: fuentes, iconos y fotos son locales, de modo que la demo funciona sin conexión. El estilo es botánico y sereno: fondo marfil, verde bosque como color principal, salvia para destacar y terracota como acento, con títulos en serifa.

Las pantallas solo muestran lo que entregan las vistas. Puntos, nivel, estado de cada planta, porcentajes y permisos los calculan los servicios de cada módulo; la plantilla no repite esos cálculos y el servidor rechaza cualquier acción sin permiso aunque el botón no se muestre.

## Estructura común

- `templates/base.html` define la estructura de todas las pantallas con sesión: barra lateral con el menú y la cuenta, y el área de contenido. En celular la barra pasa a ser una cabecera.
- `templates/base_acceso.html` hereda de la anterior y presenta iniciar sesión y crear cuenta como una pantalla dividida, con una imagen a la izquierda y el formulario a la derecha.
- `templates/componentes/` reúne las piezas compartidas: `errores.html` (resumen de errores con enlace a cada campo), `mensajes.html` (resultado de cada operación), `iconos.html`, `enlace_menu.html` y otras de uso puntual.
- Cada vista entrega su formulario con el nombre `form`. Si el envío es inválido, la misma pantalla vuelve con lo escrito y los errores; si es válido, la vista redirige y muestra un mensaje.

## Pantallas por historia

| Historias | Pantallas |
|---|---|
| HU-001, HU-002 | Crear cuenta, iniciar sesión y perfil |
| HU-003, HU-004 | Mi comunidad, crear, unirse y editar; plantas del huerto, configurar huerto, elegir, cambiar método y retirar especie |
| HU-005, HU-006 | Catálogo, ficha de planta y guía de actividades |
| HU-007 | Calendario lunar en hora de Guayaquil, con vista del mes y tabla de fases |
| HU-008 a HU-011 | Registrar actividad, historial, anular y nombrar Maestro |
| HU-010 | Mi huerto: tarjetas con estado, porcentaje y siguiente acción; avance del huerto, nivel, Maestro y puntos por miembro |
| HU-012 | Materiales compartidos con su marca de disponibilidad |

Todas se leen en un ancho de celular de 375 px sin desplazamiento lateral, y los estados y niveles siempre tienen texto, no solo color.

## Fotos con atribución

Las 18 especies del catálogo tienen una foto local reducida a 1200 px. Diecisiete provienen de Wikimedia Commons y una (matico, *Aristeguietia glutinosa*) de iNaturalist, porque Commons no tenía fotos libres de esa especie. De cada foto se revisó su página de origen para registrar autor, licencia (CC BY, CC BY-SA o CC0) y fuente, y se comprobó que la especie coincide con la ficha. Debajo de cada foto la ficha muestra el autor, la licencia con su enlace, la fuente y la nota «copia reducida».

## Bocetos y decisiones

Se dibujaron tres bocetos: iniciar sesión, crear cuenta y Mi huerto. Al construir las pantallas se ajustaron al alcance V1: acceso con nombre de usuario y sin recuperación por correo; registro con todos los campos reales, aviso de datos completo y casilla sin marcar; menú con las secciones del producto; niveles Aprendiz, Oficial y Maestro; y estados de planta en lugar de etiquetas decorativas. Las fotos y fuentes de internet de la propuesta visual se reemplazaron por recursos locales.

## Comprobación

Comprobación de desarrollo del 1 de noviembre de 2026: 188 pruebas automáticas correctas; revisión de todos los enlaces internos con una cuenta responsable (59 páginas) y otra participante (35 páginas), sin errores; y recorrido de los formularios principales en el navegador. Las pruebas formales de la interfaz están en `docs/v1/pruebas/resultados.md`: CP-01 (registro, sesiones y privacidad) fue ejecutado por Doménica el 5 de noviembre y resultó aprobado, y CP-10 (celular, teclado y funcionamiento sin internet) lo ejecutó Juan.

## Pantallas finales

Las capturas se tomaron el 7 de noviembre de 2026 con la base de demostración (`scripts/crear_demo.py`), después de las correcciones de noviembre. Van al final de la sección de diseño del informe y en el README.

- **Figura 7. Pantalla Mi huerto** (`diseno/mi_huerto_aplicacion.png`): muestra cómo el boceto del huerto se convirtió en la pantalla real, con el avance promedio del huerto, los puntos y el nivel, los accesos del responsable, una tarjeta por planta con su estado y porcentaje, y las siguientes acciones sugeridas. Todos los valores los calcula el servidor.
- **Figura 8. Ficha de planta del catálogo** (`diseno/ficha_planta_aplicacion.png`): muestra la ficha del romero con su foto local, el crédito de autor, licencia y fuente debajo de la imagen, y los datos de identificación, distribución en Ecuador y clasificación ancestral.

## Limitaciones

- Las fuentes Playfair Display y DM Sans solo se ven si están instaladas; en otro caso se usan Georgia y la fuente del sistema.
- Los puntos y el nivel de cada miembro se muestran en Mi huerto y no en Mi comunidad, porque el módulo de comunidades no consulta actividades.
