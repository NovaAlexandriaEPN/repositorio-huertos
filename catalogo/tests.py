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
        salida = StringIO()
        call_command("cargar_catalogo", stdout=salida)
        self.assertIn("contenido distinto", salida.getvalue())
        self.assertIn("No se sobrescribieron", salida.getvalue())
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
                    # Una lista de pendientes vacía significa que no queda nada por verificar.
                    if campo not in ("observaciones", "campos_no_verificados") and valor in (None, []):
                        self.assertIn(campo, ficha["campos_no_verificados"])

    def test_trece_guias_completas_y_plazos_obligatorios(self):
        from .datos import ACTIVIDADES
        self.assertEqual(len(ACTIVIDADES), 13)
        self.assertEqual({a["codigo"] for a in ACTIVIDADES}, set(TipoActividadCodigos()))
        for actividad in ACTIVIDADES:
            with self.subTest(codigo=actividad["codigo"]):
                for campo in ("instrucciones", "materiales", "precauciones"):
                    self.assertTrue(actividad[campo])
                self.assertTrue(actividad["fuentes"])
        obligatorias = {a["codigo"] for a in ACTIVIDADES if "Obligatorio:" in a["instrucciones"]}
        self.assertEqual(obligatorias, {"preparacion", "siembra", "secado", "empaquetado"})
        repetibles = {a["codigo"] for a in ACTIVIDADES if a["repetible"]}
        self.assertEqual(repetibles, {"cuidados", "riego"})

    def test_eventos_usno_en_utc(self):
        from datetime import timedelta
        from .datos import EVENTOS
        self.assertEqual(len(EVENTOS), 17)
        self.assertEqual(len({e["codigo"] for e in EVENTOS}), 17)
        for evento in EVENTOS:
            self.assertEqual(evento["instante"].utcoffset(), timedelta(0))
        primero, ultimo = EVENTOS[0], EVENTOS[-1]
        self.assertEqual((primero["tipo"], primero["instante"].isoformat()), ("menguante", "2026-09-04T07:51:00+00:00"))
        self.assertEqual((ultimo["tipo"], ultimo["instante"].isoformat()), ("menguante", "2026-12-30T18:59:00+00:00"))

    def test_opciones_con_explicacion_y_materiales_por_metodo(self):
        from .datos import MATERIALES, OPCIONES
        self.assertTrue(all(o["explicacion"] for o in OPCIONES))
        for material in MATERIALES:
            Material(**material).full_clean()
        semillas = [m["codigo"] for m in MATERIALES if not m["metodos_siembra"] or "semillas" in m["metodos_siembra"]]
        self.assertIn("semillas", semillas)
        self.assertIn("pala", semillas)
        self.assertNotIn("estacas", semillas)


def TipoActividadCodigos():
    from .models import TipoActividad
    return TipoActividad.Codigo.values


class PantallasCatalogoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from datetime import date
        from io import StringIO
        from django.contrib.auth import get_user_model
        from django.core.management import call_command
        call_command("cargar_catalogo", stdout=StringIO())
        cls.usuario = get_user_model().objects.create_user(
            username="lectora", password="clave-segura-123",
            nombre_completo="Lectora", fecha_nacimiento=date(2000, 1, 1))

    def setUp(self):
        self.client.force_login(self.usuario)

    def test_calendario_de_diciembre_muestra_hora_local_y_recomendaciones(self):
        from django.urls import reverse
        respuesta = self.client.get(reverse("catalogo:calendario"), {"mes": 12, "fecha": "2026-12-08"})
        self.assertEqual(respuesta.status_code, 200)
        # 2026-12-09 00:52 UTC es el 8 de diciembre a las 19:52 en Guayaquil.
        self.assertContains(respuesta, "08/12/2026 19:52")
        self.assertContains(respuesta, "Luna oscura (Yana Killa)")
        self.assertContains(respuesta, "Preparación de la tierra")

    def test_guia_muestra_obligatorio_y_anclas_por_actividad(self):
        from django.urls import reverse
        respuesta = self.client.get(reverse("catalogo:guia"))
        self.assertContains(respuesta, 'id="siembra"')
        self.assertContains(respuesta, "Obligatorio: Deben pasar al menos 15 días")

    def test_ficha_de_matthew_muestra_foto_con_creditos(self):
        from django.urls import reverse
        respuesta = self.client.get(reverse("catalogo:detalle_planta", args=["ortiga"]))
        self.assertContains(respuesta, "Urtica dioica")
        self.assertContains(respuesta, 'src="/static/img/plantas/ortiga.jpg"')
        self.assertContains(respuesta, "Dominicus Johannes Bergsma")
        self.assertContains(respuesta, "CC BY-SA 4.0")

class CaracteresEstandarTests(TestCase):
    """Los datos fijos usan guion, puntos y «x» en lugar de rayas, elipsis y signo de multiplicación."""

    # Raya, guion corto, puntos suspensivos y signo de multiplicación.
    NO_ESTANDAR = {chr(0x2014): "-", chr(0x2013): "-", chr(0x2026): "...", chr(0xD7): "x"}

    def textos(self, valor):
        if isinstance(valor, str):
            yield valor
        elif isinstance(valor, dict):
            for elemento in valor.values():
                yield from self.textos(elemento)
        elif isinstance(valor, (list, tuple)):
            for elemento in valor:
                yield from self.textos(elemento)

    def test_datos_del_catalogo_sin_caracteres_no_estandar(self):
        from . import datos
        for nombre in ("PLANTAS", "ACTIVIDADES", "OPCIONES", "MATERIALES", "EVENTOS"):
            for fila in getattr(datos, nombre):
                for texto in self.textos(fila):
                    for caracter, reemplazo in self.NO_ESTANDAR.items():
                        with self.subTest(lista=nombre, codigo=fila["codigo"], caracter=f"U+{ord(caracter):04X}"):
                            self.assertNotIn(caracter, texto, f"Usa «{reemplazo}» en su lugar.")

    def test_licencia_acepta_el_separador_nuevo_y_el_de_bases_anteriores(self):
        from .templatetags.presentacion import licencia
        url = "https://creativecommons.org/licenses/by-sa/4.0/"
        for separador in (" - ", f" {chr(0x2014)} "):
            with self.subTest(separador=separador):
                partes = licencia(f"CC BY-SA 4.0{separador}{url}")
                self.assertEqual(partes, {"nombre": "CC BY-SA 4.0", "url": url, "extra": ""})

