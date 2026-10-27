"""Fichas de Guillermo: paico, chilca, lavanda, salvia, cedrón y laurel.

Entregadas en el pull request #2 (g-cevallos, 26-10-2026). Consolidación de
Matthew (M2-10): se pasan al formato de 19 campos del modelo integrado, la foto
usa las claves preparadas y verificadas por Doménica (docs/v1/diseno/
fotos_plantas.md), se corrige «Laurel nobilis» por «Laurus nobilis L.» (como
indica la fuente de Kew de la propia ficha) el nombre del campo
«cualidad ancestral» en las fuentes y los caracteres tipográficos (guion
largo por «-»), según la estandarización del equipo. El contenido botánico es el de Guillermo.
"""
PLANTAS = [
    {
        "codigo": "paico",
        "nombre_comun": "Paico",
        "nombre_cientifico": "Dysphania ambrosioides",
        "otros_nombres": ["epazote", "jesuit tea"],
        "familia": "Amaranthaceae",
        "altitud_msnm": "2200-3200",
        "provincias_ecuador": ["Bolívar", "Tungurahua"],
        "ciclo": None,
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["toda la planta", "hojas", "raíz", "tallos", "ramas"],
        "usos_documentados": (
            "Se usa para sacar parásitos del intestino, ayudar a la digestión y calmar cólicos del estómago y de la menstruación. "
            "La raíz se toma para regular la menstruación, y las hojas y la raíz se usan para ayudar en el parto. "
            "También se aplica en emplastos para dolores musculares y reumatismo, y se usa para resfriados, mal aire, fiebre y dolor de cabeza. "
            "Sus hojas se comen como condimento en sopas y ensaladas."
        ),
        "contraindicaciones": (
            "No debe tomarse durante el embarazo, porque puede provocar un aborto. "
            "Hay que cuidar la dosis, sobre todo con el aceite de la planta, que es tóxico y puede intoxicar: "
            "causa mareo, vómito e irritación de la piel y, en casos graves, daño al hígado, parálisis o la muerte. "
            "Este riesgo se describe para el aceite, no para la infusión."
        ),
        "imagen_ruta": "img/plantas/paico.jpg",
        "imagen_autor": "SAplants",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Dysphania_ambrosioides_1DS-II_4-1102.jpg",
        "imagen_licencia": "CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Dysphania ambrosioides (L.) Mosyakin & Clemants. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:1198060-2",
                "referencia": "Secciones Classification, Synonyms y Distribution",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Universidad San Francisco de Quito (institución inferida del dominio; la ficha no nombra autor)",
                "titulo": "Ficha «Paico - Dysphania ambrosioides» (archivo hierbas-ilalo-paico.pdf)",
                "url": "https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-paico.pdf",
                "referencia": "Ficha completa: encabezado, altitud, propiedades, contraindicaciones, partes utilizables, usos medicinales y gastronómicos",
                "campos": ["nombre_cientifico", "otros_nombres", "altitud_msnm", "parte_utilizada",
                        "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Zea Cobos, A. G.; Orellana Robles, J. D.; Soliz Panamá, J. A.; Portilla Farfán, F. L.",
                "titulo": "Plantas medicinales de las parroquias del centro-oeste del cantón Cuenca (Cap. III), en Guía etnobotánica de plantas medicinales de las parroquias rurales de Cuenca-Ecuador",
                "url": "https://dspace.ups.edu.ec/bitstream/123456789/30576/7/Plantas%20medicinales%20de%20las%20parroquias%20del%20centro-oeste%20del%20canto%cc%81n%20Cuenca.pdf",
                "referencia": "Ficha 96 (p. 149) y Tabla 2 (p. 132). DOI: https://doi.org/10.17163/abyaups.125.3",
                "campos": ["usos_documentados", "contraindicaciones", "familia", "altitud_msnm"],
            },
            {
                "autor": "Tinitana, F.; Rios, M.; Romero-Benavides, J. C. et al.",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador. Journal of Ethnobiology and Ethnomedicine 12:29 (2016)",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5, fila Amaranthaceae: Dysphania ambrosioides, «Paico», rama, frotación, Loja",
                "campos": ["provincias_ecuador", "parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "No identificado (texto completo no accesible)",
                "titulo": "Artículo PMC12899134 sobre aceite esencial de Dysphania ambrosioides y variables edáficas en el sur de Ecuador",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12899134",
                "referencia": "Introducción (solo extracto de búsqueda)",
                "campos": ["otros_nombres", "familia"],
            },
            {
                "autor": "No identificado en el extracto",
                "titulo": "Efecto de la Radiación UV-C en la Flora Nativa y Capacidad Antioxidante de la Mezcla para Té Compuesto por Toronjil, Ortiga, Perejil y Paico Provenientes de Cotacachi - Ecuador. Revista Politécnica 39(1), 2017",
                "url": "https://scielo.senescyt.gob.ec/pdf/rpolit/v39n1/2477-8990-rpolit-39-01-00019.pdf",
                "referencia": "Introducción (solo extracto de búsqueda)",
                "campos": ["otros_nombres"],
            },
            {
                "autor": "WebMD / Natural Medicines Database",
                "titulo": "Chenopodium oil",
                "url": "https://www.webmd.com/vitamins/ai/ingredientmono-898/chenopodium-oil",
                "referencia": "Secciones Side Effects y Special Precautions (se refiere al aceite)",
                "campos": ["contraindicaciones"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 73: por sus efectos según la medicina andina. "
                ),
                "campos": ["cualidad_ancestral"],
            },
            {
                "autor": "SAplants",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Dysphania_ambrosioides_1DS-II_4-1102.jpg",
                "referencia": "CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
            "ciclo",
        ],
        "observaciones": (
            "Origen: USFQ y Zea Cobos et al. lo describen como nativo, pero POWO lista Ecuador como 'introducido' "
            "y Tinitana et al. (2016) lo marca 'Introduced'. Conviene resolverlo con el Catálogo de Plantas Vasculares del Ecuador. "
            "Altitud: USFQ indica 2200-3200 msnm (cultivo/presencia) y Zea Cobos et al. indican 0-4000 msnm (distribución). "
            "Familia: Amaranthaceae es la vigente; fuentes antiguas (Field Museum, Zea Cobos) usan Chenopodiaceae. "
            "Sinónimo científico: Chenopodium ambrosioides L."
        ),
    },
    {
        "codigo": "chilca",
        "nombre_comun": "Chilca",
        "nombre_cientifico": "Baccharis latifolia",
        "otros_nombres": ["Chilcao", "Chillca"],
        "familia": "Asteraceae",
        "altitud_msnm": "1600-3800",
        "provincias_ecuador": ["Pichincha", "Imbabura", "Cañar", "Cotopaxi", "Chimborazo", "Bolívar",
                                "Azuay", "Loja", "Napo", "Sucumbíos", "Zamora Chinchipe"],
        "ciclo": None,
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["toda la planta", "hojas", "tallos", "flores/inflorescencias", "ramas"],
        "usos_documentados": (
            "Se usa principalmente como antiinflamatorio y analgésico: en cocimiento, baños y cataplasmas para golpes, torceduras, luxaciones, fracturas y dolores reumáticos, y como pomada cicatrizante de heridas. "
            "En infusión se emplea para el dolor de estómago, cólicos, diarrea, fiebre y dolor de huesos, y su cocción se usa como tónico antidiabético y para el hígado. "
            "También se registra para dolor de muela y de cabeza y para limpias de mal aire. "
            "Además sirve como tinte de lana, cerca viva y forraje."
        ),
        "contraindicaciones": (
            "Por precaución, evitar en embarazo y lactancia, en menores de 12 años, en insuficiencia hepática y en enfermedades autoinmunes. "
            "Puede interactuar con anticoagulantes, antidiabéticos y antihipertensivos, por lo que no se recomienda combinarla con ellos. "
            "No hay una dosis oral segura establecida: es tóxica a dosis altas y se aconseja limitarla al uso tópico externo. "
            "Puede causar malestar gastrointestinal y reacciones cutáneas, sobre todo en personas alérgicas a las Asteraceae."
        ),
        "imagen_ruta": "img/plantas/chilca.jpg",
        "imagen_autor": "Dick Culbert",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Baccharis_latifolia_(14136636112).jpg",
        "imagen_licencia": "CC BY 2.0 - https://creativecommons.org/licenses/by/2.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Baccharis latifolia (Ruiz & Pav.) Pers. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:183399-1",
                "referencia": "Encabezado (nombre aceptado, publicación original) y sección Native to",
                "campos": ["nombre_cientifico"],
            },
            {
                "autor": "Zea Cobos, A. G.; Orellana Robles, J. D.; Soliz Panamá, J. A.; Portilla Farfán, F. L.",
                "titulo": "Plantas medicinales de las parroquias del centro-oeste del cantón Cuenca (Cap. III), en Guía etnobotánica de plantas medicinales de las parroquias rurales de Cuenca-Ecuador",
                "url": "https://dspace.ups.edu.ec/bitstream/123456789/30576/7/Plantas%20medicinales%20de%20las%20parroquias%20del%20centro-oeste%20del%20canto%cc%81n%20Cuenca.pdf",
                "referencia": "Ficha 85 (p. 138). DOI: https://doi.org/10.17163/abyaups.125.3",
                "campos": ["familia", "otros_nombres", "altitud_msnm", "usos_documentados"],
            },
            {
                "autor": "Bayas-Morejón, F.; Tigre, A.; Ramón, R.; Yánez, D.",
                "titulo": "Antimicrobial and antioxidant effect of natural extracts from leaves, root, stem and flowers of Baccharis latifolia from Ecuador. Int J Curr Pharm Res 12(2):78-84 (2020)",
                "url": "https://journals.innovareacademics.in/index.php/ijcpr/article/download/37495/21968",
                "referencia": "Introducción, pp. 78-79. DOI: https://doi.org/10.22159/ijcpr.2020v12i2.37495",
                "campos": ["provincias_ecuador", "usos_documentados"],
            },
            {
                "autor": "Zamora Peralta, C. L.; Acosta Acosta, M. A.",
                "titulo": "Crema natural de chilca (Baccharis latifolia) para tratar dolores reumáticos, articulares y traumas. Riobamba, 2021 (ensayo académico)",
                "url": "https://dspace.istmas.edu.ec/bitstreams/b13678cc-aaa6-40dc-94f2-568ed6d9edb7/download",
                "referencia": "pp. 7-9 (distribución, partes y usos), pp. 13-15 (usos y toxicidad), p. 26",
                "campos": ["parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Sequeda-Castañeda, L. G.; Célis, C.; Luengas-Caicedo, P. E.",
                "titulo": "Phytochemical and therapeutic use of Baccharis latifolia (Ruiz & Pav.) Pers. (Asteraceae). Pharmacologyonline 2:14-17 (2015)",
                "url": "https://pharmacologyonline.silae.it/files/archives/2015/vol2/PhOL_2015_2_A003_Celis_14_17.pdf",
                "referencia": "Secciones Traditional use y Toxicity, p. 16",
                "campos": ["parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Sandoval Velasco, M. E. (Universidad Técnica de Ambato)",
                "titulo": "Análisis de las características fitoquímicas, propiedades farmacológicas, usos y aplicaciones más comunes de la Chilca (Baccharis latifolia) en el Ecuador (2021)",
                "url": "https://repositorio.uta.edu.ec/items/ab7433be-2122-48ad-b7ba-92ff5c8f1fe0",
                "referencia": "Resumen (solo el resumen; no accedí al texto completo)",
                "campos": ["usos_documentados"],
            },
            {
                "autor": "Tinitana, F.; Rios, M.; Romero-Benavides, J. C. et al.",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador. J Ethnobiol Ethnomed 12:29 (2016)",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5, fila Baccharis latifolia: 'Chilca larga', rama, frotación, nativa, Loja",
                "campos": ["otros_nombres", "provincias_ecuador", "parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "Rios, M.; Yanchaliquin, V.; Páez, B.; Haro-Carrión, X.; Parroquia Salinas de Guaranda (The Field Museum)",
                "titulo": "Plantas Medicinales de Salinas de Guaranda, Ecuador. Rapid Color Guide #X011 v1.0 (2008)",
                "url": "https://fieldguides.fieldmuseum.org/sites/default/files/rapid-color-guides-pdfs/411_1.pdf",
                "referencia": "Página 1, ítem 14 'Chilca' (Baccharis latifolia); portada: Provincia de Bolívar",
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Prada, J.; Orduz-Díaz, L.; Coy-Barrera, E.",
                "titulo": "Baccharis latifolia: una Asteraceae poco valorada con potencialidad química y biológica en el neotrópico. Rev. Fac. Cienc. Básicas 12(1):92-105 (2016)",
                "url": "https://www.researchgate.net/publication/308632590_Baccharis_latifolia_una_Asteraceae_poco_valorada_con_potencialidad_quimica_y_biologica_en_el_neotropico",
                "referencia": "Fragmento sobre rango altitudinal (solo extracto de búsqueda). DOI citado en otra fuente: https://doi.org/10.18359/rfcb.1858",
                "campos": ["altitud_msnm"],
            },
            {
                "autor": "No identificado (sitio 'urlic', cita a Romero Corral, Espinoza Pineda y Valle Bastidas, Universidad Técnica del Norte, 2019)",
                "titulo": "Herbolaria - 15. Chilca",
                "url": "https://sites.google.com/view/urlic/plantas/15-chilca",
                "referencia": "Secciones Toxicología y Contraindicaciones (fuente secundaria)",
                "campos": ["contraindicaciones"],
            },
            {
                "autor": "Yerbateca (sitio web; autoría no indicada)",
                "titulo": "Chilca: Para Qué Sirve, 9 Usos y Propiedades Medicinales",
                "url": "https://yerbateca.org/plantas/baccharis-latifolia/",
                "referencia": "Sección Contraindicaciones, Seguridad y Precauciones (fuente secundaria, sin respaldo clínico propio)",
                "campos": ["contraindicaciones"],
            },
            {
                "autor": "Carraz, M.; Lavergne, C.; Jullian, V.; Wright, M.; Gairin, J. E.; Gonzales de La Cruz, M.; Bourdy, G.",
                "titulo": "Antiproliferative activity and phenotypic modification induced by selected Peruvian medicinal plants on human hepatocellular carcinoma Hep3B cells. J Ethnopharmacol 166:185-199 (2015)",
                "url": "https://www.documentation.ird.fr/hor/fdi:010064200",
                "referencia": "Resumen, apartado Hep3B evaluation. DOI: https://doi.org/10.1016/j.jep.2015.02.028",
                "campos": ["contraindicaciones"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 73: por sus efectos según la medicina andina. "
                ),
                "campos": ["cualidad_ancestral"],
            },
            {
                "autor": "Dick Culbert",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Baccharis_latifolia_(14136636112).jpg",
                "referencia": "CC BY 2.0 - https://creativecommons.org/licenses/by/2.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
            "ciclo",
        ],
        "observaciones": "Altitud: el rango 1600-3800 msnm describe su distribución en ecosistemas altoandinos según Zea Cobos et al. y Prada et al.",
    },
    {
        "codigo": "lavanda",
        "nombre_comun": "Lavanda",
        "nombre_cientifico": "Lavandula angustifolia Mill.",
        "otros_nombres": ["alhucema"],
        "familia": "Lamiaceae",
        "altitud_msnm": "0-3000",
        "provincias_ecuador": ["Pichincha"],
        "ciclo": "corto",
        "cualidad_ancestral": None,
        "parte_utilizada": ["hojas", "flores", "semillas"],
        "usos_documentados": (
            "Se toma en infusión de hojas y flores para calmar los nervios, la ansiedad, la depresión y la tensión, "
            "para dormir mejor y para aliviar dolores de cabeza y migrañas. "
            "Su aceite se usa sobre la piel contra los hongos y para ayudar a cicatrizar heridas y quemaduras."
        ),
        "contraindicaciones": (
            "No se recomienda en personas con epilepsia ni en quienes son alérgicos a la lavanda, y quienes tienen gastritis deben evitar tomar mucha. "
            "Por falta de estudios, no se aconseja en embarazo, lactancia ni en menores de 12 años. "
            "Puede dar sueño, por eso no se debe manejar después de tomarla, y conviene dejarla unas 2 semanas antes de una cirugía. "
            "Sobre la piel puede causar alergia, y el aceite debe usarse con cuidado en niños."
        ),
        "imagen_ruta": "img/plantas/lavanda.jpg",
        "imagen_autor": "H. Zell",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Lavandula_angustifolia_002.JPG",
        "imagen_licencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Lavandula angustifolia Mill. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/449008-1",
                "referencia": "Encabezado (nombre aceptado) y sección Distribution",
                "campos": ["nombre_cientifico"],
            },
            {
                "autor": "Universidad San Francisco de Quito (institución inferida del dominio; la ficha no nombra autor)",
                "titulo": "Ficha «Lavanda - Lavandula angustifolia» (archivo hierbas-ilalo-lavanda.pdf)",
                "url": "https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-lavanda.pdf",
                "referencia": "Ficha completa: altitud, propiedades, contraindicaciones, partes utilizables y usos",
                "campos": ["nombre_cientifico", "altitud_msnm", "parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "European Medicines Agency (HMPC)",
                "titulo": "Community herbal monograph on Lavandula angustifolia Miller, flos. EMA/HMPC/734125/2010 (27 de marzo de 2012)",
                "url": "https://www.e-lactancia.org/media/papers/LavandaFlor-EMA2012.pdf",
                "referencia": "Secciones 4.1 (indicaciones), 4.2-4.4 (niños, contraindicaciones), 4.6 (embarazo y lactancia) y 4.7 (conducción). Copia alojada en e-lactancia.org",
                "campos": ["usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Davis's Drug Guide (vía Unbound Medicine)",
                "titulo": "Lavender",
                "url": "https://www.unboundmedicine.com/washingtonmanual/view/Davis-Drug-Guide/110082/all/lavender",
                "referencia": "Secciones Trade Name(s), Contraindication/Precautions y Adverse Reactions",
                "campos": ["otros_nombres", "contraindicaciones"],
            },
            {
                "autor": "Monar B., P.; Lagla, G.; López, S. (Universidad Central del Ecuador / The Field Museum)",
                "titulo": "Plantas Medicinales de Mercados de Quito. Rapid Color Guide #851, v1 (2019)",
                "url": "https://fm-digital-assets.fieldmuseum.org/2406/904/851_ecuador_medicinal_plants_of_quito_market.pdf",
                "referencia": "Página 2, ítem 22 «Lavanda», Lavandula angustifolia, Lamiaceae; portada: Quito, Pichincha",
                "campos": ["familia", "provincias_ecuador"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo corto (lavanda, salvia, menta, ortiga, manzanilla). "
                ),
                "campos": ["ciclo"],
            },
            {
                "autor": "H. Zell",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Lavandula_angustifolia_002.JPG",
                "referencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
            "cualidad_ancestral",
        ],
        "observaciones": (
            "Altitud: la ficha de la USFQ describe 0-3000 msnm como condiciones de cultivo/adaptación. "
            "Provincias: solo Pichincha está respaldada (mercados de Quito); un blog de jardinería menciona Ibarra y el valle del Chota como zonas de cultivo, pero no es una fuente confiable. "
            "Nombres: 'espliego' se usa a veces como sinónimo, pero corresponde a otras especies."
        ),
    },
    {
        "codigo": "salvia",
        "nombre_comun": "Salvia",
        "nombre_cientifico": "Salvia officinalis",
        "otros_nombres": ["salvia real", "salve real"],
        "familia": "Lamiaceae",
        "altitud_msnm": "2200-3800",
        "provincias_ecuador": [],
        "ciclo": "corto",
        "cualidad_ancestral": None,
        "parte_utilizada": ["Toda la planta antes de florecer", "Hojas"],
        "usos_documentados": (
            "Tradicionalmente, las hojas y sumidades floridas se toman en infusión para aliviar problemas digestivos leves "
            "(como acidez y distensión abdominal) y para reducir la sudoración excesiva. "
            "En forma de gargarismos, se emplea para tratar inflamaciones de la boca y la garganta. "
            "Por vía tópica, sus extractos o infusiones se aplican para aliviar inflamaciones leves de la piel."
        ),
        "contraindicaciones": (
            "No se recomienda en mujeres embarazadas ni en periodo de lactancia debido a su contenido de tuyona, "
            "un compuesto que en altas concentraciones es neurotóxico. Por falta de estudios de seguridad, tampoco se aconseja en menores de 18 años. "
            "Dosis altas (especialmente del aceite esencial) pueden provocar taquicardia, sensación de calor, vértigo y convulsiones, "
            "por lo que deben evitarla las personas con epilepsia. Se aconseja no usar ininterrumpidamente por periodos prolongados."
        ),
        "imagen_ruta": "img/plantas/salvia.jpg",
        "imagen_autor": "H. Zell",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Salvia_officinalis_001.JPG",
        "imagen_licencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Salvia officinalis L. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:456833-1",
                "referencia": "Encabezado (nombre aceptado) y sección Taxonomy",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Organismo Andino de Salud - Convenio Hipólito Unanue (ORAS-CONHU)",
                "titulo": "Plantas Medicinales de la Subregión Andina",
                "url": "https://www.orasconhu.org/sites/default/files/file/webfiles/doc/pub_plantas_medicinales.pdf",
                "referencia": "Página 87, ficha de Salvia officinalis (nombres comunes, rango altitudinal en Ecuador y parte útil)",
                "campos": ["otros_nombres", "altitud_msnm", "parte_utilizada"],
            },
            {
                "autor": "European Medicines Agency (HMPC)",
                "titulo": "European Union herbal monograph on Salvia officinalis L., folium. EMA/HMPC/732886/2010 Rev.1",
                "url": "https://www.ema.europa.eu/en/documents/herbal-monograph/final-european-union-herbal-monograph-salvia-officinalis-l-folium-revision-1_en.pdf",
                "referencia": "Secciones 4.1 (indicaciones terapéuticas), 4.3 (contraindicaciones), 4.4 (precauciones especiales y tuyona), 4.6 (embarazo/lactancia) y 4.9 (sobredosis)",
                "campos": ["usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo corto (lavanda, salvia, menta, ortiga, manzanilla). "
                ),
                "campos": ["ciclo"],
            },
            {
                "autor": "H. Zell",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Salvia_officinalis_001.JPG",
                "referencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
            "provincias_ecuador",
            "cualidad_ancestral",
        ],
        "observaciones": (
            "Origen: POWO la identifica como nativa del sur de Europa. Al igual que la lavanda, es una planta introducida que se cultiva en la región interandina ecuatoriana. "
            "Altitud: El cultivo en Ecuador está documentado entre 2200 y 3800 msnm por el ORAS-CONHU (condiciones de cultivo/presencia). "
            "Toxicidad: La EMA hace especial énfasis en el control de la exposición diaria a la tuyona (thujone), por lo que el uso oral debe ser siempre moderado."
        ),
    },
    {
        "codigo": "cedron",
        "nombre_comun": "Cedrón",
        "nombre_cientifico": "Aloysia citrodora Paláu",
        "otros_nombres": ["cidrón", "hierbaluisa", "verbena de Indias"],
        "familia": "Verbenaceae",
        "altitud_msnm": "250-3800",
        "provincias_ecuador": ["Azuay", "Loja"],
        "ciclo": "largo",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hojas", "ramas"],
        "usos_documentados": (
            "Tradicionalmente, las hojas (y ramas) en infusión por vía oral se emplean para aliviar síntomas leves de estrés mental, "
            "ansiedad, tristeza y depresión (a veces combinadas con toronjil), así como para conciliar el sueño. "
            "También se toma en infusión para trastornos gastrointestinales leves, incluyendo cólicos estomacales, distensión abdominal, "
            "flatulencia, indigestión y diarrea, y para tratar resfriados y gripes con fiebre."
        ),
        "contraindicaciones": (
            "Contraindicado en personas con hipersensibilidad a la sustancia activa. "
            "Por falta de datos suficientes sobre su seguridad, no se recomienda su uso durante el embarazo y la lactancia, "
            "ni en niños y adolescentes menores de 18 años. "
            "Puede afectar la capacidad para conducir y utilizar maquinaria, por lo que los pacientes afectados no deben conducir."
        ),
        "imagen_ruta": "img/plantas/cedron.jpg",
        "imagen_autor": "H. Zell",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Aloysia_citriodora_002.jpg",
        "imagen_licencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Aloysia citrodora Paláu. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:1015994-1",
                "referencia": "Encabezado (nombre aceptado), sección Taxonomy y Synonyms",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "European Medicines Agency (HMPC)",
                "titulo": "European Union herbal monograph on Aloysia citrodora Paláu (syn. Aloysia triphylla (L'Hér.) Kuntze; Verbena triphylla L'Hér.; Lippia citriodora Kunth), folium. EMA/HMPC/376770/2019 (13 de enero de 2021)",
                "url": "https://www.fitoterapia.net/archivos/202108/final-european-union-herbal-monograph-aloysia-citrodora-palau-syn-aloysia-triphylla-lher-kuntze_en.pdf",
                "referencia": "Página 2 (nombre en español: Hierbaluisa, hoja de), sección 2 (parte utilizada: folium/hoja) y secciones 4.1 (indicaciones de uso tradicional), 4.2-4.4 (menores), 4.3 (contraindicaciones), 4.6 (embarazo y lactancia) y 4.7 (conducción)",
                "campos": ["nombre_cientifico", "otros_nombres", "parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Zea Cobos, A. G.; Caballero, P.; Vélez, J. L. (Universidad Politécnica Salesiana)",
                "titulo": "Saberes ancestrales: Uso de las plantas medicinales del cantón Cuenca",
                "url": "https://dspace.ups.edu.ec/bitstream/123456789/28180/4/Saberes%20ancestrales%20uso%20de%20las%20plantas%20medicinales%20del%20canto%CC%81n%20Cuenca.pdf",
                "referencia": "Registro de Aloysia citrodora (cedrón) en las parroquias de Ricaurte, Sidcay y Chiquintad (Cuenca, Azuay), entre 2500 y 3500 msnm",
                "campos": ["nombre_cientifico", "altitud_msnm", "provincias_ecuador"],
            },
            {
                "autor": "Tinitana, F.; Rios, M.; Romero-Benavides, J. C. et al.",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador. Journal of Ethnobiology and Ethnomedicine 12:29 (2016)",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4",
                "referencia": "Tabla de especies comercializadas en mercados de la provincia de Loja: «Cedrón», rama (branch), vía oral",
                "campos": ["provincias_ecuador", "parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "Andrade, J. M.; Lucero Mosquera, H.; Armijos, C.",
                "titulo": "Ethnobotany of Indigenous Saraguros: Medicinal Plants Used by Community Healers 'Hampiyachakkuna' in the San Lucas Parish, Southern Ecuador. BioMed Research International (2017)",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5514338/",
                "referencia": "Tabla de especies, ítem 10: Aloysia triphylla (L'Hér.) Britton, Verbenaceae, infusión para resfriados y cólicos en San Lucas (Loja)",
                "campos": ["familia", "provincias_ecuador", "usos_documentados"],
            },
            {
                "autor": "Universidad San Francisco de Quito (institución inferida del dominio; la ficha no nombra autor)",
                "titulo": "Ficha «Toronjil - Melissa officinalis» (archivo hierbas-ilalo-toronjil.pdf)",
                "url": "https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-toronjil.pdf",
                "referencia": "Sección Usos medicinales: mención del uso de infusión combinada con cedrón para ansiedad, tristeza, depresión y gripes",
                "campos": ["usos_documentados"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo largo (cedrón, romero, laurel, marco). "
                ),
                "campos": ["ciclo", "cualidad_ancestral"],
            },
            {
                "autor": "H. Zell",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Aloysia_citriodora_002.jpg",
                "referencia": "CC BY-SA 3.0 - https://creativecommons.org/licenses/by-sa/3.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
            "Sinónimos científicos: Aloysia triphylla (L'Hér.) Britton, Aloysia triphylla (L'Hér.) Kuntze, Lippia citriodora Kunth y Verbena triphylla L'Hér.; en algunas fuentes aparece escrito como Aloysia citriodora. "
            "Altitud: el rango 2500-3500 msnm describe su presencia documentada en parroquias rurales del cantón Cuenca según Zea Cobos et al. "
            "Origen: Zea Cobos et al. lo registran como introducido en Cuenca, mientras que Tinitana et al. (2016) lo marcan como nativo en la región andina."
        ),
    },
    {
        "codigo": "laurel",
        "nombre_comun": "Laurel",
        "nombre_cientifico": "Laurus nobilis L.",
        "otros_nombres": ["laurel de cocina", "laurel común", "laurel europeo"],
        "familia": "Lauraceae",
        "altitud_msnm": "0-4000",
        "provincias_ecuador": ["Azuay"],
        "ciclo": "largo",
        "cualidad_ancestral": None,
        "parte_utilizada": ["hojas", "frutos"],
        "usos_documentados": (
            "Tradicionalmente, las hojas en infusión por vía oral se emplean para estimular el apetito, "
            "facilitar la digestión y aliviar cólicos estomacales, flatulencias y afecciones respiratorias como gripes y bronquitis. "
            "Por vía tópica, la decocción o el aceite de hojas y frutos se aplican en baños, fricciones o cataplasmas para aliviar "
            "dolores reumáticos, musculares y articulares. Las hojas secas se usan ampliamente como condimento culinario."
        ),
        "contraindicaciones": (
            "Contraindicado en personas con alergia o hipersensibilidad a la especie o a otras plantas de la familia Lauraceae. "
            "No se recomienda su uso medicinal durante el embarazo, la lactancia ni en niños pequeños por falta de datos de seguridad, "
            " ni en personas con gastritis o úlceras gastroduodenales. "
            "Por vía tópica, el aceite esencial o los extractos pueden provocar dermatitis de contacto y reacciones de fotosensibilidad. "
            "La hoja entera no debe ingerirse directamente, ya que no se digiere y puede causar obstrucción o perforación en el tracto gastrointestinal."
        ),
        "imagen_ruta": "img/plantas/laurel.jpg",
        "imagen_autor": "Agnieszka Kwiecień, Nova",
        "imagen_fuente": "https://commons.wikimedia.org/wiki/File:Laurus_nobilis_Wawrzyn_szlachetny_2019-05-26_01.jpg",
        "imagen_licencia": "CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/",
        "fuentes": [
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Laurus nobilis L. Plants of the World Online",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:465049-1",
                "referencia": "Encabezado (nombre aceptado) y secciones Taxonomy y Distribution",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Zea Cobos, A. G.; Orellana Robles, J. D.; Soliz Panamá, J. A.; Portilla Farfán, F. L.",
                "titulo": "Plantas medicinales de las parroquias del centro-oeste del cantón Cuenca (Cap. III), en Guía etnobotánica de plantas medicinales de las parroquias rurales de Cuenca-Ecuador",
                "url": "https://dspace.ups.edu.ec/bitstream/123456789/30576/7/Plantas%20medicinales%20de%20las%20parroquias%20del%20centro-oeste%20del%20canto%cc%81n%20Cuenca.pdf",
                "referencia": "Tabla 2 y ficha correspondiente a Laurus nobilis (Lauraceae) en el cantón Cuenca (Azuay). DOI: https://doi.org/10.17163/abyaups.125.3",
                "campos": ["nombre_cientifico", "otros_nombres", "familia", "altitud_msnm", "provincias_ecuador", "parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo largo (cedrón, romero, laurel, marco). "
                ),
                "campos": ["ciclo"],
            },
            {
                "autor": "Agnieszka Kwiecień, Nova",
                "titulo": "Foto de la especie en Wikimedia Commons (preparada por Doménica, docs/v1/diseno/fotos_plantas.md)",
                "url": "https://commons.wikimedia.org/wiki/File:Laurus_nobilis_Wawrzyn_szlachetny_2019-05-26_01.jpg",
                "referencia": "CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/",
                "campos": ["imagen_ruta", "imagen_autor", "imagen_fuente", "imagen_licencia"],
            },
        ],
        "campos_no_verificados": [
            "cualidad_ancestral",
        ],
        "observaciones": (
            "Especie: corresponde al laurel aromático o de cocina (Laurus nobilis L., Lauraceae), introducido desde la región mediterránea; "
            "no debe confundirse con el laurel de cera andino (Morella pubescens, Myricaceae) ni con el laurel maderable de costa (Cordia alliodora, Boraginaceae). "
            "Altitud: el rango 0-4000 msnm corresponde a la categoría de distribución/adaptación reportada por Zea Cobos et al. en Cuenca."
        ),
    },
]