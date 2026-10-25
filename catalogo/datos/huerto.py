"""Opciones del configurador y recomendaciones de materiales (entrega M2-09).

- OPCIONES responde a «¿qué elegimos para el huerto?» (diseño, cerca,
  suelo, agua y abono). Bryan las usa en el configurador: diseño y abono son
  elecciones múltiples; cerca, suelo y agua son únicas.
- Los métodos de siembra no son opciones: son los códigos de
  catalogo.models.MetodoSiembra (semillas, estacas, esquejes, plantulas).
- MATERIALES responde a «¿qué herramienta o material necesitamos?». Juan los
  carga; la marca de «disponible» de una comunidad va en
  comunidades.MarcaMaterial (Bryan), no aquí.

`metodos_siembra` de un material lista códigos de METODOS_SIEMBRA. Lista vacía =
común a todos los métodos. Así, elegir un método devuelve sus materiales específicos
más los comunes, sin duplicar ninguno (ver servicios.materiales_para_metodo).

Fuentes de las explicaciones (páginas impresas del documento del MSP):
- MSP (2017), Lineamientos para la implementación de huertos medicinales:
  espacio físico y orientación (p. 23), suelos, Tabla 1 (p. 24), bodega
  (p. 24), cercas (p. 30-31 y Tabla 4, p. 35-36), abonos (p. 31-32),
  diseño (p. 32-33 y 41-42), tipos de siembra (p. 44-45), riego (p. 47) y
  materiales de las Tablas 4 y 9 (p. 35-36 y 53-55).
- Definición del proyecto «Huertos medicinales comunitarios», ISWD652 2026B:
  ejemplos de diseños, cercas, agua y bodega.
"""

FUENTES_HUERTO = [
    {
        'autor': 'Ministerio de Salud Pública del Ecuador (MSP), Dirección Nacional de Salud Intercultural',
        'titulo': 'Implementación de huertos medicinales en los establecimientos de salud del primer '
                  'nivel de atención. Lineamientos, 1.ª ed., Quito (2017)',
        'url': None,
        'referencia': 'p. 23-24, 30-33, 35-36, 41-47 y 53-55.',
    },
    {
        'autor': 'ISWD652 Calidad de Software, período 2026B',
        'titulo': 'Definición del proyecto «Huertos medicinales comunitarios»',
        'url': None,
        'referencia': 'Registro del huerto real y espacio de bodega (p. 1).',
    },
]

METODOS_SIEMBRA = ['semillas', 'estacas', 'esquejes', 'plantulas']

