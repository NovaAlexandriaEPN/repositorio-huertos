"""Las 13 actividades del alcance V1 y su guía ancestral (entrega de Matthew, M2-07).

Formato del modelo catalogo.TipoActividad integrado en la rama bryan: los campos
instrucciones, materiales y precauciones son texto. Alcance, puntos y
repetibilidad son los del alcance 1.4 y no se cambian.

Solo hay dos condiciones OBLIGATORIAS (alcance 1.4, sección 5): 15 días entre
preparación y siembra, y 10 días entre el inicio del secado y el empaquetado.
Aparecen al inicio de las instrucciones con la palabra «Obligatorio». Las horas
y fases lunares son recomendaciones: nunca bloquean un registro.

Fuente principal: MSP (2017), Implementación de huertos medicinales en los
establecimientos de salud del primer nivel de atención. Lineamientos. Las
páginas citadas son las impresas en el pie del documento. Se resume el texto sin
añadir instrucciones propias. Por decisión del equipo se omiten las
indicaciones que restringen la participación de personas por condiciones
personales (p. 47).
"""

MSP = "MSP (2017). Implementación de huertos medicinales en los establecimientos de salud del primer nivel de atención. Lineamientos. Quito"
FUENTE_ALCANCE = {"autor": "Equipo Nova Alexandria", "titulo": "Alcance V1, sección 5", "referencia": "docs/v1/01_Alcance_V1_Huertos_Medicinales.md (condiciones obligatorias)"}


def _msp(paginas):
    return {"autor": "Ministerio de Salud Pública del Ecuador", "titulo": MSP, "referencia": "Archivo del aula virtual; " + paginas}


