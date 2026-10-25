"""Fichas de plantas de Matthew: matico, taraxaco, marco, llantén, ortiga y violeta.

Formato: 19 claves por ficha, como el modelo Planta integrado en la rama bryan. Información educativa;
no reemplaza atención médica ni indica dosis.

Criterios usados (consultas del 19 de octubre de 2026):
- Nombre científico y familia: Plants of the World Online (Kew). Si el material
  del curso identifica otra especie con el mismo nombre común, se corrige aquí
  y se avisa a Doménica antes de elegir la foto.
- Provincias y altitud: cuando no hay una fuente ecuatoriana que las indique,
  se usan los ejemplares de herbario de GBIF para Ecuador
  (basisOfRecord = PRESERVED_SPECIMEN). Provincias: las que tienen al menos dos
  ejemplares (se descartan registros aislados que pueden ser errores de
  georreferencia). Altitud: percentiles 5 y 95 de los ejemplares con altitud,
  redondeados a 50 m. Describe dónde se ha colectado la especie (silvestre o
  cultivada), no condiciones óptimas de cultivo.
- `ciclo` y `cualidad_ancestral` usan la clasificación de los lineamientos
  del MSP (2017). Cualidad: tabla del Anexo 5 (p. 73-74); el MSP llama
  «frescas (frías)» a las plantas frías, que aquí se guardan como 'fria'.
  Ciclo: el MSP solo nombra ejemplos (p. 48): ortiga es de ciclo corto y
  marco de ciclo largo. Las otras cuatro quedan pendientes; no se deducen de
  «perenne» ni del clima.
- Fotos: archivo en static/img/plantas/<codigo>.jpg (matico, taraxaco, marco,
  llanten, ortiga, violeta). `imagen_ruta` se escribe relativa a static/
  (img/plantas/<codigo>.jpg) con autor, fuente y licencia, como las fichas de
  Juan. Mientras no exista, queda en None y figura como pendiente.
"""

_GBIF_CRITERIO = (
    'Ejemplares de herbario en Ecuador (PRESERVED_SPECIMEN). Provincias con al '
    'menos dos ejemplares; altitud = percentiles 5-95 de los ejemplares con '
    'altitud, redondeados a 50 m. Consultado el 19-10-2026.'
)

_TINITANA_2016 = {
    'autor': 'Tinitana F., Rios M., Romero-Benavides J. C., et al.',
    'titulo': 'Medicinal plants sold at traditional markets in southern Ecuador. '
              'Journal of Ethnobiology and Ethnomedicine 12, 29 (2016)',
    'url': 'https://ethnobiomed.biomedcentral.com/articles/10.1186/s13002-016-0100-4/tables/5',
    'referencia': 'Tabla de especies: nombre local, parte usada y vía de administración.',
    'campos': [],  # Se completa en cada ficha.
}


def _msp(referencia, campos):
    return {
        'autor': 'Ministerio de Salud Pública del Ecuador (MSP), Dirección Nacional de Salud Intercultural',
        'titulo': 'Implementación de huertos medicinales en los establecimientos de salud del primer '
                  'nivel de atención. Lineamientos, 1.ª ed., Quito (2017)',
        'url': None,
        'referencia': 'MSP-Lineamientos-implementacion-huertos-medicinales-PNA-2017.pdf (aula virtual); '
                      + referencia,
        'campos': campos,
    }


_P_CUALIDAD = 'Anexo 5, «Por sus efectos según la medicina andina», tabla de plantas calientes y frescas (p. 73-74).'
_P_CICLO = '«Cosecha ritual de las plantas medicinales»: ciclo corto y ciclo largo (p. 48).'
_P_USOS = 'Anexo 5, «Por su utilidad» (p. 72).'


def _tinitana(campos):
    fuente = dict(_TINITANA_2016)
    fuente['campos'] = campos
    return fuente


