"""
Pruebas automáticas del módulo actividades.

Son comprobaciones de desarrollo con `python manage.py test actividades`. La ejecución
formal de CP-05 a CP-08 la hace Guillermo en noviembre y se registra en
docs/v1/resultados.md. Las pruebas usan los modelos reales de cuentas, catálogo y
comunidades (rama de Bryan).

Organización:
    ReglasPurasTest          reglas.py (nivel y progreso; G2, Guillermo)
    ActividadesYFechasTest   CP-05
    PlazosAgricolasTest      CP-05
    ReenviosYPuntosTest      CP-06
    AnulacionesTest          CP-07
    MaestroTest              CP-08
    HuertoVirtualTest        HU-10
    IntegracionComunidadesTest  contrato con PlantaHuerto (README de Bryan)
    VistasTest               pantallas, permisos y POST
"""
import datetime
import uuid

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalogo.models import OpcionHuerto, Planta
from comunidades.models import Comunidad, Huerto, Miembro, PlantaHuerto
from cuentas.models import Usuario

from . import reglas, servicios
from .models import Actividad

Tipo = Actividad.Tipo
Estado = Actividad.Estado


def hace(dias):
    """Fecha de hoy menos `dias` días."""
    return timezone.localdate() - datetime.timedelta(days=dias)


def crear_usuario(username):
    return Usuario.objects.create_user(
        username=username,
        password="Clave-segura-123",
        nombre_completo=username.replace("_", " ").title(),
        fecha_nacimiento=datetime.date(1995, 5, 20),
    )


