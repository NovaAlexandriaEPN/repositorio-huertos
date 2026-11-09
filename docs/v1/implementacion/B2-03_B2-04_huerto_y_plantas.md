# B2-03 y B2-04: configurar el huerto y elegir plantas

## 1. Qué has construido

Antes podías entrar y pertenecer a una comunidad. Ahora el responsable puede configurar el lugar donde trabajarán y elegir sus especies.

```text
Usuario → Miembro → Comunidad → Huerto → PlantaHuerto → Planta del catálogo
                                  │
                        Opciones de configuración
```

El participante consulta esa información. El responsable puede editarla según las reglas. La aplicación comprueba el permiso en el servidor aunque alguien intente enviar una petición sin usar los botones de la página.

## 2. Cómo entrar

Inicia sesión y abre **Mi comunidad → Ver el huerto de la comunidad**.

Dirección local con el servidor funcionando:

<http://127.0.0.1:8000/comunidades/huerto/>

Si eres responsable y aún no hay huerto, aparece **Configurar el huerto**. Si participas en la comunidad, verás que su responsable debe completar la configuración.

### Dependencias que todavía necesita esta copia

Al desarrollar estas tareas, la base local tenía cero opciones y cero plantas. Los archivos de datos y el comando de carga todavía estaban pendientes en esta rama. Las pantallas muestran esa ausencia y no crean datos de catálogo por su cuenta.

Para usar el configurador con datos definitivos deben integrarse las opciones y su carga. Para elegir las plantas debe estar cargado el catálogo del equipo, que sigue incluyendo las 18 especies. No se han reducido a las especies de las pruebas.

Las pruebas automatizadas sí crean opciones y especies ficticias en su base temporal para verificar tus operaciones. No las cargan en `db.sqlite3` ni las presentan como fichas documentadas.

## 3. Qué guarda el configurador

| Dato | Regla |
| --- | --- |
| Provincia, parroquia y dirección | Texto escrito manualmente; obligatorio. |
| Área en m² | Mayor que cero y con hasta dos decimales. |
| Diseños | Uno o varios, todos de la categoría diseño. |
| Cerca | Una opción de la categoría cerca. |
| Suelo | Una opción de la categoría suelo. |
| Fuente de agua | Una opción de la categoría agua. |
| Abonos | Uno o varios, todos de la categoría abono. |

La orientación de Este a Oeste se muestra como recomendación. No se pide GPS ni se consultan mapas.

`HuertoForm`, en `comunidades/forms.py`, determina qué campos recibe el navegador. No incluye comunidad, maestro ni campos de nombramiento.

En su constructor se filtra cada lista:

```python
self.fields[campo].queryset = OpcionHuerto.objects.filter(categoria=categoria)
```

Lee esa línea así: «para este campo, ofrece únicamente las opciones de su categoría». `queryset` es la consulta que proporciona las opciones. Una opción de abono no debe aparecer como cerca.

## 4. Por qué el servicio vuelve a validar

El navegador no decide qué datos están permitidos. Alguien podría alterar el envío o llamar al servicio desde otro código de Python. Por eso `configurar_huerto`, en `comunidades/servicios.py`, comprueba de nuevo:

1. Quién es el usuario de la sesión.
2. A qué comunidad pertenece y si es su responsable.
3. Que haya diseños y abonos y correspondan a sus categorías.
4. Que ubicación, área y opciones únicas sean válidas según el modelo.

La comunidad se obtiene de la cuenta que actúa. El formulario no puede elegir la comunidad de otra persona.

El servicio busca primero si ya hay un huerto. Si existe, actualiza ese mismo registro. Si no existe, lo crea. Actualizar su ubicación no crea un segundo huerto ni reemplaza sus selecciones de plantas.

### Una relación múltiple se guarda después del huerto

```python
huerto.save()
huerto.disenos.set(disenos_validos)
huerto.abonos.set(abonos_validos)
```

Este es el orden de creación, resumido. Primero debe existir el registro del huerto con su identificador. Después Django puede escribir las relaciones que señalan qué diseños y abonos tiene.

`set(...)` deja exactamente las opciones que se seleccionaron. No acumula indefinidamente las anteriores. Todo se ejecuta dentro de una transacción: una configuración inválida no debe dejar una parte guardada y otra pendiente.

Al actualizar se usa una lista explícita de campos. El configurador no modifica al maestro ni su constancia de nombramiento.

## 5. Planta y PlantaHuerto no son lo mismo

`Planta` es la ficha de una especie compartida por todos. `PlantaHuerto` indica que esa especie fue elegida para un huerto concreto, con un método de siembra.

```text
Ficha de la especie
    ↑                  ↑
Selección del huerto A  Selección del huerto B
```

Los dos huertos pueden elegir la misma especie. Cada uno tiene su propio método e historial. Dentro de un mismo huerto no se permite elegir dos veces esa especie.

En **Elegir una especie**, las ya seleccionadas dejan de aparecer como opciones. El servicio también valida la combinación única y la base contiene una restricción para impedir duplicados.

El método se elige entre semillas, estacas, esquejes y plántulas, con los códigos compartidos de `MetodoSiembra`. La aplicación no inventa un método distinto ni restringe cada especie a un método sin una regla respaldada por el alcance.

## 6. Qué significa proteger el historial

