"""
Crea un escenario ficticio para demostrar el sistema de huertos medicinales.

Ejecución desde la raíz del proyecto:
    .venv/bin/python manage.py shell < scripts/crear_demo.py

El script no elimina ni modifica datos preexistentes. Si detecta alguna cuenta
o comunidad del escenario, se detiene antes de comenzar.

La creación de los datos se realiza dentro de una transacción. La copia de
seguridad se genera después de confirmar la transacción.
"""

from datetime import date, timedelta
from pathlib import Path
import os
import sqlite3
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connections, transaction
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone

from cuentas.aviso import AVISO_DATOS_VERSION
from cuentas.servicios import registrar_usuario

from catalogo.models import Material, OpcionHuerto, Planta
from comunidades.models import Comunidad, Huerto, Miembro
from comunidades.servicios import (
    crear_comunidad,
    configurar_huerto,
    elegir_planta,
    marcar_material,
    unirse_comunidad,
)

from actividades.models import Actividad
from actividades.servicios import (
    anular_actividad,
    nombrar_maestro,
    puntos_de_usuario,
    registrar_actividad,
)


# ============================================================
# 1. CONFIGURACIÓN DEL ESCENARIO
# ============================================================

CUENTAS = {
    "responsable_a": {
        "username": "demo_responsable_a",
        "nombre": "Ana Responsable Los Aromos",
        "password": "R3fugio!Luna_Cedro#72",
        "nacimiento": date(1988, 4, 12),
    },
    "participante_a": {
        "username": "demo_participante_a",
        "nombre": "Mateo Participante Los Aromos",
        "password": "M4nt4!Bosque_Romero#83",
        "nacimiento": date(1995, 8, 21),
    },
    "responsable_b": {
        "username": "demo_responsable_b",
        "nombre": "Lucia Responsable La Esperanza",
        "password": "V3rde!Huerto_Lavanda#94",
        "nacimiento": date(1990, 2, 17),
    },
    "participante_b": {
        "username": "demo_participante_b",
        "nombre": "Diego Participante La Esperanza",
        "password": "T1erra!Semilla_Menta#65",
        "nacimiento": date(1997, 11, 5),
    },
}

NOMBRE_COMUNIDAD_A = "Huerto Medicinal Los Aromos"
NOMBRE_COMUNIDAD_B = "Huerto Medicinal La Esperanza"

TELEFONO_FICTICIO = "0991234567"
METODO_SIEMBRA = "semillas"

CODIGOS_PLANTAS = (
    "romero",
    "menta",
    "lavanda",
)

CODIGOS_OPCIONES = (
    "diseno-tierra",
    "cerca-viva",
    "suelo-limoso",
    "agua-otro",
    "abono-compost",
)

CODIGOS_MATERIALES = (
    "pala",
)


# ============================================================
# 2. COMPROBACIONES PREVIAS
# ============================================================

def comprobar_sqlite():
    """Verifica que la base de datos predeterminada sea SQLite."""

    if connections["default"].vendor != "sqlite":
        raise RuntimeError(
            "Este script requiere que la base de datos predeterminada "
            "utilice SQLite."
        )

    nombre_bd = settings.DATABASES["default"]["NAME"]

    if str(nombre_bd) == ":memory:":
        raise RuntimeError(
            "No se puede generar una copia persistente desde una base "
            "SQLite en memoria."
        )


def comprobar_migraciones():
    """Comprueba que no existan migraciones pendientes."""

    executor = MigrationExecutor(connections["default"])

    pendientes = executor.migration_plan(
        executor.loader.graph.leaf_nodes()
    )

    if pendientes:
        nombres = [
            f"{migracion.app_label}.{migracion.name}"
            for migracion, _ in pendientes
        ]

        raise RuntimeError(
            "Hay migraciones pendientes. Ejecuta primero:\n"
            "  python manage.py migrate\n"
            "Migraciones pendientes: "
            + ", ".join(nombres)
        )


def comprobar_catalogo():
    """Comprueba que existan los elementos necesarios del catálogo."""

    faltantes = []

    for codigo in CODIGOS_PLANTAS:
        if not Planta.objects.filter(codigo=codigo).exists():
            faltantes.append(f"planta: {codigo}")

    for codigo in CODIGOS_OPCIONES:
        if not OpcionHuerto.objects.filter(codigo=codigo).exists():
            faltantes.append(f"opción: {codigo}")

    for codigo in CODIGOS_MATERIALES:
        if not Material.objects.filter(codigo=codigo).exists():
            faltantes.append(f"material: {codigo}")

    if faltantes:
        raise RuntimeError(
            "Faltan elementos del catálogo: "
            + ", ".join(faltantes)
            + ". Ejecuta primero:\n"
            "  python manage.py cargar_catalogo"
        )