class BaseActividades(TestCase):
    """Dos comunidades con huerto: la principal (con plantas) y una ajena."""

    @classmethod
    def setUpTestData(cls):
        cls.cerca = OpcionHuerto.objects.create(codigo="cerca-viva", categoria="cerca", nombre="Cerca viva")
        cls.suelo = OpcionHuerto.objects.create(codigo="suelo-franco", categoria="suelo", nombre="Franco")
        cls.agua = OpcionHuerto.objects.create(codigo="agua-lluvia", categoria="agua", nombre="Lluvia")
        cls.romero_cat = Planta.objects.create(codigo="romero", nombre_comun="Romero")
        cls.menta_cat = Planta.objects.create(codigo="menta", nombre_comun="Menta")
        cls.manzanilla_cat = Planta.objects.create(codigo="manzanilla", nombre_comun="Manzanilla")

        cls.responsable = crear_usuario("rosa_responsable")
        cls.socio1 = crear_usuario("juan_cultivador")
        cls.socio2 = crear_usuario("maria_sanadora")
        cls.ajeno = crear_usuario("pedro_ajeno")

        cls.comunidad = cls._crear_comunidad("Comunidad San Pedro", cls.responsable)
        cls.m_responsable = Miembro.objects.create(usuario=cls.responsable, comunidad=cls.comunidad)
        cls.m_socio1 = Miembro.objects.create(usuario=cls.socio1, comunidad=cls.comunidad)
        cls.m_socio2 = Miembro.objects.create(usuario=cls.socio2, comunidad=cls.comunidad)
        cls.huerto = cls._crear_huerto(cls.comunidad)
        cls.romero = PlantaHuerto.objects.create(huerto=cls.huerto, planta=cls.romero_cat, metodo_siembra="esquejes")
        cls.menta = PlantaHuerto.objects.create(huerto=cls.huerto, planta=cls.menta_cat, metodo_siembra="semillas")

        cls.comunidad_ajena = cls._crear_comunidad("Comunidad Vecina", cls.ajeno)
        cls.m_ajeno = Miembro.objects.create(usuario=cls.ajeno, comunidad=cls.comunidad_ajena)
        cls.huerto_ajeno = cls._crear_huerto(cls.comunidad_ajena)
        cls.manzanilla_ajena = PlantaHuerto.objects.create(
            huerto=cls.huerto_ajeno, planta=cls.manzanilla_cat, metodo_siembra="plantulas"
        )

    @classmethod
    def _crear_comunidad(cls, nombre, responsable):
        return Comunidad.objects.create(
            nombre=nombre, tipo="barrio", responsable=responsable,
            contacto_nombre="Contacto", contacto_telefono="0999999999",
            contacto_correo="contacto@ejemplo.com",
        )

    @classmethod
    def _crear_huerto(cls, comunidad):
        return Huerto.objects.create(
            comunidad=comunidad, provincia="Pichincha", parroquia="Chillogallo",
            direccion="Calle 1", area_m2="120.50",
            cerca=cls.cerca, suelo=cls.suelo, fuente_agua=cls.agua,
        )

    def registrar(self, usuario, tipo, dias=0, planta="romero", uuid_envio=None, huerto=None):
        """Registra con el servicio. planta: 'romero', 'menta', None o una PlantaHuerto."""
        if isinstance(planta, str):
            planta = getattr(self, planta)
        if tipo in Actividad.TIPOS_GENERALES and planta == self.romero:
            planta = None
        actividad, _creada = servicios.registrar_actividad(
            huerto=huerto or self.huerto, usuario=usuario, tipo=tipo, fecha=hace(dias),
            planta=planta, request_uuid=uuid_envio,
        )
        return actividad

    def dar_puntos(self, usuario, puntos):
        """Suma puntos con actividades de diseño (10 cada una, sin planta ni límite)."""
        for _ in range(puntos // 10):
            self.registrar(usuario, Tipo.DISENO, planta=None)

    def puntos(self, usuario):
        return servicios.puntos_de_usuario(usuario, self.huerto)


# ---------------------------------------------------------------------------
# Reglas puras (reglas.py)
# ---------------------------------------------------------------------------

class ReglasPurasTest(TestCase):
    def test_progreso_sobre_seis_hitos(self):
        self.assertEqual(reglas.calcular_progreso([]), 0.0)
        self.assertEqual(reglas.calcular_progreso(["preparacion", "siembra", "riego"]), 50.0)
        self.assertEqual(reglas.calcular_progreso(reglas.HITOS), 100.0)

    def test_progreso_ignora_repetidos_y_no_hitos(self):
        self.assertEqual(reglas.calcular_progreso(["siembra", "siembra", "ritual", "poda"]), 16.7)

    def test_limites_de_nivel(self):
        esperados = {0: 1, 49: 1, 50: 2, 99: 2, 100: 3, 199: 3, 200: 4, 299: 4, 300: 5, 900: 5}
        for puntos, nivel in esperados.items():
            with self.subTest(puntos=puntos):
                self.assertEqual(reglas.calcular_nivel(puntos)["nivel"], nivel)

    def test_elegibilidad_desde_100(self):
        self.assertFalse(reglas.calcular_nivel(99)["es_elegible_maestro"])
        self.assertTrue(reglas.calcular_nivel(100)["es_elegible_maestro"])

    def test_porcentaje_dentro_del_nivel(self):
        self.assertEqual(reglas.porcentaje_en_nivel(0), 0.0)
        self.assertEqual(reglas.porcentaje_en_nivel(75), 50.0)
        self.assertEqual(reglas.porcentaje_en_nivel(150), 50.0)
        self.assertEqual(reglas.porcentaje_en_nivel(300), 100.0)

    def test_puntos_negativos_se_tratan_como_cero(self):
        self.assertEqual(reglas.calcular_nivel(-10)["nivel"], 1)


# ---------------------------------------------------------------------------
# CP-05: actividades y fechas
# ---------------------------------------------------------------------------

class ActividadesYFechasTest(BaseActividades):
    def test_los_13_tipos_se_registran_activos(self):
        self.assertEqual(len(Tipo.values), 13)
        for tipo in Tipo.values:
            with self.subTest(tipo=tipo):
                planta = None if tipo in Actividad.TIPOS_GENERALES else self.menta
                if tipo == Tipo.SECADO:
                    self.registrar(self.socio1, Tipo.COSECHA, planta=self.menta)
                actividad = self.registrar(self.socio1, tipo, planta=planta)
                self.assertEqual(actividad.estado, Estado.ACTIVA)
                self.assertEqual(actividad.actor_original, self.socio1)

    def test_fecha_futura_rechazada(self):
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.RIEGO, dias=-1)

    def test_diseno_y_ritual_no_llevan_planta(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_actividad(self.huerto, self.socio1, Tipo.RITUAL, hace(0), planta=self.romero)

    def test_las_demas_actividades_exigen_planta(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_actividad(self.huerto, self.socio1, Tipo.PODA, hace(0), planta=None)

    def test_planta_de_otro_huerto_rechazada(self):
        with self.assertRaises(ValidationError):
            servicios.registrar_actividad(
                self.huerto, self.socio1, Tipo.RIEGO, hace(0), planta=self.manzanilla_ajena
            )

    def test_restriccion_de_base_planta_segun_tipo(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Actividad.objects.create(
                huerto=self.huerto, tipo=Tipo.RIEGO, fecha=hace(0), actor_original=self.socio1
            )

    def test_cuidado_despues_de_cosecha_permitido(self):
        self.registrar(self.socio1, Tipo.COSECHA, dias=3)
        cuidado = self.registrar(self.socio1, Tipo.CUIDADO, dias=1)
        self.assertEqual(cuidado.estado, Estado.ACTIVA)

    def test_empate_de_fecha_se_ordena_por_id(self):
        primera = self.registrar(self.socio1, Tipo.RIEGO, dias=2)
        segunda = self.registrar(self.socio1, Tipo.PODA, dias=2)
        historial = list(servicios.obtener_historial(self.huerto, self.socio1))
        self.assertLess(historial.index(segunda), historial.index(primera))


class PlazosAgricolasTest(BaseActividades):
    def test_siembra_14_dias_despues_aceptada(self):
        self.registrar(self.socio1, Tipo.PREPARACION, dias=14)
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA, dias=0).estado, Estado.ACTIVA)

    def test_siembra_15_dias_despues_rechazada(self):
        self.registrar(self.socio1, Tipo.PREPARACION, dias=15)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SIEMBRA, dias=0)

    def test_siembra_anterior_a_preparacion_rechazada(self):
        self.registrar(self.socio1, Tipo.PREPARACION, dias=2)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SIEMBRA, dias=3)

    def test_siembra_sin_preparacion_permitida(self):
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA).estado, Estado.ACTIVA)

    def test_secado_9_dias_despues_aceptado(self):
        self.registrar(self.socio1, Tipo.COSECHA, dias=9)
        self.assertEqual(self.registrar(self.socio1, Tipo.SECADO, dias=0).estado, Estado.ACTIVA)

    def test_secado_10_dias_despues_rechazado(self):
        self.registrar(self.socio1, Tipo.COSECHA, dias=10)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SECADO, dias=0)

    def test_secado_anterior_a_cosecha_rechazado(self):
        self.registrar(self.socio1, Tipo.COSECHA, dias=2)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SECADO, dias=3)

    def test_secado_sin_cosecha_rechazado(self):
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SECADO)

    def test_plazo_es_por_planta(self):
        self.registrar(self.socio1, Tipo.PREPARACION, dias=20, planta="menta")
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA, planta="romero").estado, Estado.ACTIVA)

    def test_preparacion_anulada_no_cuenta_para_el_plazo(self):
        vieja = self.registrar(self.socio1, Tipo.PREPARACION, dias=20)
        servicios.anular_actividad(vieja.id, self.socio1, "Fecha mal anotada")
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA).estado, Estado.ACTIVA)