ACTIVIDADES = [
    dict(
        codigo='preparacion', nombre='Preparación de la tierra', alcance='huerto',
        puntos_base=10, repetible=False,
        instrucciones='Obligatorio: Deben pasar al menos 15 días entre la preparación de la tierra y la siembra.\nLimpiar y abonar el terreno para que la tierra transforme los restos vegetales en abono natural antes de sembrar.\n1. Retirar la maleza con machete, azadón o pala en un día de mucho sol.\n2. Esparcir la maleza desmenuzada sobre el terreno para que se convierta en abono (el MSP lo prefiere a quemarla).\n3. Si el terreno es pobre en nutrientes, añadir abono orgánico vegetal o estiércol que haya pasado por secado al sol.\n4. Remover la tierra a mano con azadón o pala, o con yunta.\n5. Dejar reposar la tierra 15 días para que el abono se desintegre.\n6. Después del reposo, hacer surcos; terrazas si el terreno está en ladera, o camadas y camellones si el suelo es pantanoso.',
        materiales='Machete; Azadones; Palas de mano; Rastrillos; Abono orgánico (si el suelo es pobre).',
        precauciones='Si se usa tractor, no remover la tierra de forma profunda. Los abonos añadidos deben haber pasado por un secado al sol.',
        hora_recomendada='Un día de mucho sol.',
        fase_recomendada='Luna oscura (Yana Killa), tiempo de transformación de la materia orgánica.',
        fuentes=[_msp('«Preparación de la tierra» (p. 33-34); Tabla 4, materiales (p. 36).'), FUENTE_ALCANCE],
    ),
    dict(
        codigo='diseno', nombre='Elaboración del diseño', alcance='huerto',
        puntos_base=10, repetible=False,
        instrucciones='Dar forma al huerto según el espacio disponible, la región, el clima y la cultura local.\n1. Elegir el diseño según el espacio: surcos, camadas, camellones o terrazas en tierra; diseños verticales, colgantes o maceteros en espacios urbanos.\n2. En ladera, construir terrazas o andenes; en terreno cenagoso, camellones (inka wachu).\n3. Trazar los surcos con estacas y piola; en ladera, siempre de forma transversal.\n4. Para huertos urbanos, elegir el lugar con más horas de sol directo y recipientes que permitan crecer a las raíces (macetas, botellas, caña guadua, neumáticos usados).\n5. Dejar una toma de agua cerca del huerto.',
        materiales='Estacas de madera; Piola o cuerda; Macetas; Botellas de plástico vacías; Neumáticos usados.',
        precauciones='Nunca trazar los surcos en sentido vertical en una ladera. Si el huerto está junto a un río, asegurarse de que no se anegue con una creciente. La orientación Este-Oeste es opcional.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Identificación del espacio físico» (p. 23); «Diseño de los huertos medicinales» (p. 32-33); «Técnicas de siembra» (p. 37); «Iniciativas de huertos medicinales en espacios urbanos» (p. 41-42); Tabla 9 (p. 53).')],
    ),
    dict(
        codigo='ritual', nombre='Ritual de siembra', alcance='huerto',
        puntos_base=10, repetible=False,
        instrucciones='Ceremonia de «pago a la tierra» para despertar, alimentar y fortalecer a la madre tierra y bendecir semillas, estacas y plántulas antes de sembrar.\n1. Cada participante toma una pequeña porción de tierra con sus manos.\n2. Formar un círculo y poner en el centro una manta con las semillas y un plato de barro.\n3. Rodear la manta con pétalos o flores del lugar y colocar, hacia la salida del sol, un recipiente con carbón encendido y palo santo.\n4. El oficiante saluda y ofrece una oración de gratitud a la madre tierra; luego pone su tierra en el plato y lo pasa a la persona de su derecha.\n5. Cada participante repite el gesto con sus propias palabras hasta cerrar el círculo.\n6. El oficiante da consejos sobre la relación con la naturaleza y cierra con un agradecimiento.',
        materiales='Plato de barro; Porción de tierra por participante; Flores del lugar o chagrillo; Carbón; Palo santo; Recipiente para sahumar; Fósforos; Manta de 1 m x 1 m blanca o de colores vivos.',
        precauciones='Lo dirigen hombres y mujeres de sabiduría o personas espirituales del lugar. El proceso es un ejemplo: se respetan los símbolos, colores y rituales propios de cada nacionalidad y pueblo.',
        hora_recomendada='Con la salida del sol (en la mañana o al medio día).',
        fase_recomendada='Cuarto creciente o luna llena.',
        fuentes=[_msp('«Rituales de siembra», Tabla 7 (p. 42-43); «Tiempos ideales para la siembra» (p. 45-46).')],
    ),
    dict(
        codigo='siembra', nombre='Siembra', alcance='planta',
        puntos_base=15, repetible=False,
        instrucciones='Obligatorio: Deben pasar al menos 15 días desde la preparación de la tierra.\nSembrar la especie con el método elegido: semillas, estacas, esquejes o plántulas.\n1. Sembrar después del ritual de siembra.\n2. Semillas: preferir semillas de la región, ya adaptadas al entorno.\n3. Estacas: en surco, abrir un hoyo de unos 10 cm con un barretón, poner la estaca, cubrirla con tierra y regar con abundante agua; en maceta, usar tierra con abono.\n4. Esquejes: cortar con tijera podadora una rama con yemas, quitar la mayoría de hojas, ponerla en agua con un poco de abono líquido y trasplantarla cuando salgan raíces.\n5. Plántulas: germinar la semilla en el suelo o en una bolsa negra con tierra y abono, y trasplantarla al suelo o a una maceta.\n6. En surcos, poner en la parte alta las plantas que necesitan menos agua y en la parte baja las que necesitan más.',
        materiales='Semillas, estacas, esquejes o plántulas; Barretón de metal; Tijera podadora; Macetas; Abono líquido (para esquejes).',
        precauciones='Regar con agua sin cloro; si tiene cloro, dejarla reposar una noche. Las mejores aguas son de vertiente y de lluvia.',
        hora_recomendada='Desde las 08:00 o 09:00, después del ritual.',
        fase_recomendada='Cuarto creciente o luna llena.',
        fuentes=[_msp('«Técnicas de siembra» (p. 37); «Rituales de siembra» (p. 42); «Tipos de siembra» (p. 44-45); «Tiempos ideales para la siembra» (p. 45-46); Tabla 9 (p. 53).'), FUENTE_ALCANCE],
    ),
    dict(
        codigo='senaletica', nombre='Señalética', alcance='planta',
        puntos_base=5, repetible=False,
        instrucciones='Identificar cada espacio o clase de planta con un letrero después de la siembra.\n1. Preparar un letrero con: nombre en idioma indígena local, nombre vulgar, nombre científico, familia y uso general.\n2. Pintar el color de la cualidad: rojo para plantas calientes; verde o blanco para plantas frías o frescas.\n3. Colocar el letrero en el espacio de la planta después de la siembra.',
        materiales='Tablas triplex; Tirantes de madera de 1 m; Clavos de 2 pulgadas; Pintura de caucho (amarillo, azul y rojo); Brocha y pincel.',
        precauciones='La correspondencia de colores es la del mundo kichwa andino; se recomienda investigar con los involucrados la que corresponde en cada territorio.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Señalética», Gráfico 1 (p. 46-47); Tabla 9 (p. 53-54).')],
    ),
    dict(
        codigo='cuidados', nombre='Cuidados de crecimiento', alcance='planta',
        puntos_base=5, repetible=True,
        instrucciones='Cuidar los brotes durante el crecimiento.\n1. Deshierbar alrededor de las plantas.\n2. Replantar: reponer las plantas que han perecido.\n3. Aporcar las plantas.\n4. Colocar ceniza de fogón o cal alrededor de cada planta para prevenir plagas.',
        materiales='Ceniza de fogón o cal.',
        precauciones='No fumigar con ningún producto natural ni industrial; se usan cultivos asociados que se protegen entre sí. Solo entra al huerto el personal involucrado; evitar ruidos y tránsito frecuente.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Cuidados de las plantas en su etapa de crecimiento» (p. 47); Tabla 9 (p. 54).')],
    ),
    dict(
        codigo='riego', nombre='Riego', alcance='planta',
        puntos_base=5, repetible=True,
        instrucciones='Dar agua suficiente a las raíces sin maltratar las plantas.\n1. Regar por los surcos cuando haya agua de riego.\n2. Con manguera, ponerla en el suelo y dejar que el chorro moje la tierra.\n3. En huertos urbanos o sin facilidades de riego, usar regadera.',
        materiales='Manguera de 1/2 pulgada (unos 20 m); Regadera de aluminio.',
        precauciones='No asperjar chorros sobre las plantas como lluvia: las maltrata. Usar agua sin cloro.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Cuidados… Riego» (p. 47); «Tipos de siembra» (p. 44); espacios urbanos (p. 42); Tabla 9 (p. 54).')],
    ),
    dict(
        codigo='bano', nombre='Baño de la planta', alcance='planta',
        puntos_base=5, repetible=False,
        instrucciones='Regar y «limpiar» las plantas antes de la cosecha.\n1. Uno o dos días antes de la cosecha, regar las plantas; se puede usar regadera para limpiar sus impurezas.\n2. Mientras se baña a las plantas, «conversar» con ellas pidiendo su participación en la sanación.',
        materiales='Regadera.',
        precauciones='Las plantas que se van a secar se lavan en este momento, no después de cosecharlas: si se lavan después, se pudren.',
        hora_recomendada='Uno o dos días antes de la cosecha.',
        fase_recomendada='',
        fuentes=[_msp('«Cosecha ritual de las plantas medicinales» (p. 48); «Limpieza de las plantas cosechadas» (p. 50).')],
    ),
    dict(
        codigo='gratitud', nombre='Ritual de gratitud', alcance='planta',
        puntos_base=10, repetible=False,
        instrucciones='Agradecer a la madre tierra antes de cosechar, con la comunidad y el personal de salud.\n1. El oficiante hace un hoyo pequeño en el suelo.\n2. Cada participante recoge cerca ramitas, flores, frutos o semillas sin dañar las plantas.\n3. En círculo, el oficiante saluda, prende el fuego ceremonial y sahúma el huerto agradeciendo por las plantas.\n4. Cada participante besa lo que recogió y lo pone en el hoyo.\n5. El oficiante agradece, sahúma el hoyo, pone un poco de agua y lo cubre.',
        materiales='Pala; Palo santo o incienso; Carbón; Recipiente para quemar carbón; Agua; Fósforos; Manta blanca o de color vivo; Pétalos de flores (chagrillo).',
        precauciones='Al recoger ofrendas, tomar solo hojas o flores, sin dañar la planta.',
        hora_recomendada='Al amanecer, de 05:00 a 07:00.',
        fase_recomendada='',
        fuentes=[_msp('«Cosecha ritual…», Tabla 8 «Ritual de cosecha» (p. 48-49).')],
    ),
    dict(
        codigo='cosecha', nombre='Cosecha', alcance='planta',
        puntos_base=20, repetible=False,
        instrucciones='Recolectar la parte utilizada de la planta.\n1. Esperar a que el sol seque el rocío de la mañana.\n2. Cosechar a mano, tomando solo las partes que se requieren (hojas, flores o frutos).\n3. Cosechar la planta entera solo si se necesitan las raíces.\n4. Al cosechar, pedir a la planta que sea efectiva en las terapias.',
        materiales='Podadora de plantas; Hoz (cuando no se cosechan raíces).',
        precauciones='Las plantas medicinales no se cosechan con humedad. Ciclo corto: listas en unas 6 a 8 semanas desde la siembra; ciclo largo: tardan mucho más.',
        hora_recomendada='Cuando el sol ya secó el rocío, aproximadamente desde las 08:00.',
        fase_recomendada='Cuarto creciente o luna llena para hojas, flores y frutos; cuarto menguante para semillas y raíces.',
        fuentes=[_msp('«Tiempos ideales…» (p. 46); «Cosecha ritual de las plantas medicinales» (p. 48-49); Tabla 9 (p. 54).')],
    ),
    dict(
        codigo='limpieza', nombre='Limpieza de plantas', alcance='planta',
        puntos_base=5, repetible=False,
        instrucciones='Limpiar a mano la cosecha y separar las partes que se usarán.\n1. Hacer una limpieza manual exhaustiva.\n2. Escoger las partes a usarse: planta entera, hojas, tallos, raíces, flores o frutos.\n3. Colocar las partes limpias en lavacaras o cajones para el secado.',
        materiales='Lavacaras o cajones de plástico.',
        precauciones='No lavar las plantas después de cosecharlas: se pudren.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Limpieza de las plantas cosechadas» (p. 50); Tabla 9 (p. 54).')],
    ),
    dict(
        codigo='secado', nombre='Secado', alcance='planta',
        puntos_base=10, repetible=False,
        instrucciones='Obligatorio: Deben pasar al menos 10 días entre el inicio del secado y el empaquetado.\nSecar la cosecha a la sombra.\n1. Hojas, raíces y flores: ponerlas en un estante sobre papel periódico, a la sombra.\n2. Plantas completas: colgarlas a la sombra con la raíz hacia arriba.\n3. Usar un espacio seco, con techo y con corriente de aire.\n4. Dejar secar de 10 a 15 días, según las condiciones del lugar.',
        materiales='Cuerda, piola de algodón o alambre de acero delgado; Estante o mesa de madera; Papel periódico.',
        precauciones='No secar al sol. El lugar debe estar libre de animales y lejos de cuyeras, chancheras, corrales, establos y panales.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Identificación del espacio para el secado» (p. 25); «Secado de las plantas medicinales» (p. 50-51); Tabla 9 (p. 54-55).'), FUENTE_ALCANCE],
    ),
    dict(
        codigo='empaquetado', nombre='Empaquetado y etiquetado', alcance='planta',
        puntos_base=15, repetible=False,
        instrucciones='Obligatorio: Deben pasar al menos 10 días desde el inicio del secado.\nEmpacar la planta seca, etiquetarla y almacenarla.\n1. Cuando las hojas estén secas, empacarlas en fundas plásticas cerradas herméticamente, de 100 g por unidad.\n2. Etiquetar con: nombre en idioma de la nacionalidad, nombre popular, nombre científico, familia, peso, indicaciones de uso, contraindicación, fecha de empaquetado, fecha de caducidad y cualidad caliente o fría.\n3. Almacenar en un lugar fresco y seco, separando las plantas calientes y frías.',
        materiales='Bolsas de plástico transparentes; Balanza digital; Selladora eléctrica; Papel para etiquetas; Estante de madera.',
        precauciones='Caducidad: hasta 12 meses en la Sierra y 6 meses en la Costa y la Amazonía. Revisar los empaques: su conservación depende de la calidad del secado. La etiqueta del MSP incluye dosificación; la aplicación no indica dosis.',
        hora_recomendada='',
        fase_recomendada='',
        fuentes=[_msp('«Etiquetado» y «Caducidad» (p. 51-52); «Empacado y almacenaje» (p. 52); Tabla 9 (p. 55).'), FUENTE_ALCANCE],
    ),
]

# Tipos de EventoLunar (nueva, creciente, llena, menguante) a los que se refiere
# fase_recomendada; el calendario los usa para mostrar recomendaciones.
FASES_RECOMENDADAS = {'cosecha': ['creciente', 'llena', 'menguante'],
 'preparacion': ['nueva'],
 'ritual': ['creciente', 'llena'],
 'siembra': ['creciente', 'llena']}
