"""Fichas de plantas de Juan: menta, hierbabuena, toronjil, orégano, romero y manzanilla.

Primera versión, 21 de octubre de 2026.
"""

PLANTAS = [
    {
        "codigo": "menta",
        "nombre_comun": "Menta",
        "nombre_cientifico": "Mentha  xpiperita L.",
        "otros_nombres": [],
        "familia": "Lamiaceae",
        "altitud_msnm": "1000-1500",
        "provincias_ecuador": ["Imbabura", "Pichincha", "Azuay"],
        "ciclo": "corto",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hoja"],
        "usos_documentados": (
            "Uso tradicional de la hoja en infusión para aliviar síntomas digestivos leves, "
            "como dispepsia y flatulencia (EMA). El MSP la incluye entre las plantas "
            "vermífugas (Anexo 5, p. 73)."
        ),
        "contraindicaciones": (
            "No usar si hay alergia a la hoja de menta o al mentol. Evitar en caso de reflujo "
            "gastroesofágico, porque puede aumentar la acidez. Precaución con cálculos "
            "biliares y otros trastornos biliares. La EMA no la recomienda en menores de 4 "
            "años ni durante el embarazo o la lactancia, por falta de datos. Consultar a "
            "personal de salud si los síntomas duran más de 2 semanas."
        ),
        "imagen_ruta": "static/img/plantas/menta.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo corto (lavanda, salvia, menta, ortiga, manzanilla). "
                    "P. 73 (Anexo 5): planta vermífuga y planta caliente («Hierba buena y menta»). "
                    "P. 24 (Tabla 1): ejemplo para suelo arcilloso. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["ciclo", "cualidad_ancestral", "usos_documentados", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Mentha × piperita L.",
                "url": "https://powo.science.kew.org/taxon/450969-1",
                "referencia": "Nombre aceptado (híbrido de Mentha aquatica × M. spicata); familia Lamiaceae.",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Agencia Europea de Medicamentos (EMA), Comité HMPC",
                "titulo": "European Union herbal monograph on Mentha × piperita L., folium (Revision 1)",
                "url": "https://ema.europa.eu/en/documents/herbal-monograph/european-union-herbal-monograph-mentha-x-piperita-l-folium-revision-1_en.pdf",
                "referencia": "Secciones 4.1 (indicaciones tradicionales), 4.2, 4.3, 4.4, 4.6 y 4.8; infusión de la hoja seca.",
                "campos": ["parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Plantas.ec (tienda en línea de plantas, Ecuador)",
                "titulo": "La menta piperita: un tesoro de frescura y sabor",
                "url": "https://www.plantas.ec/data/origendistribucionmenta.html",
                "referencia": "Nombra Imbabura, Pichincha y Azuay como provincias propicias para su cultivo. Describe cultivo, no distribución natural. Sin autor.",
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Centro de Investigaciones Biológicas del Noroeste (CIBNOR), México",
                "titulo": "Menta (sección «hierbas»)",
                "url": "https://www.cibnor.gob.mx/personal/bmurillo/hierbas/menta.php",
                "referencia": "Página personal de B. Murillo en el sitio del CIBNOR.",
                "campos": ["altitud_msnm"],
            },
            {
                "autor": "Journal of Ethnobiology and Ethnomedicine (BioMed Central)",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador, 2016",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5: Mentha spicata y Mentha × piperita comparten los nombres locales «hierba buena», «menta» y «menta negra». Autores no anotados.",
                "campos": ["observaciones"],
            },
            {
                "autor": "F 植生记 (Zhishengji), en Pexels",
                "titulo": "Fresh Green Mint Leaves in Natural Light",
                "url": "https://www.pexels.com/photo/34296580/",
                "referencia": (
                    "Licencia Pexels (https://www.pexels.com/license/). "
                    "Archivo: https://images.pexels.com/photos/34296580/pexels-photo-34296580.jpeg"
                ),
                "campos": ["static/img/plantas/menta.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
    {
        "codigo": "hierbabuena",
        "nombre_comun": "Hierbabuena",
        "nombre_cientifico": "Mentha spicata L.",
        "otros_nombres": ["Yerbabuena", "Menta verde", "Hierbahuerto"],
        "familia": "Lamiaceae",
        "altitud_msnm": "1600-2600",
        "provincias_ecuador": ["Loja", "Azuay", "Pichincha"],
        "ciclo": "largo",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hoja"],
        "usos_documentados": (
            "Uso tradicional de la hoja por vía oral (mercados del sur del Ecuador). Fuentes de "
            "divulgación la asocian con molestias digestivas como gases e indigestión, con "
            "evidencia insuficiente. El MSP no describe sus usos medicinales."
        ),
        "contraindicaciones": (
            "No se encontró una monografía institucional. Una fuente de divulgación (RxList) "
            "indica: en el embarazo, evitar cantidades grandes de té; en la lactancia, no "
            "superar las cantidades usadas en alimentos; precaución en enfermedad hepática o "
            "renal; posible interacción con sedantes y con medicamentos que pueden dañar el "
            "hígado. Consultar a personal de salud antes de usarla."
        ),
        "imagen_ruta": "static/img/plantas/hierbabuena.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 73 (Anexo 5): planta caliente («Hierba buena y menta»). "
                    "P. 66 (Anexo 3): controla plagas de insectos de las plantas cercanas. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["cualidad_ancestral", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Mentha spicata L.",
                "url": "https://powo.science.kew.org/taxon/451162-1",
                "referencia": "Nombre aceptado; familia Lamiaceae.",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Plantas.ec (tienda en línea de plantas, Ecuador)",
                "titulo": "Yerba buena: la hierba de los tesoros naturales de Ecuador",
                "url": "https://www.plantas.ec/data/origendistribucionyerba.html",
                "referencia": "Nombra Loja, Azuay y Pichincha. Describe cultivo, no distribución natural. Sin autor ni altitud.",
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Journal of Ethnobiology and Ethnomedicine (BioMed Central)",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador, 2016",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5: Mentha spicata L., nombres locales «hierba buena», «menta» y «menta negra»; parte usada: hoja; vía oral. Autores no anotados.",
                "campos": ["parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "RxList",
                "titulo": "Spearmint (supplement monograph)",
                "url": "https://www.rxlist.com/supplements/spearmint.htm",
                "referencia": "Secciones Overview, Uses, Precautions e Interactions. Fuente de divulgación, no institucional.",
                "campos": ["usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "El Huerto Urbano (revista)",
                "titulo": "La hierbabuena",
                "url": "https://www.elhuertourbano.net/la-hierbabuena/",
                "referencia": "Nombres: hierbabuena, yerbabuena, menta verde, hierbahuerto. Planta perenne.",
                "campos": ["otros_nombres"],
            },
            {
                "autor": "Oro Verde Semillas (empresa de semillas)",
                "titulo": "Hierbabuena",
                "url": "https://oroverdesemillas.com/semillas/hierbabuena/",
                "referencia": "Adaptabilidad: 1600-2600 msnm (condiciones de cultivo). Planta perenne; 60-80 días entre siembra y cosecha.",
                "campos": ["altitud_msnm", "ciclo"],
            },
            {
                "autor": "Federico Lopez Barranchina (Wikimedia Commons)",
                "titulo": "Hierba_buena.JPG",
                "url": "https://commons.wikimedia.org/wiki/File:Hierba_buena.JPG",
                "referencia": "Licencia CC0 (dominio público). Miniatura usada: https://thumb.wikimedia.org/wikipedia/commons/thumb/b/ba/Hierba_buena.JPG/1920px-Hierba_buena.JPG",
                "campos": ["static/img/plantas/hierbabuena.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
    {
        "codigo": "toronjil",
        "nombre_comun": "Toronjil",
        "nombre_cientifico": "Melissa officinalis L.",
        "otros_nombres": ["Melisa"],
        "familia": "Lamiaceae",
        "altitud_msnm": "1200-3200",
        "provincias_ecuador": ["Bolívar", "Loja", "Chimborazo", "Cotopaxi", "Pichincha", "Imbabura"],
        "ciclo": "largo",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hoja", "flor"],
        "usos_documentados": (
            "Uso tradicional de hojas y flores en infusión: cólicos estomacales, dolores "
            "menstruales, insomnio y afecciones nerviosas; las hojas machacadas se usan en "
            "compresas para golpes y picaduras (ficha de la USFQ sobre hierbas del Ilaló). La "
            "EMA reconoce como uso tradicional de la hoja el alivio de síntomas leves de estrés "
            "mental, la ayuda para dormir y las molestias digestivas leves, como hinchazón y "
            "flatulencia."
        ),
        "contraindicaciones": (
            "No usar si hay hipersensibilidad a la planta. La EMA no recomienda su uso en "
            "menores de 12 años ni durante el embarazo o la lactancia, por falta de datos. "
            "Consultar a personal de salud si los síntomas duran más de 2 semanas. La USFQ "
            "indica cuidar la dosificación."
        ),
        "imagen_ruta": "static/img/plantas/toronjil.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 74 (Anexo 5): planta caliente. "
                    "P. 24 (Tabla 1): ejemplo para suelo arcilloso. "
                    "P. 66 (Anexo 3): atrae abejas. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["cualidad_ancestral", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Melissa officinalis L.",
                "url": "https://powo.science.kew.org/taxon/450084-1",
                "referencia": "Nombre aceptado; familia Lamiaceae.",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Universidad San Francisco de Quito (USFQ)",
                "titulo": "Hierbas del Ilaló: toronjil (ficha en PDF)",
                "url": "https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-toronjil.pdf",
                "referencia": "Nombres «toronjil» y «melisa»; hojas y flores; usos; altitud de 1.200 a 3.200 m s. n. m.; indica cuidar la dosificación.",
                "campos": ["nombre_cientifico", "otros_nombres", "altitud_msnm", "parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Agencia Europea de Medicamentos (EMA), Comité HMPC",
                "titulo": "Community herbal monograph on Melissa officinalis L., folium (EMA/HMPC/196745/2012), adoptada el 14 de mayo de 2013",
                "url": "https://www.e-lactancia.org/media/papers/Melisa-EMEA2013.pdf",
                "referencia": "Copia de la monografía final alojada en e-lactancia.org. Secciones 4.1, 4.2, 4.3, 4.4, 4.6 y 4.8.",
                "campos": ["usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Henry Gabriel Pinanjota Guaytarilla (Universidad Técnica del Norte)",
                "titulo": "Efectos de los parámetros de deshidratado en bandeja sobre el toronjil Melissa officinalis L. para la comercialización de té a granel (2023)",
                "url": "https://repositorio.utn.edu.ec/server/api/core/bitstreams/cfb82782-e683-461f-9b73-47625fe06cda/content",
                "referencia": (
                    "Plan de trabajo de titulación. Sección 2.2 (p. 16): provincias Bolívar, Loja, Chimborazo, "
                    "Cotopaxi, Pichincha e Imbabura; hojas y brotes (Sección 2.2.7, p. 23); usos (Sección 2.2.6, p. 22). "
                    "Planta perenne (Sección 2.2.1, p. 17). No indica el tiempo hasta la cosecha."
                ),
                "campos": ["provincias_ecuador", "parte_utilizada", "usos_documentados", "observaciones"],
            },
            {
                "autor": "Wouterhagens (Wikimedia Commons)",
                "titulo": "Citroenkruid.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:Citroenkruid.jpg",
                "referencia": "Licencia CC BY 3.0 (exige atribución al autor; no es dominio público).",
                "campos": ["static/img/plantas/toronjil.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
    {
        "codigo": "oregano",
        "nombre_comun": "Orégano",
        "nombre_cientifico": "Origanum vulgare L.",
        "otros_nombres": ["Orenga", "Ourego"],
        "familia": "Lamiaceae",
        "altitud_msnm": "1800-3800",
        "provincias_ecuador": ["Tungurahua", "Guayas", "Los Ríos"],
        "ciclo": "largo",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hoja", "flor"],
        "usos_documentados": (
            "Uso tradicional de hojas y flores: infusión para cólicos estomacales, indigestión "
            "y diarrea, y para malestares de gripe y tos; compresas calientes para "
            "hinchazones, reumatismos y cólicos menstruales (ficha de la USFQ sobre hierbas del "
            "Ilaló). También se usa como condimento. El MSP la incluye entre las plantas "
            "antioxidantes (Anexo 5, p. 72). La evidencia sobre su eficacia es insuficiente en "
            "la mayoría de estos usos (RxList)."
        ),
        "contraindicaciones": (
            "La USFQ indica cuidar la dosificación: en exceso puede tener efectos "
            "anticoagulantes. Una fuente de divulgación (RxList) añade: evitar dosis medicinales "
            "en el embarazo y la lactancia; posible alergia en personas sensibles a la familia "
            "Lamiaceae; precaución en diabetes y trastornos hemorrágicos; posible interacción "
            "con antidiabéticos y anticoagulantes; suspenderlo 2 semanas antes de una cirugía. "
            "No se encontró una monografía institucional para esta especie. Consultar a "
            "personal de salud."
        ),
        "imagen_ruta": "static/img/plantas/oregano.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 72 (Anexo 5): planta antioxidante. "
                    "P. 74 (Anexo 5): planta caliente; la mejorana se lista aparte. "
                    "P. 24 (Tabla 1): ejemplo para suelo gredoso. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["cualidad_ancestral", "usos_documentados", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Origanum vulgare L.",
                "url": "https://powo.science.kew.org/taxon/453395-1",
                "referencia": "Nombre aceptado; familia Lamiaceae.",
                "campos": ["nombre_cientifico", "familia"],
            },
            {
                "autor": "Universidad San Francisco de Quito (USFQ)",
                "titulo": "Hierbas del Ilaló: orégano (ficha en PDF)",
                "url": "https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-oregano.pdf",
                "referencia": "Nombra Origanum vulgare; usos; hojas y flores; altitud de 1.800 a 3.800 m s. n. m.; advierte efectos anticoagulantes en exceso.",
                "campos": ["nombre_cientifico", "altitud_msnm", "parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "RxList",
                "titulo": "Oregano (supplement monograph)",
                "url": "https://www.rxlist.com/supplements/oregano.htm",
                "referencia": "Secciones Uses, Precautions e Interactions. Fuente de divulgación, no institucional.",
                "campos": ["usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Benítez Cruz, G.; González-Tejero, R.; Molero Mesa, J.",
                "titulo": "Origanum vulgare L. (ficha del Inventario Español de los Conocimientos Tradicionales relativos a la Biodiversidad)",
                "url": "https://www.miteco.gob.es/content/dam/miteco/es/biodiversidad/temas/inventarios-nacionales/iect_origanum_vulgare_tcm30-164102.pdf_tcm30-164102.pdf",
                "referencia": (
                    "Ministerio para la Transición Ecológica (España). P. 203: nombres «orenga» (catalán) y «ourego» (gallego); "
                    "sumidades floridas, hojas y flores; usos tradicionales en España (pp. 203-205). "
                    "La ficha no documenta toxicidad ni contraindicaciones."
                ),
                "campos": ["otros_nombres", "parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "Fernando Folleco Goya y Marcos Tenemaza Alvarez (ESPOL)",
                "titulo": "Proyecto para la exportación del orégano al mercado de Brasil y Estados Unidos (c. 2006)",
                "url": "https://www.dspace.espol.edu.ec/bitstream/123456789/1091/1/2145.pdf",
                "referencia": (
                    "Sección 2.2, Cuadro 2.1: lista zonas de cultivo de plantas medicinales en general por provincia "
                    "(Sierra: Loja, Chimborazo, Bolívar, Imbabura, Pichincha, Cotopaxi/Tungurahua; Costa: Guayas, Los Ríos). "
                    "El cuadro no asocia ninguna provincia con el orégano en particular."
                ),
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Journal of Ethnobiology and Ethnomedicine (BioMed Central)",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador, 2016",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5: «orégano» aparece como Origanum × majoricum Camb. Autores no anotados.",
                "campos": ["observaciones"],
            },
            {
                "autor": "Mariya Muschard (Pexels)",
                "titulo": "Oregano Plants Close-Up Photo",
                "url": "https://www.pexels.com/photo/11506322/",
                "referencia": (
                    "Licencia Pexels (https://www.pexels.com/license/). "
                    "Archivo: https://images.pexels.com/photos/11506322/pexels-photo-11506322.jpeg"
                ),
                "campos": ["static/img/plantas/oregano.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
    {
        "codigo": "romero",
        "nombre_comun": "Romero",
        "nombre_cientifico": "Salvia rosmarinus Spenn.",
        "otros_nombres": ["Resmarina", "Rosmarino", "Hierba de las coronas"],
        "familia": "Lamiaceae",
        "altitud_msnm": "1500",
        "provincias_ecuador": ["Pichincha", "Imbabura", "Cotopaxi", "Tungurahua"],
        "ciclo": "largo",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["hoja", "rama"],
        "usos_documentados": (
            "Uso tradicional de la hoja, en infusión o como aditivo de baño, para aliviar la "
            "dispepsia y los trastornos espasmódicos digestivos leves, los dolores musculares y "
            "articulares menores y los trastornos circulatorios periféricos menores (EMA). En "
            "mercados del sur del Ecuador se vende la rama para baño después del parto, "
            "limpieza de heridas y uso oral. El MSP la incluye entre las plantas astringentes y "
            "tónicas (Anexo 5, p. 72)."
        ),
        "contraindicaciones": (
            "No usar si hay alergia a la planta, obstrucción de las vías biliares, inflamación "
            "de la vesícula, cálculos biliares o enfermedad del hígado. La EMA no lo recomienda "
            "en menores de 12 años ni durante el embarazo o la lactancia. No aplicar sobre piel "
            "rota o irritada. Puede causar dermatitis de contacto. Consultar a personal de "
            "salud si los síntomas duran más de 2 semanas (uso oral) o más de 4 semanas (baño). "
            "Estos textos describen preparados de hoja, no el aceite esencial."
        ),
        "imagen_ruta": "static/img/plantas/romero.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo largo (cedrón, romero, laurel, marco). "
                    "P. 72 (Anexo 5): planta astringente y tónica. "
                    "P. 74 (Anexo 5): planta caliente. "
                    "P. 24 (Tabla 1): ejemplo para suelo arenoso. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["ciclo", "cualidad_ancestral", "usos_documentados", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Salvia rosmarinus Spenn.",
                "url": "https://powo.science.kew.org/taxon/457138-1",
                "referencia": "Nombre aceptado; Rosmarinus officinalis L. figura como sinónimo; familia Lamiaceae.",
                "campos": ["nombre_cientifico", "familia", "observaciones"],
            },
            {
                "autor": "Agencia Europea de Medicamentos (EMA), Comité HMPC",
                "titulo": "Rosmarini folium: monografía de la Unión Europea (Revisión 1, opinión final del HMPC de 26/09/2024)",
                "url": "https://www.ema.europa.eu/en/medicines/herbal/rosmarini-folium",
                "referencia": "Secciones sobre usos tradicionales, formas de preparación, cuándo no se recomienda y riesgos; resumen público EMA/HMPC/387754/2025.",
                "campos": ["parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Journal of Ethnobiology and Ethnomedicine (BioMed Central)",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador, 2016",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5: Rosmarinus officinalis L., «romero»; parte usada: rama; baño después del parto, limpieza de heridas y vía oral. Autores no anotados.",
                "campos": ["parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "Sociedad Española de Biología Evolutiva y Medicina (SEBEM), Universitat de València",
                "titulo": "Plantas medicinales: romero",
                "url": "https://www.uv.es/sebem/wpm/romero.html",
                "referencia": "Otros nombres: resmarina, rosmarino, hierba de las coronas. Partes aéreas o sumidades floridas. No usar en el embarazo.",
                "campos": ["otros_nombres", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Plantas.ec (vivero en línea, Ecuador)",
                "titulo": "Romero (Rosmarinus officinalis): origen y producción en Ecuador",
                "url": "https://www.plantas.ec/data/origendistribucionromero.html",
                "referencia": "Nombra Pichincha, Imbabura, Cotopaxi y Tungurahua. Describe cultivo, no distribución natural. Sin autor ni altitud.",
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Región de Murcia digital (regmurcia.com)",
                "titulo": "Romero (reportaje)",
                "url": "https://www.regmurcia.com/servlet/s.Sl?sit=c,543,m,2719&r=ReP-19848-DETALLE_REPORTAJESPADRE",
                "referencia": "Reportaje DETALLE_REPORTAJESPADRE, código ReP-19848.",
                "campos": ["altitud_msnm"],
            },
            {
                "autor": "Christina & Peter (@christina99999, Pexels)",
                "titulo": "Close-up of Sunlit Rosemary Plant Outdoors",
                "url": "https://www.pexels.com/photo/30856378/",
                "referencia": (
                    "Licencia Pexels (https://www.pexels.com/license/). "
                    "Archivo: https://images.pexels.com/photos/30856378/pexels-photo-30856378.jpeg"
                ),
                "campos": ["static/img/plantas/romero.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
    {
        "codigo": "manzanilla",
        "nombre_comun": "Manzanilla",
        "nombre_cientifico": "Matricaria chamomilla L.",
        "otros_nombres": ["Manzanilla alemana", "Camomila alemana", "Manzanilla común", "Manzanilla dulce", "Cimarrona"],
        "familia": "Asteraceae",
        "altitud_msnm": "0-1300",
        "provincias_ecuador": ["Carchi", "Imbabura", "Pichincha", "Cotopaxi", "Tungurahua", "Bolívar", "Chimborazo", "Cañar", "Azuay", "Loja"],
        "ciclo": "corto",
        "cualidad_ancestral": "caliente",
        "parte_utilizada": ["flor"],
        "usos_documentados": (
            "Uso tradicional de la flor, en infusión, para molestias digestivas leves como "
            "hinchazón y espasmos leves, síntomas del resfriado común, inflamaciones leves de "
            "boca y garganta e irritación leve de la piel (EMA). En mercados del sur del "
            "Ecuador se usa para limpiar heridas y para gárgaras. El MSP la clasifica como "
            "antiespasmódica, sedante y sudorífica (Anexo 5, p. 72)."
        ),
        "contraindicaciones": (
            "No usar si hay hipersensibilidad a la manzanilla o a otras plantas de la familia "
            "Asteraceae (Compositae). Pueden ocurrir reacciones alérgicas, a veces graves, si "
            "preparados líquidos tocan mucosas como la de la boca. No usar en baños completos "
            "si hay problemas cardíacos o circulatorios graves, ni en baños con heridas "
            "abiertas, daño extenso de la piel, enfermedad cutánea aguda, fiebre alta o "
            "infecciones graves. Normalmente es para adultos y mayores de 12 años; consultar a "
            "personal de salud si los síntomas duran más de una semana. La página de la EMA "
            "consultada no trae información sobre embarazo y lactancia: consultar antes de "
            "usarla. No confundir con la manzanilla romana (Chamaemelum nobile), que es otra "
            "especie."
        ),
        "imagen_ruta": "static/img/plantas/manzanilla.jpg",
        "fuentes": [
            {
                "autor": "Ministerio de Salud Pública del Ecuador, Dirección Nacional de Salud Intercultural",
                "titulo": "Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos (2017)",
                "url": "https://www.salud.gob.ec/wp-content/uploads/2022/09/MSP-Lineamientos-implementaci%D0%B2n-huertos-medicinales-PNA-2017-2.pdf",
                "referencia": (
                    "MSP-Lineamientos-implementación-huertos-medicinales-PNA-2017-2.pdf. "
                    "P. 48: ciclo corto (lavanda, salvia, menta, ortiga, manzanilla). "
                    "P. 72 (Anexo 5): planta antiespasmódica, sedante y sudorífica. "
                    "P. 74 (Anexo 5): planta caliente. "
                    "P. 66 (Anexo 3): atrae abejas y protege a las plantas cercanas. "
                    "P. 20: se podría sembrar en la Sierra."
                ),
                "campos": ["ciclo", "cualidad_ancestral", "usos_documentados", "observaciones"],
            },
            {
                "autor": "Royal Botanic Gardens, Kew",
                "titulo": "Plants of the World Online: Matricaria chamomilla L.",
                "url": "https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:154715-2",
                "referencia": "Nombre aceptado; Matricaria recutita L. figura como sinónimo; familia Asteraceae.",
                "campos": ["nombre_cientifico", "familia", "observaciones"],
            },
            {
                "autor": "Agencia Europea de Medicamentos (EMA), Comité HMPC",
                "titulo": "Matricariae flos: medicamento herbal (monografía EMA/HMPC/55843/2011, primera versión)",
                "url": "https://www.ema.europa.eu/pt/medicines/herbal/matricariae-flos",
                "referencia": "Secciones sobre usos tradicionales, formas de preparación y riesgos. La página no contiene información sobre embarazo y lactancia.",
                "campos": ["parte_utilizada", "usos_documentados", "contraindicaciones"],
            },
            {
                "autor": "Journal of Ethnobiology and Ethnomedicine (BioMed Central)",
                "titulo": "Medicinal plants sold at traditional markets in southern Ecuador, 2016",
                "url": "https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5",
                "referencia": "Tabla 5: Matricaria recutita L., «manzanilla»; limpieza de heridas y gárgaras. Autores no anotados.",
                "campos": ["usos_documentados"],
            },
            {
                "autor": "Raúl García de Paredes (revista digital Sierra de Baza)",
                "titulo": "Manzanilla (Matricaria chamomilla = Matricaria recutita)",
                "url": "https://sierradebaza.org/fichas-tecnicas/fichas-flora-plantas/flora-j-a-n/manzanilla-matricaria-chamomilla-matricaria-recutita",
                "referencia": "Nombres: manzanilla o camomila alemana. Anual. Capítulos florales. Su «manzanilla de campo» es otra especie (Anthemis arvensis).",
                "campos": ["otros_nombres", "parte_utilizada", "usos_documentados"],
            },
            {
                "autor": "Vicente Martínez Centelles (Botanical-online)",
                "titulo": "Características de la manzanilla",
                "url": "https://www.botanical-online.com/botanica/manzanilla-caracteristicas",
                "referencia": "Nombres: manzanilla, manzanilla común, manzanilla dulce, manzanilla alemana, cimarrona. Altitud de 0 a 1.300 m (hábitat; la página no indica el país). Anual.",
                "campos": ["otros_nombres", "altitud_msnm"],
            },
            {
                "autor": "Ministerio de Cultura y Patrimonio del Ecuador",
                "titulo": "Manzanilla (Wiki del patrimonio alimentario)",
                "url": "https://patrimonioalimentario.culturaypatrimonio.gob.ec/wiki/index.php/Manzanilla",
                "referencia": "Ficha «Manzanilla» de la wiki del patrimonio alimentario del Ecuador.",
                "campos": ["provincias_ecuador"],
            },
            {
                "autor": "Simplicus (Wikimedia Commons)",
                "titulo": "Kamille_01.jpg",
                "url": "https://commons.wikimedia.org/wiki/File:Kamille_01.jpg",
                "referencia": (
                    "Licencia CC BY 3.0 (exige atribución al autor; no es dominio público). "
                    "Miniatura usada: https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f4/Kamille_01.jpg/1920px-Kamille_01.jpg"
                ),
                "campos": ["static/img/plantas/manzanilla.jpg"],
            },
        ],
        "campos_no_verificados": [
        ],
        "observaciones": (
        ),
    },
]
