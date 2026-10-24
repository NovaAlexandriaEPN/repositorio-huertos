from datetime import date
from decimal import Decimal
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, connection, models, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase, TransactionTestCase
from django.test.utils import isolate_apps
from django.urls import reverse
from django.utils import timezone

from catalogo.models import Material, MetodoSiembra, OpcionHuerto, Planta
from cuentas.models import Usuario
from cuentas.aviso import AVISO_DATOS_VERSION

from .models import Comunidad, Huerto, MarcaMaterial, Miembro, PlantaHuerto
from .servicios import (
    cambiar_metodo_siembra,
    configurar_huerto,
    crear_comunidad,
    editar_comunidad,
    elegir_planta,
    listar_miembros,
    listar_materiales,
    marcar_material,
    obtener_comunidad,
    obtener_huerto,
    retirar_planta,
    unirse_comunidad,
)


def crear_usuario(username):
    return Usuario.objects.create_user(
        username=username,
        nombre_completo=username,
        fecha_nacimiento=date(2000, 1, 1),
    )


def datos_comunidad(responsable, **cambios):
    datos = {
        "nombre": "Comunidad de prueba",
        "tipo": Comunidad.Tipo.FAMILIA,
        "responsable": responsable,
        "contacto_nombre": "Contacto de prueba",
        "contacto_telefono": "0991234567",
        "contacto_correo": "contacto@example.com",
    }
    datos.update(cambios)
    return datos


class ComunidadMiembroTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.responsable = crear_usuario("responsable")
        cls.participante = crear_usuario("participante")
        cls.otro_responsable = crear_usuario("otro_responsable")
        cls.sin_comunidad = crear_usuario("sin_comunidad")
        cls.comunidad = Comunidad.objects.create(**datos_comunidad(cls.responsable))
        cls.otra_comunidad = Comunidad.objects.create(**datos_comunidad(cls.otro_responsable))
        cls.miembro_responsable = Miembro.objects.create(
            usuario=cls.responsable, comunidad=cls.comunidad
        )
        cls.miembro_participante = Miembro.objects.create(
            usuario=cls.participante, comunidad=cls.comunidad
        )

    def test_responsable_y_participante_se_derivan_de_la_comunidad(self):
        self.assertTrue(self.miembro_responsable.es_responsable)
        self.assertFalse(self.miembro_participante.es_responsable)
        self.assertEqual(self.responsable.miembro.comunidad, self.comunidad)

    def test_cuenta_no_puede_tener_dos_pertenencias(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Miembro.objects.create(usuario=self.participante, comunidad=self.otra_comunidad)

    def test_cuenta_no_puede_responsabilizarse_de_dos_comunidades(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comunidad.objects.create(**datos_comunidad(self.responsable))

    def test_codigo_tiene_formato_se_conserva_y_es_unico(self):
        codigo = self.comunidad.codigo_invitacion
        self.assertRegex(codigo, r"^[A-F0-9]{12}$")
        self.comunidad.nombre = "Nombre actualizado"
        self.comunidad.save(update_fields=["nombre"])
        self.comunidad.refresh_from_db()
        self.assertEqual(self.comunidad.codigo_invitacion, codigo)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Comunidad.objects.create(
                **datos_comunidad(self.sin_comunidad, codigo_invitacion=codigo)
            )

    def test_no_se_transfieren_responsable_usuario_ni_pertenencia(self):
        self.comunidad.responsable = self.sin_comunidad
        with self.assertRaises(ValidationError) as error:
            self.comunidad.full_clean()
        self.assertIn("responsable", error.exception.message_dict)

        for campo, nuevo_valor in (
            ("usuario", self.sin_comunidad),
            ("comunidad", self.otra_comunidad),
        ):
            with self.subTest(campo=campo):
                miembro = Miembro.objects.get(pk=self.miembro_participante.pk)
                setattr(miembro, campo, nuevo_valor)
                with self.assertRaises(ValidationError) as error:
                    miembro.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_responsable_no_puede_pertenecer_a_otra_comunidad(self):
        nueva = Comunidad(**datos_comunidad(self.participante))
        with self.assertRaises(ValidationError) as error:
            nueva.full_clean()
        self.assertIn("responsable", error.exception.message_dict)

        miembro = Miembro(usuario=self.otro_responsable, comunidad=self.comunidad)
        with self.assertRaises(ValidationError) as error:
            miembro.full_clean()
        self.assertIn("comunidad", error.exception.message_dict)

    def test_tipo_y_contacto_invalidos_se_rechazan(self):
        Comunidad(**datos_comunidad(self.sin_comunidad)).full_clean()
        for campo, valor in (
            ("tipo", "tipo_inventado"),
            ("contacto_correo", "correo-invalido"),
            ("contacto_telefono", "-------"),
        ):
            with self.subTest(campo=campo):
                comunidad = Comunidad(**datos_comunidad(self.sin_comunidad, **{campo: valor}))
                with self.assertRaises(ValidationError) as error:
                    comunidad.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_referencias_impiden_borrar_una_cuenta_o_comunidad_en_uso(self):
        for objeto in (self.responsable, self.participante, self.comunidad):
            with self.subTest(modelo=type(objeto).__name__):
                with self.assertRaises(ProtectedError):
                    objeto.delete()


class HuertoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.responsable = crear_usuario("responsable")
        cls.participante = crear_usuario("participante")
        cls.otro_responsable = crear_usuario("otro_responsable")
        cls.comunidad = Comunidad.objects.create(**datos_comunidad(cls.responsable))
        cls.otra_comunidad = Comunidad.objects.create(**datos_comunidad(cls.otro_responsable))
        cls.miembro = Miembro.objects.create(usuario=cls.participante, comunidad=cls.comunidad)
        cls.miembro_responsable = Miembro.objects.create(
            usuario=cls.responsable, comunidad=cls.comunidad
        )
        cls.miembro_ajeno = Miembro.objects.create(
            usuario=cls.otro_responsable, comunidad=cls.otra_comunidad
        )
        cls.opciones = {}
        for codigo, categoria in (
            ("cerca_viva", OpcionHuerto.Categoria.CERCA),
            ("suelo_limoso", OpcionHuerto.Categoria.SUELO),
            ("agua_goteo", OpcionHuerto.Categoria.AGUA),
            ("diseno_tierra", OpcionHuerto.Categoria.DISENO),
            ("diseno_vertical", OpcionHuerto.Categoria.DISENO),
            ("abono_compost", OpcionHuerto.Categoria.ABONO),
        ):
            cls.opciones[codigo] = OpcionHuerto.objects.create(
                codigo=codigo, categoria=categoria, nombre=codigo
            )

    def datos_huerto(self, **cambios):
        datos = {
            "comunidad": self.comunidad,
            "provincia": "Pichincha",
            "parroquia": "Parroquia de prueba",
            "direccion": "Dirección ficticia",
            "area_m2": Decimal("12.50"),
            "cerca": self.opciones["cerca_viva"],
            "suelo": self.opciones["suelo_limoso"],
            "fuente_agua": self.opciones["agua_goteo"],
        }
        datos.update(cambios)
        return datos

    def test_guarda_configuracion_y_varios_disenos(self):
        huerto = Huerto(**self.datos_huerto())
        huerto.full_clean()
        huerto.save()
        huerto.disenos.set([
            self.opciones["diseno_tierra"], self.opciones["diseno_vertical"]
        ])
        huerto.abonos.add(self.opciones["abono_compost"])

        huerto.refresh_from_db()
        self.assertEqual(self.comunidad.huerto, huerto)
        self.assertEqual(huerto.area_m2, Decimal("12.50"))
        self.assertEqual(huerto.disenos.count(), 2)
        self.assertEqual(huerto.abonos.count(), 1)
        self.assertIsNone(huerto.maestro)

    def test_comunidad_no_puede_tener_dos_huertos(self):
        Huerto.objects.create(**self.datos_huerto())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Huerto.objects.create(**self.datos_huerto())

    def test_area_debe_ser_positiva_en_validacion_y_base(self):
        for area in (Decimal("0"), Decimal("-1")):
            with self.subTest(area=area):
                with self.assertRaises(ValidationError) as error:
                    Huerto(**self.datos_huerto(area_m2=area)).full_clean()
                self.assertIn("area_m2", error.exception.message_dict)
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Huerto.objects.create(**self.datos_huerto(area_m2=area))

    def test_opciones_unicas_deben_ser_de_la_categoria_correcta(self):
        for campo in ("cerca", "suelo", "fuente_agua"):
            with self.subTest(campo=campo):
                huerto = Huerto(**self.datos_huerto(**{campo: self.opciones["abono_compost"]}))
                with self.assertRaises(ValidationError) as error:
                    huerto.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_maestro_guarda_constancia_y_no_concede_el_rol_responsable(self):
        huerto = Huerto(**self.datos_huerto(
            maestro=self.miembro,
            maestro_motivo="Puede guiar la preparación y la siembra.",
            maestro_nombrado_por=self.responsable,
            maestro_fecha=timezone.now(),
        ))
        huerto.full_clean()
        huerto.save()
        self.assertEqual(huerto.maestro, self.miembro)
        self.assertFalse(huerto.maestro.es_responsable)
        self.assertTrue(huerto.maestro_motivo)

        # El responsable también puede recibir el reconocimiento.
        huerto.maestro = self.miembro_responsable
        huerto.full_clean()

    def test_constancia_incompleta_de_maestro_no_se_guarda(self):
        for constancia in (
            {"maestro": self.miembro},
            {"maestro_motivo": "Motivo sin nombramiento"},
            {"maestro_fecha": timezone.now()},
        ):
            with self.subTest(constancia=constancia):
                with self.assertRaises(ValidationError):
                    Huerto(**self.datos_huerto(**constancia)).full_clean()
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Huerto.objects.create(**self.datos_huerto(**constancia))

    def test_maestro_ajeno_autor_incorrecto_y_motivo_vacio_se_rechazan(self):
        base = {
            "maestro": self.miembro,
            "maestro_motivo": "Puede guiar la siembra.",
            "maestro_nombrado_por": self.responsable,
            "maestro_fecha": timezone.now(),
        }
        for campo, valor in (
            ("maestro", self.miembro_ajeno),
            ("maestro_nombrado_por", self.otro_responsable),
            ("maestro_motivo", "  "),
        ):
            with self.subTest(campo=campo):
                huerto = Huerto(**self.datos_huerto(**{**base, campo: valor}))
                with self.assertRaises(ValidationError) as error:
                    huerto.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_huerto_no_se_traslada_y_sus_opciones_unicas_estan_protegidas(self):
        huerto = Huerto.objects.create(**self.datos_huerto())
        with self.assertRaises(ProtectedError):
            self.opciones["cerca_viva"].delete()

        huerto.comunidad = self.otra_comunidad
        with self.assertRaises(ValidationError) as error:
            huerto.full_clean()
        self.assertIn("comunidad", error.exception.message_dict)


class SeleccionesMaterialesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        opciones = {}
        for categoria in (
            OpcionHuerto.Categoria.CERCA,
            OpcionHuerto.Categoria.SUELO,
            OpcionHuerto.Categoria.AGUA,
        ):
            opciones[categoria] = OpcionHuerto.objects.create(
                codigo=categoria, categoria=categoria, nombre=categoria
            )
        cls.huertos = []
        for numero in (1, 2):
            usuario = crear_usuario(f"responsable_{numero}")
            comunidad = Comunidad.objects.create(**datos_comunidad(usuario))
            Miembro.objects.create(usuario=usuario, comunidad=comunidad)
            cls.huertos.append(Huerto.objects.create(
                comunidad=comunidad, provincia="Pichincha",
                parroquia="Parroquia ficticia", direccion="Dirección ficticia",
                area_m2=Decimal("10.00"), cerca=opciones["cerca"],
                suelo=opciones["suelo"], fuente_agua=opciones["agua"],
            ))
        cls.planta = Planta.objects.create(codigo="primera", nombre_comun="Primera")
        cls.otra_planta = Planta.objects.create(codigo="segunda", nombre_comun="Segunda")
        cls.seleccion = PlantaHuerto.objects.create(
            huerto=cls.huertos[0], planta=cls.planta,
            metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        cls.material = Material.objects.create(
            codigo="pala", nombre="Pala", grupo=Material.Grupo.HERRAMIENTAS
        )
        cls.otro_material = Material.objects.create(
            codigo="regadera", nombre="Regadera", grupo=Material.Grupo.HERRAMIENTAS
        )
        cls.marca = MarcaMaterial.objects.create(
            huerto=cls.huertos[0], material=cls.material
        )

    def test_especie_es_unica_en_un_huerto_y_se_comparte_entre_huertos(self):
        duplicada = PlantaHuerto(
            huerto=self.huertos[0], planta=self.planta,
            metodo_siembra=MetodoSiembra.ESQUEJES,
        )
        with self.assertRaises(ValidationError):
            duplicada.full_clean()
        with self.assertRaises(IntegrityError), transaction.atomic():
            duplicada.save()

        otra_seleccion = PlantaHuerto(
            huerto=self.huertos[1], planta=self.planta,
            metodo_siembra=MetodoSiembra.PLANTULAS,
        )
        otra_seleccion.full_clean()
        otra_seleccion.save()
        self.assertEqual(self.planta.selecciones_huerto.count(), 2)

    def test_metodos_validos_y_rechazo_de_inventado_en_validacion_y_base(self):
        for metodo in MetodoSiembra.values:
            self.seleccion.metodo_siembra = metodo
            self.seleccion.full_clean()
        invalida = PlantaHuerto(
            huerto=self.huertos[0], planta=self.otra_planta, metodo_siembra="inventado"
        )
        with self.assertRaises(ValidationError) as error:
            invalida.full_clean()
        self.assertIn("metodo_siembra", error.exception.message_dict)
        with self.assertRaises(IntegrityError), transaction.atomic():
            invalida.save()

    def test_identidad_de_seleccion_no_se_reasigna(self):
        for campo, valor in (("huerto", self.huertos[1]), ("planta", self.otra_planta)):
            with self.subTest(campo=campo):
                seleccion = PlantaHuerto.objects.get(pk=self.seleccion.pk)
                setattr(seleccion, campo, valor)
                with self.assertRaises(ValidationError) as error:
                    seleccion.full_clean()
                self.assertIn(campo, error.exception.message_dict)

    def test_metodo_puede_cambiar_antes_de_tener_historial(self):
        self.assertFalse(self.seleccion.tiene_historial)
        self.seleccion.metodo_siembra = MetodoSiembra.ESQUEJES
        self.seleccion.full_clean()
        self.seleccion.save(update_fields=["metodo_siembra"])
        self.seleccion.refresh_from_db()
        self.assertEqual(self.seleccion.metodo_siembra, MetodoSiembra.ESQUEJES)

    def test_metodo_no_cambia_si_hay_historial(self):
        # Comprueba la regla del modelo; la relación real llegará con Actividad.
        with patch.object(PlantaHuerto, "tiene_historial", new_callable=PropertyMock) as historial:
            historial.return_value = True
            self.seleccion.metodo_siembra = MetodoSiembra.ESTACAS
            with self.assertRaises(ValidationError) as error:
                self.seleccion.full_clean()
        self.assertIn("metodo_siembra", error.exception.message_dict)
        self.seleccion.refresh_from_db()
        self.assertEqual(self.seleccion.metodo_siembra, MetodoSiembra.SEMILLAS)

    def test_referencias_al_catalogo_y_huerto_se_protegen_de_borrado(self):
        for objeto in (self.planta, self.material, self.huertos[0]):
            with self.subTest(modelo=type(objeto).__name__):
                with self.assertRaises(ProtectedError):
                    objeto.delete()

    def test_material_es_unico_por_huerto_y_otro_huerto_tiene_su_propia_marca(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            MarcaMaterial.objects.create(huerto=self.huertos[0], material=self.material)
        otra_marca = MarcaMaterial.objects.create(
            huerto=self.huertos[1], material=self.material, disponible=True
        )
        self.assertTrue(otra_marca.disponible)
        self.assertFalse(self.marca.disponible)

    def test_disponibilidad_se_guarda_sin_afectar_otro_huerto(self):
        otra_marca = MarcaMaterial.objects.create(
            huerto=self.huertos[1], material=self.material
        )
        for disponible in (True, False):
            self.marca.disponible = disponible
            self.marca.full_clean()
            self.marca.save(update_fields=["disponible"])
            self.marca.refresh_from_db()
            otra_marca.refresh_from_db()
            self.assertEqual(self.marca.disponible, disponible)
            self.assertFalse(otra_marca.disponible)
        self.assertEqual(MarcaMaterial.objects.filter(huerto=self.huertos[0]).count(), 1)

    def test_identidad_de_marca_no_se_reasigna(self):
        for campo, valor in (("huerto", self.huertos[1]), ("material", self.otro_material)):
            with self.subTest(campo=campo):
                marca = MarcaMaterial.objects.get(pk=self.marca.pk)
                setattr(marca, campo, valor)
                with self.assertRaises(ValidationError) as error:
                    marca.full_clean()
                self.assertIn(campo, error.exception.message_dict)


class OperacionesComunidadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.responsable = crear_usuario("responsable_servicio")
        cls.participante = crear_usuario("participante_servicio")
        cls.libre = crear_usuario("libre_servicio")
        cls.otro_responsable = crear_usuario("otro_servicio")
        cls.datos = {
            "nombre": "Huerto del barrio",
            "tipo": Comunidad.Tipo.BARRIO,
            "contacto_nombre": "Ana de prueba",
            "contacto_telefono": "0991234567",
            "contacto_correo": "ana@example.com",
        }
        cls.comunidad = crear_comunidad(actor=cls.responsable, **cls.datos)
        cls.otra = crear_comunidad(
            actor=cls.otro_responsable, **{**cls.datos, "nombre": "Comunidad ajena"}
        )
        unirse_comunidad(actor=cls.participante, codigo_invitacion=cls.comunidad.codigo_invitacion)

    def test_crear_incluye_al_responsable_sin_inventar_un_huerto(self):
        comunidad = crear_comunidad(actor=self.libre, **self.datos)
        miembro = Miembro.objects.get(usuario=self.libre)
        self.assertEqual(miembro.comunidad, comunidad)
        self.assertEqual(comunidad.responsable, self.libre)
        self.assertTrue(miembro.es_responsable)
        self.assertFalse(Huerto.objects.filter(comunidad=comunidad).exists())

    def test_unirse_normaliza_codigo_y_no_crea_otra_comunidad(self):
        total = Comunidad.objects.count()
        miembro = unirse_comunidad(
            actor=self.libre, codigo_invitacion=" " + self.comunidad.codigo_invitacion.lower() + " "
        )
        self.assertEqual(miembro.comunidad, self.comunidad)
        self.assertFalse(miembro.es_responsable)
        self.assertEqual(Comunidad.objects.count(), total)

    def test_no_se_duplican_pertenencias_ni_se_cambia_de_comunidad(self):
        for actor in (self.responsable, self.participante):
            with self.subTest(actor=actor.username):
                with self.assertRaises(ValidationError):
                    crear_comunidad(actor=actor, **self.datos)
                for codigo in (self.comunidad.codigo_invitacion, self.otra.codigo_invitacion):
                    with self.assertRaises(ValidationError):
                        unirse_comunidad(actor=actor, codigo_invitacion=codigo)
                self.assertEqual(Miembro.objects.filter(usuario=actor).count(), 1)
                self.assertEqual(obtener_comunidad(actor=actor), self.comunidad)

    def test_codigo_invalido_o_inexistente_no_crea_pertenencia(self):
        for codigo in ("no-es-codigo", " ", "F" * 12):
            with self.subTest(codigo=codigo):
                with self.assertRaises(ValidationError):
                    unirse_comunidad(actor=self.libre, codigo_invitacion=codigo)
                self.assertFalse(Miembro.objects.filter(usuario=self.libre).exists())

    def test_solo_responsable_edita_y_no_cambia_identidades(self):
        codigo = self.comunidad.codigo_invitacion
        actualizada = editar_comunidad(
            actor=self.responsable, **{**self.datos, "nombre": "Nombre corregido"}
        )
        self.assertEqual(actualizada.nombre, "Nombre corregido")
        self.assertEqual(actualizada.codigo_invitacion, codigo)
        self.assertEqual(actualizada.responsable, self.responsable)
        with self.assertRaises(PermissionDenied):
            editar_comunidad(actor=self.participante, **self.datos)
        with self.assertRaises(PermissionDenied):
            editar_comunidad(actor=self.libre, **self.datos)

    def test_cada_responsable_solo_edita_su_propia_comunidad(self):
        editar_comunidad(actor=self.otro_responsable, **{**self.datos, "nombre": "Otra editada"})
        self.comunidad.refresh_from_db()
        self.otra.refresh_from_db()
        self.assertEqual(self.comunidad.nombre, "Huerto del barrio")
        self.assertEqual(self.otra.nombre, "Otra editada")

    def test_entrada_invalida_no_deja_comunidad_ni_pertenencia(self):
        with self.assertRaises(ValidationError):
            crear_comunidad(actor=self.libre, **{**self.datos, "contacto_correo": "invalido"})
        self.assertFalse(Comunidad.objects.filter(responsable=self.libre).exists())
        self.assertFalse(Miembro.objects.filter(usuario=self.libre).exists())

    def test_cuenta_anonima_o_desactivada_no_puede_usar_los_servicios(self):
        # La instancia conserva is_active=True; la comprobación consulta el estado real.
        Usuario.objects.filter(pk=self.libre.pk).update(is_active=False)
        for actor in (AnonymousUser(), self.libre):
            with self.subTest(actor=type(actor).__name__):
                with self.assertRaises(PermissionDenied):
                    crear_comunidad(actor=actor, **self.datos)
                with self.assertRaises(PermissionDenied):
                    unirse_comunidad(actor=actor, codigo_invitacion=self.comunidad.codigo_invitacion)
                with self.assertRaises(PermissionDenied):
                    editar_comunidad(actor=actor, **self.datos)

    def test_consulta_aislada_y_miembros_sin_datos_privados(self):
        self.assertIsNone(obtener_comunidad(actor=self.libre))
        self.assertEqual(listar_miembros(actor=self.libre), [])
        miembros = listar_miembros(actor=self.participante)
        self.assertEqual({m["usuario_id"] for m in miembros}, {self.responsable.pk, self.participante.pk})
        for miembro in miembros:
            self.assertEqual(set(miembro), {"usuario_id", "nombre"})


class PantallasComunidadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.responsable = crear_usuario("ana_pantallas")
        cls.participante = crear_usuario("luis_pantallas")
        cls.libre = crear_usuario("persona_libre")
        cls.ajeno = crear_usuario("persona_ajena")
        cls.datos = {
            "nombre": "Comunidad de Ana",
            "tipo": Comunidad.Tipo.FAMILIA,
            "contacto_nombre": "Ana de prueba",
            "contacto_telefono": "0991234567",
            "contacto_correo": "ana@example.com",
        }
        cls.comunidad = crear_comunidad(actor=cls.responsable, **cls.datos)
        cls.otra = crear_comunidad(
            actor=cls.ajeno, **{**cls.datos, "nombre": "Nombre ajeno reservado"}
        )
        unirse_comunidad(actor=cls.participante, codigo_invitacion=cls.comunidad.codigo_invitacion)

    def test_todas_las_pantallas_exigen_sesion(self):
        for nombre in ("mi_comunidad", "crear", "unirse", "editar"):
            with self.subTest(pantalla=nombre):
                url = reverse("comunidades:" + nombre)
                response = self.client.get(url)
                self.assertRedirects(response, reverse("cuentas:login") + "?next=" + url)

    def test_sin_comunidad_ofrece_crear_o_unirse_sin_crear_registros_por_get(self):
        self.client.force_login(self.libre)
        response = self.client.get(reverse("comunidades:mi_comunidad"))
        self.assertContains(response, reverse("comunidades:crear"))
        self.assertContains(response, reverse("comunidades:unirse"))
        for nombre in ("crear", "unirse"):
            self.assertEqual(self.client.get(reverse("comunidades:" + nombre)).status_code, 200)
        self.assertFalse(Miembro.objects.filter(usuario=self.libre).exists())
        self.assertFalse(Comunidad.objects.filter(responsable=self.libre).exists())

    def test_crear_por_post_ignora_campos_de_permiso_inyectados(self):
        self.client.force_login(self.libre)
        response = self.client.post(reverse("comunidades:crear"), {
            **self.datos,
            "responsable": self.ajeno.pk,
            "codigo_invitacion": "0" * 12,
        })
        self.assertRedirects(response, reverse("comunidades:mi_comunidad"))
        nueva = Comunidad.objects.get(responsable=self.libre)
        self.assertEqual(self.libre.miembro.comunidad, nueva)
        self.assertNotEqual(nueva.codigo_invitacion, "0" * 12)

    def test_unirse_con_codigo_y_reenvio_no_duplica(self):
        self.client.force_login(self.libre)
        datos = {"codigo_invitacion": self.comunidad.codigo_invitacion.lower()}
        self.assertRedirects(
            self.client.post(reverse("comunidades:unirse"), datos),
            reverse("comunidades:mi_comunidad"),
        )
        response = self.client.post(reverse("comunidades:unirse"), datos)
        self.assertContains(response, "Ya perteneces a una comunidad")
        self.assertEqual(Miembro.objects.filter(usuario=self.libre).count(), 1)

    def test_codigo_inexistente_muestra_error_junto_al_formulario(self):
        self.client.force_login(self.libre)
        response = self.client.post(reverse("comunidades:unirse"), {"codigo_invitacion": "F" * 12})
        self.assertFormError(response.context["form"], "codigo_invitacion", "No se encontró una comunidad con ese código.")
        self.assertContains(response, "No se encontró una comunidad con ese código.")
        self.assertFalse(Miembro.objects.filter(usuario=self.libre).exists())

    def test_participante_no_edita_aunque_envie_post_directamente(self):
        self.client.force_login(self.participante)
        for method in (self.client.get, self.client.post):
            with self.subTest(method=method.__name__):
                response = method(reverse("comunidades:editar"), self.datos)
                self.assertEqual(response.status_code, 403)
        self.comunidad.refresh_from_db()
        self.assertEqual(self.comunidad.nombre, self.datos["nombre"])

    def test_responsable_edita_solo_su_comunidad_y_conserva_codigo(self):
        self.client.force_login(self.responsable)
        response = self.client.post(reverse("comunidades:editar"), {
            **self.datos, "nombre": "Comunidad actualizada",
            "comunidad": self.otra.pk, "responsable": self.ajeno.pk,
            "codigo_invitacion": "0" * 12,
        })
        self.assertRedirects(response, reverse("comunidades:mi_comunidad"))
        codigo = self.comunidad.codigo_invitacion
        self.comunidad.refresh_from_db()
        self.otra.refresh_from_db()
        self.assertEqual(self.comunidad.nombre, "Comunidad actualizada")
        self.assertEqual(self.comunidad.responsable, self.responsable)
        self.assertEqual(self.comunidad.codigo_invitacion, codigo)
        self.assertEqual(self.otra.nombre, "Nombre ajeno reservado")

    def test_consulta_no_expone_comunidad_ajena_ni_perfil_de_otro_miembro(self):
        self.participante.fecha_nacimiento = date(2001, 2, 3)
        self.participante.genero = Usuario.Genero.NO_BINARIO
        self.participante.save(update_fields=["fecha_nacimiento", "genero"])
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comunidades:mi_comunidad"), {
            "comunidad": self.otra.pk, "codigo_invitacion": self.otra.codigo_invitacion,
        })
        self.assertContains(response, self.participante.nombre_completo)
        self.assertNotContains(response, self.otra.nombre)
        self.assertNotContains(response, self.otra.codigo_invitacion)
        self.assertNotContains(response, "2001-02-03")
        self.assertNotContains(response, "no_binario")
        self.assertNotContains(response, "Nacimiento")
        self.assertTrue(response.context["puede_editar"])
        for miembro in response.context["miembros"]:
            self.assertEqual(set(miembro), {"usuario_id", "nombre"})

    def test_participante_no_ve_enlace_de_edicion_y_miembro_no_crea_otra(self):
        self.client.force_login(self.participante)
        response = self.client.get(reverse("comunidades:mi_comunidad"))
        self.assertNotContains(response, reverse("comunidades:editar"))
        response = self.client.post(reverse("comunidades:crear"), self.datos)
        self.assertContains(response, "Ya perteneces a una comunidad")
        self.assertEqual(Comunidad.objects.count(), 2)

    def test_post_sin_csrf_se_rechaza_y_formulario_con_token_funciona(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.libre)
        url = reverse("comunidades:crear")
        self.assertEqual(client.post(url, self.datos).status_code, 403)
        self.assertFalse(Comunidad.objects.filter(responsable=self.libre).exists())
        client.get(url)
        response = client.post(url, self.datos, HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value)
        self.assertRedirects(response, reverse("comunidades:mi_comunidad"))

    def test_metodos_no_permitidos_no_modifican_registros(self):
        self.client.force_login(self.responsable)
        self.assertEqual(self.client.post(reverse("comunidades:mi_comunidad")).status_code, 405)
        for nombre in ("crear", "unirse", "editar"):
            self.assertEqual(self.client.delete(reverse("comunidades:" + nombre)).status_code, 405)


def preparar_datos_configurador(destino):
    """Datos ficticios exclusivos de la base temporal de las pruebas."""
    destino.responsable = crear_usuario("responsable_configuracion")
    destino.participante = crear_usuario("participante_configuracion")
    destino.otro_responsable = crear_usuario("responsable_ajeno_configuracion")
    destino.sin_comunidad = crear_usuario("sin_comunidad_configuracion")
    destino.comunidad = crear_comunidad(
        actor=destino.responsable,
        **{k: v for k, v in datos_comunidad(destino.responsable).items() if k != "responsable"},
    )
    destino.otra_comunidad = crear_comunidad(
        actor=destino.otro_responsable,
        **{k: v for k, v in datos_comunidad(destino.otro_responsable).items() if k != "responsable"},
    )
    unirse_comunidad(
        actor=destino.participante, codigo_invitacion=destino.comunidad.codigo_invitacion,
    )
    destino.opciones = {}
    for categoria in OpcionHuerto.Categoria.values:
        destino.opciones[categoria] = [
            OpcionHuerto.objects.create(
                codigo=f"{categoria}_prueba_{numero}", categoria=categoria,
                nombre=f"{categoria} de prueba {numero}",
            ) for numero in (1, 2)
        ]
    destino.planta = Planta.objects.create(codigo="especie_prueba_1", nombre_comun="Especie uno")
    destino.otra_planta = Planta.objects.create(codigo="especie_prueba_2", nombre_comun="Especie dos")


def datos_configuracion(opciones, **cambios):
    datos = {
        "provincia": "Provincia de prueba", "parroquia": "Parroquia de prueba",
        "direccion": "Dirección ficticia", "area_m2": Decimal("12.50"),
        "disenos": opciones["diseno"], "abonos": opciones["abono"],
        "cerca": opciones["cerca"][0], "suelo": opciones["suelo"][0],
        "fuente_agua": opciones["agua"][0],
    }
    datos.update(cambios)
    return datos


class ConfiguracionSeleccionServiciosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        preparar_datos_configurador(cls)

    def configurar(self, **cambios):
        return configurar_huerto(actor=self.responsable, **datos_configuracion(self.opciones, **cambios))

    def test_configuracion_persiste_y_reenvio_actualiza_el_mismo_huerto(self):
        huerto = self.configurar()
        consultado = obtener_huerto(actor=self.participante)
        self.assertEqual(consultado.pk, huerto.pk)
        self.assertEqual(consultado.area_m2, Decimal("12.50"))
        self.assertEqual(set(consultado.disenos.all()), set(self.opciones["diseno"]))
        self.assertEqual(set(consultado.abonos.all()), set(self.opciones["abono"]))
        actualizado = self.configurar(
            direccion="Otra dirección ficticia", disenos=self.opciones["diseno"][:1],
        )
        self.assertEqual(actualizado.pk, huerto.pk)
        self.assertEqual(Huerto.objects.filter(comunidad=self.comunidad).count(), 1)
        self.assertEqual(actualizado.disenos.count(), 1)

    def test_area_y_ubicacion_invalidas_no_crean_un_huerto(self):
        for cambios in (
            {"area_m2": Decimal("0")}, {"area_m2": Decimal("-2")},
            {"provincia": "  "}, {"parroquia": ""}, {"direccion": "  "},
        ):
            with self.subTest(cambios=cambios), self.assertRaises(ValidationError):
                self.configurar(**cambios)
        self.assertFalse(Huerto.objects.exists())

    def test_categorias_y_listas_vacias_se_rechazan_tambien_sin_formulario(self):
        for campo, opcion in (
            ("cerca", self.opciones["suelo"][0]),
            ("suelo", self.opciones["agua"][0]),
            ("fuente_agua", self.opciones["cerca"][0]),
            ("disenos", self.opciones["abono"]),
            ("abonos", self.opciones["diseno"]),
            ("disenos", []), ("abonos", []),
        ):
            with self.subTest(campo=campo), self.assertRaises(ValidationError) as error:
                self.configurar(**{campo: opcion})
            self.assertIn(campo, error.exception.message_dict)
        self.assertFalse(Huerto.objects.exists())

    def test_actualizacion_invalida_conserva_configuracion_y_relaciones(self):
        huerto = self.configurar()
        with self.assertRaises(ValidationError):
            self.configurar(direccion="Cambio que no debe persistir", abonos=[])
        huerto.refresh_from_db()
        self.assertEqual(huerto.direccion, "Dirección ficticia")
        self.assertEqual(set(huerto.abonos.all()), set(self.opciones["abono"]))

    def test_actualizar_configuracion_no_borra_selecciones_ni_nombramiento(self):
        huerto = self.configurar()
        seleccion = elegir_planta(
            actor=self.responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        # La constancia es un dato de modelo; el nombramiento por puntos es de actividades.
        huerto.maestro = self.participante.miembro
        huerto.maestro_motivo = "Constancia ficticia para probar su conservación."
        huerto.maestro_nombrado_por = self.responsable
        huerto.maestro_fecha = timezone.now()
        huerto.save()
        self.configurar(area_m2=Decimal("20.00"))
        huerto.refresh_from_db()
        self.assertEqual(huerto.maestro_id, self.participante.miembro.pk)
        self.assertTrue(huerto.maestro_motivo)
        self.assertTrue(PlantaHuerto.objects.filter(pk=seleccion.pk).exists())

    def test_participante_y_persona_sin_comunidad_no_pueden_configurar(self):
        for actor in (self.participante, self.sin_comunidad, AnonymousUser()):
            with self.subTest(actor=actor), self.assertRaises(PermissionDenied):
                configurar_huerto(actor=actor, **datos_configuracion(self.opciones))
        self.assertFalse(Huerto.objects.exists())

    def test_no_se_elige_una_planta_antes_de_configurar(self):
        with self.assertRaises(ValidationError):
            elegir_planta(actor=self.responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS)
        self.assertFalse(PlantaHuerto.objects.exists())

    def test_especie_unica_por_huerto_y_metodo_valido(self):
        self.configurar()
        elegir_planta(actor=self.responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS)
        for planta, metodo in (
            (self.planta, MetodoSiembra.ESQUEJES), (self.otra_planta, "inventado"),
        ):
            with self.subTest(metodo=metodo), self.assertRaises(ValidationError):
                elegir_planta(actor=self.responsable, planta=planta, metodo_siembra=metodo)
        configurar_huerto(actor=self.otro_responsable, **datos_configuracion(self.opciones))
        elegir_planta(actor=self.otro_responsable, planta=self.planta, metodo_siembra=MetodoSiembra.ESTACAS)
        self.assertEqual(PlantaHuerto.objects.filter(planta=self.planta).count(), 2)

    def test_cambio_y_retiro_sin_historial_conservan_la_ficha_del_catalogo(self):
        self.configurar()
        seleccion = elegir_planta(
            actor=self.responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        cambiar_metodo_siembra(
            actor=self.responsable, seleccion_id=seleccion.pk, metodo_siembra=MetodoSiembra.ESQUEJES,
        )
        seleccion.refresh_from_db()
        self.assertEqual(seleccion.metodo_siembra, MetodoSiembra.ESQUEJES)
        retirar_planta(actor=self.responsable, seleccion_id=seleccion.pk)
        self.assertFalse(PlantaHuerto.objects.filter(pk=seleccion.pk).exists())
        self.assertTrue(Planta.objects.filter(pk=self.planta.pk).exists())

    def test_seleccion_ajena_no_se_consulta_modifica_ni_retira(self):
        self.configurar()
        configurar_huerto(actor=self.otro_responsable, **datos_configuracion(self.opciones))
        seleccion = elegir_planta(
            actor=self.otro_responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        with self.assertRaises(PlantaHuerto.DoesNotExist):
            cambiar_metodo_siembra(
                actor=self.responsable, seleccion_id=seleccion.pk, metodo_siembra=MetodoSiembra.ESTACAS,
            )
        with self.assertRaises(PlantaHuerto.DoesNotExist):
            retirar_planta(actor=self.responsable, seleccion_id=seleccion.pk)
        self.assertIsNone(obtener_huerto(actor=self.sin_comunidad))
        seleccion.refresh_from_db()
        self.assertEqual(seleccion.metodo_siembra, MetodoSiembra.SEMILLAS)


class ConfiguracionSeleccionPantallasTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        preparar_datos_configurador(cls)

    def datos_post(self):
        datos = datos_configuracion(self.opciones)
        for campo in ("cerca", "suelo", "fuente_agua"):
            datos[campo] = datos[campo].pk
        for campo in ("disenos", "abonos"):
            datos[campo] = [opcion.pk for opcion in datos[campo]]
        return datos

    def preparar_seleccion(self, actor=None):
        actor = actor or self.responsable
        configurar_huerto(actor=actor, **datos_configuracion(self.opciones))
        return elegir_planta(actor=actor, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS)

    def test_rutas_de_huerto_exigen_sesion(self):
        for nombre, kwargs in (
            ("mi_huerto", {}), ("configurar_huerto", {}), ("elegir_planta", {}),
            ("cambiar_metodo", {"seleccion_id": 1}), ("retirar_planta", {"seleccion_id": 1}),
        ):
            with self.subTest(pantalla=nombre):
                url = reverse("comunidades:" + nombre, kwargs=kwargs)
                self.assertRedirects(self.client.get(url), reverse("cuentas:login") + "?next=" + url)

    def test_configurar_por_post_y_reabrir_conserva_todos_los_valores(self):
        self.client.force_login(self.responsable)
        url = reverse("comunidades:configurar_huerto")
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertFalse(Huerto.objects.exists())
        response = self.client.post(url, {
            **self.datos_post(), "comunidad": self.otra_comunidad.pk,
            "maestro": self.participante.miembro.pk, "maestro_motivo": "No aceptado",
        })
        self.assertRedirects(response, reverse("comunidades:mi_huerto"))
        huerto = Huerto.objects.get(comunidad=self.comunidad)
        self.assertIsNone(huerto.maestro)
        form = self.client.get(url).context["form"]
        self.assertEqual(form["provincia"].value(), "Provincia de prueba")
        self.assertEqual(Decimal(form["area_m2"].value()), Decimal("12.50"))
        for campo in ("disenos", "abonos"):
            self.assertEqual(set(form[campo].value()), set(self.datos_post()[campo]))
        self.assertFalse(Huerto.objects.filter(comunidad=self.otra_comunidad).exists())

    def test_opcion_de_categoria_incorrecta_no_pasa_el_formulario(self):
        self.client.force_login(self.responsable)
        datos = {**self.datos_post(), "disenos": [self.opciones["abono"][0].pk]}
        response = self.client.post(reverse("comunidades:configurar_huerto"), datos)
        self.assertEqual(response.status_code, 200)
        self.assertIn("disenos", response.context["form"].errors)
        self.assertFalse(Huerto.objects.exists())

    def test_catalogo_vacio_muestra_ausencia_sin_inventar_opciones(self):
        OpcionHuerto.objects.all().delete()
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comunidades:configurar_huerto"))
        self.assertContains(response, "Aún faltan opciones disponibles")
        self.assertContains(response, 'disabled')
        self.assertEqual(len(response.context["form"].categorias_pendientes), 5)

    def test_elegir_antes_de_configurar_lleva_al_configurador(self):
        self.client.force_login(self.responsable)
        self.assertRedirects(
            self.client.get(reverse("comunidades:elegir_planta")),
            reverse("comunidades:configurar_huerto"),
        )

    def test_catalogo_de_plantas_vacio_informa_y_no_crea_selecciones(self):
        configurar_huerto(actor=self.responsable, **datos_configuracion(self.opciones))
        Planta.objects.all().delete()
        self.client.force_login(self.responsable)
        response = self.client.get(reverse("comunidades:elegir_planta"))
        self.assertContains(response, "Aún no hay especies disponibles en el catálogo.")
        self.assertFalse(response.context["hay_disponibles"])
        self.assertFalse(PlantaHuerto.objects.exists())

    def test_elegir_no_duplica_y_no_acepta_huerto_inyectado(self):
        configurar_huerto(actor=self.responsable, **datos_configuracion(self.opciones))
        otro = configurar_huerto(actor=self.otro_responsable, **datos_configuracion(self.opciones))
        self.client.force_login(self.responsable)
        url = reverse("comunidades:elegir_planta")
        datos = {"planta": self.planta.pk, "metodo_siembra": MetodoSiembra.ESQUEJES, "huerto": otro.pk}
        self.assertRedirects(self.client.post(url, datos), reverse("comunidades:mi_huerto"))
        response = self.client.post(url, datos)
        self.assertEqual(response.status_code, 200)
        seleccion = PlantaHuerto.objects.get(planta=self.planta)
        self.assertEqual(seleccion.huerto.comunidad, self.comunidad)
        self.assertNotIn(self.planta, response.context["form"].fields["planta"].queryset)

    def test_cambiar_y_retirar_requieren_post_y_conservan_identidad(self):
        seleccion = self.preparar_seleccion()
        self.client.force_login(self.responsable)
        url = reverse("comunidades:cambiar_metodo", args=[seleccion.pk])
        response = self.client.post(url, {
            "metodo_siembra": MetodoSiembra.PLANTULAS, "planta": self.otra_planta.pk,
        })
        self.assertRedirects(response, reverse("comunidades:mi_huerto"))
        seleccion.refresh_from_db()
        self.assertEqual(seleccion.planta, self.planta)
        self.assertEqual(seleccion.metodo_siembra, MetodoSiembra.PLANTULAS)
        url = reverse("comunidades:retirar_planta", args=[seleccion.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(PlantaHuerto.objects.filter(pk=seleccion.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("comunidades:mi_huerto"))
        self.assertTrue(Planta.objects.filter(pk=self.planta.pk).exists())

    def test_participante_solo_consulta_y_post_directo_no_cambia_el_huerto(self):
        seleccion = self.preparar_seleccion()
        self.client.force_login(self.participante)
        response = self.client.get(reverse("comunidades:mi_huerto"))
        self.assertContains(response, self.planta.nombre_comun)
        self.assertNotContains(response, reverse("comunidades:configurar_huerto"))
        for nombre, kwargs in (
            ("configurar_huerto", {}), ("elegir_planta", {}),
            ("cambiar_metodo", {"seleccion_id": seleccion.pk}),
            ("retirar_planta", {"seleccion_id": seleccion.pk}),
        ):
            for metodo in (self.client.get, self.client.post):
                with self.subTest(ruta=nombre, metodo=metodo.__name__):
                    self.assertEqual(metodo(reverse("comunidades:" + nombre, kwargs=kwargs)).status_code, 403)

    def test_otro_responsable_no_accede_a_una_seleccion_ajena_por_id(self):
        self.preparar_seleccion()
        ajena = self.preparar_seleccion(actor=self.otro_responsable)
        self.client.force_login(self.responsable)
        for nombre in ("cambiar_metodo", "retirar_planta"):
            url = reverse("comunidades:" + nombre, args=[ajena.pk])
            self.assertEqual(self.client.get(url).status_code, 404)
            self.assertEqual(self.client.post(url, {"metodo_siembra": "semillas"}).status_code, 404)

    def test_escrituras_sin_csrf_y_metodos_no_permitidos_se_rechazan(self):
        seleccion = self.preparar_seleccion()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.responsable)
        for nombre, kwargs in (
            ("configurar_huerto", {}), ("elegir_planta", {}),
            ("cambiar_metodo", {"seleccion_id": seleccion.pk}),
            ("retirar_planta", {"seleccion_id": seleccion.pk}),
        ):
            url = reverse("comunidades:" + nombre, kwargs=kwargs)
            self.assertEqual(client.post(url).status_code, 403)
            self.client.force_login(self.responsable)
            self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertTrue(PlantaHuerto.objects.filter(pk=seleccion.pk).exists())


class ContratoHistorialSeleccionTests(TransactionTestCase):
    @isolate_apps("comunidades")
    def test_registros_reales_incluidos_anulados_bloquean_cambio_y_retiro(self):
        """Una tabla temporal prueba el contrato sin crear el modelo de Fernando."""
        from django.db.models.options import Options
        from .checks import comprobar_contrato_actividades

        preparar_datos_configurador(self)
        configurar_huerto(actor=self.responsable, **datos_configuracion(self.opciones))
        seleccion = elegir_planta(
            actor=self.responsable, planta=self.planta, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        anterior = getattr(PlantaHuerto, "actividades", None)
        Options.default_apps.register_model("comunidades", PlantaHuerto)

        class SoloActivos(models.Manager):
            def get_queryset(self):
                return super().get_queryset().filter(anulado=False)

        class RegistroContrato(models.Model):
            planta = models.ForeignKey(
                PlantaHuerto, on_delete=models.PROTECT, related_name="actividades",
                null=True, blank=True,
            )
            anulado = models.BooleanField(default=False)
            objects = SoloActivos()

            class Meta:
                app_label = "comunidades"
                db_table = "prueba_temporal_historial_b2"

        try:
            with connection.schema_editor() as editor:
                editor.create_model(RegistroContrato)
            registro = RegistroContrato.objects.create(planta=seleccion)
            self.client.force_login(self.responsable)
            for anulado in (False, True):
                registro.anulado = anulado
                registro.save(update_fields=["anulado"])
                with self.subTest(anulado=anulado):
                    self.assertTrue(seleccion.tiene_historial)
                    if anulado:
                        self.assertFalse(seleccion.actividades.exists())
                    with self.assertRaises(ValidationError):
                        cambiar_metodo_siembra(
                            actor=self.responsable, seleccion_id=seleccion.pk,
                            metodo_siembra=MetodoSiembra.ESQUEJES,
                        )
                    with self.assertRaises(ValidationError):
                        retirar_planta(actor=self.responsable, seleccion_id=seleccion.pk)
                    for nombre in ("cambiar_metodo", "retirar_planta"):
                        response = self.client.post(
                            reverse("comunidades:" + nombre, args=[seleccion.pk]),
                            {"metodo_siembra": MetodoSiembra.ESQUEJES},
                        )
                        self.assertContains(response, "con historial")
                    seleccion.refresh_from_db()
                    self.assertEqual(seleccion.metodo_siembra, MetodoSiembra.SEMILLAS)

            with patch("comunidades.checks.apps.get_model", return_value=RegistroContrato):
                self.assertEqual(comprobar_contrato_actividades(None), [])
                campo = RegistroContrato._meta.get_field("planta")
                campo.remote_field.on_delete = models.CASCADE
                self.assertEqual(comprobar_contrato_actividades(None)[0].id, "comunidades.E001")
                campo.remote_field.on_delete = models.PROTECT
        finally:
            with connection.schema_editor() as editor:
                editor.delete_model(RegistroContrato)
            if anterior is None:
                delattr(PlantaHuerto, "actividades")
            else:
                PlantaHuerto.actividades = anterior


class RecorridoInicialIntegradoTests(TestCase):
    """Comprobación de desarrollo: formularios reales y una misma base temporal."""

    @classmethod
    def setUpTestData(cls):
        cls.opciones = {
            categoria: OpcionHuerto.objects.create(
                codigo=f"{categoria}_recorrido", categoria=categoria,
                nombre=f"{categoria} de prueba",
            ) for categoria in OpcionHuerto.Categoria.values
        }
        cls.planta = Planta.objects.create(
            codigo="especie_recorrido", nombre_comun="Especie de prueba del recorrido",
        )
        cls.material = Material.objects.create(
            codigo="material_recorrido", nombre="Material común de prueba",
            grupo=Material.Grupo.HERRAMIENTAS,
        )

    def enviar(self, cliente, ruta, datos, *, destino=None):
        pagina = cliente.get(ruta)
        self.assertEqual(pagina.status_code, 200)
        return cliente.post(destino or ruta, {
            **datos, "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
        })

    def registrar_y_entrar(self, cliente, username):
        clave_prueba = "Recorrido!Semilla82Valida"
        response = self.enviar(cliente, reverse("cuentas:registro"), {
            "username": username, "nombre_completo": username,
            "fecha_nacimiento": "2000-01-02", "genero": "",
            "talentos_ancestrales": "", "password1": clave_prueba,
            "password2": clave_prueba, "acepta_aviso": "on",
            "aviso_version": AVISO_DATOS_VERSION,
        })
        self.assertRedirects(response, reverse("cuentas:login"))
        response = self.enviar(cliente, reverse("cuentas:login"), {
            "username": username, "password": clave_prueba,
        })
        self.assertRedirects(response, reverse("cuentas:perfil"))
        return Usuario.objects.get(username=username)

    def test_recorrido_completo_registro_sesion_comunidad_huerto_y_seleccion(self):
        responsable = Client(enforce_csrf_checks=True)
        participante = Client(enforce_csrf_checks=True)
        ana = self.registrar_y_entrar(responsable, "ana_recorrido")
        perfil = responsable.get(reverse("cuentas:perfil"))
        self.assertContains(perfil, "Continuar a mi comunidad")
        self.assertRedirects(responsable.get(reverse("inicio")), reverse("comunidades:mi_comunidad"))
        response = self.enviar(responsable, reverse("comunidades:crear"), {
            "nombre": "Comunidad del recorrido", "tipo": Comunidad.Tipo.FAMILIA,
            "contacto_nombre": "Ana de prueba", "contacto_telefono": "0991234567",
            "contacto_correo": "ana@example.com",
        })
        self.assertRedirects(response, reverse("comunidades:mi_comunidad"))
        comunidad = Comunidad.objects.get(responsable=ana)
        response = self.enviar(responsable, reverse("comunidades:configurar_huerto"), {
            "provincia": "Provincia de prueba", "parroquia": "Parroquia de prueba",
            "direccion": "Dirección ficticia", "area_m2": "12.50",
            "disenos": [self.opciones["diseno"].pk], "abonos": [self.opciones["abono"].pk],
            "cerca": self.opciones["cerca"].pk, "suelo": self.opciones["suelo"].pk,
            "fuente_agua": self.opciones["agua"].pk,
        })
        self.assertRedirects(response, reverse("comunidades:mi_huerto"))
        response = self.enviar(responsable, reverse("comunidades:elegir_planta"), {
            "planta": self.planta.pk, "metodo_siembra": MetodoSiembra.SEMILLAS,
        })
        self.assertRedirects(response, reverse("comunidades:mi_huerto"))
        huerto = Huerto.objects.get(comunidad=comunidad)
        self.assertTrue(PlantaHuerto.objects.filter(huerto=huerto, planta=self.planta).exists())
        luis = self.registrar_y_entrar(participante, "luis_recorrido")
        response = self.enviar(participante, reverse("comunidades:unirse"), {
            "codigo_invitacion": comunidad.codigo_invitacion,
        })
        self.assertRedirects(response, reverse("comunidades:mi_comunidad"))
        self.assertEqual(luis.miembro.comunidad, comunidad)
        self.assertContains(participante.get(reverse("comunidades:mi_huerto")), self.planta.nombre_comun)
        self.assertEqual(Comunidad.objects.count(), 1)
        self.assertEqual(Huerto.objects.count(), 1)
        self.assertEqual(Miembro.objects.filter(comunidad=comunidad).count(), 2)
        self.assertEqual(participante.post(reverse("comunidades:configurar_huerto"), {
            "csrfmiddlewaretoken": participante.cookies["csrftoken"].value,
        }).status_code, 403)
        response = self.enviar(participante, reverse("comunidades:materiales"), {
            f"material-{self.material.pk}-disponible": "on",
        }, destino=reverse("comunidades:marcar_material", args=[self.material.pk]))
        self.assertRedirects(response, reverse("comunidades:materiales"))
        self.assertTrue(MarcaMaterial.objects.get(huerto=huerto, material=self.material).disponible)
        response = participante.post(reverse("cuentas:logout"), {
            "csrfmiddlewaretoken": participante.cookies["csrftoken"].value,
        })
        self.assertRedirects(response, reverse("cuentas:login"))
        destino = reverse("comunidades:mi_huerto")
        self.assertRedirects(participante.get(destino), reverse("cuentas:login") + "?next=" + destino)

    def test_inicio_exige_sesion_y_no_acepta_escrituras(self):
        self.assertRedirects(self.client.get(reverse("inicio")), reverse("cuentas:login") + "?next=/")
        usuario = crear_usuario("inicio_recorrido")
        self.client.force_login(usuario)
        self.assertEqual(self.client.post(reverse("inicio")).status_code, 405)


class MaterialesCompartidosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        preparar_datos_configurador(cls)
        cls.huerto = configurar_huerto(actor=cls.responsable, **datos_configuracion(cls.opciones))
        cls.otro_huerto = configurar_huerto(
            actor=cls.otro_responsable, **datos_configuracion(cls.opciones),
        )
        cls.seleccion = elegir_planta(
            actor=cls.responsable, planta=cls.planta, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        cls.comun = Material.objects.create(
            codigo="pala_compartida", nombre="Pala de prueba", grupo=Material.Grupo.HERRAMIENTAS,
        )
        cls.abono = Material.objects.create(
            codigo="abono_compartido", nombre="Abono de prueba", grupo=Material.Grupo.ABONOS,
        )
        cls.semillas = Material.objects.create(
            codigo="material_semillas", nombre="Material para semillas", grupo=Material.Grupo.SIEMBRA,
            metodos_siembra=[MetodoSiembra.SEMILLAS],
        )
        cls.esquejes = Material.objects.create(
            codigo="material_esquejes", nombre="Material para esquejes", grupo=Material.Grupo.SIEMBRA,
            metodos_siembra=[MetodoSiembra.ESQUEJES],
        )

    def test_lectura_recomienda_por_metodos_y_no_crea_marcas(self):
        filas = listar_materiales(actor=self.participante)
        self.assertEqual({fila["material"] for fila in filas}, {self.comun, self.abono, self.semillas})
        self.assertTrue(all(fila["disponible"] is False for fila in filas))
        self.assertFalse(MarcaMaterial.objects.exists())
        otras = listar_materiales(actor=self.otro_responsable)
        self.assertEqual({fila["material"] for fila in otras}, {self.comun, self.abono})

    def test_participante_y_responsable_comparten_marca_y_reenvio_no_duplica(self):
        marca = marcar_material(actor=self.participante, material_id=self.comun.pk, disponible=True)
        reenvio = marcar_material(actor=self.participante, material_id=self.comun.pk, disponible=True)
        self.assertEqual(marca.pk, reenvio.pk)
        self.assertEqual(MarcaMaterial.objects.filter(huerto=self.huerto, material=self.comun).count(), 1)
        filas = listar_materiales(actor=self.responsable)
        self.assertTrue(next(fila for fila in filas if fila["material"] == self.comun)["disponible"])
        marcar_material(actor=self.responsable, material_id=self.comun.pk, disponible=False)
        marca.refresh_from_db()
        self.assertFalse(marca.disponible)

    def test_disponibilidad_de_otra_comunidad_no_se_lee_ni_sobrescribe(self):
        ajena = marcar_material(actor=self.otro_responsable, material_id=self.comun.pk, disponible=True)
        propia = next(fila for fila in listar_materiales(actor=self.participante) if fila["material"] == self.comun)
        self.assertFalse(propia["disponible"])
        marcar_material(actor=self.participante, material_id=self.comun.pk, disponible=False)
        ajena.refresh_from_db()
        self.assertTrue(ajena.disponible)

    def test_material_ajeno_al_metodo_o_inexistente_no_se_guarda(self):
        for identificador in (self.esquejes.pk, 999999):
            with self.subTest(material=identificador), self.assertRaises(Material.DoesNotExist):
                marcar_material(actor=self.participante, material_id=identificador, disponible=True)
        self.assertFalse(MarcaMaterial.objects.exists())

    def test_el_servicio_exige_un_booleano_real(self):
        for valor in ("false", "on", 0, 1, None):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                marcar_material(actor=self.participante, material_id=self.comun.pk, disponible=valor)
        self.assertFalse(MarcaMaterial.objects.exists())

    def test_cambio_de_metodo_no_borra_marcas_que_pueden_volver_a_ser_relevantes(self):
        marca = marcar_material(actor=self.responsable, material_id=self.semillas.pk, disponible=True)
        cambiar_metodo_siembra(
            actor=self.responsable, seleccion_id=self.seleccion.pk, metodo_siembra=MetodoSiembra.ESQUEJES,
        )
        filas = listar_materiales(actor=self.participante)
        self.assertNotIn(self.semillas, {fila["material"] for fila in filas})
        self.assertIn(self.esquejes, {fila["material"] for fila in filas})
        self.assertTrue(MarcaMaterial.objects.filter(pk=marca.pk).exists())
        cambiar_metodo_siembra(
            actor=self.responsable, seleccion_id=self.seleccion.pk, metodo_siembra=MetodoSiembra.SEMILLAS,
        )
        fila = next(f for f in listar_materiales(actor=self.participante) if f["material"] == self.semillas)
        self.assertTrue(fila["disponible"])

    def test_anonimo_cuenta_inactiva_o_sin_comunidad_no_acceden(self):
        Usuario.objects.filter(pk=self.participante.pk).update(is_active=False)
        for actor in (AnonymousUser(), self.participante, self.sin_comunidad):
            with self.subTest(actor=actor):
                with self.assertRaises(PermissionDenied):
                    listar_materiales(actor=actor)
                with self.assertRaises(PermissionDenied):
                    marcar_material(actor=actor, material_id=self.comun.pk, disponible=True)

    def test_post_ignora_ids_de_huerto_comunidad_o_marca_ajena(self):
        ajena = marcar_material(actor=self.otro_responsable, material_id=self.comun.pk, disponible=False)
        self.client.force_login(self.participante)
        url = reverse("comunidades:marcar_material", args=[self.comun.pk])
        datos = {
            f"material-{self.comun.pk}-disponible": "on", "huerto": self.otro_huerto.pk,
            "comunidad": self.otra_comunidad.pk, "marca": ajena.pk,
        }
        self.assertRedirects(self.client.post(url, datos), reverse("comunidades:materiales"))
        ajena.refresh_from_db()
        self.assertFalse(ajena.disponible)
        self.assertTrue(MarcaMaterial.objects.get(huerto=self.huerto, material=self.comun).disponible)

    def test_pagina_de_materiales_usa_formularios_reales_y_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.participante)
        pagina_url = reverse("comunidades:materiales")
        url = reverse("comunidades:marcar_material", args=[self.comun.pk])
        self.assertEqual(cliente.post(url).status_code, 403)
        pagina = cliente.get(pagina_url)
        self.assertContains(pagina, self.comun.nombre)
        self.assertNotContains(pagina, self.esquejes.nombre)
        datos = {
            f"material-{self.comun.pk}-disponible": "on",
            "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
        }
        self.assertRedirects(cliente.post(url, datos), pagina_url)
        pagina = cliente.get(pagina_url)
        fila = next(f for f in pagina.context["materiales"] if f["material"] == self.comun)
        self.assertTrue(fila["form"]["disponible"].value())
        self.assertRedirects(cliente.post(url, {
            "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
        }), pagina_url)
        self.assertFalse(MarcaMaterial.objects.get(huerto=self.huerto, material=self.comun).disponible)

    def test_post_de_material_no_recomendado_o_inexistente_responde_404(self):
        self.client.force_login(self.participante)
        for identificador in (self.esquejes.pk, 999999):
            response = self.client.post(reverse("comunidades:marcar_material", args=[identificador]))
            self.assertEqual(response.status_code, 404)

    def test_catalogo_de_materiales_vacio_se_muestra_sin_crear_datos(self):
        Material.objects.all().delete()
        self.client.force_login(self.participante)
        response = self.client.get(reverse("comunidades:materiales"))
        self.assertContains(response, "Aún no hay materiales recomendados disponibles para este huerto.")
        self.assertFalse(MarcaMaterial.objects.exists())

    def test_comunidad_sin_huerto_no_crea_marcas_y_vuelve_al_huerto(self):
        self.otro_huerto.delete()
        self.client.force_login(self.otro_responsable)
        self.assertRedirects(
            self.client.get(reverse("comunidades:materiales")),
            reverse("comunidades:mi_huerto"),
        )
        self.assertRedirects(
            self.client.post(reverse("comunidades:marcar_material", args=[self.comun.pk])),
            reverse("comunidades:mi_huerto"),
        )
        self.assertFalse(MarcaMaterial.objects.exists())

    def test_materiales_no_se_modifican_con_get_y_las_rutas_exigen_sesion(self):
        listado = reverse("comunidades:materiales")
        guardado = reverse("comunidades:marcar_material", args=[self.comun.pk])
        for ruta in (listado, guardado):
            self.assertRedirects(self.client.get(ruta), reverse("cuentas:login") + "?next=" + ruta)
        self.client.force_login(self.participante)
        self.assertEqual(self.client.get(guardado).status_code, 405)
        self.assertEqual(self.client.post(listado).status_code, 405)
        self.assertFalse(MarcaMaterial.objects.exists())
