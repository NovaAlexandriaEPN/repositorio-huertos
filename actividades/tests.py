"""Comprobaciones de integración contra el alcance V1; datos y usuarios de prueba."""
from datetime import timedelta
from io import StringIO
from uuid import uuid4

from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from catalogo.models import OpcionHuerto, Planta, TipoActividad
from comunidades.models import Miembro, PlantaHuerto
from comunidades.servicios import (crear_comunidad, unirse_comunidad, configurar_huerto,
    elegir_planta, cambiar_metodo_siembra, retirar_planta)
from cuentas.models import Usuario
from . import servicios
from .forms import RegistroActividadForm
from .models import Actividad
from .reglas import calcular_nivel, calcular_progreso

Tipo = Actividad.Tipo


class CalculosTests(SimpleTestCase):
    def test_tres_niveles_y_nombramiento_explicito(self):
        for puntos, nombre in [(0, "Aprendiz"), (99, "Aprendiz"), (100, "Oficial"), (300, "Oficial")]:
            with self.subTest(puntos=puntos):
                self.assertEqual(calcular_nivel(puntos)["nombre"], nombre)
        self.assertEqual(calcular_nivel(100, True)["nombre"], "Maestro")
        self.assertEqual(calcular_nivel(99, True)["nombre"], "Aprendiz")

    def test_crecimiento_unico_y_empaquetado_sexto_hito(self):
        self.assertAlmostEqual(calcular_progreso(["preparacion", "siembra"]), 100 / 3)
        self.assertEqual(calcular_progreso(["cuidados", "riego", "riego"]), 100 / 6)
        self.assertEqual(calcular_progreso(["preparacion", "siembra", "riego", "cosecha", "secado", "empaquetado"]), 100)

    def test_sin_hitos_es_cero_y_los_desconocidos_no_suman(self):
        self.assertEqual(calcular_progreso([]), 0)
        self.assertEqual(calcular_progreso(["baño", "gratitud", "limpieza"]), 0)

    def test_cuidados_y_riego_juntos_son_un_solo_hito(self):
        self.assertAlmostEqual(calcular_progreso(["preparacion", "cuidados", "riego"]), 100 / 3)
        self.assertEqual(calcular_progreso(["cuidados", "riego"]), 100 / 6)

    def test_hitos_repetidos_no_suman_dos_veces(self):
        self.assertEqual(calcular_progreso(["siembra", "siembra", "siembra"]), 100 / 6)

    def test_ejemplo_del_alcance_promedio_58_3(self):
        completa = calcular_progreso(["preparacion", "siembra", "riego", "cosecha", "secado", "empaquetado"])
        planeada = calcular_progreso(["preparacion"])
        self.assertAlmostEqual((completa + planeada) / 2, 58.3, places=1)

    def test_trescientos_puntos_no_nombran_maestro(self):
        self.assertEqual(calcular_nivel(300)["nombre"], "Oficial")
        self.assertEqual(calcular_nivel(300, True)["nombre"], "Maestro")

    def test_elegibilidad_para_maestro_desde_cien_puntos(self):
        self.assertFalse(calcular_nivel(99)["es_elegible_maestro"])
        self.assertTrue(calcular_nivel(100)["es_elegible_maestro"])

class ActividadesIntegradasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("cargar_catalogo", stdout=StringIO())
        def cuenta(nombre):
            return Usuario.objects.create_user(username=nombre, password="ClaveDePrueba_2026!",
                nombre_completo=nombre, fecha_nacimiento=timezone.localdate() - timedelta(days=7000))
        cls.responsable = cuenta("responsable_prueba")
        cls.participante = cuenta("participante_prueba")
        cls.ajeno = cuenta("ajeno_prueba")
        cls.comunidad = crear_comunidad(actor=cls.responsable, nombre="Comunidad de prueba",
            tipo="barrio", contacto_nombre="Responsable", contacto_telefono="0990000000", contacto_correo="ficticio@example.com")
        unirse_comunidad(actor=cls.participante, codigo_invitacion=cls.comunidad.codigo_invitacion)
        opciones = {c: OpcionHuerto.objects.filter(categoria=c).first() for c in OpcionHuerto.Categoria.values}
        cls.huerto = configurar_huerto(actor=cls.responsable, provincia="Pichincha", parroquia="Prueba", direccion="Ficticia",
            area_m2=10, disenos=[opciones["diseno"]], cerca=opciones["cerca"], suelo=opciones["suelo"],
            fuente_agua=opciones["agua"], abonos=[opciones["abono"]])
        cls.planta = elegir_planta(actor=cls.responsable, planta=Planta.objects.get(codigo="menta"), metodo_siembra="semillas")
        cls.base = timezone.now().replace(second=0, microsecond=0) - timedelta(days=60)

    def registrar(self, tipo, dias=0, *, actor=None, seleccion=None, **datos):
        return servicios.registrar_actividad(self.huerto, actor or self.participante, tipo,
            self.base + timedelta(days=dias),
            planta=None if tipo in Actividad.TIPOS_GENERALES else (seleccion or self.planta), **datos)[0]

    def sembrar(self):
        preparacion = self.registrar(Tipo.PREPARACION)
        siembra = self.registrar(Tipo.SIEMBRA, 15)
        return preparacion, siembra

    def ciclo(self, seleccion=None, generales=True):
        registros = []
        if generales:
            for tipo in Actividad.TIPOS_GENERALES:
                registros.append(self.registrar(tipo))
        for tipo, dias in [(Tipo.SIEMBRA, 15), (Tipo.SENALETICA, 15), (Tipo.CUIDADOS, 16), (Tipo.RIEGO, 16),
            (Tipo.BANO, 16), (Tipo.GRATITUD, 16), (Tipo.COSECHA, 20), (Tipo.LIMPIEZA, 20),
            (Tipo.SECADO, 20), (Tipo.EMPAQUETADO, 30)]:
            registros.append(self.registrar(tipo, dias, seleccion=seleccion))
        return registros

    def resumen(self):
        return servicios.obtener_resumen_huerto(self.huerto, self.participante)

    def test_los_trece_tipos_con_puntos_y_transiciones_acordadas(self):
        registros = self.ciclo()
        self.assertEqual(len(registros), 13)
        self.assertEqual([r.puntos for r in registros], [10, 10, 10, 15, 5, 5, 5, 5, 10, 20, 5, 10, 15])
        self.assertEqual(servicios.puntos_de_usuario(self.participante, self.huerto), 125)
        resumen = self.resumen()
        self.assertEqual(resumen["tarjetas"][0]["estado"], "empacada")
        self.assertEqual(resumen["progreso_huerto"], 100)
        self.assertEqual(resumen["nivel_usuario"]["nombre"], "Oficial")

    def test_siembra_exige_preparacion_y_minimo_quince_dias(self):
        with self.assertRaises(ValidationError): self.registrar(Tipo.SIEMBRA, 15)
        self.registrar(Tipo.PREPARACION)
        with self.assertRaises(ValidationError): self.registrar(Tipo.SIEMBRA, 14)
        self.registrar(Tipo.SIEMBRA, 15)
        self.assertEqual(Actividad.objects.count(), 2)

    def test_diseno_y_ritual_no_son_prerrequisitos(self):
        self.sembrar()
        self.assertEqual(self.resumen()["tarjetas"][0]["estado"], "sembrada")

    def test_empaquetado_exige_minimo_diez_dias_desde_secado(self):
        self.sembrar(); self.registrar(Tipo.CUIDADOS, 16); self.registrar(Tipo.COSECHA, 20)
        self.registrar(Tipo.SECADO, 25)
        with self.assertRaises(ValidationError): self.registrar(Tipo.EMPAQUETADO, 34)
        self.registrar(Tipo.EMPAQUETADO, 35)
        self.assertEqual(self.resumen()["progreso_huerto"], 100)

    def test_secado_no_tiene_plazo_maximo_desde_cosecha(self):
        self.sembrar(); self.registrar(Tipo.RIEGO, 16); self.registrar(Tipo.COSECHA, 20)
        self.registrar(Tipo.SECADO, 40)

    def test_rechaza_fecha_futura_y_fecha_anterior_a_ultima(self):
        self.sembrar(); self.registrar(Tipo.RIEGO, 18)
        with self.assertRaises(ValidationError): self.registrar(Tipo.CUIDADOS, 17)
        with self.assertRaises(ValidationError): self.registrar(Tipo.CUIDADOS, 61)

    def test_no_admite_estados_incorrectos(self):
        for tipo in ESTADOS_ANTES_DE_SEMBRAR:
            with self.subTest(tipo=tipo), self.assertRaises(ValidationError): self.registrar(tipo, 16)
        self.sembrar(); self.registrar(Tipo.CUIDADOS, 16); self.registrar(Tipo.COSECHA, 20)
        for tipo in (Tipo.RIEGO, Tipo.CUIDADOS, Tipo.SENALETICA, Tipo.BANO, Tipo.GRATITUD):
            with self.subTest(tipo=tipo), self.assertRaises(ValidationError): self.registrar(tipo, 21)

    def test_actividades_sin_transicion_conservan_el_estado(self):
        self.sembrar(); self.registrar(Tipo.SENALETICA, 15)
        self.assertEqual(self.resumen()["tarjetas"][0]["estado"], "sembrada")
        self.registrar(Tipo.CUIDADOS, 16); self.registrar(Tipo.BANO, 16); self.registrar(Tipo.GRATITUD, 16)
        self.assertEqual(self.resumen()["tarjetas"][0]["estado"], "creciendo")
        self.registrar(Tipo.COSECHA, 20); self.registrar(Tipo.LIMPIEZA, 20)
        self.assertEqual(self.resumen()["tarjetas"][0]["estado"], "cosechada")

    def test_generales_sin_planta_y_bloqueadas_tras_siembra(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_actividad(self.huerto, self.participante, Tipo.PREPARACION, self.base, self.planta)
        self.sembrar()
        for tipo in Actividad.TIPOS_GENERALES:
            with self.subTest(tipo=tipo), self.assertRaises(ValidationError): self.registrar(tipo, 16)

    def test_reenvio_igual_antes_de_comprobar_estado_incluso_anulado(self):
        self.sembrar(); envio = uuid4()
        r = self.registrar(Tipo.CUIDADOS, 16, request_uuid=envio, detalles="  Nota original  ")
        self.registrar(Tipo.COSECHA, 20)
        repetido, creado = servicios.registrar_actividad(self.huerto, self.participante, Tipo.CUIDADOS,
            self.base + timedelta(days=16), self.planta, "Nota original", envio)
        self.assertFalse(creado); self.assertEqual(repetido.pk, r.pk)
        # Anular primero la cosecha y después el cuidado, sin borrar historia.
        ultima = Actividad.objects.order_by("fecha", "id").last()
        servicios.anular_actividad(ultima.pk, self.responsable, "Corregir")
        servicios.anular_actividad(r.pk, self.responsable, "Corregir")
        repetido, creado = servicios.registrar_actividad(self.huerto, self.participante, Tipo.CUIDADOS,
            self.base + timedelta(days=16), self.planta, "Nota original", envio)
        self.assertFalse(creado); self.assertTrue(repetido.es_anulada)

    def test_reenvio_carga_nota_actor_y_huerto_distintos_rechazados(self):
        self.registrar(Tipo.PREPARACION, request_uuid=(envio := uuid4()), detalles="Original")
        for actor, tipo, nota in [(self.participante, Tipo.PREPARACION, "Otra"),
            (self.responsable, Tipo.PREPARACION, "Original"), (self.participante, Tipo.DISENO, "Original")]:
            with self.subTest(actor=actor, tipo=tipo, nota=nota), self.assertRaises(ValidationError):
                self.registrar(tipo, actor=actor, request_uuid=envio, detalles=nota)

    def test_otro_uuid_no_duplica_actividad_no_repetible(self):
        self.sembrar()
        with self.assertRaises(ValidationError): self.registrar(Tipo.SIEMBRA, 15)
        self.registrar(Tipo.SENALETICA, 15)
        with self.assertRaises(ValidationError): self.registrar(Tipo.SENALETICA, 15)

    def test_repetibles_primer_activo_cinco_siguientes_cero(self):
        self.sembrar()
        for indice, tipo in enumerate((Tipo.RIEGO, Tipo.CUIDADOS)):
            primero = self.registrar(tipo, 16 + indice * 2)
            segundo = self.registrar(tipo, 17 + indice * 2)
            self.assertEqual((primero.puntos, segundo.puntos), (5, 0))
        self.assertEqual(self.resumen()["tarjetas"][0]["hitos"], ["preparacion", "siembra", "crecimiento"])

    def test_solo_responsable_anula_incluso_si_actor_es_participante(self):
        r = self.registrar(Tipo.PREPARACION)
        with self.assertRaises(PermissionDenied): servicios.anular_actividad(r.pk, self.participante, "Corregir")
        with self.assertRaises(PermissionDenied): servicios.anular_actividad(r.pk, self.ajeno, "Corregir")
        with self.assertRaises(ValidationError): servicios.anular_actividad(r.pk, self.responsable, "   ")
        servicios.anular_actividad(r.pk, self.responsable, "Corregir")
        r.refresh_from_db()
        self.assertEqual(r.actor_original_id, self.participante.pk)
        self.assertEqual(r.anulada_por_id, self.responsable.pk)
        self.assertIsNotNone(r.fecha_anulacion)

    def test_anulacion_por_orden_inverso_y_empates_por_id(self):
        prep, siembra = self.sembrar()
        cuidado = self.registrar(Tipo.CUIDADOS, 15)
        with self.assertRaises(ValidationError): servicios.anular_actividad(siembra.pk, self.responsable, "Corregir")
        with self.assertRaises(ValidationError): servicios.anular_actividad(prep.pk, self.responsable, "Corregir")
        servicios.anular_actividad(cuidado.pk, self.responsable, "Corregir")
        servicios.anular_actividad(siembra.pk, self.responsable, "Corregir")
        servicios.anular_actividad(prep.pk, self.responsable, "Corregir")
        self.assertEqual(self.resumen()["progreso_huerto"], 0)

    def test_diseno_y_ritual_se_anulan_independientes_sin_transferir_puntos(self):
        diseno = self.registrar(Tipo.DISENO); ritual = self.registrar(Tipo.RITUAL)
        self.sembrar()
        for r in (diseno, ritual): servicios.anular_actividad(r.pk, self.responsable, "Corregir")
        self.assertEqual(servicios.puntos_de_usuario(self.responsable, self.huerto), 0)
        self.assertEqual(servicios.puntos_de_usuario(self.participante, self.huerto), 25)
        with self.assertRaises(ValidationError): self.registrar(Tipo.DISENO)

    def test_valores_historicos_no_se_reescriben_al_cambiar_catalogo(self):
        self.sembrar(); r = self.registrar(Tipo.CUIDADOS, 16)
        TipoActividad.objects.filter(codigo=Tipo.CUIDADOS).update(puntos_base=30)
        s = self.registrar(Tipo.CUIDADOS, 17)
        servicios.anular_actividad(s.pk, self.responsable, "Corregir")
        r.refresh_from_db(); self.assertEqual(r.puntos_base, 5); self.assertEqual(r.puntos, 5)
        self.assertEqual(servicios.puntos_de_usuario(self.participante, self.huerto), 30)

    def test_promedio_de_plantas_y_descenso_al_agregar_otra(self):
        self.ciclo()
        elegir_planta(actor=self.responsable, planta=Planta.objects.get(codigo="romero"), metodo_siembra="esquejes")
        self.assertAlmostEqual(self.resumen()["progreso_huerto"], 58.3333333333)
        servicios.anular_actividad(Actividad.objects.filter(tipo_id=Tipo.EMPAQUETADO).get().pk, self.responsable, "Corregir")
        self.assertLess(self.resumen()["progreso_huerto"], 58.34)

    def test_sin_plantas_progreso_cero(self):
        self.planta.delete()
        self.assertEqual(self.resumen()["progreso_huerto"], 0)

    def test_historial_real_incluido_anulado_bloquea_metodo_y_retiro(self):
        self.sembrar(); siembra = Actividad.objects.get(tipo_id=Tipo.SIEMBRA)
        servicios.anular_actividad(siembra.pk, self.responsable, "Corregir")
        self.assertTrue(self.planta.tiene_historial)
        with self.assertRaises(ValidationError): cambiar_metodo_siembra(actor=self.responsable, seleccion_id=self.planta.pk, metodo_siembra="esquejes")
        with self.assertRaises(ValidationError): retirar_planta(actor=self.responsable, seleccion_id=self.planta.pk)

    def test_maestro_con_motivo_umbral_y_retiro_al_bajar_de_cien(self):
        candidato = Miembro.objects.get(usuario=self.participante)
        with self.assertRaises(ValidationError): servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Puede guiar", maestro_esperado_id=None)
        self.ciclo()
        with self.assertRaises(ValidationError): servicios.nombrar_maestro(self.huerto, self.responsable, candidato, " ", maestro_esperado_id=None)
        with self.assertRaises(PermissionDenied): servicios.nombrar_maestro(self.huerto, self.participante, candidato, "Puede guiar", maestro_esperado_id=None)
        servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Puede guiar una siembra", maestro_esperado_id=None)
        self.assertEqual(self.resumen()["nivel_usuario"]["nombre"], "Maestro")
        for tipo in (Tipo.EMPAQUETADO, Tipo.SECADO, Tipo.LIMPIEZA):
            _, retirado = servicios.anular_actividad(Actividad.objects.get(tipo_id=tipo).pk, self.responsable, "Corregir")
        self.assertTrue(retirado)
        self.huerto.refresh_from_db()
        self.assertIsNone(self.huerto.maestro_id); self.assertEqual(self.huerto.maestro_motivo, "")
        self.assertIsNone(self.huerto.maestro_nombrado_por_id); self.assertIsNone(self.huerto.maestro_fecha)

    def test_maestro_no_se_nombra_por_trescientos_y_formulario_viejo_rechazado(self):
        self.ciclo()
        for codigo in ("romero", "toronjil"):
            seleccion = elegir_planta(actor=self.responsable, planta=Planta.objects.get(codigo=codigo), metodo_siembra="semillas")
            self.ciclo(seleccion, generales=False)
        self.assertGreaterEqual(servicios.puntos_de_usuario(self.participante, self.huerto), 300)
        self.assertIsNone(self.resumen()["maestro"])
        candidato = Miembro.objects.get(usuario=self.participante)
        servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Puede guiar", maestro_esperado_id=None)
        with self.assertRaises(ValidationError): servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Otra", maestro_esperado_id=None)

    def test_pertenencia_y_cuenta_desactivada_se_validan_en_servicio(self):
        with self.assertRaises(PermissionDenied): self.registrar(Tipo.PREPARACION, actor=self.ajeno)
        Usuario.objects.filter(pk=self.participante.pk).update(is_active=False)
        with self.assertRaises(PermissionDenied): self.registrar(Tipo.PREPARACION)
        with self.assertRaises(PermissionDenied): self.resumen()

    def test_restriccion_bd_impide_duplicado_no_repetible(self):
        r = self.registrar(Tipo.PREPARACION)
        r.pk = None; r.uuid = uuid4()
        with self.assertRaises(IntegrityError), transaction.atomic(): r.save()

    def test_formulario_fecha_hora_y_uuid_se_conservan_en_error(self):
        envio = uuid4()
        f = RegistroActividadForm({"uuid": str(envio), "tipo": "siembra", "fecha": "incorrecta"}, huerto=self.huerto)
        self.assertFalse(f.is_valid()); self.assertEqual(f["uuid"].value(), str(envio))
        f = RegistroActividadForm({"uuid": str(envio), "tipo": "preparacion", "fecha": "2026-01-01T08:00"}, huerto=self.huerto)
        self.assertTrue(f.is_valid(), f.errors)
        self.assertTrue(timezone.is_aware(f.cleaned_data["fecha"]))

    def test_pantallas_integradas_y_menu_tienen_rutas_reales(self):
        self.client.force_login(self.participante)
        for ruta, args in [("actividades:inicio_huerto_virtual", [self.huerto.pk]),
            ("actividades:registrar_actividad", [self.huerto.pk]), ("actividades:historial_actividades", [self.huerto.pk]),
            ("catalogo:lista_plantas", []), ("catalogo:detalle_planta", ["menta"]),
            ("catalogo:guia", []), ("catalogo:calendario", [])]:
            with self.subTest(ruta=ruta):
                response = self.client.get(reverse(ruta, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, "Disponible próximamente")
        self.assertEqual(self.client.put(reverse("actividades:registrar_actividad", args=[self.huerto.pk])).status_code, 405)

    def test_otro_huerto_no_se_consulta_ni_modifica_por_id(self):
        r = self.registrar(Tipo.PREPARACION)
        self.client.force_login(self.ajeno)
        for ruta, args in [("actividades:inicio_huerto_virtual", [self.huerto.pk]),
            ("actividades:registrar_actividad", [self.huerto.pk]), ("actividades:historial_actividades", [self.huerto.pk]),
            ("actividades:nombrar_maestro", [self.huerto.pk]), ("actividades:anular_actividad", [r.pk])]:
            for metodo in ("get", "post"):
                with self.subTest(ruta=ruta, metodo=metodo):
                    esperado = 405 if metodo == "post" and ruta in {"actividades:inicio_huerto_virtual", "actividades:historial_actividades"} else 403
                    self.assertEqual(getattr(self.client, metodo)(reverse(ruta, args=args)).status_code, esperado)

    def test_tarjeta_abre_el_registro_con_planta_y_actividad_sugerida(self):
        """F3-03: desde cada tarjeta se registra la siguiente actividad de esa planta."""
        self.client.force_login(self.participante)
        pagina = self.client.get(reverse("actividades:inicio_huerto_virtual", args=[self.huerto.pk]))
        enlace = reverse("actividades:registrar_actividad", args=[self.huerto.pk]) + f"?planta={self.planta.pk}&amp;tipo=siembra"
        self.assertContains(pagina, enlace)
        self.assertContains(pagina, reverse("actividades:historial_actividades", args=[self.huerto.pk]) + f"?planta={self.planta.pk}")
        formulario = self.client.get(reverse("actividades:registrar_actividad", args=[self.huerto.pk]),
                                     {"planta": self.planta.pk, "tipo": "siembra"}).context["form"]
        self.assertEqual(formulario["planta"].value(), self.planta.pk)
        self.assertEqual(formulario["tipo"].value(), "siembra")

    def test_preseleccion_ignora_plantas_ajenas_y_tipos_invalidos(self):
        self.client.force_login(self.participante)
        formulario = self.client.get(reverse("actividades:registrar_actividad", args=[self.huerto.pk]),
                                     {"planta": "999999", "tipo": "inventado"}).context["form"]
        self.assertIsNone(formulario["planta"].value())
        self.assertNotEqual(formulario["tipo"].value(), "inventado")

    def test_post_real_con_csrf_y_reenvio_no_duplica(self):
        client = Client(enforce_csrf_checks=True); client.force_login(self.participante)
        url = reverse("actividades:registrar_actividad", args=[self.huerto.pk])
        response = client.get(url)
        envio = str(response.context["form"]["uuid"].value())
        datos = {"uuid": envio, "tipo": "preparacion", "fecha": self.base.strftime("%Y-%m-%dT%H:%M"), "detalles": "Mi labor"}
        self.assertEqual(client.post(url, datos).status_code, 403)
        datos["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        self.assertEqual(client.post(url, datos).status_code, 302)
        self.assertEqual(client.post(url, datos).status_code, 302)
        self.assertEqual(Actividad.objects.count(), 1)
        r = Actividad.objects.get()
        self.assertEqual(r.actor_original_id, self.participante.pk)
        client.force_login(self.responsable)
        pagina = client.get(reverse("actividades:historial_actividades", args=[self.huerto.pk]))
        self.assertContains(pagina, "Mi labor")

    def test_ciclo_de_trece_actividades_desde_formularios_reales(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.participante)
        url = reverse("actividades:registrar_actividad", args=[self.huerto.pk])
        secuencia = [(t, 0) for t in Actividad.TIPOS_GENERALES] + [
            (Tipo.SIEMBRA, 15), (Tipo.SENALETICA, 15), (Tipo.CUIDADOS, 16), (Tipo.RIEGO, 16),
            (Tipo.BANO, 16), (Tipo.GRATITUD, 16), (Tipo.COSECHA, 20), (Tipo.LIMPIEZA, 20),
            (Tipo.SECADO, 20), (Tipo.EMPAQUETADO, 30)]
        for tipo, dias in secuencia:
            with self.subTest(tipo=tipo):
                pagina = client.get(url)
                fecha = timezone.localtime(self.base + timedelta(days=dias))
                response = client.post(url, {
                    "uuid": str(pagina.context["form"]["uuid"].value()),
                    "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
                    "tipo": tipo, "fecha": fecha.strftime("%Y-%m-%dT%H:%M"),
                    "planta": "" if tipo in Actividad.TIPOS_GENERALES else self.planta.pk,
                    "actor_original": self.responsable.pk, "puntos": 9999,
                })
                self.assertEqual(response.status_code, 302, response.content.decode())
        self.assertEqual(self.resumen()["progreso_huerto"], 100)
        self.assertEqual(servicios.puntos_de_usuario(self.participante, self.huerto), 125)
        self.assertEqual(servicios.puntos_de_usuario(self.responsable, self.huerto), 0)
        cliente_anular = Client(enforce_csrf_checks=True)
        cliente_anular.force_login(self.responsable)
        ultima = Actividad.objects.get(tipo_id=Tipo.EMPAQUETADO)
        url = reverse("actividades:anular_actividad", args=[ultima.pk])
        cliente_anular.get(url)
        response = cliente_anular.post(url, {"motivo": "Corregir dato ficticio",
            "csrfmiddlewaretoken": cliente_anular.cookies["csrftoken"].value})
        self.assertEqual(response.status_code, 302)
        self.assertLess(self.resumen()["progreso_huerto"], 100)

    def test_responsable_puede_ser_maestro(self):
        for tipo in Actividad.TIPOS_GENERALES: self.registrar(tipo, actor=self.responsable)
        for tipo, dias in [(Tipo.SIEMBRA, 15), (Tipo.CUIDADOS, 16), (Tipo.COSECHA, 20),
            (Tipo.LIMPIEZA, 20), (Tipo.SECADO, 20), (Tipo.EMPAQUETADO, 30)]:
            self.registrar(tipo, dias, actor=self.responsable)
        candidato = Miembro.objects.get(usuario=self.responsable)
        servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Puede guiar", maestro_esperado_id=None)
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro_id, candidato.pk)


    def test_sustitucion_rechaza_formulario_antiguo_y_candidato_ajeno(self):
        self.ciclo()  # Participante: 125 puntos.
        otra = elegir_planta(actor=self.responsable, planta=Planta.objects.get(codigo="romero"), metodo_siembra="semillas")
        # Responsable: 95 por esta planta y otros 15 por la siguiente.
        for tipo, dias in [(Tipo.SIEMBRA, 15), (Tipo.SENALETICA, 15), (Tipo.CUIDADOS, 16), (Tipo.RIEGO, 16),
            (Tipo.BANO, 16), (Tipo.GRATITUD, 16), (Tipo.COSECHA, 20), (Tipo.LIMPIEZA, 20),
            (Tipo.SECADO, 20), (Tipo.EMPAQUETADO, 30)]:
            self.registrar(tipo, dias, actor=self.responsable, seleccion=otra)
        tercera = elegir_planta(actor=self.responsable, planta=Planta.objects.get(codigo="toronjil"), metodo_siembra="semillas")
        self.registrar(Tipo.SIEMBRA, 15, actor=self.responsable, seleccion=tercera)
        primero = Miembro.objects.get(usuario=self.participante)
        segundo = Miembro.objects.get(usuario=self.responsable)
        servicios.nombrar_maestro(self.huerto, self.responsable, primero, "Puede guiar", maestro_esperado_id=None)
        with self.assertRaises(ValidationError):
            servicios.nombrar_maestro(self.huerto, self.responsable, segundo, "Puede guiar", maestro_esperado_id=None)
        servicios.nombrar_maestro(self.huerto, self.responsable, segundo, "Sustitución justificada", maestro_esperado_id=primero.pk)
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro_id, segundo.pk)
        self.assertEqual(self.resumen()["nivel_usuario"]["nombre"], "Oficial")
        crear_comunidad(actor=self.ajeno, nombre="Otra", tipo="persona", contacto_nombre="Otro",
            contacto_telefono="0990000001", contacto_correo="otro@example.com")
        with self.assertRaises(ValidationError):
            servicios.nombrar_maestro(self.huerto, self.responsable, Miembro.objects.get(usuario=self.ajeno),
                "No pertenece", maestro_esperado_id=segundo.pk)
        self.huerto.refresh_from_db(); self.assertEqual(self.huerto.maestro_id, segundo.pk)

    def test_cargar_catalogo_no_modifica_historial_ni_maestro(self):
        self.ciclo()
        candidato = Miembro.objects.get(usuario=self.participante)
        servicios.nombrar_maestro(self.huerto, self.responsable, candidato, "Puede guiar", maestro_esperado_id=None)
        antes = list(Actividad.objects.values())
        call_command("cargar_catalogo", stdout=StringIO())
        self.assertEqual(list(Actividad.objects.values()), antes)
        self.huerto.refresh_from_db(); self.assertEqual(self.huerto.maestro_id, candidato.pk)



ESTADOS_ANTES_DE_SEMBRAR = tuple(t for t in Tipo.values if t not in Actividad.TIPOS_GENERALES and t != Tipo.SIEMBRA)
