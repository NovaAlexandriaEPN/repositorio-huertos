"""
Pruebas automáticas del módulo de actividades.
Cubre las reglas críticas del plan de trabajo (CP-05 a CP-08):
- Actividades y fechas (13 tipos, plazos de preparación 14/15 y secado 9/10, fecha futura/anterior,
  empate por ID, cuidado post-cosecha)
- Reenvíos y puntos (idempotencia por UUID, carga distinta, anulado no reactivado, otro UUID no
  duplica hito, 5/0 en cuidado y riego)
- Anulaciones (última activa por planta, preparación con siembras bloqueada, diseño/ritual independientes,
  conservación del actor original, auditoría de motivo/autor/fecha, deducción de puntos)
- Maestro de huerto (umbral de 100 pts, pertenencia, permiso de admin, motivo, sustitución,
  formulario desactualizado, retiro bajo 100)
- Reglas puras de Guillermo (progreso sobre 6 hitos y niveles)
"""
import uuid
from datetime import timedelta
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.utils import timezone

from cuentas.models import Usuario
from comunidades.models import Comunidad, Huerto, Miembro
from actividades.models import Actividad
from actividades import servicios, reglas


class ReglasPurasTest(TestCase):
    """Pruebas unitarias para las funciones puras de reglas.py (Guillermo - G2)."""

    def test_calcular_progreso_seis_hitos(self):
        """El progreso debe calcularse exactamente sobre los 6 hitos (0 a 100%)."""
        self.assertEqual(reglas.calcular_progreso([]), 0.0)
        self.assertEqual(reglas.calcular_progreso(['siembra']), 16.7)
        self.assertEqual(reglas.calcular_progreso(['preparacion', 'siembra', 'riego']), 50.0)
        todos_hitos = ['preparacion', 'siembra', 'riego', 'cuidado', 'cosecha', 'secado']
        self.assertEqual(reglas.calcular_progreso(todos_hitos), 100.0)

    def test_calcular_nivel_y_umbrales(self):
        """Verifica los 5 niveles, nombres de rangos y umbral para Maestro (>= 100)."""
        nivel1 = reglas.calcular_nivel(30)
        self.assertEqual(nivel1['nivel'], 1)
        self.assertFalse(nivel1['es_elegible_maestro'])

        nivel2 = reglas.calcular_nivel(99)
        self.assertEqual(nivel2['nivel'], 2)
        self.assertFalse(nivel2['es_elegible_maestro'])

        nivel3 = reglas.calcular_nivel(100)
        self.assertEqual(nivel3['nivel'], 3)
        self.assertTrue(nivel3['es_elegible_maestro'])

        nivel4 = reglas.calcular_nivel(250)
        self.assertEqual(nivel4['nivel'], 4)
        self.assertTrue(nivel4['es_elegible_maestro'])

        nivel5 = reglas.calcular_nivel(350)
        self.assertEqual(nivel5['nivel'], 5)
        self.assertTrue(nivel5['es_elegible_maestro'])

    def test_puntos_primero_vs_siguientes_cuidado_riego(self):
        """Cuidado y riego otorgan 5 la primera vez y 0 las siguientes."""
        self.assertEqual(reglas.calcular_puntos_actividad('cuidado', es_primera_en_planta=True), 5)
        self.assertEqual(reglas.calcular_puntos_actividad('cuidado', es_primera_en_planta=False), 0)
        self.assertEqual(reglas.calcular_puntos_actividad('riego', es_primera_en_planta=True), 5)
        self.assertEqual(reglas.calcular_puntos_actividad('riego', es_primera_en_planta=False), 0)
        self.assertEqual(reglas.calcular_puntos_actividad('siembra', es_primera_en_planta=True), 15)


