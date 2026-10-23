"""
Configuración de Django para el proyecto Huertos medicinales comunitarios (V1).

Referencia: https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Seguridad -------------------------------------------------------------

# La clave se lee de la variable de entorno DJANGO_SECRET_KEY (ver README).
# Nunca se escribe en este archivo ni se sube a Git.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        'Falta la variable de entorno DJANGO_SECRET_KEY. '
        'Sigue la sección "Clave secreta" del README.'
    )

# Desarrollo y demo local: DEBUG activo salvo que se defina DJANGO_DEBUG=0.
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

# Hosts adicionales (por ejemplo, la IP local para probar desde el celular),
# separados por comas en DJANGO_ALLOWED_HOSTS.
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + [
    host.strip()
    for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')
    if host.strip()
]


# --- Aplicaciones ----------------------------------------------------------

# Sin django.contrib.admin: V1 no tiene panel técnico de administración.
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Módulos del dominio
    'cuentas.apps.CuentasConfig',
    'catalogo.apps.CatalogoConfig',
    'comunidades.apps.ComunidadesConfig',
    'actividades.apps.ActividadesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Todas las vistas requieren sesión salvo las marcadas con login_not_required.
    'django.contrib.auth.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'huertos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'huertos.wsgi.application'


# --- Base de datos ---------------------------------------------------------

# SQLite con transacciones IMMEDIATE y espera breve para serializar escrituras
# cortas (registro, anulación, nombramiento de maestro).
# https://docs.djangoproject.com/en/5.2/ref/databases/#sqlite-notes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'transaction_mode': 'IMMEDIATE',
            'timeout': 5,
        },
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- Autenticación ---------------------------------------------------------

# Debe existir antes de la primera migración (cuentas/models.py: Usuario).
AUTH_USER_MODEL = 'cuentas.Usuario'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {'user_attributes': ('username', 'nombre_completo')},
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'cuentas:login'
LOGIN_REDIRECT_URL = 'cuentas:perfil'
LOGOUT_REDIRECT_URL = 'cuentas:login'


# --- Idioma y zona horaria -------------------------------------------------

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# --- Archivos estáticos ----------------------------------------------------

# Bootstrap, estilos e imágenes se sirven localmente (demo sin internet).
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


# --- Mensajes --------------------------------------------------------------

# Bootstrap usa "danger" en lugar de "error".
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}
