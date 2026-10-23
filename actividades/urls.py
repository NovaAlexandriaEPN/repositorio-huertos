"""
Rutas de la aplicación actividades.
Configura las URLs para registro, historial, anulación, nombramiento de maestro y huerto virtual.
"""
from django.urls import path
from . import views

app_name = 'actividades'

urlpatterns = [
    # Huerto virtual y tarjetas
    path('<int:huerto_id>/huerto-virtual/', views.inicio_huerto_virtual_view, name='inicio_huerto_virtual'),

    # Registro y consulta de actividades
    path('<int:huerto_id>/registrar/', views.registrar_actividad_view, name='registrar_actividad'),
    path('<int:huerto_id>/historial/', views.historial_actividades_view, name='historial_actividades'),

    # Anulación con auditoría
    path('anular/<int:actividad_id>/', views.anular_actividad_view, name='anular_actividad'),

    # Nombramiento y sustitución de Maestro de huerto
    path('<int:huerto_id>/maestro/', views.nombrar_maestro_view, name='nombrar_maestro'),
]