class BaseActividadesTestCase(TestCase):
    """Configuración base para pruebas de integración con modelos del dominio."""

    def setUp(self):
        # Usuarios
        self.admin_user = Usuario.objects.create_user(
            username='admin_huerto',
            password='Password123!',
            first_name='Admin',
            last_name='General'
        )
        self.socio1 = Usuario.objects.create_user(
            username='juan_cultivador',
            password='Password123!',
            first_name='Juan',
            last_name='Cultivador'
        )
        self.socio2 = Usuario.objects.create_user(
            username='maria_sanadora',
            password='Password123!',
            first_name='Maria',
            last_name='Sanadora'
        )
        self.ajeno = Usuario.objects.create_user(
            username='usuario_ajeno',
            password='Password123!',
            first_name='Pedro',
            last_name='Ajeno'
        )

        # Comunidad y Huerto
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad San Pedro',
            codigo='CSP-001',
            creador=self.admin_user
        )
        self.huerto = Huerto.objects.create(
            comunidad=self.comunidad,
            nombre='Huerto Ancestral San Pedro',
            area_m2=120.5
        )

        # Membresías
        self.m_admin = Miembro.objects.create(
            usuario=self.admin_user,
            comunidad=self.comunidad,
            rol='ADMIN',
            puntos=0
        )
        self.m_socio1 = Miembro.objects.create(
            usuario=self.socio1,
            comunidad=self.comunidad,
            rol='MIEMBRO',
            puntos=0
        )
        self.m_socio2 = Miembro.objects.create(
            usuario=self.socio2,
            comunidad=self.comunidad,
            rol='MIEMBRO',
            puntos=0
        )


class ActividadesYFechasTest(BaseActividadesTestCase):
    """Pruebas para el Caso CP-05: Actividades y fechas."""

    def test_recorrer_los_13_tipos_con_datos_ficticios(self):
        """Los 13 tipos de actividad deben poder registrarse válidamente."""
        hoy = timezone.localdate()
        todos_los_tipos = [choice[0] for choice in Actividad.TIPO_ACTIVIDAD_CHOICES]
        self.assertEqual(len(todos_los_tipos), 13)

        for tipo in todos_los_tipos:
            planta = 'Menta' if tipo not in ('diseno', 'ritual') else ''
            act = servicios.registrar_actividad(
                huerto=self.huerto,
                usuario=self.socio1,
                tipo=tipo,
                fecha=hoy,
                planta=planta,
                detalles=f"Labor de {tipo}"
            )
            self.assertEqual(act.estado, Actividad.ESTADO_ACTIVA)
            self.assertEqual(act.actor_original, self.socio1)

    def test_rechazo_de_fecha_futura(self):
        """No se debe permitir registrar una actividad con fecha futura."""
        fecha_futura = timezone.localdate() + timedelta(days=2)
        with self.assertRaises(ValidationError) as ctx:
            servicios.registrar_actividad(
                huerto=self.huerto,
                usuario=self.socio1,
                tipo='siembra',
                fecha=fecha_futura,
                planta='Manzanilla'
            )
        self.assertIn("fecha futura", str(ctx.exception).lower())

    def test_empate_por_id_en_historial(self):
        """Cuando dos actividades tienen la misma fecha, el orden secundario debe ser por ID."""
        hoy = timezone.localdate()
        act1 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='preparacion',
            fecha=hoy,
            planta='Toronjil'
        )
        act2 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy,
            planta='Toronjil'
        )
        # En el historial descendente, la más reciente en ID aparece primero
        historial = list(servicios.obtener_historial_actividades(self.huerto, self.socio1, planta='Toronjil'))
        self.assertEqual(historial[0].id, act2.id)
        self.assertEqual(historial[1].id, act1.id)

    def test_cuidado_despues_de_cosecha_permitido(self):
        """Cuidado después de cosecha debe ser aceptado si la planta sigue en el huerto."""
        hoy = timezone.localdate()
        fecha_cosecha = hoy - timedelta(days=3)
        fecha_cuidado = hoy - timedelta(days=1)

        servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cosecha',
            fecha=fecha_cosecha,
            planta='Romero'
        )
        act_cuidado = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cuidado',
            fecha=fecha_cuidado,
            planta='Romero'
        )
        self.assertEqual(act_cuidado.estado, Actividad.ESTADO_ACTIVA)