Una selección puede cambiar de método o retirarse únicamente si no tiene ninguna actividad. Una actividad anulada sigue siendo historial.

```text
Selección sin actividades → puede cambiar de método o retirarse
Selección con actividad activa → se conserva
Selección con actividad anulada → también se conserva
```

No se cambia una selección para que pase a representar otra especie u otro huerto. Si no tiene historial, se retira y se elige lo que corresponda. Si lo tiene, se conserva su identidad.

### Dónde se decide

`PlantaHuerto.tiene_historial` consulta si existe alguna actividad relacionada. Los servicios de cambio de método y retiro revisan esa propiedad antes de guardar o borrar.

El modelo también rechaza cambiar el método con historial al ejecutar `full_clean()`. El futuro campo `Actividad.planta` debe usar `PROTECT` para impedir el borrado de una selección referenciada.

La consulta usa el gestor base de actividades. Esto evita perder de vista una anulación si otro gestor habitual de ese modelo muestra únicamente actividades activas. No se filtra por `anulado=False` para decidir si existe historial.

## 7. Cómo se conecta con el trabajo de Fernando

En el modelo `Actividad`, la referencia prevista es:

```python
planta = models.ForeignKey(
    "comunidades.PlantaHuerto",
    on_delete=models.PROTECT,
    related_name="actividades",
    null=True,
    blank=True,
)
```

Este fragmento documenta el contrato. No crea por sí solo el modelo de actividades en esta rama.

- La referencia señala una selección del huerto, no la ficha de la especie.
- `related_name="actividades"` permite consultar las actividades desde la selección.
- `PROTECT` conserva la selección cuando una actividad la referencia.
- La referencia opcional permite que las actividades generales pertenezcan al huerto sin señalar una planta.

`comunidades` no importa `actividades.models`. Usa la relación que Django crea entre ambos modelos. Así no aparece un ciclo de importaciones entre las dos carpetas.

`comunidades/checks.py` añade una comprobación: cuando exista el modelo `Actividad`, revisa que el campo cumpla ese contrato. Si la relación está mal definida, `manage.py check` devuelve `comunidades.E001` con una indicación de la corrección.

Los servicios que Fernando implemente para registrar y anular deben usar también las transacciones acordadas y verificar la comunidad. La prueba final de su ciclo completo se hace al integrar ese trabajo.

## 8. Qué debes probar desde el navegador

Cuando estén cargadas las opciones y plantas del catálogo:

1. Entra como responsable y abre el huerto.
2. Completa la ubicación y un área positiva. Elige varios diseños y abonos y una cerca, un suelo y una fuente de agua.
3. Guarda y vuelve a abrir el configurador. Deben conservarse todos los valores.
4. Prueba área cero o deja una selección múltiple vacía. Debe aparecer un error y conservarse la configuración anterior.
5. Elige una especie y un método de siembra.
6. Abre el selector otra vez. Esa especie no debe ofrecerse por segunda vez en el mismo huerto.
7. Sin historial, cambia su método. Deben conservarse la especie y el huerto.
8. Abre **Retirar del huerto**. Visitar la confirmación no retira nada. Solo el botón que envía POST realiza el retiro.
9. Entra como participante. Puedes consultar la configuración y las plantas; no debes poder editarlas, ni siquiera enviando directamente una petición a sus direcciones.
10. Cuando esté integrado `Actividad`, registra una actividad de esa selección y prueba los bloqueos. Anúlala con el flujo correspondiente y verifica que la selección siga protegida.

No uses un ID de otra comunidad para elegir el destino de una operación. El servidor siempre busca la selección dentro del huerto de la cuenta autorizada; un ID ajeno no se encuentra y responde con HTTP 404.

## 9. Cómo se comprobó antes de publicar

Los casos nuevos cubren configuración persistente, categorías incorrectas, áreas y ubicaciones inválidas, permisos, duplicados, aislamiento entre comunidades, cambios de método, retiro, métodos HTTP y CSRF.

La prueba de historial crea una tabla temporal con registros reales en la base de pruebas, usando la relación prevista. Comprueba actividad activa y anulada, incluso cuando el gestor habitual oculta anuladas. Verifica que los servicios y los envíos a las pantallas bloqueen tanto el cambio como el retiro.

Esa tabla solo existe durante la prueba. No introduce el modelo definitivo de Fernando, ni actividades reales en la base local, ni migraciones de producción. Se elimina al terminar.

Para repetir las comprobaciones con el entorno y la clave local configurados según el README:

```powershell
python manage.py test comunidades
python manage.py test
python manage.py makemigrations --check --dry-run
```

## 10. Orden recomendado para leer el código

1. `HuertoForm`: identifica los campos que se pueden enviar.
2. `configurar_huerto`: localiza dónde se comprueban responsable y categorías y dónde se guardan las relaciones.
3. La vista `configurar`: sigue el paso de GET a POST, formulario, servicio y redirección.
4. `elegir_planta`: observa cómo recibe una ficha y crea la selección propia del huerto.
5. `cambiar_metodo_siembra` y `retirar_planta`: identifica el filtro por huerto y el rechazo del historial.
6. `PlantaHuerto.tiene_historial`: sigue la conexión con las actividades.

El patrón sigue siendo el mismo de B2-02: formulario para los campos, servicio para la operación, modelo para los datos y vista para coordinar. Las nuevas piezas se apoyan en esa organización.
