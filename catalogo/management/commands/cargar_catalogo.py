"""Carga inicial por código: no sincroniza ni borra registros existentes."""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from catalogo import datos
from catalogo.models import EventoLunar, Material, OpcionHuerto, Planta, TipoActividad


class Command(BaseCommand):
    help = "Carga los datos Python entregados, sin duplicar ni modificar los existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        nuevos = 0
        distintos = 0
        for modelo, filas in [(Planta, datos.PLANTAS), (TipoActividad, datos.ACTIVIDADES),
                              (OpcionHuerto, datos.OPCIONES), (Material, datos.MATERIALES),
                              (EventoLunar, datos.EVENTOS)]:
            codigos = set()
            for fila in filas:
                codigo = fila.get("codigo")
                if not codigo or codigo in codigos:
                    raise CommandError(f"Código vacío o repetido en los datos de {modelo.__name__}.")
                codigos.add(codigo)
                existente = modelo.objects.filter(codigo=codigo).first()
                if existente is not None:
                    if any(getattr(existente, campo) != valor for campo, valor in fila.items()):
                        distintos += 1
                    continue
                registro = modelo(**fila)
                try:
                    registro.full_clean()
                except ValidationError as error:
                    raise CommandError(f"{modelo.__name__} {codigo}: {error}") from error
                registro.save()
                nuevos += 1
            self.stdout.write(f"{modelo.__name__}: {len(filas)} registros entregados.")
        self.stdout.write(self.style.SUCCESS(f"Carga completada: {nuevos} registros nuevos. Los existentes se conservaron."))
        if distintos:
            self.stdout.write(self.style.WARNING(
                f"Hay {distintos} registros con contenido distinto al archivo Python. "
                "No se sobrescribieron. Consulta la actualización de bases existentes en "
                "docs/v1/integracion_equipo.md."
            ))
        if Planta.objects.count() < 18:
            self.stdout.write(self.style.WARNING("Faltan fichas: V1 requiere las 18 especies. Esta carga no completa ese requisito."))
        if not datos.EVENTOS:
            self.stdout.write(self.style.WARNING("Calendario sin eventos verificados entregados."))
