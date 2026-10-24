from django.urls import path

from . import views

app_name = "comunidades"

urlpatterns = [
    path("", views.mi_comunidad, name="mi_comunidad"),
    path("crear/", views.crear, name="crear"),
    path("unirse/", views.unirse, name="unirse"),
    path("editar/", views.editar, name="editar"),
]
