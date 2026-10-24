from django.urls import path

from . import views

app_name = "comunidades"

urlpatterns = [
    path("", views.mi_comunidad, name="mi_comunidad"),
    path("crear/", views.crear, name="crear"),
    path("unirse/", views.unirse, name="unirse"),
    path("editar/", views.editar, name="editar"),
    path("huerto/", views.mi_huerto, name="mi_huerto"),
    path("huerto/configurar/", views.configurar, name="configurar_huerto"),
    path("huerto/plantas/elegir/", views.elegir, name="elegir_planta"),
    path("huerto/plantas/<int:seleccion_id>/metodo/", views.cambiar_metodo, name="cambiar_metodo"),
    path("huerto/plantas/<int:seleccion_id>/retirar/", views.retirar, name="retirar_planta"),
]