class ReenviosYPuntosTest(BaseActividadesTestCase):
    """Pruebas para el Caso CP-06: Reenvíos y puntos."""

    def test_uuid_y_carga_iguales_devuelve_existente(self):
        """Mismo UUID y misma carga devuelve la actividad existente sin duplicar puntos ni registros."""
        hoy = timezone.localdate()
        req_uuid = uuid.uuid4()

        act1 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy,
            planta='Matico',
            request_uuid=req_uuid
        )
        puntos_iniciales = act1.puntos
        self.m_socio1.refresh_from_db()
        puntos_miembro_1 = self.m_socio1.puntos
        self.assertEqual(puntos_miembro_1, puntos_iniciales)

        # Reenvío idéntico
        act2 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy,
            planta='Matico',
            request_uuid=req_uuid
        )
        self.assertEqual(act1.id, act2.id)
        self.assertEqual(Actividad.objects.filter(uuid=req_uuid).count(), 1)

        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, puntos_miembro_1)

    def test_carga_distinta_con_mismo_uuid_rechazada(self):
        """Mismo UUID con carga distinta debe ser rechazado con ValidationError."""
        hoy = timezone.localdate()
        req_uuid = uuid.uuid4()

        servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy,
            planta='Ortiga',
            request_uuid=req_uuid
        )

        with self.assertRaises(ValidationError) as ctx:
            servicios.registrar_actividad(
                huerto=self.huerto,
                usuario=self.socio1,
                tipo='cosecha',  # carga distinta
                fecha=hoy,
                planta='Ortiga',
                request_uuid=req_uuid
            )
        self.assertIn("carga de datos distinta", str(ctx.exception))

    def test_actividad_anulada_con_mismo_uuid_no_reactivada(self):
        """Un reenvío de un UUID que ya fue anulado no reactiva la actividad."""
        hoy = timezone.localdate()
        req_uuid = uuid.uuid4()

        act = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy,
            planta='Llantén',
            request_uuid=req_uuid
        )
        servicios.anular_actividad(act.id, self.socio1, motivo="Error de prueba")

        with self.assertRaises(ValidationError) as ctx:
            servicios.registrar_actividad(
                huerto=self.huerto,
                usuario=self.socio1,
                tipo='siembra',
                fecha=hoy,
                planta='Llantén',
                request_uuid=req_uuid
            )
        self.assertIn("no puede ser reactivada", str(ctx.exception).lower())

    def test_cuidado_y_riego_primero_5_y_siguientes_0(self):
        """El primer cuidado/riego otorga 5 pts y los siguientes 0 pts."""
        hoy = timezone.localdate()

        # Primer riego
        r1 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='riego',
            fecha=hoy,
            planta='Cedrón'
        )
        self.assertEqual(r1.puntos, 5)

        # Segundo riego en la misma planta
        r2 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='riego',
            fecha=hoy,
            planta='Cedrón'
        )
        self.assertEqual(r2.puntos, 0)

        # Primer cuidado
        c1 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cuidado',
            fecha=hoy,
            planta='Cedrón'
        )
        self.assertEqual(c1.puntos, 5)

        # Segundo cuidado
        c2 = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cuidado',
            fecha=hoy,
            planta='Cedrón'
        )
        self.assertEqual(c2.puntos, 0)

        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, 10)  # 5 + 0 + 5 + 0

    def test_actor_y_objetos_ajenos_protegidos(self):
        """Un usuario que no pertenece a la comunidad no puede registrar ni consultar actividades."""
        hoy = timezone.localdate()
        with self.assertRaises(PermissionDenied):
            servicios.registrar_actividad(
                huerto=self.huerto,
                usuario=self.ajeno,
                tipo='siembra',
                fecha=hoy,
                planta='Lavanda'
            )

        with self.assertRaises(PermissionDenied):
            servicios.obtener_historial_actividades(self.huerto, self.ajeno)


