# B3-01: conectar cuentas, comunidades y huertos

## Qué se conectó

La aplicación tiene una entrada en `/`, que lleva a la comunidad de la cuenta identificada por la sesión. Antes esa dirección no tenía una ruta.

El menú permite ir a perfil, comunidad y huerto. El perfil incluye **Continuar a mi comunidad**. Las plantillas usan nombres de rutas reales mediante `{% url ... %}`; no necesitan escribir direcciones distintas a las del servidor.

El recorrido es:

```text
Registro → Inicio de sesión → Perfil → Mi comunidad
                                          │
                       Crear comunidad o unirse con código
                                          ↓
                             Mi huerto → Configurar
                                          ↓
                                   Elegir especies
```

El responsable configura y elige las especies. Un participante de la misma comunidad consulta el mismo huerto. No se crean bases separadas para cuentas y comunidades.

## Cómo se comprobó

`RecorridoInicialIntegradoTests`, en `comunidades/tests.py`, utiliza los formularios, las rutas y las plantillas reales con dos clientes distintos. Ambos comparten la misma base temporal de la prueba.

La comprobación:

1. Registra una cuenta aceptando la versión vigente del aviso.
2. Inicia sesión con su contraseña.
3. Crea una comunidad y comprueba su pertenencia.
4. Configura el huerto con opciones de las cinco categorías.
5. Elige una especie con un método de siembra.
6. Registra una segunda cuenta e inicia su sesión.
7. La une con el código y comprueba que consulta el mismo huerto.
8. Rechaza una operación de responsable intentada por ese participante.
9. Cierra su sesión y comprueba que pierde el acceso privado.

Los clientes exigen CSRF. No se usa `force_login` para saltar el registro o el inicio de sesión en ese recorrido. Las opciones y la especie de prueba se crean únicamente en la base temporal.

Es una comprobación automática de desarrollo. No registra una ejecución formal de CP-01 a CP-10 ni escribe resultados en `docs/v1/resultados.md`.

```powershell
python manage.py test comunidades.tests.RecorridoInicialIntegradoTests
```

## Qué necesita la interfaz del equipo

Doménica puede modificar la presentación manteniendo los nombres de rutas y campos. Las vistas ya entregan:

| Pantalla | Variables principales |
| --- | --- |
| Registro y perfil | `form`, `aviso_secciones`, `aviso_version` |
| Comunidad | `comunidad`, `miembros`, `puede_editar` |
| Huerto | `huerto`, `comunidad`, `selecciones`, `puede_editar` |
| Configuración | `form`, con `categorias_pendientes` |
| Elegir especie | `form`, `hay_disponibles`, `catalogo_vacio` |
| Cambiar método o retirar | `form`, `seleccion`, `con_historial` |

Los enlaces pueden ocultarse según esos datos, pero la autorización sigue en el servidor. Cada formulario de escritura conserva `method="post"` y `{% csrf_token %}`. El cierre de sesión también es POST.

Esta documentación prepara la integración técnica; no sustituye una revisión conjunta de los diseños que el equipo incorpore después.

## Cómo leer la conexión desde Python

En `huertos/urls.py`, la ruta vacía selecciona `huertos.views.inicio`. Esa vista redirige a `comunidades:mi_comunidad`. El middleware de Django exige sesión y la vista de comunidad obtiene la pertenencia desde `request.user`.

`request.user` es la conexión entre iniciar sesión y trabajar en una comunidad. No hay que pedir nuevamente el nombre ni aceptar un ID de usuario del formulario para averiguar quién actúa.

## Límite actual

El recorrido está verificado con contenido ficticio en una base de pruebas. Para usarlo de principio a fin en la base local, el equipo debe incorporar y cargar las opciones y las 18 fichas definitivas del catálogo. No se inventó ese contenido ni se redujo el alcance.
