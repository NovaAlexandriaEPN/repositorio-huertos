"""Carga inicial por código: no sincroniza ni borra registros existentes.

Lee las listas reunidas en catalogo/datos/__init__.py y crea, con el ORM, los
registros cuyo código estable todavía no existe. Solo usa modelos de catalogo:
no consulta ni modifica cuentas, comunidades, huertos, selecciones, marcas de
materiales, actividades ni nombramientos de maestro.
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from catalogo import datos
from catalogo.models import EventoLunar, Material, OpcionHuerto, Planta, TipoActividad


class Command(BaseCommand):
    help = (
        "Carga los datos Python entregados, sin duplicar ni modificar los existentes. "
        "Con -v 2 lista los códigos cuyo contenido difiere del archivo Python."
    )

    def handle(self, *args, **options):
        conjuntos = [(Planta, datos.PLANTAS), (TipoActividad, datos.ACTIVIDADES),
                     (OpcionHuerto, datos.OPCIONES), (Material, datos.MATERIALES),
                     (EventoLunar, datos.EVENTOS)]
        # Un error en cualquier fila revierte la carga completa: no queda un catálogo parcial.
        with transaction.atomic():
            resumen = [self.cargar(modelo, filas) for modelo, filas in conjuntos]

        for fila in resumen:
            self.stdout.write(
                f"{fila['modelo']}: entregados {fila['entregados']}, nuevos {fila['nuevos']}, "
                f"ya existían {fila['existentes']} ({len(fila['distintos'])} con contenido distinto), "
                f"en la base {fila['en_base']}."
            )
        nuevos = sum(fila["nuevos"] for fila in resumen)
        self.stdout.write(self.style.SUCCESS(f"Carga completada: {nuevos} registros nuevos. Los existentes se conservaron."))
        distintos = sum(len(fila["distintos"]) for fila in resumen)
        if distintos:
            self.stdout.write(self.style.WARNING(
                f"Hay {distintos} registros con contenido distinto al archivo Python. "
                "No se sobrescribieron. Consulta la actualización de bases existentes en "
                "docs/v1/integracion_equipo.md."
            ))
            if options["verbosity"] >= 2:
                for fila in resumen:
                    if fila["distintos"]:
                        self.stdout.write(f"  {fila['modelo']} con contenido distinto: {', '.join(fila['distintos'])}")
            else:
                self.stdout.write("Ejecuta el comando con -v 2 para ver qué códigos difieren.")
        if Planta.objects.count() < 18:
            self.stdout.write(self.style.WARNING("Faltan fichas: V1 requiere las 18 especies. Esta carga no completa ese requisito."))
        if not datos.EVENTOS:
            self.stdout.write(self.style.WARNING("Calendario sin eventos verificados entregados."))

    def cargar(self, modelo, filas):
        """Crea los códigos nuevos de un modelo y compara los existentes sin tocarlos."""
        nombre = modelo.__name__
        campos = {campo.name for campo in modelo._meta.concrete_fields if not campo.primary_key}
        codigos = set()
        nuevos = 0
        distintos = []
        for fila in filas:
            codigo = fila.get("codigo")
            if not codigo or codigo in codigos:
                raise CommandError(f"Código vacío o repetido en los datos de {nombre}.")
            codigos.add(codigo)
            desconocidos = sorted(set(fila) - campos)
            if desconocidos:
                raise CommandError(
                    f"{nombre} {codigo}: el archivo Python trae campos que el modelo no tiene: "
                    f"{', '.join(desconocidos)}. Corrige la ficha o acuerda el cambio del modelo."
                )
            existente = modelo.objects.filter(codigo=codigo).first()
            if existente is not None:
                if any(getattr(existente, campo) != valor for campo, valor in fila.items()):
                    distintos.append(codigo)
                continue
            registro = modelo(**fila)
            try:
                registro.full_clean()
            except ValidationError as error:
                raise CommandError(f"{nombre} {codigo}: {error}") from error
            registro.save()
            nuevos += 1
        return {
            "modelo": nombre,
            "entregados": len(filas),
            "nuevos": nuevos,
            "existentes": len(filas) - nuevos,
            "distintos": distintos,
            "en_base": modelo.objects.count(),
        }