class AnulacionesTest(BaseActividadesTestCase):
    """Pruebas para el Caso CP-07: Anulaciones."""

    def test_ultima_activa_por_planta(self):
        """Solo se puede anular la última actividad activa registrada para una planta."""
        hoy = timezone.localdate()
        act_prep = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='preparacion',
            fecha=hoy - timedelta(days=2),
            planta='Salvia'
        )
        act_siembra = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy - timedelta(days=1),
            planta='Salvia'
        )

        # Intentar anular la preparación teniendo una siembra posterior
        with self.assertRaises(ValidationError) as ctx:
            servicios.anular_actividad(act_prep.id, self.socio1, motivo="Quiero anular la preparacion")
        self.assertIn("última actividad activa", str(ctx.exception).lower())

        # Anular la siembra (que es la última activa) sí debe funcionar
        anulada = servicios.anular_actividad(act_siembra.id, self.socio1, motivo="Siembra fallida")
        self.assertEqual(anulada.estado, Actividad.ESTADO_ANULADA)

    def test_preparacion_con_siembras_bloqueada(self):
        """No se puede anular una preparación si existen siembras activas posteriores."""
        hoy = timezone.localdate()
        act_prep = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='preparacion',
            fecha=hoy - timedelta(days=5),
            planta='Laurel'
        )
        servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy - timedelta(days=2),
            planta='Laurel'
        )

        with self.assertRaises(ValidationError):
            servicios.anular_actividad(act_prep.id, self.socio1, motivo="Anular prep")

    def test_diseno_y_ritual_independientes(self):
        """Diseño y ritual pueden anularse independientemente de otras actividades."""
        hoy = timezone.localdate()
        act_diseno = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='diseno',
            fecha=hoy - timedelta(days=10),
            planta=''
        )
        servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='siembra',
            fecha=hoy - timedelta(days=2),
            planta='Chilca'
        )

        # Anular diseño es independiente
        anulada = servicios.anular_actividad(act_diseno.id, self.socio1, motivo="Reajuste del croquis")
        self.assertEqual(anulada.estado, Actividad.ESTADO_ANULADA)

    def test_conservar_actor_original_y_auditoria_completa(self):
        """Al anular, el actor original no cambia, y se registran motivo, autor y fecha."""
        hoy = timezone.localdate()
        act = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='ritual',
            fecha=hoy,
            planta=''
        )
        self.assertEqual(act.actor_original, self.socio1)

        # El admin anula la actividad
        anulada = servicios.anular_actividad(act.id, self.admin_user, motivo="Ritual duplicado por error")
        self.assertEqual(anulada.actor_original, self.socio1)  # CONSERVA ACTOR ORIGINAL
        self.assertEqual(anulada.autor_anulacion, self.admin_user)
        self.assertEqual(anulada.motivo_anulacion, "Ritual duplicado por error")
        self.assertIsNotNone(anulada.fecha_anulacion)

    def test_deduccion_de_puntos_tras_anular(self):
        """Al anular una actividad se deben deducir los puntos ganados."""
        hoy = timezone.localdate()
        self.m_socio1.refresh_from_db()
        puntos_antes = self.m_socio1.puntos

        act = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cosecha',
            fecha=hoy,
            planta='Paico'
        )
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, puntos_antes + 20)

        servicios.anular_actividad(act.id, self.socio1, motivo="Cosecha registrada con peso equivocado")
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, puntos_antes)