# ---------------------------------------------------------------------------
# CP-06: reenvíos y puntos
# ---------------------------------------------------------------------------

class ReenviosYPuntosTest(BaseActividades):
    def test_mismo_uuid_y_carga_devuelve_la_existente(self):
        envio = uuid.uuid4()
        primera, creada = servicios.registrar_actividad(
            self.huerto, self.socio1, Tipo.SIEMBRA, hace(0), planta=self.romero, request_uuid=envio
        )
        repetida, creada_otra_vez = servicios.registrar_actividad(
            self.huerto, self.socio1, Tipo.SIEMBRA, hace(0), planta=self.romero, request_uuid=envio
        )
        self.assertTrue(creada)
        self.assertFalse(creada_otra_vez)
        self.assertEqual(primera.pk, repetida.pk)
        self.assertEqual(Actividad.objects.count(), 1)
        self.assertEqual(self.puntos(self.socio1), 15)

    def test_mismo_uuid_con_otra_carga_rechazado(self):
        envio = uuid.uuid4()
        self.registrar(self.socio1, Tipo.SIEMBRA, uuid_envio=envio)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.SIEMBRA, planta="menta", uuid_envio=envio)

    def test_mismo_uuid_de_otra_persona_rechazado(self):
        envio = uuid.uuid4()
        self.registrar(self.socio1, Tipo.RIEGO, uuid_envio=envio)
        with self.assertRaises(ValidationError):
            self.registrar(self.socio2, Tipo.RIEGO, uuid_envio=envio)

    def test_uuid_de_actividad_anulada_no_la_reactiva(self):
        envio = uuid.uuid4()
        actividad = self.registrar(self.socio1, Tipo.RIEGO, uuid_envio=envio)
        servicios.anular_actividad(actividad.id, self.socio1, "Registro por error")
        with self.assertRaises(ValidationError):
            self.registrar(self.socio1, Tipo.RIEGO, uuid_envio=envio)
        actividad.refresh_from_db()
        self.assertEqual(actividad.estado, Estado.ANULADA)

    def test_otro_uuid_no_duplica_un_hito(self):
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA).puntos, 15)
        self.assertEqual(self.registrar(self.socio2, Tipo.SIEMBRA).puntos, 0)
        self.assertEqual(self.puntos(self.socio1) + self.puntos(self.socio2), 15)

    def test_riego_y_cuidado_dan_5_y_luego_0(self):
        for tipo in (Tipo.RIEGO, Tipo.CUIDADO):
            with self.subTest(tipo=tipo):
                self.assertEqual(self.registrar(self.socio1, tipo).puntos, 5)
                self.assertEqual(self.registrar(self.socio1, tipo).puntos, 0)

    def test_mismo_hito_en_otra_planta_si_suma(self):
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA, planta="romero").puntos, 15)
        self.assertEqual(self.registrar(self.socio1, Tipo.SIEMBRA, planta="menta").puntos, 15)

    def test_labores_que_no_son_hito_suman_siempre(self):
        self.assertEqual(self.registrar(self.socio1, Tipo.PODA).puntos, 5)
        self.assertEqual(self.registrar(self.socio1, Tipo.PODA).puntos, 5)
        self.assertEqual(self.registrar(self.socio1, Tipo.RITUAL, planta=None).puntos, 10)

    def test_persona_ajena_no_registra_ni_consulta(self):
        with self.assertRaises(PermissionDenied):
            self.registrar(self.ajeno, Tipo.RIEGO)
        with self.assertRaises(PermissionDenied):
            servicios.obtener_historial(self.huerto, self.ajeno)
        with self.assertRaises(PermissionDenied):
            servicios.obtener_resumen_huerto(self.huerto, self.ajeno)

    def test_actor_original_es_quien_registra(self):
        actividad = self.registrar(self.socio2, Tipo.ABONO)
        self.assertEqual(actividad.actor_original, self.socio2)


