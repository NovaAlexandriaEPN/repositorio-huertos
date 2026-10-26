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


class CargaInicialTests(TestCase):
    """J2-08: cargar_catalogo crea el catálogo en una base nueva por código estable."""

    def cargar(self, *args):
        from io import StringIO
        from django.core.management import call_command
        salida = StringIO()
        call_command("cargar_catalogo", *args, stdout=salida)
        return salida.getvalue()

    def test_base_nueva_recibe_todas_las_listas_y_un_resumen_por_modelo(self):
        from . import datos
        from .models import EventoLunar, OpcionHuerto, TipoActividad
        salida = self.cargar()
        for modelo, filas in [(Planta, datos.PLANTAS), (TipoActividad, datos.ACTIVIDADES),
                              (OpcionHuerto, datos.OPCIONES), (Material, datos.MATERIALES),
                              (EventoLunar, datos.EVENTOS)]:
            with self.subTest(modelo=modelo.__name__):
                self.assertEqual(modelo.objects.count(), len(filas))
                self.assertEqual(set(modelo.objects.values_list("codigo", flat=True)),
                                 {fila["codigo"] for fila in filas})
                n = len(filas)
                self.assertIn(f"{modelo.__name__}: entregados {n}, nuevos {n}, ya existían 0 "
                              f"(0 con contenido distinto), en la base {n}.", salida)
        self.assertNotIn("contenido distinto al archivo Python", salida)

    def test_campo_desconocido_detiene_la_carga_con_un_mensaje_claro(self):
        from unittest.mock import patch
        from django.core.management import CommandError
        from . import datos
        ficha = dict(datos.PLANTAS[0], codigo="ficha-con-error", campo_inventado="valor")
        with patch("catalogo.datos.PLANTAS", [ficha]):
            with self.assertRaises(CommandError) as error:
                self.cargar()
        self.assertIn("ficha-con-error", str(error.exception))
        self.assertIn("campo_inventado", str(error.exception))
        self.assertFalse(Planta.objects.exists())

    def test_verbosidad_2_lista_los_codigos_que_difieren_sin_corregirlos(self):
        self.cargar()
        Planta.objects.filter(codigo="romero").update(observaciones="Corrección local")
        normal = self.cargar()
        self.assertIn("Ejecuta el comando con -v 2", normal)
        self.assertNotIn("Planta con contenido distinto: romero", normal)
        detallada = self.cargar("-v", "2")
        self.assertIn("Planta con contenido distinto: romero", detallada)
        self.assertEqual(Planta.objects.get(codigo="romero").observaciones, "Corrección local")


