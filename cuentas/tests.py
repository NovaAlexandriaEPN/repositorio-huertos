from datetime import timedelta

from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .aviso import AVISO_DATOS_VERSION
from .models import Usuario
from .servicios import actualizar_perfil, registrar_usuario


class UsuarioTests(TestCase):
    def datos_usuario(self, **cambios):
        datos = {
            "username": "bryan_prueba",
            "nombre_completo": "Bryan Ayala",
            "fecha_nacimiento": timezone.localdate() - timedelta(days=365 * 20),
        }
        datos.update(cambios)
        return datos

    def test_rechaza_fecha_de_nacimiento_futura(self):
        usuario = Usuario(
            **self.datos_usuario(
                fecha_nacimiento=timezone.localdate() + timedelta(days=1)
            )
        )

        with self.assertRaises(ValidationError) as error:
            usuario.full_clean(exclude=["password"])

        self.assertIn("fecha_nacimiento", error.exception.message_dict)

    def test_permite_fecha_de_nacimiento_de_menor_de_catorce(self):
        usuario = Usuario(
            **self.datos_usuario(
                fecha_nacimiento=timezone.localdate() - timedelta(days=365 * 12)
            )
        )

        usuario.full_clean(exclude=["password"])

    def test_permite_no_indicar_genero_sin_inventar_consentimiento(self):
        usuario = Usuario(**self.datos_usuario(genero=""))

        usuario.full_clean(exclude=["password"])

        self.assertIsNone(usuario.consentimiento_fecha)
        self.assertEqual(usuario.consentimiento_version, "")

    def test_guarda_perfil_y_constancia_del_consentimiento(self):
        fecha_aceptacion = timezone.now()
        usuario = Usuario.objects.create_user(
            **self.datos_usuario(),
            password="ClaveFicticiaSoloParaPruebas!",
            consentimiento_fecha=fecha_aceptacion,
            consentimiento_version="aviso-prueba-1",
        )

        usuario.refresh_from_db()

        self.assertEqual(usuario.get_full_name(), "Bryan Ayala")
        self.assertEqual(usuario.consentimiento_fecha, fecha_aceptacion)
        self.assertEqual(usuario.consentimiento_version, "aviso-prueba-1")

    def test_validacion_rechaza_constancia_incompleta(self):
        constancias_incompletas = [
            {"consentimiento_fecha": timezone.now()},
            {"consentimiento_version": "aviso-prueba-1"},
        ]

        for constancia in constancias_incompletas:
            with self.subTest(constancia=constancia):
                usuario = Usuario(**self.datos_usuario(**constancia))

                with self.assertRaises(ValidationError):
                    usuario.full_clean(exclude=["password"])

    def test_base_de_datos_rechaza_constancia_incompleta(self):
        constancias_incompletas = [
            {"consentimiento_fecha": timezone.now()},
            {"consentimiento_version": "aviso-prueba-1"},
        ]

        for constancia in constancias_incompletas:
            with self.subTest(constancia=constancia):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Usuario.objects.create(**self.datos_usuario(**constancia))


