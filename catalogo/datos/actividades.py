"""Reglas V1. La guía de dominio ampliada y sus fuentes quedan a cargo de su entrega."""
FUENTE = {"titulo": "Alcance V1, secciones 5 y 7", "referencia": "docs/v1/01_Alcance_V1_Huertos_Medicinales.md"}
# código, nombre, alcance, puntos, instrucción breve de integración
FILAS = [
    ("preparacion", "Preparación de la tierra", "huerto", 10, "Preparar la tierra. Esperar al menos 15 días antes de sembrar."),
    ("diseno", "Elaboración del diseño", "huerto", 10, "Registrar el diseño elegido antes de iniciar las siembras."),
    ("ritual", "Ritual de siembra", "huerto", 10, "Registrar el ritual antes de iniciar las siembras. El amanecer es una recomendación."),
    ("siembra", "Siembra", "planta", 15, "Usar el método de la selección. Exige preparación al menos 15 días antes."),
    ("senaletica", "Señalética", "planta", 5, "Identificar la planta y consultar su cualidad ancestral en la ficha."),
    ("cuidados", "Cuidados de crecimiento", "planta", 5, "Registrar los cuidados de crecimiento mientras esté sembrada o creciendo."),
    ("riego", "Riego", "planta", 5, "Registrar el riego mientras esté sembrada o creciendo."),
    ("bano", "Baño de la planta", "planta", 5, "Consultar la guía ancestral antes de realizar el baño de una planta en crecimiento."),
    ("gratitud", "Ritual de gratitud", "planta", 10, "Registrar la gratitud mientras la planta esté creciendo."),
    ("cosecha", "Cosecha", "planta", 20, "Cosechar después del crecimiento según la parte utilizada en la ficha."),
    ("limpieza", "Limpieza de plantas", "planta", 5, "Registrar la limpieza de lo cosechado."),
    ("secado", "Secado", "planta", 10, "Iniciar el secado a la sombra después de cosechar."),
    ("empaquetado", "Empaquetado y etiquetado", "planta", 15, "Empaquetar y etiquetar al menos 10 días después del inicio del secado."),
]
ACTIVIDADES = [dict(codigo=c, nombre=n, alcance=a, puntos_base=p,
    repetible=c in {"cuidados", "riego"}, instrucciones=i,
    fuentes=[FUENTE], materiales="Pendiente de completar con el material del curso.",
    precauciones="Información educativa. Revisar la ficha y la guía del curso antes de actuar.")
    for c, n, a, p, i in FILAS]