OPCIONES = [
    # Diseño (múltiple). Ejemplos: Definición del proyecto; MSP p. 32-33 y 41-42.
    {'codigo': 'diseno-tierra', 'categoria': 'diseno', 'nombre': 'Tierra',
     'explicacion': 'Siembra en el suelo: surcos, camadas, camellones o terrazas.'},
    {'codigo': 'diseno-vertical', 'categoria': 'diseno', 'nombre': 'Vertical',
     'explicacion': 'Plantas en las paredes, aprovechando espacios urbanos pequeños.'},
    {'codigo': 'diseno-colgante', 'categoria': 'diseno', 'nombre': 'Colgante',
     'explicacion': 'Recipientes colgados de techos o paredes, por ejemplo con botellas recicladas.'},
    {'codigo': 'diseno-piso', 'categoria': 'diseno', 'nombre': 'Piso',
     'explicacion': 'Maceteros, botellas o llantas en patios, terrazas, gradas, balcones o filos de ventana.'},

    # Cerca (única). MSP p. 30-31 y Tabla 4; ejemplos de la Definición del proyecto.
    {'codigo': 'cerca-viva', 'categoria': 'cerca', 'nombre': 'Viva',
     'explicacion': 'Siembra de plantas ornamentales, frutales, arbustos y árboles energéticos, '
                    'como higuerilla, marco, floripondio, agave o lavanda.'},
    {'codigo': 'cerca-natural', 'categoria': 'cerca', 'nombre': 'Natural',
     'explicacion': 'Materiales propios del lugar: tapial, bahareque, bejucos, carrizos, caña guadua o piedras.'},
    {'codigo': 'cerca-reciclada', 'categoria': 'cerca', 'nombre': 'Reciclada',
     'explicacion': 'Verja con materiales reciclados: alambres, tablas, botellas de plástico o neumáticos.'},
    {'codigo': 'cerca-metalica', 'categoria': 'cerca', 'nombre': 'Metálica',
     'explicacion': 'Cortavientos, mallas metálicas o alambre de púas con postes de madera o cemento.'},
    {'codigo': 'cerca-convencional', 'categoria': 'cerca', 'nombre': 'Convencional',
     'explicacion': 'Cerramiento con materiales de construcción: varillas, bloques, ladrillos, piedra o cemento.'},

    # Suelo (única). MSP Tabla 1 «Cultivos según tipos de suelos» (p. 24).
    {'codigo': 'suelo-arcilloso', 'categoria': 'suelo', 'nombre': 'Arcilloso',
     'explicacion': 'Al humedecerse no deja pasar el agua ni el aire; requiere drenaje. '
                    'Ejemplos: menta, toronjil.'},
    {'codigo': 'suelo-limoso', 'categoria': 'suelo', 'nombre': 'Limoso',
     'explicacion': 'Contiene limo o material arrastrado por los ríos; está cerca de sus lechos. '
                    'Ejemplo: ortiga.'},
    {'codigo': 'suelo-arenoso', 'categoria': 'suelo', 'nombre': 'Arenoso',
     'explicacion': 'No retiene el agua y requiere riego abundante. Ejemplos: salvia, romero, lavanda.'},
    {'codigo': 'suelo-margoso', 'categoria': 'suelo', 'nombre': 'Margoso',
     'explicacion': 'Contiene arcilla, limo y arena con material vegetal. Ejemplos: albahaca, milenrama.'},
    {'codigo': 'suelo-gredoso', 'categoria': 'suelo', 'nombre': 'Gredoso',
     'explicacion': 'Suelo ligero y con facilidad de drenaje. Ejemplos: orégano, cedrón.'},
    {'codigo': 'suelo-pantanoso', 'categoria': 'suelo', 'nombre': 'Pantanoso',
     'explicacion': 'Suelo cubierto con agua, cenagoso; se siembra en camellones. '
                    'Ejemplos: cola de caballo, berros.'},

    # Fuente de agua (única). Definición del proyecto; MSP p. 47.
    {'codigo': 'agua-rio', 'categoria': 'agua', 'nombre': 'Río',
     'explicacion': 'Agua tomada de un río; asegurarse de que el huerto no se anegue con una creciente.'},
    {'codigo': 'agua-canal', 'categoria': 'agua', 'nombre': 'Canal',
     'explicacion': 'Agua de riego conducida por un canal; permite regar por los surcos.'},
    {'codigo': 'agua-goteo', 'categoria': 'agua', 'nombre': 'Goteo',
     'explicacion': 'Riego por goteo. El MSP recomienda mojar el suelo y no asperjar chorros sobre las plantas.'},
    {'codigo': 'agua-otro', 'categoria': 'agua', 'nombre': 'Otro',
     'explicacion': 'Otra fuente, como grifo con regadera o agua de lluvia; preferir agua sin cloro.'},

    # Abono (múltiple). MSP «Elaboración de abono natural» (p. 31-32).
    {'codigo': 'abono-barbecho', 'categoria': 'abono', 'nombre': 'Barbecho',
     'explicacion': 'Restos de plantas que se incorporan a la tierra y reposan al menos 15 días para '
                    'transformarse en abono.'},
    {'codigo': 'abono-restos-vegetales', 'categoria': 'abono', 'nombre': 'Restos vegetales',
     'explicacion': 'Restos de la siembra anterior, rastrojo, ramas o restos de cocina, tapados 15 días.'},
    {'codigo': 'abono-hojas', 'categoria': 'abono', 'nombre': 'Hojas',
     'explicacion': 'Hojas de plantas que aportan nitrógeno, como chochos, fréjol, habas, lentejas o alfalfa.'},
    {'codigo': 'abono-compost', 'categoria': 'abono', 'nombre': 'Compost',
     'explicacion': 'Abono orgánico elaborado en un espacio cerca del huerto.'},
]