class RegistroTests(TestCase):
    def setUp(self):
        self.url = reverse("cuentas:registro")
        self.url_login = reverse("cuentas:login")

    def datos_registro(self, **cambios):
        datos = {
            "username": "bryan_prueba",
            "nombre_completo": "Bryan Ayala",
            "fecha_nacimiento": (
                timezone.localdate() - timedelta(days=365 * 20)
            ).isoformat(),
            "genero": "",
            "talentos_ancestrales": "Cuidado de plantas",
            "password1": "Rama!Rio42Cobre",
            "password2": "Rama!Rio42Cobre",
            "acepta_aviso": "on",
            "aviso_version": AVISO_DATOS_VERSION,
        }
        datos.update(cambios)
        return datos

    def test_muestra_formulario_y_aviso_sin_aceptacion_previa(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "cuentas/registro.html")
        self.assertContains(respuesta, "Aviso sobre el uso de tus datos")
        self.assertContains(respuesta, "14 años")
        self.assertEqual(respuesta.context["aviso_version"], AVISO_DATOS_VERSION)
        self.assertFalse(respuesta.context["form"].is_bound)
        self.assertFalse(respuesta.context["form"]["acepta_aviso"].value())
        self.assertEqual(Usuario.objects.count(), 0)

    def test_registro_guarda_hash_y_consentimiento_del_servidor(self):
        antes = timezone.now()
        datos = self.datos_registro()

        respuesta = self.client.post(self.url, datos)

        self.assertRedirects(respuesta, self.url_login, fetch_redirect_response=False)
        usuario = Usuario.objects.get()
        self.assertTrue(usuario.check_password(datos["password1"]))
        self.assertNotEqual(usuario.password, datos["password1"])
        self.assertEqual(usuario.nombre_completo, datos["nombre_completo"])
        self.assertEqual(usuario.genero, "")
        self.assertEqual(usuario.consentimiento_version, AVISO_DATOS_VERSION)
        self.assertGreaterEqual(usuario.consentimiento_fecha, antes)
        self.assertLessEqual(usuario.consentimiento_fecha, timezone.now())

        # Actualizar la página final no vuelve a enviar el formulario.
        final = self.client.get(self.url_login)
        self.assertContains(final, "Tu cuenta se ha creado.")
        self.client.get(self.url)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_rechaza_registro_sin_consentimiento(self):
        datos = self.datos_registro()
        del datos["acepta_aviso"]

        respuesta = self.client.post(self.url, datos)

        self.assertFormError(
            respuesta.context["form"],
            "acepta_aviso",
            "Para crear tu cuenta debes aceptar el aviso de datos.",
        )
        self.assertEqual(Usuario.objects.count(), 0)

    def test_datos_invalidos_no_crean_cuenta(self):
        casos = [
            ({"password2": "Otra!Clave24Distinta"}, "password2"),
            ({"password1": "123", "password2": "123"}, "password1"),
            (
                {"password1": "Bryan Ayala", "password2": "Bryan Ayala"},
                "password1",
            ),
            (
                {
                    "fecha_nacimiento": (
                        timezone.localdate() + timedelta(days=1)
                    ).isoformat()
                },
                "fecha_nacimiento",
            ),
            ({"fecha_nacimiento": "2026-02-30"}, "fecha_nacimiento"),
            ({"username": "usuario con espacios"}, "username"),
            ({"nombre_completo": "   "}, "nombre_completo"),
            ({"genero": "valor_inexistente"}, "genero"),
        ]

        for cambios, campo in casos:
            with self.subTest(cambios=cambios):
                respuesta = self.client.post(self.url, self.datos_registro(**cambios))

                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(campo, respuesta.context["form"].errors)
                self.assertEqual(Usuario.objects.count(), 0)

    def test_rechaza_usuario_duplicado_sin_modificar_cuenta_existente(self):
        self.client.post(self.url, self.datos_registro())

        respuesta = self.client.post(
            self.url, self.datos_registro(nombre_completo="Otra persona")
        )

        self.assertIn("username", respuesta.context["form"].errors)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Usuario.objects.get().nombre_completo, "Bryan Ayala")

    def test_edad_menor_de_catorce_no_bloquea_el_registro(self):
        respuesta = self.client.post(
            self.url,
            self.datos_registro(
                fecha_nacimiento=(
                    timezone.localdate() - timedelta(days=365 * 12)
                ).isoformat()
            ),
        )

        self.assertRedirects(respuesta, self.url_login)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_campos_extra_no_dan_privilegios_ni_falsifican_consentimiento(self):
        respuesta = self.client.post(
            self.url,
            self.datos_registro(
                is_staff="on",
                is_superuser="on",
                consentimiento_fecha="2000-01-01T00:00:00Z",
                consentimiento_version="version-inventada",
            ),
        )

        self.assertRedirects(respuesta, self.url_login)
        usuario = Usuario.objects.get()
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertEqual(usuario.consentimiento_version, AVISO_DATOS_VERSION)
        self.assertEqual(usuario.consentimiento_fecha.date(), timezone.now().date())

    def test_version_anterior_del_aviso_exige_revisar_la_actual(self):
        respuesta = self.client.post(
            self.url, self.datos_registro(aviso_version="version-anterior")
        )

        self.assertIn("__all__", respuesta.context["form"].errors)
        self.assertContains(respuesta, "El aviso de datos cambió.")
        self.assertEqual(Usuario.objects.count(), 0)

    def test_post_vacio_muestra_errores_y_no_crea_cuenta(self):
        respuesta = self.client.post(self.url, {})

        self.assertTrue(respuesta.context["form"].is_bound)
        self.assertIn("username", respuesta.context["form"].errors)
        self.assertIn("acepta_aviso", respuesta.context["form"].errors)
        self.assertEqual(Usuario.objects.count(), 0)

    def test_contrasenas_no_se_devuelven_en_html_con_errores(self):
        datos = self.datos_registro(password2="Otra!Clave24Distinta")

        respuesta = self.client.post(self.url, datos)

        self.assertNotContains(respuesta, datos["password1"])
        self.assertNotContains(respuesta, datos["password2"])

    def test_post_requiere_token_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        pagina = cliente.get(self.url)
        token = pagina.context["csrf_token"]

        sin_token = cliente.post(self.url, self.datos_registro())
        self.assertEqual(sin_token.status_code, 403)
        self.assertEqual(Usuario.objects.count(), 0)

        con_token = cliente.post(
            self.url, {**self.datos_registro(), "csrfmiddlewaretoken": token}
        )
        self.assertRedirects(con_token, self.url_login)
        self.assertEqual(Usuario.objects.count(), 1)

    def test_servicio_tambien_exige_consentimiento_y_version_vigente(self):
        for cambios in [
            {"acepta_aviso": False},
            {"aviso_version": "version-anterior"},
        ]:
            with self.subTest(cambios=cambios):
                datos = {
                    "username": "bryan_prueba",
                    "password": "Rama!Rio42Cobre",
                    "nombre_completo": "Bryan Ayala",
                    "fecha_nacimiento": timezone.localdate(),
                    "acepta_aviso": True,
                    "aviso_version": AVISO_DATOS_VERSION,
                    **cambios,
                }

                with self.assertRaises(ValidationError):
                    registrar_usuario(**datos)

                self.assertEqual(Usuario.objects.count(), 0)


