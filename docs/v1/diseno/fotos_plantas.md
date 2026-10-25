# Fotos de las 18 plantas (D2-01)

Autora: Doménica Astudillo. Revisión de especies y fotos: 24 y 25 de octubre de 2026.

Las fotos están en `static/img/plantas/<codigo>.jpg`. Proceden de Wikimedia Commons, salvo la del matico, que es de iNaturalist (no hay fotos libres de *Aristeguietia glutinosa* en Commons); se leyó la página de cada archivo para tomar autor y licencia. Cada archivo es una **copia reducida a 1200 px de lado mayor** (formato JPG, como el original); no se recortó ni se editó el contenido. La chilca y el orégano se guardan con su tamaño original (557 × 720 y 1000 × 665), que es menor.

## Estado de conexión con las fichas (25 de octubre)

- **Juan:** sus seis fichas ya usan estas fotos. Reemplazan a las que él había subido; se cambiaron solo las cuatro claves de imagen y la fuente de la foto en `plantas_juan.py`.
- **Matthew:** sus seis fichas ya usan estas fotos y las claves de imagen salieron de `campos_no_verificados`. Las especies coinciden con las de su ficha; el matico se cambió a *Aristeguietia glutinosa*, la especie que él confirmó.
- **Guillermo:** las seis fotos están listas, pero `plantas_guillermo.py` sigue vacío; él copia las claves de abajo al crear sus fichas.

## Las cuatro claves para cada ficha

La ruta no empieza con `static/`.

### Juan (`plantas_juan.py`)

```python
"menta": {
    "imagen_ruta": "img/plantas/menta.jpg",
    "imagen_autor": "Kızıl",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Mentha_%C3%97_piperita%E2%80%93IMG_6075.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"hierbabuena": {
    "imagen_ruta": "img/plantas/hierbabuena.jpg",
    "imagen_autor": "Simon Eugster",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Minze.jpg",
    "imagen_licencia": "CC BY-SA 3.0 — https://creativecommons.org/licenses/by-sa/3.0/",
},
"toronjil": {
    "imagen_ruta": "img/plantas/toronjil.jpg",
    "imagen_autor": "Lazaregagnidze",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Melissa_officinalis_Bee_Balm,Lemon_Balm_%E1%83%91%E1%83%90%E1%83%A0%E1%83%90%E1%83%9B%E1%83%91%E1%83%9D.JPG",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"oregano": {
    "imagen_ruta": "img/plantas/oregano.jpg",
    "imagen_autor": "David J. Stang",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Origanum_vulgare_Variegata_0zz.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"romero": {
    "imagen_ruta": "img/plantas/romero.jpg",
    "imagen_autor": "David J. Stang",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Rosmarinus_officinalis_13zz.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"manzanilla": {
    "imagen_ruta": "img/plantas/manzanilla.jpg",
    "imagen_autor": "Robert Flogaus-Faust",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Matricaria_chamomilla_2_RF.jpg",
    "imagen_licencia": "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
},
```

### Matthew (`plantas_matthew.py`)

```python
"matico": {
    "imagen_ruta": "img/plantas/matico.jpg",
    "imagen_autor": "Diego F. Cisneros-Heredia (iNaturalist)",
    "imagen_fuente": "https://www.inaturalist.org/observations/20253557",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"taraxaco": {
    "imagen_ruta": "img/plantas/taraxaco.jpg",
    "imagen_autor": "Agnes Monkelbaan",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Paardenbloem_(Taraxacum_officinale)_26-04-2020._(actm.)_01.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"marco": {
    "imagen_ruta": "img/plantas/marco.jpg",
    "imagen_autor": "Carlo Brescia",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Ambrosia_arborescens_en_la_quebrada_Shongo,_detalle_de_flor_y_hojas.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"llanten": {
    "imagen_ruta": "img/plantas/llanten.jpg",
    "imagen_autor": "Sanjay Acharya",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Broadleaf_Plantain_Spike.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"ortiga": {
    "imagen_ruta": "img/plantas/ortiga.jpg",
    "imagen_autor": "Dominicus Johannes Bergsma",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Brandnetel,_Urtica_dioica,_Locatie,_Famberhorst.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"violeta": {
    "imagen_ruta": "img/plantas/violeta.jpg",
    "imagen_autor": "AnRo0002",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:20130407Viola_odorata1.jpg",
    "imagen_licencia": "CC0 1.0 (dominio público) — https://creativecommons.org/publicdomain/zero/1.0/",
},
```

### Guillermo (`plantas_guillermo.py`)