class SegundaCargaTests(TestCase):
    """J2-09: repetir la carga sobre una base con datos de trabajo.

    Es la única clase de catálogo que usa comunidades y actividades: los necesita
    para comprobar que el comando no los altera. El comando no los importa.
    """

    @classmethod
    def setUpTestData(cls):
        from datetime import timedelta
        from io import StringIO
        from django.core.management import call_command
        from django.utils import timezone
        from actividades import servicios as actividades
        from actividades.models import Actividad
        from comunidades.servicios import (configurar_huerto, crear_comunidad, elegir_planta,
                                           marcar_material, unirse_comunidad)
        from cuentas.models import Usuario
        from .models import OpcionHuerto

        call_command("cargar_catalogo", stdout=StringIO())

        def cuenta(nombre):
            return Usuario.objects.create_user(
                username=nombre, password="ClaveDePrueba_2026!", nombre_completo=nombre,
                fecha_nacimiento=timezone.localdate() - timedelta(days=7000))

        # Base ficticia: comunidad con huerto, planta, material marcado, historial y maestro.
        responsable = cuenta("responsable_j2")
        participante = cuenta("participante_j2")
        comunidad = crear_comunidad(
            actor=responsable, nombre="Comunidad ficticia J2", tipo="barrio",
            contacto_nombre="Responsable", contacto_telefono="0990000000",
            contacto_correo="ficticio@example.com")
        miembro = unirse_comunidad(actor=participante, codigo_invitacion=comunidad.codigo_invitacion)
        opciones = {c: OpcionHuerto.objects.filter(categoria=c).first() for c in OpcionHuerto.Categoria.values}
        cls.huerto = configurar_huerto(
            actor=responsable, provincia="Pichincha", parroquia="Ficticia", direccion="Calle ficticia",
            area_m2=12, disenos=[opciones["diseno"]], cerca=opciones["cerca"], suelo=opciones["suelo"],
            fuente_agua=opciones["agua"], abonos=[opciones["abono"]])
        seleccion = elegir_planta(actor=responsable, planta=Planta.objects.get(codigo="menta"),
                                  metodo_siembra="semillas")
        marcar_material(actor=participante, material_id=Material.objects.get(codigo="pala").pk, disponible=True)

        Tipo = Actividad.Tipo
        inicio = timezone.now().replace(second=0, microsecond=0) - timedelta(days=60)
        registros = {}
        for tipo, dias in [(Tipo.PREPARACION, 0), (Tipo.DISENO, 0), (Tipo.RITUAL, 0),
                           (Tipo.SIEMBRA, 15), (Tipo.SENALETICA, 15), (Tipo.CUIDADOS, 16),
                           (Tipo.RIEGO, 16), (Tipo.BANO, 16), (Tipo.GRATITUD, 16),
                           (Tipo.COSECHA, 20), (Tipo.LIMPIEZA, 20), (Tipo.SECADO, 20),
                           (Tipo.EMPAQUETADO, 30)]:
            planta = None if tipo in Actividad.TIPOS_GENERALES else seleccion
            registros[tipo] = actividades.registrar_actividad(
                cls.huerto, participante, tipo, inicio + timedelta(days=dias), planta=planta)[0]
        actividades.anular_actividad(registros[Tipo.DISENO].pk, responsable, "Registro de prueba duplicado")
        actividades.nombrar_maestro(cls.huerto, responsable, miembro, "Guió la siembra ficticia",
                                    maestro_esperado_id=None)

    def foto_catalogo(self):
        from .models import EventoLunar, OpcionHuerto, TipoActividad
        return {modelo.__name__: list(modelo.objects.order_by("pk").values())
                for modelo in (Planta, TipoActividad, OpcionHuerto, Material, EventoLunar)}

    def foto_trabajo(self):
        """Cada fila de los datos de trabajo, con todos sus campos."""
        from actividades.models import Actividad
        from comunidades.models import Comunidad, Huerto, MarcaMaterial, Miembro, PlantaHuerto
        from cuentas.models import Usuario
        foto = {modelo.__name__: list(modelo.objects.order_by("pk").values())
                for modelo in (Usuario, Comunidad, Miembro, Huerto, PlantaHuerto, MarcaMaterial, Actividad)}
        foto["opciones_multiples"] = [
            (h.pk, sorted(h.disenos.values_list("pk", flat=True)), sorted(h.abonos.values_list("pk", flat=True)))
            for h in Huerto.objects.order_by("pk")]
        return foto

    def test_la_base_ficticia_tiene_los_datos_que_se_van_a_proteger(self):
        from actividades.models import Actividad
        self.huerto.refresh_from_db()
        self.assertIsNotNone(self.huerto.maestro_id)
        self.assertEqual(Actividad.objects.filter(estado=Actividad.Estado.ANULADA).count(), 1)
        self.assertEqual(Actividad.objects.filter(estado=Actividad.Estado.ACTIVA).count(), 12)
        self.assertTrue(self.huerto.marcas_materiales.filter(disponible=True).exists())

    def test_segunda_carga_sin_cambios_no_duplica_ni_altera_nada(self):
        from io import StringIO
        from django.core.management import call_command
        catalogo, trabajo = self.foto_catalogo(), self.foto_trabajo()
        salida = StringIO()
        call_command("cargar_catalogo", stdout=salida)
        self.assertIn("Carga completada: 0 registros nuevos.", salida.getvalue())
        self.assertEqual(self.foto_catalogo(), catalogo)
        self.assertEqual(self.foto_trabajo(), trabajo)

    def test_datos_python_cambiados_solo_agregan_codigos_nuevos(self):
        from io import StringIO
        from unittest.mock import patch
        from django.core.management import call_command
        from . import datos
        from .models import TipoActividad
        catalogo, trabajo = self.foto_catalogo(), self.foto_trabajo()
        ficha_nueva = dict(datos.PLANTAS[0], codigo="planta-ficticia-j2", nombre_comun="Planta ficticia")
        # Un cambio de puntos en el archivo no debe reescribir la guía guardada ni el historial.
        guias = [dict(guia, puntos_base=99) if guia["codigo"] == "preparacion" else guia
                 for guia in datos.ACTIVIDADES]
        salida = StringIO()
        with patch("catalogo.datos.PLANTAS", [*datos.PLANTAS, ficha_nueva]), \
                patch("catalogo.datos.ACTIVIDADES", guias):
            call_command("cargar_catalogo", stdout=salida)

        n = len(datos.PLANTAS)
        self.assertIn(f"Planta: entregados {n + 1}, nuevos 1, ya existían {n} (0 con contenido distinto), "
                      f"en la base {n + 1}.", salida.getvalue())
        self.assertIn("TipoActividad: entregados 13, nuevos 0, ya existían 13 (1 con contenido distinto)",
                      salida.getvalue())
        despues = self.foto_catalogo()
        self.assertEqual(despues["Planta"][:-1], catalogo["Planta"])
        self.assertEqual(despues["Planta"][-1]["codigo"], "planta-ficticia-j2")
        for modelo in ("TipoActividad", "OpcionHuerto", "Material", "EventoLunar"):
            self.assertEqual(despues[modelo], catalogo[modelo], modelo)
        self.assertEqual(TipoActividad.objects.get(codigo="preparacion").puntos_base, 10)
        self.assertEqual(self.foto_trabajo(), trabajo)