class SesionesTests(TestCase):
    password = "Rama!Rio42Cobre"

    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="sesion_prueba",
            password=cls.password,
            nombre_completo="Persona de prueba",
            fecha_nacimiento=timezone.localdate() - timedelta(days=365 * 20),
        )
        cls.inactivo = Usuario.objects.create_user(
            username="cuenta_inactiva",
            password=cls.password,
            nombre_completo="Persona inactiva",
            fecha_nacimiento=timezone.localdate() - timedelta(days=365 * 20),
            is_active=False,
        )

    def setUp(self):
        self.url_login = reverse("cuentas:login")
        self.url_perfil = reverse("cuentas:perfil")
        self.url_logout = reverse("cuentas:logout")

    def test_login_publico_muestra_formulario_sin_datos_personales(self):
        respuesta = self.client.get(self.url_login)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "cuentas/login.html")
        self.assertContains(respuesta, 'autocomplete="current-password"')
        self.assertNotContains(respuesta, self.usuario.nombre_completo)

    def test_login_crea_sesion_cambia_su_clave_y_permite_consultar_perfil(self):
        sesion_previa = self.client.session
        sesion_previa["dato_previo"] = "prueba"
        sesion_previa.save()
        clave_previa = sesion_previa.session_key

        respuesta = self.client.post(
            self.url_login,
            {"username": self.usuario.username, "password": self.password},
        )

        self.assertRedirects(respuesta, self.url_perfil)
        self.assertEqual(self.client.session[SESSION_KEY], str(self.usuario.pk))
        self.assertNotEqual(self.client.session.session_key, clave_previa)
        perfil = self.client.get(self.url_perfil)
        self.assertEqual(perfil.context["user"].pk, self.usuario.pk)

    def test_credenciales_incorrectas_e_inactividad_dan_el_mismo_error(self):
        casos = [
            (self.usuario.username, "Clave!Equivocada42"),
            ("cuenta_que_no_existe", self.password),
            (self.inactivo.username, self.password),
        ]
        for username, password in casos:
            with self.subTest(username=username):
                respuesta = self.client.post(
                    self.url_login, {"username": username, "password": password}
                )

                self.assertFormError(
                    respuesta.context["form"],
                    None,
                    "Usuario o contraseña incorrectos.",
                )
                self.assertNotContains(respuesta, password)
                self.assertNotIn(SESSION_KEY, self.client.session)

    def test_login_conserva_un_destino_interno(self):
        destino = self.url_perfil + "?origen=prueba"
        pagina = self.client.get(self.url_login, {"next": destino})
        self.assertEqual(pagina.context["next"], destino)

        respuesta = self.client.post(
            self.url_login,
            {
                "username": self.usuario.username,
                "password": self.password,
                "next": destino,
            },
        )

        self.assertRedirects(respuesta, destino)

    def test_login_no_redirige_a_sitios_externos_ni_rebaja_https(self):
        casos = [
            ("https://fuera.example/perfil/", False),
            ("//fuera.example/perfil/", False),
            ("///fuera.example/perfil/", False),
            ("javascript:alert(1)", False),
            ("http://testserver/cuentas/perfil/", True),
        ]
        for destino, seguro in casos:
            with self.subTest(destino=destino):
                cliente = Client()
                respuesta = cliente.post(
                    self.url_login,
                    {
                        "username": self.usuario.username,
                        "password": self.password,
                        "next": destino,
                    },
                    secure=seguro,
                )

                self.assertEqual(respuesta.status_code, 302)
                self.assertEqual(respuesta["Location"], self.url_perfil)

    def test_cuenta_con_sesion_no_vuelve_a_registrarse_ni_cambia_de_identidad(self):
        self.client.force_login(self.usuario)
        for url in [self.url_login, reverse("cuentas:registro")]:
            for metodo in [self.client.get, self.client.post]:
                with self.subTest(url=url, metodo=metodo.__name__):
                    respuesta = metodo(url)

                    self.assertRedirects(respuesta, self.url_perfil)
                    self.assertEqual(self.client.session[SESSION_KEY], str(self.usuario.pk))
                    self.assertEqual(Usuario.objects.count(), 2)

    def test_logout_solo_por_post_elimina_el_acceso_privado(self):
        self.client.force_login(self.usuario)

        por_get = self.client.get(self.url_logout)
        self.assertEqual(por_get.status_code, 405)
        self.assertIn(SESSION_KEY, self.client.session)

        por_post = self.client.post(self.url_logout)
        self.assertRedirects(por_post, self.url_login)
        self.assertNotIn(SESSION_KEY, self.client.session)
        privado = self.client.get(self.url_perfil)
        self.assertRedirects(
            privado, self.url_login + "?next=" + self.url_perfil,
            fetch_redirect_response=False,
        )

    def test_csrf_protege_login_edicion_y_cierre_de_sesion(self):
        cliente = Client(enforce_csrf_checks=True)
        pagina = cliente.get(self.url_login)
        credenciales = {"username": self.usuario.username, "password": self.password}

        self.assertEqual(cliente.post(self.url_login, credenciales).status_code, 403)
        self.assertNotIn(SESSION_KEY, cliente.session)
        entrada = cliente.post(
            self.url_login,
            {**credenciales, "csrfmiddlewaretoken": pagina.context["csrf_token"]},
        )
        self.assertRedirects(entrada, self.url_perfil)

        perfil = cliente.get(self.url_perfil)
        datos = {
            "nombre_completo": "Nombre actualizado",
            "fecha_nacimiento": self.usuario.fecha_nacimiento.isoformat(),
            "genero": "",
            "talentos_ancestrales": "",
        }
        self.assertEqual(cliente.post(self.url_perfil, datos).status_code, 403)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Persona de prueba")
        guardado = cliente.post(
            self.url_perfil,
            {**datos, "csrfmiddlewaretoken": perfil.context["csrf_token"]},
        )
        self.assertRedirects(guardado, self.url_perfil)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Nombre actualizado")

        self.assertEqual(cliente.post(self.url_logout).status_code, 403)
        self.assertIn(SESSION_KEY, cliente.session)
        salida = cliente.post(
            self.url_logout, {"csrfmiddlewaretoken": perfil.context["csrf_token"]}
        )
        self.assertRedirects(salida, self.url_login)
        self.assertNotIn(SESSION_KEY, cliente.session)