```python
"paico": {
    "imagen_ruta": "img/plantas/paico.jpg",
    "imagen_autor": "SAplants",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Dysphania_ambrosioides_1DS-II_4-1102.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
"chilca": {
    "imagen_ruta": "img/plantas/chilca.jpg",
    "imagen_autor": "Dick Culbert",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Baccharis_latifolia_(14136636112).jpg",
    "imagen_licencia": "CC BY 2.0 — https://creativecommons.org/licenses/by/2.0/",
},
"lavanda": {
    "imagen_ruta": "img/plantas/lavanda.jpg",
    "imagen_autor": "H. Zell",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Lavandula_angustifolia_002.JPG",
    "imagen_licencia": "CC BY-SA 3.0 — https://creativecommons.org/licenses/by-sa/3.0/",
},
"salvia": {
    "imagen_ruta": "img/plantas/salvia.jpg",
    "imagen_autor": "H. Zell",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Salvia_officinalis_001.JPG",
    "imagen_licencia": "CC BY-SA 3.0 — https://creativecommons.org/licenses/by-sa/3.0/",
},
"cedron": {
    "imagen_ruta": "img/plantas/cedron.jpg",
    "imagen_autor": "H. Zell",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Aloysia_citriodora_002.jpg",
    "imagen_licencia": "CC BY-SA 3.0 — https://creativecommons.org/licenses/by-sa/3.0/",
},
"laurel": {
    "imagen_ruta": "img/plantas/laurel.jpg",
    "imagen_autor": "Agnieszka Kwiecień, Nova",
    "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Laurus_nobilis_Wawrzyn_szlachetny_2019-05-26_01.jpg",
    "imagen_licencia": "CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/",
},
```

## Resumen

| Código | Especie de la ficha | Pendiente de confirmar | Tamaño guardado | Licencia |
|---|---|---|---|---|
| menta | *Mentha × piperita* | | 1200 × 1200 | CC BY-SA 4.0 |
| hierbabuena | *Mentha spicata* | | 1200 × 900 | CC BY-SA 3.0 |
| toronjil | *Melissa officinalis* | | 797 × 1200 | CC BY-SA 4.0 |
| oregano | *Origanum vulgare* ('Variegata') | | 1000 × 665 | CC BY-SA 4.0 |
| romero | *Salvia rosmarinus* | | 798 × 1200 | CC BY-SA 4.0 |
| manzanilla | *Matricaria chamomilla* | | 1009 × 1200 | CC BY 4.0 |
| matico | *Aristeguietia glutinosa* (iNaturalist, Quito) | | 900 × 1200 | CC BY-SA 4.0 |
| taraxaco | *Taraxacum officinale* | | 1200 × 1200 | CC BY-SA 4.0 |
| marco | *Ambrosia arborescens* | | 1200 × 796 | CC BY-SA 4.0 |
| llanten | *Plantago major* | | 800 × 1200 | CC BY-SA 4.0 |
| ortiga | *Urtica dioica* | | 1200 × 944 | CC BY-SA 4.0 |
| violeta | *Viola odorata* | | 900 × 1200 | CC0 |
| paico | *Dysphania ambrosioides* | | 800 × 1200 | CC BY-SA 4.0 |
| chilca | *Baccharis latifolia* | Sí | 557 × 720 | CC BY 2.0 |
| lavanda | *Lavandula angustifolia* | | 901 × 1200 | CC BY-SA 3.0 |
| salvia | *Salvia officinalis* | | 1200 × 900 | CC BY-SA 3.0 |
| cedron | *Aloysia citrodora* | | 900 × 1200 | CC BY-SA 3.0 |
| laurel | *Laurus nobilis* | Sí | 900 × 1200 | CC BY-SA 4.0 |

## Si una foto se ve rota en tu base

`cargar_catalogo` no cambia plantas que ya existen. Una base cargada antes de esta revisión puede guardar rutas o créditos antiguos (por ejemplo, el toronjil con `static/img/plantas/toronjil.jpg`, que deja la imagen rota). Respalda `db.sqlite3` y ejecuta desde la raíz del proyecto:

```powershell
python manage.py shell -c "exec(open('docs/v1/diseno/actualizar_fotos_base.py', encoding='utf-8').read())"
```

Solo copia los datos de foto, fuentes, pendientes y observaciones de las fichas; no toca huertos, actividades ni cuentas.

## Cómo se muestra la atribución

En la ficha de la planta, debajo de la foto, se muestra autor, licencia y enlace a la fuente (clase `atribucion`), por ejemplo:

> Foto: Kızıl · CC BY-SA 4.0 · [Fuente](https://commons.wikimedia.org/wiki/File:Mentha_%C3%97_piperita%E2%80%93IMG_6075.jpg) · copia reducida

Las licencias CC BY y CC BY-SA obligan a mostrar autor y licencia. Como las copias están reducidas, se indica «copia reducida». Si se recorta o modifica una foto CC BY-SA, la versión modificada mantiene la misma licencia.
