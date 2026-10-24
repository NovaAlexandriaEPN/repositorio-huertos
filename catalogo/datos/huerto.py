"""Opciones del alcance V1 y lista inicial de materiales para integrar el recorrido."""
CATEGORIAS = {
    "diseno": [("tierra", "Tierra"), ("vertical", "Vertical"), ("colgante", "Colgante"), ("piso", "Piso")],
    "cerca": [("viva", "Viva"), ("natural", "Natural"), ("reciclada", "Reciclada"), ("metalica", "Metálica"), ("convencional", "Convencional")],
    "suelo": [("arcilloso", "Arcilloso"), ("limoso", "Limoso"), ("arenoso", "Arenoso"), ("margoso", "Margoso"), ("gredoso", "Gredoso"), ("pantanoso", "Pantanoso")],
    "agua": [("rio", "Río"), ("canal", "Canal"), ("goteo", "Goteo"), ("otro", "Otro")],
    "abono": [("barbecho", "Barbecho"), ("restos-vegetales", "Restos vegetales"), ("hojas", "Hojas"), ("compost", "Compost")],
}
OPCIONES = [dict(codigo=f"{categoria}-{codigo}", categoria=categoria, nombre=nombre)
    for categoria, filas in CATEGORIAS.items() for codigo, nombre in filas]
MATERIALES = [
    dict(codigo="herramientas", nombre="Herramientas e implementos", grupo="herramientas", recomendacion="Revisar disponibilidad antes de trabajar. Guardar en una bodega seca, ventilada y con luz natural.", metodos_siembra=[]),
    dict(codigo="abono", nombre="Abono", grupo="abonos", recomendacion="Preparar el abono elegido en el configurador.", metodos_siembra=[]),
    *[dict(codigo=f"material-{codigo}", nombre=nombre, grupo="siembra", recomendacion="Material para el método elegido.", metodos_siembra=[codigo])
      for codigo, nombre in [("semillas", "Semillas"), ("estacas", "Estacas"), ("esquejes", "Esquejes"), ("plantulas", "Plántulas")]],
]