class MaestroDeHuertoTest(BaseActividadesTestCase):
    """Pruebas para el Caso CP-08: Nombramiento y sustitución del Maestro."""

    def test_nombramiento_requiere_umbral_100_puntos(self):
        """Un usuario con menos de 100 puntos no puede ser nombrado Maestro."""
        self.m_socio2.puntos = 95
        self.m_socio2.save()

        with self.assertRaises(ValidationError) as ctx:
            servicios.nombrar_o_sustituir_maestro(
                huerto=self.huerto,
                usuario_autor=self.admin_user,
                nuevo_maestro_usuario=self.socio2,
                motivo="Gran conocimiento medicinal"
            )
        self.assertIn("100 puntos", str(ctx.exception))

    def test_nombramiento_exitoso_y_sustitucion(self):
        """Con >= 100 puntos y motivo, un miembro puede ser nombrado y sustituido como único Maestro."""
        self.m_socio1.puntos = 120
        self.m_socio1.save()

        self.m_socio2.puntos = 150
        self.m_socio2.save()

        # Primer nombramiento
        servicios.nombrar_o_sustituir_maestro(
            huerto=self.huerto,
            usuario_autor=self.admin_user,
            nuevo_maestro_usuario=self.socio1,
            motivo="Dedicación comprobada en el huerto"
        )
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio1)
        self.assertEqual(self.huerto.autor_maestro, self.admin_user)

        # Sustitución por socio2
        servicios.nombrar_o_sustituir_maestro(
            huerto=self.huerto,
            usuario_autor=self.admin_user,
            nuevo_maestro_usuario=self.socio2,
            motivo="Nuevo ciclo agrícola liderado por María"
        )
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio2)

    def test_retiro_automatico_de_maestro_bajo_100_puntos(self):
        """Si una anulación reduce los puntos del Maestro bajo 100, se retira su nombramiento."""
        hoy = timezone.localdate()
        self.m_socio1.puntos = 85
        self.m_socio1.save()

        # Registrar cosecha (+20 pts) -> 105 pts
        act = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cosecha',
            fecha=hoy,
            planta='Violeta'
        )
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, 105)

        # Nombrar maestro
        servicios.nombrar_o_sustituir_maestro(
            huerto=self.huerto,
            usuario_autor=self.admin_user,
            nuevo_maestro_usuario=self.socio1,
            motivo="Superó los 100 puntos"
        )
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio1)

        # Anular la cosecha: pierde 20 pts -> 85 pts (< 100)
        servicios.anular_actividad(act.id, self.admin_user, motivo="Cosecha anulada")
        self.huerto.refresh_from_db()
        self.assertIsNone(self.huerto.maestro)
        self.assertIn("Retiro automático", self.huerto.motivo_maestro)

    def test_300_puntos_no_concede_nombramiento_automatico(self):
        """Tener 300 puntos no nombra automáticamente a un miembro ni da admin."""
        self.m_socio1.puntos = 300
        self.m_socio1.save()

        self.huerto.refresh_from_db()
        self.assertIsNone(self.huerto.maestro)
        self.assertEqual(self.m_socio1.rol, 'MIEMBRO')