def comprobar_escenario_no_existe():
    """
    Evita duplicar las cuentas o comunidades de la demostración.

    No elimina ni modifica registros existentes.
    """

    usernames = [
        datos["username"]
        for datos in CUENTAS.values()
    ]

    existentes = list(
        get_user_model().objects.filter(
            username__in=usernames
        ).values_list("username", flat=True)
    )

    nombres = [
        NOMBRE_COMUNIDAD_A,
        NOMBRE_COMUNIDAD_B,
    ]

    comunidades_existentes = list(
        Comunidad.objects.filter(
            nombre__in=nombres
        ).values_list("nombre", flat=True)
    )

    if existentes or comunidades_existentes:
        detalles = []

        if existentes:
            detalles.append(
                "Cuentas existentes: " + ", ".join(existentes)
            )

        if comunidades_existentes:
            detalles.append(
                "Comunidades existentes: "
                + ", ".join(comunidades_existentes)
            )

        raise RuntimeError(
            "El escenario parece haberse creado anteriormente. "
            "No se modificó ningún registro.\n"
            + "\n".join(detalles)
            + "\nUtiliza una base de datos de demostración limpia "
            "o revisa los registros existentes antes de continuar."
        )


# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

def obtener_opcion(codigo):
    return OpcionHuerto.objects.get(codigo=codigo)


def crear_cuenta(datos):
    """Crea una cuenta utilizando el servicio de registro del proyecto."""

    return registrar_usuario(
        username=datos["username"],
        password=datos["password"],
        nombre_completo=datos["nombre"],
        fecha_nacimiento=datos["nacimiento"],
        acepta_aviso=True,
        aviso_version=AVISO_DATOS_VERSION,
    )


def configurar_huerto_demo(actor, direccion):
    """Configura un huerto con opciones existentes del catálogo."""

    return configurar_huerto(
        actor=actor,
        provincia="Pichincha",
        parroquia="Quito",
        direccion=direccion,
        area_m2="24.00",
        disenos=[
            obtener_opcion("diseno-tierra"),
        ],
        cerca=obtener_opcion("cerca-viva"),
        suelo=obtener_opcion("suelo-limoso"),
        fuente_agua=obtener_opcion("agua-otro"),
        abonos=[
            obtener_opcion("abono-compost"),
        ],
    )


def registrar(huerto, actor, tipo, fecha, planta=None, detalles=""):
    """Registra una actividad y comprueba que sea una creación nueva."""

    actividad, creada = registrar_actividad(
        huerto=huerto,
        usuario=actor,
        tipo=tipo,
        fecha=fecha,
        planta=planta,
        detalles=detalles,
    )

    if not creada:
        raise RuntimeError(
            f"La actividad '{tipo}' no se creó como un registro nuevo."
        )

    print(
        f"  Actividad registrada: {tipo} | "
        f"{timezone.localtime(fecha)}"
    )

    return actividad


# ============================================================
# 4. COPIA DE SEGURIDAD SQLITE
# ============================================================

def crear_copia_sqlite():
    """
    Crea una copia consistente de SQLite.

    Utiliza la función backup de SQLite para incluir los datos confirmados
    aunque la base utilice el mecanismo WAL.
    """

    ruta_bd = Path(
        settings.DATABASES["default"]["NAME"]
    ).resolve()

    if not ruta_bd.exists():
        raise RuntimeError(
            f"No se encontró la base de datos: {ruta_bd}"
        )

    carpeta = Path(settings.BASE_DIR) / "copias"
    carpeta.mkdir(parents=True, exist_ok=True)

    destino = carpeta / "demo_huertos.sqlite3"

    # Se cierra la conexión de Django antes de realizar la copia.
    connections["default"].close()

    descriptor, nombre_temporal = tempfile.mkstemp(
        prefix="demo_huertos_",
        suffix=".sqlite3",
        dir=carpeta,
    )

    os.close(descriptor)

    temporal = Path(nombre_temporal)

    try:
        with sqlite3.connect(str(ruta_bd)) as origen:
            with sqlite3.connect(str(temporal)) as copia:
                origen.backup(copia)

        # Verificar la integridad de la copia.
        with sqlite3.connect(str(temporal)) as copia:
            resultado = copia.execute(
                "PRAGMA integrity_check"
            ).fetchone()[0]

        if resultado != "ok":
            raise RuntimeError(
                "La comprobación de integridad falló: "
                + resultado
            )

        # Reemplazar la copia anterior únicamente después de verificarla.
        os.replace(temporal, destino)

        return destino

    finally:
        if temporal.exists():
            temporal.unlink()