def _gbif(taxon_key, nombre, campos):
    return {
        'autor': 'GBIF.org',
        'titulo': f'Búsqueda de ocurrencias: {nombre}, Ecuador, ejemplares de herbario',
        'url': (
            'https://www.gbif.org/occurrence/search?'
            f'taxon_key={taxon_key}&country=EC&basis_of_record=PRESERVED_SPECIMEN'
        ),
        'referencia': _GBIF_CRITERIO,
        'campos': campos,
    }


PLANTAS = [
    # ------------------------------------------------------------------ M2-01
    {
        'codigo': 'matico',
        'nombre_comun': 'Matico',
        'nombre_cientifico': 'Aristeguietia glutinosa (Lam.) R.M.King & H.Rob.',
        'otros_nombres': [],
        'familia': 'Asteraceae',
        'altitud_msnm': '2000-4000 m (distribución en los Andes ecuatorianos)',
        'provincias_ecuador': [
            'Azuay', 'Cañar', 'Chimborazo', 'Cotopaxi', 'Imbabura', 'Napo',
            'Pichincha', 'Tungurahua',
        ],
        'ciclo': None,
        'cualidad_ancestral': 'caliente',
        'parte_utilizada': ['Hoja', 'Tallo', 'Flor'],
        'usos_documentados': (
            'Uso tradicional en Ecuador como astringente, antirreumático y '
            'antimicrobiano, y para molestias del estómago, úlceras, diarrea y '
            'dolor de cabeza. Las hojas se usan en infusión o en cataplasma para '
            'heridas, erupciones de la piel y tos; también se mencionan baños con '
            'la infusión. Las actividades antimicrobianas descritas proceden de '
            'estudios de laboratorio, no de ensayos en personas.'
        ),
        'contraindicaciones': None,
        'imagen_ruta': 'img/plantas/matico.jpg',
        'imagen_autor': 'Diego F. Cisneros-Heredia (iNaturalist)',
        'imagen_fuente': 'https://www.inaturalist.org/observations/20253557',
        'imagen_licencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/',
        'fuentes': [
            _msp(_P_CUALIDAD, ['cualidad_ancestral']),
            {
                'autor': 'Royal Botanic Gardens, Kew',
                'titulo': 'Plants of the World Online: Aristeguietia glutinosa (Lam.) R.M.King & H.Rob.',
                'url': 'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:19108-2',
                'referencia': 'Nombre aceptado; familia; sinónimo Eupatorium glutinosum Lam.; '
                              'rango nativo: Ecuador.',
                'campos': ['nombre_cientifico', 'familia', 'observaciones'],
            },
            {
                'autor': 'Valdés Sáenz M. A., Rodríguez Guerra Y., Díaz Valdés K., Pérez Díaz M. K., '
                         'Hernández Ramos H.',
                'titulo': 'Apuntes sobre cuatro plantas medicinales endémicas de Ecuador. '
                          'Ciencia Latina Revista Científica Multidisciplinar 8(4), 4252-4275 (2024). '
                          'DOI 10.37811/cl_rcm.v8i4.12649',
                'url': 'https://ciencialatina.org/index.php/cienciala/article/view/12649',
                'referencia': 'Apartado Aristeguietia glutinosa: nombre vulgar (p. 4256); '
                              'distribución, altitud y provincias citando a León et al. 2019 '
                              '(p. 4257); usos citando a De la Torre et al. 2008 (p. 4261-4262); '
                              'partes y preparaciones citando a Rivero 2021 (p. 4263).',
                'campos': ['altitud_msnm', 'provincias_ecuador', 'parte_utilizada',
                           'usos_documentados'],
            },
            {
                'autor': 'Diego F. Cisneros-Heredia (iNaturalist)',
                'titulo': 'Aristeguietia glutinosa, Quito (observación 20253557, foto 31262137)',
                'url': 'https://www.inaturalist.org/observations/20253557',
                'referencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/. Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/matico.jpg'],
            },
        ],
        'campos_no_verificados': [
            'otros_nombres',
            'ciclo',
            'contraindicaciones',
        ],
        'observaciones': (
            'Especie endémica de Ecuador; Kew recoge Eupatorium glutinosum Lam. '
            'como sinónimo. «Matico» también designa a otras especies: Piper '
            'aduncum (Perú y mercados del sur de Ecuador), Salvia scutellarioides '
            '(sur de Ecuador) y Buddleja globosa (Chile y Argentina). Se eligió '
            'A. glutinosa por ser el matico andino ecuatoriano; confirmar con el '
            'material del curso antes de elegir la foto. No se encontraron '
            'contraindicaciones documentadas: eso no significa que no existan.'
        ),
    },
    # ------------------------------------------------------------------ M2-02
    {
        'codigo': 'taraxaco',
        'nombre_comun': 'Taraxaco (diente de león)',
        'nombre_cientifico': 'Taraxacum officinale F.H.Wigg.',
        'otros_nombres': ['Diente de león', 'Tani'],
        'familia': 'Asteraceae',
        'altitud_msnm': '900-3850 m (ejemplares de herbario en Ecuador)',
        'provincias_ecuador': [
            'Azuay', 'Bolívar', 'Cañar', 'Carchi', 'Chimborazo', 'Cotopaxi',
            'Galápagos', 'Imbabura', 'Loja', 'Pichincha', 'Tungurahua',
        ],
        'ciclo': 'largo',
        'cualidad_ancestral': 'fria',
        'parte_utilizada': ['Raíz', 'Planta entera'],
        'usos_documentados': (
            'EMA describe usos tradicionales de preparados de raíz para aliviar '
            'síntomas de trastornos digestivos leves (sensación de llenura, '
            'flatulencia, digestión lenta), para la pérdida temporal del apetito '
            'y para aumentar la cantidad de orina como coadyuvante en molestias '
            'urinarias leves. Estos usos se basan en la utilización prolongada, '
            'no en ensayos clínicos. En mercados del sur de Ecuador se vende la '
            'planta entera para uso oral. El MSP clasifica el diente de león '
            'entre las plantas diuréticas y laxantes.'
        ),
        'contraindicaciones': (
            'Para los preparados de raíz descritos por EMA: no usar en personas '
            'alérgicas a la planta o a otras de la familia Asteraceae; no se '
            'recomienda con obstrucción de vías biliares, colangitis, enfermedad '
            'hepática, cálculos biliares u otras enfermedades biliares, ni cuando '
            'el médico indica reducir la ingesta de líquidos. No se recomienda en '
            'menores de 12 años ni durante embarazo o lactancia. Pueden aparecer '
            'reacciones alérgicas. Resumen parcial: consultar la fuente.'
        ),
        'imagen_ruta': 'img/plantas/taraxaco.jpg',
        'imagen_autor': 'Agnes Monkelbaan',
        'imagen_fuente': 'https://commons.wikimedia.org/wiki/File:Paardenbloem_(Taraxacum_officinale)_26-04-2020._(actm.)_01.jpg',
        'imagen_licencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/',
        'fuentes': [
            {
                'autor': 'Richters Herbs',
                'titulo': 'Farming Dandelions -- How Much to Grow? (preguntas y respuestas de cultivo)',
                'url': 'https://www.richters.com/questions-and-answers/05-20080421-4',
                'referencia': 'Raíz: «first harvest one year later, in June or July».',
                'campos': ['ciclo'],
            },
            _msp(_P_CUALIDAD + ' ' + _P_USOS, ['otros_nombres', 'cualidad_ancestral', 'usos_documentados']),
            {
                'autor': 'European Medicines Agency (EMA), HMPC',
                'titulo': 'European Union herbal monograph on Taraxacum officinale F.H.Wigg., radix. '
                          'EMA/HMPC/475726/2020 (24-11-2021)',
                'url': 'https://www.ema.europa.eu/en/documents/herbal-monograph/'
                       'final-european-union-herbal-monograph-taraxacum-officinale-fh-wigg-radix_en.pdf',
                'referencia': 'Secciones 2, 4.1, 4.2, 4.3, 4.4, 4.6 y 4.8.',
                'campos': ['nombre_cientifico', 'parte_utilizada', 'usos_documentados',
                           'contraindicaciones'],
            },
            _tinitana(['otros_nombres', 'familia', 'parte_utilizada', 'usos_documentados']),
            _gbif(5394163, 'Taraxacum officinale', ['altitud_msnm', 'provincias_ecuador']),
            {
                'autor': 'Agnes Monkelbaan',
                'titulo': 'Paardenbloem (Taraxacum officinale) 26-04-2020. (actm.) 01.jpg',
                'url': 'https://commons.wikimedia.org/wiki/File:Paardenbloem_(Taraxacum_officinale)_26-04-2020._(actm.)_01.jpg',
                'referencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/. Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/taraxaco.jpg'],
            },
        ],
        'campos_no_verificados': [
        ],
        'observaciones': (
            'Ciclo: el MSP (p. 48) llama de ciclo corto a las plantas listas para cosechar en 6 a 8 semanas desde la siembra. La raíz, parte con monografía de EMA, se cosecha por primera vez un año después de sembrar (Richters), por eso se clasifica como largo. Las hojas tiernas pueden recogerse antes. '
            'Un solo registro para «taraxaco» y «diente de león»; el código '
            'estable es taraxaco. Kew (POWO) trata Taraxacum officinale como '
            'sinónimo de Taraxacum sect. Taraxacum (grupo de especies); EMA y '
            'GBIF usan Taraxacum officinale. Introducida en Ecuador. Los usos y '
            'precauciones de EMA se refieren a preparados de raíz; no se '
            'extrapolan automáticamente a la hoja.'
        ),
    },
    # ------------------------------------------------------------------ M2-03
    {
        'codigo': 'marco',
        'nombre_comun': 'Marco',
        'nombre_cientifico': 'Ambrosia arborescens Mill.',
        'otros_nombres': ['Altamiso', 'Altamisa'],
        'familia': 'Asteraceae',
        'altitud_msnm': '1600-3400 m (ejemplares de herbario en Ecuador)',
        'provincias_ecuador': [
            'Azuay', 'Bolívar', 'Cañar', 'Carchi', 'Chimborazo', 'Cotopaxi',
            'Galápagos', 'Imbabura', 'Loja', 'Pichincha', 'Tungurahua',
        ],
        'ciclo': 'largo',
        'cualidad_ancestral': 'caliente',
        'parte_utilizada': ['Rama', 'Hoja'],
        'usos_documentados': (
            'En mercados del sur de Ecuador se vende la rama para aplicación '
            'tópica y frotaciones. Una revisión peruana recoge el uso tradicional '
            'de las hojas soasadas, en cocimiento o en ungüento, como '
            'antiinflamatorio y antirreumático, y del zumo de las ramas para '
            'hemorroides y dolor de estómago. En el huerto, el MSP la '
            'describe como planta protectora («protege el huerto, protege la casa y '
            'absorbe energías pesadas»), la usa en recetas de abono líquido y en '
            'cercas vivas.'
        ),
        'contraindicaciones': None,
        'imagen_ruta': 'img/plantas/marco.jpg',
        'imagen_autor': 'Carlo Brescia',
        'imagen_fuente': 'https://commons.wikimedia.org/wiki/File:Ambrosia_arborescens_en_la_quebrada_Shongo,_detalle_de_flor_y_hojas.jpg',
        'imagen_licencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/',
        'fuentes': [
            _msp(_P_CUALIDAD + ' ' + _P_CICLO + ' Anexo 3, plantas protectoras (p. 66); '
                 'Tabla 3, abono líquido (p. 31); Tabla 4, cercas con arbustos (p. 35).',
                 ['otros_nombres', 'ciclo', 'cualidad_ancestral', 'usos_documentados']),
            {
                'autor': 'Royal Botanic Gardens, Kew',
                'titulo': 'Plants of the World Online: Ambrosia arborescens Mill.',
                'url': 'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:176055-1',
                'referencia': 'Nombre aceptado; familia; rango nativo (incluye Ecuador); sinónimos.',
                'campos': ['nombre_cientifico', 'familia', 'observaciones'],
            },
            _tinitana(['otros_nombres', 'parte_utilizada', 'usos_documentados']),
            {
                'autor': 'Cano de Terrones T.',
                'titulo': 'Caracterización de una espirolactona sesquiterpénica obtenida de '
                          'Ambrosia arborescens Miller y evaluación de su actividad biológica en '
                          'Trypanosoma cruzi. Revista de la Sociedad Química del Perú 80(2), 124-135 (2014)',
                'url': 'https://www.redalyc.org/pdf/3719/371937638006.pdf',
                'referencia': 'Introducción, usos tradicionales (p. 125).',
                'campos': ['parte_utilizada', 'usos_documentados'],
            },
            _gbif(8424273, 'Ambrosia arborescens', ['altitud_msnm', 'provincias_ecuador']),
            {
                'autor': 'Carlo Brescia',
                'titulo': 'Ambrosia arborescens en la quebrada Shongo, detalle de flor y hojas.jpg',
                'url': 'https://commons.wikimedia.org/wiki/File:Ambrosia_arborescens_en_la_quebrada_Shongo,_detalle_de_flor_y_hojas.jpg',
                'referencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/. Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/marco.jpg'],
            },
        ],
        'campos_no_verificados': [
            'contraindicaciones',
        ],
        'observaciones': (
            'Nativa de los Andes de Ecuador según Kew. Los usos de hoja y zumo '
            'proceden de comunidades andinas de Perú; los de Ecuador, del '
            'estudio de mercados del sur del país. No se encontraron '
            'contraindicaciones documentadas: eso no significa que no existan. '
            'Confirmar con el material del curso que «marco» corresponde a esta '
            'especie.'
        ),
    },
    # ------------------------------------------------------------------ M2-04
    {
        'codigo': 'llanten',
        'nombre_comun': 'Llantén',
        'nombre_cientifico': 'Plantago major L.',
        'otros_nombres': ['Llantén mayor', 'Llantén macho', 'Llantén hembra'],
        'familia': 'Plantaginaceae',
        'altitud_msnm': '1000-3800 m',
        'provincias_ecuador': [
            'Azuay', 'Bolívar', 'Cañar', 'Carchi', 'Chimborazo', 'Cotopaxi',
            'Esmeraldas', 'Galápagos', 'Imbabura', 'Loja', 'Los Ríos', 'Manabí',
            'Morona Santiago', 'Pichincha', 'Tungurahua', 'Zamora Chinchipe',
        ],
        'ciclo': None,
        'cualidad_ancestral': 'fria',
        'parte_utilizada': ['Hoja', 'Raíz', 'Flor', 'Semilla'],
        'usos_documentados': (
            'Uso tradicional en Ecuador: infusión de hojas frescas o secas para '
            'molestias gastrointestinales y úlceras; jugo de hojas frescas para '
            'congestión nasal; cataplasmas o cocimiento de hojas sobre heridas e '
            'inflamaciones de la piel; masticar la raíz para dolor de muelas e '
            'inflamación de encías. En mercados del sur de Ecuador se vende la '
            'planta entera para uso oral. El MSP lo clasifica entre las plantas '
            'astringentes, diuréticas y laxantes.'
        ),
        'contraindicaciones': (
            'No se recomienda su consumo excesivo en niños ni durante el embarazo '
            'o la lactancia (USFQ). Resumen parcial; no se encontró una '
            'monografía oficial para esta especie.'
        ),
        'imagen_ruta': 'img/plantas/llanten.jpg',
        'imagen_autor': 'Sanjay Acharya',
        'imagen_fuente': 'https://commons.wikimedia.org/wiki/File:Broadleaf_Plantain_Spike.jpg',
        'imagen_licencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/',
        'fuentes': [
            _msp(_P_CUALIDAD + ' ' + _P_USOS, ['cualidad_ancestral', 'usos_documentados']),
            {
                'autor': 'Royal Botanic Gardens, Kew',
                'titulo': 'Plants of the World Online: Plantago major L.',
                'url': 'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:321286-2',
                'referencia': 'Nombre aceptado; familia; rango nativo Eurasia (introducida en América).',
                'campos': ['nombre_cientifico', 'familia', 'observaciones'],
            },
            {
                'autor': 'Universidad San Francisco de Quito (USFQ)',
                'titulo': 'Hierbas del Ilaló: Llantén (ficha divulgativa, PDF)',
                'url': 'https://www.usfq.edu.ec/sites/default/files/2025-03/hierbas-ilalo-llanten.pdf',
                'referencia': 'Nombres comunes, partes usadas, usos, precauciones y altitud '
                              '(ficha de una página, sin numeración).',
                'campos': ['otros_nombres', 'altitud_msnm', 'parte_utilizada',
                           'usos_documentados', 'contraindicaciones'],
            },
            _tinitana(['usos_documentados']),
            _gbif(3189767, 'Plantago major', ['provincias_ecuador']),
            {
                'autor': 'Sanjay Acharya',
                'titulo': 'Broadleaf Plantain Spike.jpg',
                'url': 'https://commons.wikimedia.org/wiki/File:Broadleaf_Plantain_Spike.jpg',
                'referencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/. Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/llanten.jpg'],
            },
        ],
        'campos_no_verificados': [
            'ciclo',
        ],
        'observaciones': (
            'En código, ruta e imagen se usa llanten; el texto visible conserva '
            'la tilde. La ficha de la USFQ trata juntos Plantago major y Plantago '
            'minor; aquí se describe P. major. No confundir con el llantén menor '
            '(Plantago lanceolata), que tiene otra monografía. Kew no lista '
            'Ecuador en su distribución, pero GBIF registra ejemplares de herbario '
            'en el país (introducida). La USFQ menciona inhalaciones junto con '
            'matico; no se incluyeron porque mezclan especies.'
        ),
    },
    # ------------------------------------------------------------------ M2-05
    {
        'codigo': 'ortiga',
        'nombre_comun': 'Ortiga',
        'nombre_cientifico': 'Urtica dioica L.',
        'otros_nombres': ['Chine', 'Tsini'],
        'familia': 'Urticaceae',
        'altitud_msnm': '750-3350 m (15 ejemplares de herbario con altitud en Ecuador)',
        'provincias_ecuador': [
            'Chimborazo', 'Cotopaxi', 'Imbabura', 'Loja', 'Pichincha', 'Tungurahua',
        ],
        'ciclo': 'corto',
        'cualidad_ancestral': 'caliente',
        'parte_utilizada': ['Hoja', 'Parte aérea'],
        'usos_documentados': (
            'EMA describe usos tradicionales de preparados de hoja para aliviar '
            'dolores articulares leves y para aumentar la cantidad de orina como '
            'coadyuvante en molestias urinarias leves. Se basan en la utilización '
            'prolongada, no en ensayos clínicos. En mercados del sur de Ecuador '
            'se vende la planta sin raíz para uso oral y frotaciones. El MSP la clasifica entre las plantas '
            'antiinflamatorias, diuréticas y «energéticas» (usadas como limpiadoras).'
        ),
        'contraindicaciones': (
            'Para los preparados de hoja descritos por EMA: no usar en personas '
            'alérgicas a la planta ni en condiciones en que se recomienda reducir '
            'líquidos (por ejemplo, enfermedad cardíaca o renal grave). No se '
            'recomienda en menores de 12 años ni durante embarazo o lactancia. Si '
            'el dolor articular viene con hinchazón, enrojecimiento o fiebre, '
            'consultar a un médico. Los pelos de la planta fresca son urticantes: '
            'manipular con guantes. Resumen parcial: consultar la fuente.'
        ),
        'imagen_ruta': 'img/plantas/ortiga.jpg',
        'imagen_autor': 'Dominicus Johannes Bergsma',
        'imagen_fuente': 'https://commons.wikimedia.org/wiki/File:Brandnetel,_Urtica_dioica,_Locatie,_Famberhorst.jpg',
        'imagen_licencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/',
        'fuentes': [
            _msp(_P_CUALIDAD + ' ' + _P_CICLO + ' ' + _P_USOS + ' Anexo 3, plantas protectoras (p. 66); '
                 'tipos de siembra: plántulas (p. 45).',
                 ['otros_nombres', 'ciclo', 'cualidad_ancestral', 'usos_documentados']),
            {
                'autor': 'Royal Botanic Gardens, Kew',
                'titulo': 'Plants of the World Online: Urtica dioica L.',
                'url': 'https://powo.science.kew.org/taxon/260630-2',
                'referencia': 'Nombre aceptado; familia; introducida en Ecuador.',
                'campos': ['nombre_cientifico', 'familia', 'observaciones'],
            },
            {
                'autor': 'European Medicines Agency (EMA), HMPC',
                'titulo': 'Community herbal monograph on Urtica dioica L.; Urtica urens L., folium. '
                          'EMA/HMPC/508015/2007 (14-01-2010)',
                'url': 'https://www.ema.europa.eu/en/documents/herbal-monograph/'
                       'final-community-herbal-monograph-urtica-dioica-l-urtica-urens-l-folium_en.pdf',
                'referencia': 'Secciones 4.1, 4.2, 4.3, 4.4 y 4.6.',
                'campos': ['parte_utilizada', 'usos_documentados', 'contraindicaciones'],
            },
            _tinitana(['otros_nombres', 'parte_utilizada', 'usos_documentados']),
            _gbif(7960979, 'Urtica dioica', ['altitud_msnm', 'provincias_ecuador']),
            {
                'autor': 'Dominicus Johannes Bergsma',
                'titulo': 'Brandnetel, Urtica dioica, Locatie, Famberhorst.jpg',
                'url': 'https://commons.wikimedia.org/wiki/File:Brandnetel,_Urtica_dioica,_Locatie,_Famberhorst.jpg',
                'referencia': 'CC BY-SA 4.0 - https://creativecommons.org/licenses/by-sa/4.0/. Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/ortiga.jpg'],
            },
        ],
        'campos_no_verificados': [
        ],
        'observaciones': (
            'En Ecuador «ortiga» y «chine» se aplican a Urtica dioica y a Urtica '
            'urens; la monografía de EMA cubre la hoja de ambas. Se eligió U. '
            'dioica; confirmar con el material del curso. La altitud se basa en '
            'pocos ejemplares y es aproximada. La advertencia sobre pelos '
            'urticantes es una precaución de manipulación, no de consumo.'
        ),
    },
    # ------------------------------------------------------------------ M2-06
    {
        'codigo': 'violeta',
        'nombre_comun': 'Violeta',
        'nombre_cientifico': 'Viola odorata L.',
        'otros_nombres': ['Violeta de jardín'],
        'familia': 'Violaceae',
        'altitud_msnm': None,
        'provincias_ecuador': [
            'Azuay', 'Cañar', 'Chimborazo', 'Galápagos', 'Loja', 'Pichincha',
        ],
        'ciclo': 'largo',
        'cualidad_ancestral': 'fria',
        'parte_utilizada': ['Flor', 'Hoja'],
        'usos_documentados': (
            'En mercados del sur de Ecuador se venden flor y hoja para uso oral. '
            'Tiene reputación popular para la tos y afecciones respiratorias; '
            'también se mencionan molestias digestivas y ayuda para el sueño. '
            'Son usos tradicionales, no indicaciones comprobadas.'
        ),
        'contraindicaciones': (
            'Durante embarazo y lactancia no hay información fiable suficiente: '
            'evitar su uso (Departamento de Salud de Abu Dabi). Resumen parcial; '
            'no se encontró una monografía oficial para esta especie.'
        ),
        'imagen_ruta': 'img/plantas/violeta.jpg',
        'imagen_autor': 'AnRo0002',
        'imagen_fuente': 'https://commons.wikimedia.org/wiki/File:20130407Viola_odorata1.jpg',
        'imagen_licencia': 'CC0 1.0 - https://creativecommons.org/publicdomain/zero/1.0/ (dominio público)',
        'fuentes': [
            {
                'autor': 'Kušen M., Vokurka A., Židovec V.',
                'titulo': 'Sweet Violet (Viola odorata L.): Botanical, Horticultural, Pharmacological, '
                          'and Economic Aspects. Plants 15(18), 2747 (2026). DOI 10.3390/plants15182747',
                'url': 'https://www.mdpi.com/2223-7747/15/18/2747',
                'referencia': 'Sección 7, Propagation and Cultivation: las plantas sembradas en otoño '
                              '«do not flower in the first year».',
                'campos': ['ciclo'],
            },
            _msp(_P_CUALIDAD, ['cualidad_ancestral']),
            {
                'autor': 'Royal Botanic Gardens, Kew',
                'titulo': 'Plants of the World Online: Viola odorata L.',
                'url': 'https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:868828-1',
                'referencia': 'Nombre aceptado; familia; nativa de Europa a Irán; introducida en Ecuador.',
                'campos': ['nombre_cientifico', 'familia', 'observaciones'],
            },
            _tinitana(['otros_nombres', 'parte_utilizada', 'usos_documentados']),
            {
                'autor': 'Department of Health - Abu Dhabi',
                'titulo': 'Medicinal plants: Viola odorata (ficha educativa)',
                'url': 'https://medicinalplants.doh.gov.ae/Public-education-plants-leaflets/Viola-odorata',
                'referencia': 'Partes usadas, usos tradicionales y advertencias.',
                'campos': ['usos_documentados', 'contraindicaciones'],
            },
            _gbif(5331181, 'Viola odorata', ['provincias_ecuador']),
            {
                'autor': 'AnRo0002',
                'titulo': '20130407Viola odorata1.jpg',
                'url': 'https://commons.wikimedia.org/wiki/File:20130407Viola_odorata1.jpg',
                'referencia': 'CC0 1.0 - https://creativecommons.org/publicdomain/zero/1.0/ (dominio público). Copia reducida a 1200 px (static/img/plantas). Metadatos consultados el 24 de octubre de 2026.',
                'campos': ['static/img/plantas/violeta.jpg'],
            },
        ],
        'campos_no_verificados': [
            'altitud_msnm',
        ],
        'observaciones': (
            'Ciclo: el MSP (p. 48) llama de ciclo corto a las plantas listas para cosechar en 6 a 8 semanas desde la siembra. Sembrada de semilla, la violeta no florece el primer año (Kušen et al. 2026); como se usa la flor, se clasifica como largo. '
            'Violeta de olor, introducida y cultivada en Ecuador. No confundir '
            'con la violeta africana (Saintpaulia), que es ornamental, ni con el '
            'pensamiento (Viola tricolor), que tiene otra monografía. Para la '
            'foto, Doménica debe buscar Viola odorata. La altitud queda pendiente: '
            'los ejemplares de GBIF van de 10 a 3000 m, mezclando Galápagos y '
            'jardines andinos, y no describen bien la especie.'
        ),
    },
]
