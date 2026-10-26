from django.urls import path
from . import views
app_name = "catalogo"
urlpatterns = [
    path("plantas/", views.lista_plantas, name="lista_plantas"),
    path("plantas/<slug:codigo>/", views.detalle_planta, name="detalle_planta"),
    path("guia/", views.guia, name="guia"),
    path("calendario/", views.calendario, name="calendario"),
]