# ============================================================
# 5. CREACIÓN DEL ESCENARIO
# ============================================================

print("\n=== PREPARANDO DEMOSTRACIÓN ===")

comprobar_sqlite()
comprobar_migraciones()
comprobar_catalogo()
comprobar_escenario_no_existe()

print("Base de datos SQLite verificada.")
print("Migraciones aplicadas.")
print("Catálogo verificado.")
print("No existen cuentas ni comunidades de esta demostración.")


try:

    with transaction.atomic():

        # ----------------------------------------------------
        # 5.1. CUENTAS
        # ----------------------------------------------------

        print("\n=== 1. CREANDO CUENTAS ===")

        responsable_a = crear_cuenta(
            CUENTAS["responsable_a"]
        )

        participante_a = crear_cuenta(
            CUENTAS["participante_a"]
        )

        responsable_b = crear_cuenta(
            CUENTAS["responsable_b"]
        )

        participante_b = crear_cuenta(
            CUENTAS["participante_b"]
        )

        print("Creadas las cuatro cuentas ficticias.")

        # ----------------------------------------------------
        # 5.2. COMUNIDADES
        # ----------------------------------------------------

        print("\n=== 2. CREANDO COMUNIDADES ===")

        comunidad_a = crear_comunidad(
            actor=responsable_a,
            nombre=NOMBRE_COMUNIDAD_A,
            tipo=Comunidad.Tipo.BARRIO,
            contacto_nombre=responsable_a.nombre_completo,
            contacto_telefono=TELEFONO_FICTICIO,
            contacto_correo="aromos@example.test",
        )

        comunidad_b = crear_comunidad(
            actor=responsable_b,
            nombre=NOMBRE_COMUNIDAD_B,
            tipo=Comunidad.Tipo.BARRIO,
            contacto_nombre=responsable_b.nombre_completo,
            contacto_telefono=TELEFONO_FICTICIO,
            contacto_correo="esperanza@example.test",
        )

        unirse_comunidad(
            actor=participante_a,
            codigo_invitacion=comunidad_a.codigo_invitacion,
        )

        unirse_comunidad(
            actor=participante_b,
            codigo_invitacion=comunidad_b.codigo_invitacion,
        )

        print("Creadas las dos comunidades y sus participantes.")

        # ----------------------------------------------------
        # 5.3. HUERTOS
        # ----------------------------------------------------

        print("\n=== 3. CONFIGURANDO HUERTOS ===")

        huerto_a = configurar_huerto_demo(
            responsable_a,
            "Dirección ficticia de demostración, Los Aromos",
        )

        huerto_b = configurar_huerto_demo(
            responsable_b,
            "Dirección ficticia de demostración, La Esperanza",
        )

        print("Ambos huertos están configurados.")

        # ----------------------------------------------------
        # 5.4. PLANTAS
        # ----------------------------------------------------

        print("\n=== 4. SELECCIONANDO PLANTAS ===")

        romero = elegir_planta(
            actor=responsable_a,
            planta=Planta.objects.get(codigo="romero"),
            metodo_siembra=METODO_SIEMBRA,
        )

        menta = elegir_planta(
            actor=responsable_a,
            planta=Planta.objects.get(codigo="menta"),
            metodo_siembra=METODO_SIEMBRA,
        )

        elegir_planta(
            actor=responsable_b,
            planta=Planta.objects.get(codigo="lavanda"),
            metodo_siembra=METODO_SIEMBRA,
        )

        print("Romero y Menta seleccionados en Los Aromos.")
        print("Lavanda seleccionada en La Esperanza.")

        # ----------------------------------------------------
        # 5.5. MATERIALES
        # ----------------------------------------------------

        print("\n=== 5. REGISTRANDO MATERIALES ===")

        pala = Material.objects.get(codigo="pala")

        marcar_material(
            actor=participante_a,
            material_id=pala.pk,
            disponible=True,
        )

        marcar_material(
            actor=participante_b,
            material_id=pala.pk,
            disponible=True,
        )

        print("La pala está marcada como disponible en ambos huertos.")

        # ----------------------------------------------------
        # 5.6. HISTORIAL DEL ROMERO
        # ----------------------------------------------------

        print("\n=== 6. REGISTRANDO HISTORIAL DEL ROMERO ===")

        ahora = timezone.now()

        fechas = {
            "preparacion": ahora - timedelta(days=180),
            "diseno": ahora - timedelta(days=179),
            "ritual": ahora - timedelta(days=178),
            "siembra": ahora - timedelta(days=165),
            "senaletica": ahora - timedelta(days=164),
            "cuidados": ahora - timedelta(days=160),
            "bano": ahora - timedelta(days=155),
            "gratitud": ahora - timedelta(days=150),
            "cosecha": ahora - timedelta(days=90),
            "limpieza": ahora - timedelta(days=89),
            "secado": ahora - timedelta(days=88),
            "empaquetado": ahora - timedelta(days=78),
        }

        registrar(
            huerto_a,
            participante_a,
            "preparacion",
            fechas["preparacion"],
            detalles="Preparación inicial de la tierra del huerto.",
        )

        registrar(
            huerto_a,
            participante_a,
            "diseno",
            fechas["diseno"],
            detalles="Distribución de los espacios de cultivo.",
        )

        registrar(
            huerto_a,
            participante_a,
            "ritual",
            fechas["ritual"],
            detalles="Ritual comunitario previo a la siembra.",
        )

        secuencia_romero = (
            ("siembra", "Siembra de Romero."),
            ("senaletica", "Identificación de la planta."),
            ("cuidados", "Primer registro de cuidados."),
            ("bano", "Baño de la planta."),
            ("gratitud", "Ritual de gratitud."),
            ("cosecha", "Cosecha del Romero."),
            ("limpieza", "Limpieza posterior a la cosecha."),
            ("secado", "Inicio del secado."),
            ("empaquetado", "Empaquetado y etiquetado."),
        )

        for tipo, detalle in secuencia_romero:
            registrar(
                huerto_a,
                participante_a,
                tipo,
                fechas[tipo],
                planta=romero,
                detalles=detalle,
            )

        puntos_iniciales = puntos_de_usuario(
            participante_a,
            huerto_a,
        )

        if puntos_iniciales != 120:
            raise RuntimeError(
                "Se esperaban 120 puntos antes del nombramiento, "
                f"pero se obtuvieron {puntos_iniciales}."
            )

        print(
            "Puntos del participante antes del nombramiento:",
            puntos_iniciales,
        )

        # ----------------------------------------------------
        # 5.7. NOMBRAMIENTO DEL MAESTRO
        # ----------------------------------------------------

        print("\n=== 7. NOMBRANDO AL MAESTRO ===")

        miembro_a = Miembro.objects.get(
            usuario=participante_a
        )

        nombrar_maestro(
            huerto=huerto_a,
            usuario_autor=responsable_a,
            candidato=miembro_a,
            motivo=(
                "Ha completado el ciclo de cultivo del Romero y demuestra "
                "experiencia en preparación, siembra, cuidados, cosecha y "
                "procesamiento de plantas medicinales."
            ),
            maestro_esperado_id=None,
        )

        print("Mateo ha sido nombrado Maestro de Los Aromos.")

        # ----------------------------------------------------
        # 5.8. VALIDACIÓN DE LOS 15 DÍAS
        # ----------------------------------------------------

        print("\n=== 8. PROBANDO LA REGLA DE LOS 15 DÍAS ===")

        fecha_rechazada = (
            fechas["preparacion"] + timedelta(days=14)
        )

        try:
            registrar_actividad(
                huerto=huerto_a,
                usuario=participante_a,
                tipo="siembra",
                fecha=fecha_rechazada,
                planta=menta,
                detalles="Prueba de siembra antes del plazo mínimo.",
            )

        except ValidationError as error:

            mensaje = " ".join(error.messages)

            if "15 días" not in mensaje:
                raise

            print(
                "Validación correcta: se rechazó la siembra a los 14 días."
            )
            print("Mensaje:", mensaje)

        else:
            raise RuntimeError(
                "La aplicación aceptó una siembra antes de los 15 días."
            )

        # ----------------------------------------------------
        # 5.9. SIEMBRA Y ANULACIÓN DE MENTA
        # ----------------------------------------------------

        print(
            "\n=== 9. REGISTRANDO Y ANULANDO LA SIEMBRA DE MENTA ==="
        )

        actividad_menta, creada = registrar_actividad(
            huerto=huerto_a,
            usuario=participante_a,
            tipo="siembra",
            fecha=timezone.now(),
            planta=menta,
            detalles=(
                "Siembra válida de prueba para demostrar la anulación."
            ),
        )

        if not creada:
            raise RuntimeError(
                "No se creó una nueva actividad de Menta."
            )

        puntos_tras_siembra = puntos_de_usuario(
            participante_a,
            huerto_a,
        )

        if puntos_tras_siembra != 135:
            raise RuntimeError(
                "Se esperaban 135 puntos después de la siembra, "
                f"pero se obtuvieron {puntos_tras_siembra}."
            )

        print(
            "Puntos después de la siembra:",
            puntos_tras_siembra,
        )

        actividad_anulada, maestro_retirado = anular_actividad(
            actividad_id=actividad_menta.pk,
            usuario_autor=responsable_a,
            motivo=(
                "Anulación de la actividad de prueba para demostrar "
                "la reversión del estado y de los puntos."
            ),
        )

        if maestro_retirado:
            raise RuntimeError(
                "El sistema retiró al Maestro cuando debía conservarlo."
            )

        puntos_finales = puntos_de_usuario(
            participante_a,
            huerto_a,
        )

        if puntos_finales != 120:
            raise RuntimeError(
                "Se esperaban 120 puntos después de la anulación, "
                f"pero se obtuvieron {puntos_finales}."
            )

        if actividad_anulada.estado != Actividad.Estado.ANULADA:
            raise RuntimeError(
                "La actividad de Menta no quedó anulada."
            )

        print("Actividad de Menta anulada correctamente.")
        print("Puntos después de la anulación:", puntos_finales)
        print("Mateo conserva su nombramiento como Maestro.")

        # ----------------------------------------------------
        # 5.10. VALIDACIÓN FINAL
        # ----------------------------------------------------

        print("\n=== 10. VERIFICANDO RESULTADOS ===")

        huerto_a.refresh_from_db()
        huerto_b.refresh_from_db()

        if huerto_a.maestro_id != miembro_a.pk:
            raise RuntimeError(
                "No se conservó el nombramiento del Maestro."
            )

        activas = Actividad.objects.filter(
            huerto=huerto_a,
            estado=Actividad.Estado.ACTIVA,
        ).count()

        anuladas = Actividad.objects.filter(
            huerto=huerto_a,
            estado=Actividad.Estado.ANULADA,
        ).count()

        if activas != 12 or anuladas != 1:
            raise RuntimeError(
                "Conteo inesperado de actividades: "
                f"{activas} activas y {anuladas} anuladas."
            )

        if Huerto.objects.filter(
            comunidad=comunidad_a
        ).count() != 1:
            raise RuntimeError(
                "La Comunidad A no tiene exactamente un huerto."
            )

        if Huerto.objects.filter(
            comunidad=comunidad_b
        ).count() != 1:
            raise RuntimeError(
                "La Comunidad B no tiene exactamente un huerto."
            )

        print("Comunidad A:", comunidad_a.nombre)
        print("Huerto A ID:", huerto_a.pk)
        print(
            "Maestro:",
            huerto_a.maestro.usuario.nombre_completo,
        )
        print("Puntos del participante:", puntos_finales)
        print("Actividades activas:", activas)
        print("Actividades anuladas:", anuladas)

        print("\nComunidad B:", comunidad_b.nombre)
        print("Huerto B ID:", huerto_b.pk)

        print("\n=== RESUMEN DE CUENTAS ===")

        for rol, datos in CUENTAS.items():
            print(f"{rol}: {datos['username']}")

    # La transacción se confirma al salir del bloque.

except Exception:
    print(
        "\nERROR: la creación no se completó. "
        "La transacción fue revertida. Revisa el error anterior."
    )
    raise


# ============================================================
# 6. GENERAR COPIA DE SEGURIDAD
# ============================================================

print("\n=== CREANDO COPIA DE LA BASE DE DATOS ===")

try:
    copia = crear_copia_sqlite()

except Exception as error:
    print(
        "\nATENCIÓN: los datos de demostración sí se crearon y "
        "confirmaron, pero no se pudo generar la copia de seguridad."
    )
    print("Error de respaldo:", error)
    raise

print("Copia de demostración:", copia)
print("Integridad SQLite: ok")

print("\n=== DEMOSTRACIÓN PREPARADA CORRECTAMENTE ===")