class VistasActividadesTestCase(BaseActividadesTestCase):
    """Pruebas de peticiones HTTP para formularios y vistas de actividades."""

    def setUp(self):
        super().setUp()
        self.client.force_login(self.socio1)

    def test_vista_huerto_virtual_get_200(self):
        """GET al huerto virtual debe retornar status 200 y mostrar datos del huerto."""
        url = f"/actividades/{self.huerto.id}/huerto-virtual/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.huerto.nombre)

    def test_vista_registrar_actividad_get_y_post(self):
        """GET muestra formulario con UUID y POST registra la actividad con redirección."""
        url = f"/actividades/{self.huerto.id}/registrar/"
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "uuid")

        req_uuid = uuid.uuid4()
        hoy = timezone.localdate().isoformat()
        datos = {
            'uuid': str(req_uuid),
            'tipo': 'siembra',
            'planta': 'Manzanilla',
            'fecha': hoy,
            'detalles': 'Siembra comunitaria matutina'
        }
        resp_post = self.client.post(url, data=datos, follow=True)
        self.assertEqual(resp_post.status_code, 200)
        self.assertTrue(Actividad.objects.filter(uuid=req_uuid).exists())

    def test_vista_historial_get(self):
        """GET al historial debe mostrar las actividades y permitir filtros."""
        hoy = timezone.localdate()
        servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='riego',
            fecha=hoy,
            planta='Menta'
        )
        url = f"/actividades/{self.huerto.id}/historial/?planta=Menta"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Menta")

    def test_vista_anular_actividad_get_y_post(self):
        """GET muestra pantalla de confirmación y POST anula la actividad."""
        hoy = timezone.localdate()
        act = servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo='cosecha',
            fecha=hoy,
            planta='Toronjil'
        )
        url = f"/actividades/anular/{act.id}/"
        resp_get = self.client.get(url)
        self.assertEqual(resp_get.status_code, 200)
        self.assertContains(resp_get, "Confirmar Anulación")

        resp_post = self.client.post(url, data={'motivo': 'Error en fecha de cosecha'}, follow=True)
        self.assertEqual(resp_post.status_code, 200)
        act.refresh_from_db()
        self.assertEqual(act.estado, Actividad.ESTADO_ANULADA)
        self.assertEqual(act.motivo_anulacion, 'Error en fecha de cosecha')

    def test_vista_nombrar_maestro_por_admin(self):
        """Solo administradores pueden acceder y postear nombramiento de Maestro."""
        # socio1 (no admin) intenta acceder -> redirigido con error
        url = f"/actividades/{self.huerto.id}/maestro/"
        resp_no_admin = self.client.get(url, follow=True)
        self.assertEqual(resp_no_admin.status_code, 200)

        # Login con admin
        self.client.force_login(self.admin_user)
        self.m_socio1.puntos = 150
        self.m_socio1.save()

        resp_admin_get = self.client.get(url)
        self.assertEqual(resp_admin_get.status_code, 200)

        resp_admin_post = self.client.post(url, data={
            'candidato': self.socio1.id,
            'motivo': 'Trayectoria destacada en plantas medicinales'
        }, follow=True)
        self.assertEqual(resp_admin_post.status_code, 200)
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio1)



class PlazosAgricolasTest(BaseActividadesTestCase):
    """CP-05: plazos de preparación 14/15 días y secado 9/10 días, y orden de fechas."""

    def _registrar(self, tipo, dias_atras, planta='Toronjil'):
        return servicios.registrar_actividad(
            huerto=self.huerto,
            usuario=self.socio1,
            tipo=tipo,
            fecha=timezone.localdate() - timedelta(days=dias_atras),
            planta=planta
        )

    def test_siembra_14_dias_despues_de_preparacion_aceptada(self):
        """El día 14 después de la preparación es el último día válido para sembrar."""
        self._registrar('preparacion', 14)
        siembra = self._registrar('siembra', 0)
        self.assertEqual(siembra.estado, Actividad.ESTADO_ACTIVA)

    def test_siembra_15_dias_despues_de_preparacion_rechazada(self):
        """El día 15 después de la preparación ya no se puede sembrar."""
        self._registrar('preparacion', 15)
        with self.assertRaises(ValidationError) as ctx:
            self._registrar('siembra', 0)
        self.assertIn("14 días", str(ctx.exception))

    def test_siembra_anterior_a_preparacion_rechazada(self):
        """Una siembra con fecha anterior a la preparación de la planta se rechaza."""
        self._registrar('preparacion', 2)
        with self.assertRaises(ValidationError):
            self._registrar('siembra', 5)

    def test_siembra_sin_preparacion_permitida(self):
        """Si la planta no tiene preparación registrada, la siembra no se bloquea por plazo."""
        siembra = self._registrar('siembra', 0, planta='Ruda')
        self.assertEqual(siembra.estado, Actividad.ESTADO_ACTIVA)

    def test_secado_9_dias_despues_de_cosecha_aceptado(self):
        """El día 9 después de la cosecha es el último día válido para el secado."""
        self._registrar('cosecha', 9)
        secado = self._registrar('secado', 0)
        self.assertEqual(secado.estado, Actividad.ESTADO_ACTIVA)

    def test_secado_10_dias_despues_de_cosecha_rechazado(self):
        """El día 10 después de la cosecha ya no se puede registrar el secado."""
        self._registrar('cosecha', 10)
        with self.assertRaises(ValidationError) as ctx:
            self._registrar('secado', 0)
        self.assertIn("9 días", str(ctx.exception))

    def test_secado_antes_de_cosecha_rechazado(self):
        """El secado no puede tener fecha anterior a la cosecha."""
        self._registrar('cosecha', 1)
        with self.assertRaises(ValidationError):
            self._registrar('secado', 3)

    def test_secado_sin_cosecha_rechazado(self):
        """No se puede registrar secado de una planta sin cosecha activa."""
        with self.assertRaises(ValidationError):
            self._registrar('secado', 0, planta='Matico')

    def test_preparacion_anulada_no_cuenta_para_el_plazo(self):
        """Una preparación anulada no habilita ni bloquea la siembra."""
        prep = self._registrar('preparacion', 30)
        servicios.anular_actividad(prep.id, self.socio1, motivo="Registrada por error")
        siembra = self._registrar('siembra', 0)
        self.assertEqual(siembra.estado, Actividad.ESTADO_ACTIVA)