MATERIALES = [
    # Herramientas e implementos (comunes). Definición del proyecto; MSP Tablas 4 y 9.
    {'codigo': 'pala', 'nombre': 'Pala', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para retirar maleza y remover la tierra en la preparación.'},
    {'codigo': 'azadon', 'nombre': 'Azadón', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para remover la tierra a mano y abrir surcos.'},
    {'codigo': 'rastrillo', 'nombre': 'Rastrillo', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para emparejar la tierra preparada.'},
    {'codigo': 'machete', 'nombre': 'Machete', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para retirar la maleza.'},
    {'codigo': 'regadera', 'nombre': 'Regadera de aluminio', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para regar cuando no hay facilidades de riego y para el baño de las plantas.'},
    {'codigo': 'manguera', 'nombre': 'Manguera', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para regar con el chorro en el suelo, sin asperjar las plantas.'},
    {'codigo': 'podadora', 'nombre': 'Tijera podadora', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para cosechar ramas y flores.'},
    {'codigo': 'hoz', 'nombre': 'Hoz', 'grupo': 'herramientas', 'metodos_siembra': [],
     'recomendacion': 'Para cosechar cuando no se necesitan las raíces.'},
    {'codigo': 'barreton', 'nombre': 'Barretón de metal', 'grupo': 'herramientas',
     'metodos_siembra': ['estacas'],
     'recomendacion': 'Para abrir un hoyo de unos 10 cm y sembrar estacas en surco.'},
    {'codigo': 'estacas-piola', 'nombre': 'Estacas de madera y piola', 'grupo': 'herramientas',
     'metodos_siembra': [],
     'recomendacion': 'Para trazar surcos y camellones.'},

    # Material de siembra (específico por método). MSP «Tipos de siembra» y Tabla 9.
    {'codigo': 'semillas', 'nombre': 'Semillas', 'grupo': 'siembra', 'metodos_siembra': ['semillas'],
     'recomendacion': 'Preferir semillas de la región, ya adaptadas al entorno.'},
    {'codigo': 'estacas', 'nombre': 'Estacas', 'grupo': 'siembra', 'metodos_siembra': ['estacas'],
     'recomendacion': 'Pedazos de tallo con yema de la planta madre.'},
    {'codigo': 'esquejes', 'nombre': 'Esquejes', 'grupo': 'siembra', 'metodos_siembra': ['esquejes'],
     'recomendacion': 'Ramas con yemas, puestas en agua con un poco de abono líquido hasta que echen raíces.'},
    {'codigo': 'plantulas', 'nombre': 'Plántulas', 'grupo': 'siembra', 'metodos_siembra': ['plantulas'],
     'recomendacion': 'Plantas germinadas listas para trasplantar.'},
    {'codigo': 'bolsas-germinacion', 'nombre': 'Bolsas negras con tierra y abono', 'grupo': 'siembra',
     'metodos_siembra': ['plantulas'],
     'recomendacion': 'Para germinar la semilla antes del trasplante.'},
    {'codigo': 'macetas', 'nombre': 'Macetas, botellas o neumáticos', 'grupo': 'siembra',
     'metodos_siembra': [],
     'recomendacion': 'Recipientes para huertos urbanos; deben dejar crecer las raíces.'},

    # Abonos (comunes). MSP «Elaboración de abono natural».
    {'codigo': 'abono-organico', 'nombre': 'Abono orgánico', 'grupo': 'abonos', 'metodos_siembra': [],
     'recomendacion': 'Abono vegetal o estiércol secado al sol, para suelos pobres.'},
    {'codigo': 'abono-liquido', 'nombre': 'Abono líquido (purín)', 'grupo': 'abonos', 'metodos_siembra': [],
     'recomendacion': 'Preparado con ortiga, marco y agua sin cloro; se aplica alrededor de las plantas.'},
]

# Orientaciones que muestra el configurador (alcance 1.4, secciones 3 y 9).
RECOMENDACION_ORIENTACION = 'Orientación Este-Oeste (opcional; MSP p. 23).'
RECOMENDACION_BODEGA = (
    'Bodega para herramientas, semillas y abonos: seca, ventilada, con abundante luz '
    'natural, seguridades adecuadas y espacio para las plantas secas empacadas '
    '(MSP p. 24; alcance 1.4, sección 9).'
)

# Nota de carga: cargar_catalogo solo crea códigos nuevos. En una base que ya
# cargó la lista inicial de integración (6 materiales genéricos), estos 18 se
# añaden sin borrar aquellos; para la demo conviene una base nueva.
