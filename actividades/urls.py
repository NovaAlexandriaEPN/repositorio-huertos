"""Rutas del módulo actividades. Todas son privadas (LoginRequiredMiddleware)."""
from django.urls import path

from . import views

app_name = "actividades"

urlpatterns = [
    path("", views.mi_huerto, name="mi_huerto"),
    path("<int:huerto_id>/", views.huerto_virtual, name="inicio_huerto_virtual"),
    path("<int:huerto_id>/registrar/", views.registrar_actividad, name="registrar_actividad"),
    path("<int:huerto_id>/historial/", views.historial, name="historial_actividades"),
    path("<int:huerto_id>/maestro/", views.nombrar_maestro, name="nombrar_maestro"),
    path("actividad/<int:actividad_id>/anular/", views.anular_actividad, name="anular_actividad"),
]