class HitosSinDuplicarTest(BaseActividadesTestCase):
    """CP-06 y CP-07: otro UUID no duplica los puntos de un hito ya cumplido."""

    def test_regla_pura_hito_repetido_da_cero(self):
        """calcular_puntos_actividad da 0 a un hito que ya se cumplió en la planta."""
        self.assertEqual(reglas.calcular_puntos_actividad('siembra', es_primera_en_planta=False), 0)
        self.assertEqual(reglas.calcular_puntos_actividad('cosecha', es_primera_en_planta=False), 0)
        # Las labores que no son hito mantienen su puntaje aunque se repitan
        self.assertEqual(reglas.calcular_puntos_actividad('poda', es_primera_en_planta=False), 5)

    def test_otro_uuid_no_duplica_puntos_de_siembra(self):
        """Dos siembras de la misma planta con UUID distintos suman 15 puntos, no 30."""
        hoy = timezone.localdate()
        primera = servicios.registrar_actividad(
            self.huerto, self.socio1, 'siembra', hoy, planta='Llantén', request_uuid=uuid.uuid4()
        )
        segunda = servicios.registrar_actividad(
            self.huerto, self.socio1, 'siembra', hoy, planta='Llantén', request_uuid=uuid.uuid4()
        )
        self.assertEqual(primera.puntos, 15)
        self.assertEqual(segunda.puntos, 0)
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, 15)

    def test_mismo_hito_en_otra_planta_si_suma(self):
        """El hito se cuenta por planta: sembrar otra especie vuelve a dar puntos."""
        hoy = timezone.localdate()
        a = servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='Ortiga')
        b = servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='Violeta')
        self.assertEqual((a.puntos, b.puntos), (15, 15))

    def test_puntos_correctos_tras_anular_y_volver_a_registrar(self):
        """Si se anula la siembra, registrarla de nuevo vuelve a dar 15 puntos (CP-07)."""
        hoy = timezone.localdate()
        siembra = servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='Marco')
        servicios.anular_actividad(siembra.id, self.socio1, motivo="Especie equivocada")
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, 0)

        nueva = servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='Marco')
        self.assertEqual(nueva.puntos, 15)
        self.m_socio1.refresh_from_db()
        self.assertEqual(self.m_socio1.puntos, 15)