class PerfilTests(TestCase):
    password = "Rama!Rio42Cobre"

    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="titular_prueba",
            password=cls.password,
            nombre_completo="Titular de prueba",
            fecha_nacimiento=timezone.localdate() - timedelta(days=365 * 20),
            genero=Usuario.Genero.OTRO,
            talentos_ancestrales="Cuidado de plantas",
            consentimiento_fecha=timezone.now(),
            consentimiento_version=AVISO_DATOS_VERSION,
        )
        cls.otra_persona = Usuario.objects.create_user(
            username="otra_persona",
            password=cls.password,
            nombre_completo="Otra persona de prueba",
            fecha_nacimiento=timezone.localdate() - timedelta(days=365 * 35),
            genero=Usuario.Genero.FEMENINO,
        )

    def setUp(self):
        self.url = reverse("cuentas:perfil")
        self.client.force_login(self.usuario)

    def datos_perfil(self, **cambios):
        datos = {
            "nombre_completo": "Titular actualizado",
            "fecha_nacimiento": self.usuario.fecha_nacimiento.isoformat(),
            "genero": "",
            "talentos_ancestrales": "Preparación de la tierra",
        }
        datos.update(cambios)
        return datos

    def test_anonimo_no_puede_leer_ni_editar_perfil(self):
        cliente = Client()
        for metodo in [cliente.get, cliente.post]:
            with self.subTest(metodo=metodo.__name__):
                datos = self.datos_perfil() if metodo.__name__ == "post" else {}
                respuesta = metodo(self.url, datos)

                self.assertRedirects(
                    respuesta,
                    reverse("cuentas:login") + "?next=" + self.url,
                    fetch_redirect_response=False,
                )
                self.assertNotContains(
                    respuesta, self.usuario.fecha_nacimiento.isoformat(), status_code=302
                )
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Titular de prueba")

    def test_muestra_perfil_propio_y_aviso_con_constancia_sin_cache(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["form"].instance.pk, self.usuario.pk)
        self.assertEqual(
            respuesta.context["form"]["fecha_nacimiento"].value(),
            self.usuario.fecha_nacimiento,
        )
        self.assertNotIn("username", respuesta.context["form"].fields)
        self.assertContains(respuesta, "Aviso sobre el uso de tus datos")
        self.assertContains(respuesta, "Aceptaste la versión " + AVISO_DATOS_VERSION)
        self.assertIn("no-store", respuesta["Cache-Control"])
        self.assertIn("private", respuesta["Cache-Control"])

    def test_edita_solo_datos_permitidos_y_conserva_cuenta_y_consentimiento(self):
        constancia = (
            self.usuario.consentimiento_fecha, self.usuario.consentimiento_version
        )
        hash_previo = self.usuario.password
        respuesta = self.client.post(
            self.url,
            self.datos_perfil(
                username="usuario_distinto",
                password="Otra!Clave24Distinta",
                is_staff="on",
                is_superuser="on",
                is_active="",
                consentimiento_fecha="2000-01-01T00:00:00Z",
                consentimiento_version="inventada",
            ),
        )

        self.assertRedirects(respuesta, self.url)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Titular actualizado")
        self.assertEqual(self.usuario.genero, "")
        self.assertEqual(self.usuario.talentos_ancestrales, "Preparación de la tierra")
        self.assertEqual(self.usuario.username, "titular_prueba")
        self.assertEqual(self.usuario.password, hash_previo)
        self.assertFalse(self.usuario.is_staff)
        self.assertFalse(self.usuario.is_superuser)
        self.assertTrue(self.usuario.is_active)
        self.assertEqual(
            (self.usuario.consentimiento_fecha, self.usuario.consentimiento_version),
            constancia,
        )
        self.assertEqual(self.client.session[SESSION_KEY], str(self.usuario.pk))

    def test_id_ajeno_no_permite_consultar_ni_modificar_otra_cuenta(self):
        consulta = self.client.get(self.url, {"usuario_id": self.otra_persona.pk})
        self.assertEqual(consulta.context["form"].instance.pk, self.usuario.pk)
        self.assertEqual(
            consulta.context["form"]["genero"].value(), self.usuario.genero
        )
        self.assertNotContains(consulta, self.otra_persona.nombre_completo)
        self.assertNotContains(consulta, self.otra_persona.fecha_nacimiento.isoformat())
        ruta_ajena = self.client.get(self.url + str(self.otra_persona.pk) + "/")
        self.assertEqual(ruta_ajena.status_code, 404)

        cambio = self.client.post(
            self.url + "?usuario_id=" + str(self.otra_persona.pk),
            self.datos_perfil(
                usuario_id=self.otra_persona.pk,
                id=self.otra_persona.pk,
                pk=self.otra_persona.pk,
            ),
        )

        self.assertRedirects(cambio, self.url)
        self.otra_persona.refresh_from_db()
        self.assertEqual(self.otra_persona.nombre_completo, "Otra persona de prueba")
        self.assertEqual(self.otra_persona.genero, Usuario.Genero.FEMENINO)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Titular actualizado")

    def test_datos_invalidos_no_se_guardan(self):
        casos = [
            (
                {"fecha_nacimiento": (timezone.localdate() + timedelta(days=1)).isoformat()},
                "fecha_nacimiento",
            ),
            ({"nombre_completo": "   "}, "nombre_completo"),
            ({"genero": "inexistente"}, "genero"),
        ]
        for cambios, campo in casos:
            with self.subTest(campo=campo):
                respuesta = self.client.post(self.url, self.datos_perfil(**cambios))

                self.assertIn(campo, respuesta.context["form"].errors)
                self.usuario.refresh_from_db()
                self.assertEqual(self.usuario.nombre_completo, "Titular de prueba")
                self.assertEqual(self.usuario.genero, Usuario.Genero.OTRO)

    def test_fecha_de_menor_de_catorce_y_genero_no_indicado_son_validos(self):
        fecha_menor = timezone.localdate() - timedelta(days=365 * 12)
        respuesta = self.client.post(
            self.url,
            self.datos_perfil(fecha_nacimiento=fecha_menor.isoformat(), genero=""),
        )

        self.assertRedirects(respuesta, self.url)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.fecha_nacimiento, fecha_menor)
        self.assertEqual(self.usuario.genero, "")

    def test_servicio_rechaza_actor_anonimo_o_inactivo_y_datos_invalidos(self):
        datos = {
            "nombre_completo": "Cambio no permitido",
            "fecha_nacimiento": self.usuario.fecha_nacimiento,
        }
        self.usuario.is_active = False
        for actor in [AnonymousUser(), self.usuario]:
            with self.subTest(actor=type(actor).__name__):
                with self.assertRaises(PermissionDenied):
                    actualizar_perfil(actor=actor, **datos)

        self.usuario.refresh_from_db()
        with self.assertRaises(ValidationError):
            actualizar_perfil(
                actor=self.usuario,
                **{**datos, "fecha_nacimiento": timezone.localdate() + timedelta(days=1)},
            )
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombre_completo, "Titular de prueba")
