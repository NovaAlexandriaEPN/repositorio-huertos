from datetime import date
from decimal import Decimal
from unittest.mock import PropertyMock, patch

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from catalogo.models import Material, MetodoSiembra, OpcionHuerto, Planta
from cuentas.models import Usuario

from .models import Comunidad, Huerto, MarcaMaterial, Miembro, PlantaHuerto
from .servicios import (
    crear_comunidad,
    editar_comunidad,
    listar_miembros,
    obtener_comunidad,
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