class FormularioDesactualizadoTest(BaseActividadesTestCase):
    """CP-08: un formulario de Maestro abierto antes de otro cambio se rechaza."""

    def setUp(self):
        super().setUp()
        self.m_socio1.puntos = 120
        self.m_socio1.save()
        self.m_socio2.puntos = 150
        self.m_socio2.save()

    def test_servicio_rechaza_maestro_esperado_distinto(self):
        """Si el Maestro cambió desde que se abrió el formulario, el nombramiento se rechaza."""
        # El formulario se abrió sin Maestro (esperado None), pero otro admin nombró a socio1
        servicios.nombrar_o_sustituir_maestro(
            self.huerto, self.admin_user, self.socio1, "Primer nombramiento", maestro_esperado_id=None
        )
        with self.assertRaises(ValidationError) as ctx:
            servicios.nombrar_o_sustituir_maestro(
                self.huerto, self.admin_user, self.socio2, "Formulario viejo", maestro_esperado_id=None
            )
        self.assertIn("cambió", str(ctx.exception))
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio1)

    def test_servicio_acepta_maestro_esperado_actual(self):
        """Con el Maestro esperado correcto, la sustitución se realiza."""
        servicios.nombrar_o_sustituir_maestro(
            self.huerto, self.admin_user, self.socio1, "Primer nombramiento", maestro_esperado_id=None
        )
        servicios.nombrar_o_sustituir_maestro(
            self.huerto, self.admin_user, self.socio2, "Sustitución", maestro_esperado_id=self.socio1.id
        )
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio2)

    def test_vista_rechaza_formulario_desactualizado(self):
        """Por HTTP: el campo oculto viejo provoca un error y el Maestro no cambia."""
        self.client.force_login(self.admin_user)
        url = f"/actividades/{self.huerto.id}/maestro/"
        resp_get = self.client.get(url)
        self.assertContains(resp_get, 'name="maestro_esperado"')

        # Otro administrador nombra a socio1 mientras tanto
        servicios.nombrar_o_sustituir_maestro(self.huerto, self.admin_user, self.socio1, "Cambio intermedio")

        resp_post = self.client.post(url, data={
            'candidato': self.socio2.id,
            'motivo': 'Enviado desde un formulario viejo',
            'maestro_esperado': '',
        }, follow=True)
        self.assertContains(resp_post, "cambió mientras completaba el formulario")
        self.huerto.refresh_from_db()
        self.assertEqual(self.huerto.maestro, self.socio1)


class ResumenHuertoVirtualTest(BaseActividadesTestCase):
    """HU-10: datos de las tarjetas del Huerto Virtual."""

    def test_plantas_cultivadas_sin_repetir(self):
        """Varias labores de la misma planta cuentan como una sola especie."""
        hoy = timezone.localdate()
        for tipo in ('preparacion', 'siembra', 'riego'):
            servicios.registrar_actividad(self.huerto, self.socio1, tipo, hoy, planta='Toronjil')
        servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='toronjil ')
        servicios.registrar_actividad(self.huerto, self.socio1, 'siembra', hoy, planta='Menta')
        resumen = servicios.obtener_resumen_huerto(self.huerto, self.socio1)
        self.assertEqual(sorted(resumen['plantas_cultivadas']), ['Menta', 'Toronjil'])

    def test_porcentaje_dentro_del_nivel(self):
        """La barra del usuario muestra el avance dentro de su nivel, no los puntos totales."""
        self.m_socio1.puntos = 150   # nivel 3 (100 a 199): 50 % del nivel
        self.m_socio1.save()
        self.assertEqual(servicios.obtener_resumen_huerto(self.huerto, self.socio1)['porcentaje_nivel'], 50.0)
        self.m_socio1.puntos = 320   # nivel máximo
        self.m_socio1.save()
        self.assertEqual(servicios.obtener_resumen_huerto(self.huerto, self.socio1)['porcentaje_nivel'], 100.0)

    def test_barra_de_progreso_usa_punto_decimal(self):
        """Con idioma es-ec el ancho CSS debe escribirse con punto (66.7%), no con coma."""
        hoy = timezone.localdate()
        for tipo in ('preparacion', 'siembra', 'riego', 'cosecha'):
            servicios.registrar_actividad(self.huerto, self.socio1, tipo, hoy, planta='Romero')
        self.client.force_login(self.socio1)
        resp = self.client.get(f"/actividades/{self.huerto.id}/huerto-virtual/")
        self.assertContains(resp, 'width: 66.7%')
        self.assertNotContains(resp, 'width: 66,7%')