# ---------------------------------------------------------------------------
# CP-07: anulaciones
# ---------------------------------------------------------------------------

class AnulacionesTest(BaseActividades):
    def test_solo_se_anula_la_ultima_activa_de_la_planta(self):
        primera = self.registrar(self.socio1, Tipo.PREPARACION, dias=5)
        segunda = self.registrar(self.socio1, Tipo.RIEGO, dias=2)
        with self.assertRaises(ValidationError):
            servicios.anular_actividad(primera.id, self.socio1, "Intento intermedio")
        servicios.anular_actividad(segunda.id, self.socio1, "Riego registrado dos veces")

    def test_misma_fecha_se_decide_por_id(self):
        primera = self.registrar(self.socio1, Tipo.RIEGO, dias=1)
        self.registrar(self.socio1, Tipo.PODA, dias=1)
        with self.assertRaises(ValidationError):
            servicios.anular_actividad(primera.id, self.socio1, "No es la última")

    def test_preparacion_con_siembras_activas_bloqueada(self):
        # Siembra sin preparación previa y, después, una preparación del mismo día:
        # la preparación es la última, pero la planta ya tiene una siembra activa.
        self.registrar(self.socio1, Tipo.SIEMBRA, dias=1)
        preparacion = self.registrar(self.socio1, Tipo.PREPARACION, dias=1)
        with self.assertRaises(ValidationError):
            servicios.anular_actividad(preparacion.id, self.socio1, "Preparación tardía")

    def test_diseno_y_ritual_se_anulan_aparte(self):
        self.registrar(self.socio1, Tipo.SIEMBRA, dias=0)
        diseno = self.registrar(self.socio1, Tipo.DISENO, dias=5, planta=None)
        ritual = self.registrar(self.socio1, Tipo.RITUAL, dias=4, planta=None)
        servicios.anular_actividad(diseno.id, self.socio1, "Diseño repetido")
        servicios.anular_actividad(ritual.id, self.socio1, "Ritual repetido")

    def test_constancia_y_actor_original(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        servicios.anular_actividad(actividad.id, self.responsable, "Se registró en la planta equivocada")
        actividad.refresh_from_db()
        self.assertEqual(actividad.estado, Estado.ANULADA)
        self.assertEqual(actividad.motivo_anulacion, "Se registró en la planta equivocada")
        self.assertEqual(actividad.anulada_por, self.responsable)
        self.assertIsNotNone(actividad.fecha_anulacion)
        self.assertEqual(actividad.actor_original, self.socio1)
        self.assertTrue(Actividad.objects.filter(pk=actividad.pk).exists())

    def test_motivo_obligatorio(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        with self.assertRaises(ValidationError):
            servicios.anular_actividad(actividad.id, self.socio1, "   ")

    def test_no_se_anula_dos_veces(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        servicios.anular_actividad(actividad.id, self.socio1, "Error de registro")
        with self.assertRaises(ValidationError):
            servicios.anular_actividad(actividad.id, self.socio1, "Otra vez")

    def test_otro_miembro_no_puede_anular(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        with self.assertRaises(PermissionDenied):
            servicios.anular_actividad(actividad.id, self.socio2, "No es mía")
        with self.assertRaises(PermissionDenied):
            servicios.anular_actividad(actividad.id, self.ajeno, "Ni siquiera es mi huerto")

    def test_puntos_estado_y_progreso_al_anular_y_volver_a_registrar(self):
        siembra = self.registrar(self.socio1, Tipo.SIEMBRA)
        self.assertEqual(self.puntos(self.socio1), 15)
        servicios.anular_actividad(siembra.id, self.socio1, "Fecha equivocada")
        self.assertEqual(self.puntos(self.socio1), 0)
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        self.assertEqual(resumen["progreso_huerto"], 0.0)
        otra = self.registrar(self.socio1, Tipo.SIEMBRA)
        self.assertEqual(otra.puntos, 15)
        self.assertEqual(self.puntos(self.socio1), 15)

    def test_restriccion_de_base_constancia_completa(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Actividad.objects.filter(pk=actividad.pk).update(estado=Estado.ANULADA)


# ---------------------------------------------------------------------------
# CP-08: Maestro del huerto
# ---------------------------------------------------------------------------

class MaestroTest(BaseActividades):
    def nombrar(self, candidato, autor=None, motivo="Conoce los saberes del huerto", **kwargs):
        return servicios.nombrar_maestro(self.huerto, autor or self.responsable, candidato, motivo, **kwargs)

    def test_umbral_de_100_puntos(self):
        self.dar_puntos(self.socio1, 90)
        self.registrar(self.socio1, Tipo.PODA)
        self.assertEqual(self.puntos(self.socio1), 95)
        with self.assertRaises(ValidationError):
            self.nombrar(self.m_socio1)
        self.registrar(self.socio1, Tipo.PODA)
        self.nombrar(self.m_socio1)
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.m_socio1)

    def test_constancia_del_nombramiento(self):
        self.dar_puntos(self.socio1, 100)
        self.nombrar(self.m_socio1, motivo="Guía la siembra de romero")
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro_motivo, "Guía la siembra de romero")
        self.assertEqual(self.huerto.maestro_nombrado_por, self.responsable)
        self.assertIsNotNone(self.huerto.maestro_fecha)

    def test_solo_el_responsable_nombra(self):
        self.dar_puntos(self.socio1, 100)
        with self.assertRaises(PermissionDenied):
            self.nombrar(self.m_socio1, autor=self.socio2)

    def test_candidato_de_otra_comunidad_rechazado(self):
        with self.assertRaises(ValidationError):
            self.nombrar(self.m_ajeno)

    def test_motivo_obligatorio(self):
        self.dar_puntos(self.socio1, 100)
        with self.assertRaises(ValidationError):
            self.nombrar(self.m_socio1, motivo="  ")

    def test_como_maximo_uno_y_sustitucion(self):
        self.dar_puntos(self.socio1, 100)
        self.dar_puntos(self.socio2, 100)
        self.nombrar(self.m_socio1)
        self.nombrar(self.m_socio2, motivo="Asume la guía del ciclo de cosecha")
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.m_socio2)
        self.assertEqual(Huerto.objects.filter(maestro__isnull=False).count(), 1)

    def test_no_se_renombra_al_mismo(self):
        self.dar_puntos(self.socio1, 100)
        self.nombrar(self.m_socio1)
        with self.assertRaises(ValidationError):
            self.nombrar(self.m_socio1)

    def test_formulario_desactualizado_rechazado(self):
        self.dar_puntos(self.socio1, 100)
        self.dar_puntos(self.socio2, 100)
        # Dos pestañas abiertas sin Maestro; la primera nombra a socio1.
        self.nombrar(self.m_socio1, maestro_esperado_id=None)
        with self.assertRaises(ValidationError):
            self.nombrar(self.m_socio2, maestro_esperado_id=None)
        self.nombrar(self.m_socio2, maestro_esperado_id=self.m_socio1.pk)

    def test_retiro_automatico_bajo_100(self):
        self.dar_puntos(self.socio1, 100)
        self.nombrar(self.m_socio1)
        ultimo = Actividad.objects.filter(actor_original=self.socio1).order_by("-id").first()
        _actividad, retirado = servicios.anular_actividad(ultimo.id, self.socio1, "Diseño repetido")
        self.assertTrue(retirado)
        self.huerto.refresh_from_db()
        self.assertIsNone(self.huerto.maestro)
        self.assertEqual(self.huerto.maestro_motivo, "")
        self.assertIsNone(self.huerto.maestro_nombrado_por)
        self.assertIsNone(self.huerto.maestro_fecha)

    def test_anular_actividad_de_otra_persona_no_retira_al_maestro(self):
        self.dar_puntos(self.socio1, 100)
        self.nombrar(self.m_socio1)
        riego = self.registrar(self.socio2, Tipo.RIEGO)
        _actividad, retirado = servicios.anular_actividad(riego.id, self.socio2, "Error")
        self.assertFalse(retirado)
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.m_socio1)

    def test_300_puntos_no_nombran_ni_dan_permisos(self):
        self.dar_puntos(self.socio1, 300)
        self.assertEqual(reglas.calcular_nivel(self.puntos(self.socio1))["nivel"], 5)
        self.huerto.refresh_from_db()
        self.assertIsNone(self.huerto.maestro)
        self.dar_puntos(self.socio2, 100)
        with self.assertRaises(PermissionDenied):
            self.nombrar(self.m_socio2, autor=self.socio1)
        riego_ajeno = self.registrar(self.socio2, Tipo.RIEGO)
        with self.assertRaises(PermissionDenied):
            servicios.anular_actividad(riego_ajeno.id, self.socio1, "Intento sin permiso")

    def test_ser_maestro_no_da_permiso_de_anular(self):
        self.dar_puntos(self.socio1, 100)
        self.nombrar(self.m_socio1)
        riego = self.registrar(self.socio2, Tipo.RIEGO)
        with self.assertRaises(PermissionDenied):
            servicios.anular_actividad(riego.id, self.socio1, "El Maestro no administra")

    def test_candidatos_solo_con_100_o_mas(self):
        self.dar_puntos(self.socio1, 100)
        self.dar_puntos(self.socio2, 50)
        candidatos = [m for m, _p in servicios.candidatos_a_maestro(self.huerto)]
        self.assertEqual(candidatos, [self.m_socio1])


# ---------------------------------------------------------------------------
# HU-10: Huerto Virtual
# ---------------------------------------------------------------------------

class HuertoVirtualTest(BaseActividades):
    def test_tarjeta_por_planta_con_etapa_y_progreso(self):
        self.registrar(self.socio1, Tipo.PREPARACION, dias=3, planta="romero")
        self.registrar(self.socio1, Tipo.SIEMBRA, dias=1, planta="romero")
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        tarjetas = {t["nombre"]: t for t in resumen["tarjetas"]}
        self.assertEqual(set(tarjetas), {"Romero", "Menta"})
        self.assertEqual(tarjetas["Romero"]["etapa"], "Sembrada")
        self.assertEqual(tarjetas["Romero"]["progreso"], 33.3)
        self.assertEqual(tarjetas["Menta"]["etapa"], "Sin iniciar")

    def test_plantas_cultivadas_cuentan_cada_seleccion_una_vez(self):
        self.registrar(self.socio1, Tipo.SIEMBRA, planta="romero")
        self.registrar(self.socio2, Tipo.SIEMBRA, planta="romero")
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        self.assertEqual(resumen["plantas_cultivadas"], 1)

    def test_progreso_del_huerto_junta_hitos_de_todas_las_plantas(self):
        self.registrar(self.socio1, Tipo.PREPARACION, planta="romero")
        self.registrar(self.socio1, Tipo.RIEGO, planta="menta")
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        self.assertEqual(resumen["progreso_huerto"], 33.3)

    def test_totales_puntos_y_nivel(self):
        self.dar_puntos(self.socio1, 70)
        riego = self.registrar(self.socio1, Tipo.RIEGO)
        servicios.anular_actividad(riego.id, self.socio1, "Error")
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        self.assertEqual(resumen["puntos_usuario"], 70)
        self.assertEqual(resumen["nivel_usuario"]["nivel"], 2)
        self.assertEqual(resumen["porcentaje_nivel"], 40.0)
        self.assertEqual(resumen["total_activas"], 7)
        self.assertEqual(resumen["total_anuladas"], 1)
        self.assertEqual(resumen["miembros"][0]["miembro"], self.m_socio1)


# ---------------------------------------------------------------------------
# Contrato con comunidades (README de Bryan)
# ---------------------------------------------------------------------------

class IntegracionComunidadesTest(BaseActividades):
    def test_actividad_da_historial_y_bloquea_cambio_de_metodo(self):
        self.assertFalse(self.romero.tiene_historial)
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        servicios.anular_actividad(actividad.id, self.socio1, "Error")
        seleccion = PlantaHuerto.objects.get(pk=self.romero.pk)
        self.assertTrue(seleccion.tiene_historial)
        seleccion.metodo_siembra = "semillas"
        with self.assertRaises(ValidationError):
            seleccion.full_clean()

    def test_no_se_borra_una_planta_con_actividades(self):
        self.registrar(self.socio1, Tipo.RIEGO)
        with self.assertRaises(ProtectedError):
            self.romero.delete()


# ---------------------------------------------------------------------------
# Vistas y permisos
# ---------------------------------------------------------------------------

class VistasTest(BaseActividades):
    def url(self, nombre, *args):
        return reverse(f"actividades:{nombre}", args=args)

    def test_anonimo_va_al_inicio_de_sesion(self):
        respuesta = self.client.get(self.url("inicio_huerto_virtual", self.huerto.id))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("cuentas:login"), respuesta["Location"])

    def test_miembro_ve_sus_pantallas(self):
        self.client.force_login(self.socio1)
        for nombre in ("inicio_huerto_virtual", "registrar_actividad", "historial_actividades"):
            with self.subTest(pantalla=nombre):
                self.assertEqual(self.client.get(self.url(nombre, self.huerto.id)).status_code, 200)

    def test_persona_ajena_recibe_403(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        self.client.force_login(self.ajeno)
        for url in (
            self.url("inicio_huerto_virtual", self.huerto.id),
            self.url("registrar_actividad", self.huerto.id),
            self.url("historial_actividades", self.huerto.id),
            self.url("nombrar_maestro", self.huerto.id),
            self.url("anular_actividad", actividad.id),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_mi_huerto_redirige_al_huerto_propio(self):
        self.client.force_login(self.socio1)
        respuesta = self.client.get(self.url("mi_huerto"))
        self.assertRedirects(respuesta, self.url("inicio_huerto_virtual", self.huerto.id))

    def test_registrar_por_post_y_reenvio_sin_duplicar(self):
        self.client.force_login(self.socio1)
        datos = {
            "uuid": str(uuid.uuid4()), "tipo": Tipo.SIEMBRA, "planta": self.romero.id,
            "fecha": hace(0).isoformat(), "detalles": "Esquejes del vecino",
        }
        url = self.url("registrar_actividad", self.huerto.id)
        self.assertRedirects(self.client.post(url, datos), self.url("historial_actividades", self.huerto.id))
        self.client.post(url, datos)
        self.assertEqual(Actividad.objects.count(), 1)
        self.assertEqual(self.puntos(self.socio1), 15)

    def test_registrar_muestra_error_de_regla(self):
        self.client.force_login(self.socio1)
        datos = {"uuid": str(uuid.uuid4()), "tipo": Tipo.SECADO, "planta": self.romero.id,
                 "fecha": hace(0).isoformat()}
        respuesta = self.client.post(self.url("registrar_actividad", self.huerto.id), datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "cosecha activa")
        self.assertEqual(Actividad.objects.count(), 0)

    def test_anular_por_post(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        self.client.force_login(self.socio1)
        respuesta = self.client.post(self.url("anular_actividad", actividad.id), {"motivo": "Registro duplicado"})
        self.assertRedirects(respuesta, self.url("historial_actividades", self.huerto.id))
        actividad.refresh_from_db()
        self.assertEqual(actividad.estado, Estado.ANULADA)

    def test_otro_miembro_no_abre_la_anulacion(self):
        actividad = self.registrar(self.socio1, Tipo.RIEGO)
        self.client.force_login(self.socio2)
        self.assertEqual(self.client.get(self.url("anular_actividad", actividad.id)).status_code, 403)

    def test_solo_el_responsable_abre_el_nombramiento(self):
        self.client.force_login(self.socio1)
        self.assertEqual(self.client.get(self.url("nombrar_maestro", self.huerto.id)).status_code, 403)
        self.client.force_login(self.responsable)
        self.assertEqual(self.client.get(self.url("nombrar_maestro", self.huerto.id)).status_code, 200)

    def test_nombrar_por_post_y_formulario_desactualizado(self):
        self.dar_puntos(self.socio1, 100)
        self.dar_puntos(self.socio2, 100)
        self.client.force_login(self.responsable)
        url = self.url("nombrar_maestro", self.huerto.id)
        datos = {"candidato": self.m_socio1.id, "motivo": "Guía la siembra", "maestro_esperado": ""}
        self.assertRedirects(self.client.post(url, datos), self.url("inicio_huerto_virtual", self.huerto.id))
        # Segunda pestaña abierta antes del primer nombramiento.
        datos_viejos = {"candidato": self.m_socio2.id, "motivo": "Guía la cosecha", "maestro_esperado": ""}
        respuesta = self.client.post(url, datos_viejos)
        self.assertContains(respuesta, "cambió mientras completabas")
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.m_socio1)
