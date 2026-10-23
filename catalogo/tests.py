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
