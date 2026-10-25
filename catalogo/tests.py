from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Material, MetodoSiembra, Planta


class DependenciasCatalogoTests(TestCase):
    def test_ficha_con_las_19_claves_conserva_pendientes_y_fuentes(self):
        ficha = {
            "codigo": "planta_prueba",
            "nombre_comun": "Planta ficticia",
            "nombre_cientifico": None,
            "otros_nombres": [],
            "familia": None,
            "altitud_msnm": None,
            "provincias_ecuador": [],
            "ciclo": None,
            "cualidad_ancestral": None,
            "parte_utilizada": [],
            "usos_documentados": None,
            "contraindicaciones": None,
            "imagen_ruta": None,
            "imagen_autor": None,
            "imagen_fuente": None,
            "imagen_licencia": None,
            "fuentes": [{"titulo": "Referencia ficticia para pruebas", "campos": []}],
            "campos_no_verificados": ["nombre_cientifico", "familia"],
            "observaciones": "Datos ficticios.",
        }
        planta = Planta(**ficha)
        planta.full_clean()
        planta.save()
        planta.refresh_from_db()

        self.assertIsNone(planta.nombre_cientifico)
        self.assertEqual(planta.fuentes, ficha["fuentes"])
        self.assertEqual(planta.campos_no_verificados, ficha["campos_no_verificados"])

    def test_listas_de_fichas_no_se_comparten_entre_instancias(self):
        primera = Planta(codigo="primera", nombre_comun="Primera")
        segunda = Planta(codigo="segunda", nombre_comun="Segunda")
        primera.otros_nombres.append("Nombre de prueba")
        self.assertEqual(segunda.otros_nombres, [])

    def test_rechaza_listas_y_clasificaciones_invalidas(self):
        casos = [
            ("otros_nombres", "Un texto en lugar de lista"),
            ("provincias_ecuador", [123]),
            ("parte_utilizada", {}),
            ("fuentes", ["Referencia sin estructura"]),
            ("campos_no_verificados", None),
            ("ciclo", "inventado"),
            ("cualidad_ancestral", "inventada"),
        ]
        for campo, valor in casos:
            with self.subTest(campo=campo):
                planta = Planta(codigo="prueba", nombre_comun="Prueba", **{campo: valor})
                with self.assertRaises(ValidationError) as error:
                    planta.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_material_admite_metodos_conocidos_o_lista_vacia_para_comunes(self):
        for metodos in ([], [MetodoSiembra.SEMILLAS, MetodoSiembra.PLANTULAS]):
            with self.subTest(metodos=metodos):
                Material(
                    codigo="material_prueba", nombre="Material ficticio",
                    grupo=Material.Grupo.HERRAMIENTAS, metodos_siembra=metodos,
                ).full_clean()
        for metodos in ("semillas", ["inventado"], {"semillas": True}):
            with self.subTest(metodos=metodos):
                material = Material(
                    codigo="prueba", nombre="Prueba",
                    grupo=Material.Grupo.SIEMBRA, metodos_siembra=metodos,
                )
                with self.assertRaises(ValidationError) as error:
                    material.full_clean()
                self.assertIn("metodos_siembra", error.exception.message_dict)

    def test_grupo_de_material_invalido_es_rechazado_en_la_base(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Material.objects.create(codigo="prueba", nombre="Prueba", grupo="inventado")


class CargaIntegradaTests(TestCase):
    def test_carga_repetida_conserva_contenido_y_datos_del_huerto(self):
        from io import StringIO
        from django.core.management import call_command
        from .models import TipoActividad, OpcionHuerto
        call_command("cargar_catalogo", stdout=StringIO())
        planta = Planta.objects.get(codigo="menta")
        id_inicial = planta.pk
        planta.observaciones = "Corrección interna que no debe reemplazar el comando"
        planta.save(update_fields=["observaciones"])
        call_command("cargar_catalogo", stdout=StringIO())
        from .datos import PLANTAS
        self.assertEqual(Planta.objects.count(), len(PLANTAS))
        self.assertEqual(TipoActividad.objects.count(), 13)
        self.assertEqual(OpcionHuerto.objects.count(), 23)
        planta.refresh_from_db()
        self.assertEqual(planta.pk, id_inicial)
        self.assertEqual(planta.observaciones, "Corrección interna que no debe reemplazar el comando")

    def test_fichas_cumplen_formato_y_fotos_verificadas_tienen_archivo_y_creditos(self):
        from pathlib import Path
        from django.conf import settings
        from .datos import PLANTAS
        campos = {f.name for f in Planta._meta.fields} - {"id"}
        for ficha in PLANTAS:
            with self.subTest(codigo=ficha["codigo"]):
                self.assertEqual(set(ficha), campos)
                self.assertIsInstance(ficha["observaciones"], str)
                Planta(**ficha).full_clean()
                if "imagen_ruta" in ficha["campos_no_verificados"]:
                    # Foto pendiente o no verificada: la ficha no la presenta como
                    # confirmada; si hay ruta, el archivo debe existir.
                    if ficha["imagen_ruta"]:
                        self.assertTrue((settings.BASE_DIR / "static" / ficha["imagen_ruta"]).is_file())
                    continue
                self.assertTrue((settings.BASE_DIR / "static" / ficha["imagen_ruta"]).is_file())
                for campo in ("imagen_autor", "imagen_fuente", "imagen_licencia"):
                    self.assertTrue(ficha[campo])

    def test_fallo_de_carga_no_deja_un_catalogo_parcial(self):
        from io import StringIO
        from unittest.mock import patch
        from django.core.management import call_command, CommandError
        with patch("catalogo.datos.OPCIONES", [{"codigo": "opcion-mala", "categoria": "invalida", "nombre": "Error"}]):
            with self.assertRaises(CommandError): call_command("cargar_catalogo", stdout=StringIO())
        self.assertFalse(Planta.objects.exists())

    def test_calendario_convierte_mes_local_sin_inventar_eventos(self):
        from datetime import date, datetime, timezone as utc
        from .models import EventoLunar
        from .servicios import calendario_local
        # Dato ficticio UTC al inicio del 1 de octubre = 30 de septiembre en Ecuador.
        EventoLunar.objects.create(codigo="evento-ficticio", tipo="llena",
            instante=datetime(2026, 10, 1, 2, tzinfo=utc.utc), fuente="https://example.com/ficticio")
        self.assertEqual(calendario_local(9, date(2026, 9, 30))["eventos"].count(), 1)
        self.assertEqual(calendario_local(10, date(2026, 10, 1))["eventos"].count(), 0)
        fuera = calendario_local(8, date(2026, 8, 1))
        self.assertFalse(fuera["dentro_periodo"])
        self.assertIsNone(fuera["anterior"]); self.assertIsNone(fuera["siguiente"])


class EntregaMatthewTests(TestCase):
    """Contenido de Matthew: fichas, guías, opciones, materiales y luna (M2)."""

    def test_seis_fichas_de_matthew_con_campos_vacios_marcados_como_pendientes(self):
        from .datos import PLANTAS
        from .datos.plantas_matthew import PLANTAS as MIAS
        self.assertEqual({f["codigo"] for f in MIAS},
                         {"matico", "taraxaco", "marco", "llanten", "ortiga", "violeta"})
        codigos = [f["codigo"] for f in PLANTAS]
        self.assertEqual(len(codigos), len(set(codigos)))
        for ficha in MIAS:
            with self.subTest(codigo=ficha["codigo"]):
                self.assertIn(ficha["cualidad_ancestral"], ("caliente", "fria"))
                for campo, valor in ficha.items():
                    if campo != "observaciones" and valor in (None, []):
                        self.assertIn(campo, ficha["campos_no_verificados"])
