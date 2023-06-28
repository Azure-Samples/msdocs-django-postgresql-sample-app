from django.urls import path
from . import views

# Template tagging
app_name = "ing"

urlpatterns = [
    path("user_login/", views.user_login, name="user_login"),
    path("sedes/", views.SedeListView.as_view(), name="sedes"),
    path("sede/<int:sede_id>/", views.sede, name="sede"),
    path("req_hoy/", views.req_hoy, name="req_hoy"),
    path("crear_req/", views.crear_req, name="crear_req"),
    path("modificar_req/<int:req_id>", views.mod_req, name="mod_req"),
    path("borrar_req/<int:req_id>", views.borrar_req, name="borrar_req"),
    path("search_portador/", views.autocomplete_portador, name="search_portador"),
    path("search_equipo/", views.autocomplete_equipo, name="search_equipo"),
    path("crear_persona/", views.crear_persona, name="crear_persona"),
    path("crear_equipo/", views.crear_equipo, name="crear_equipo"),
    path(
        "registrar_salida_equipo/<int:req_id>/",
        views.registrar_salida_equipo,
        name="registrar_salida_equipo",
    ),
    path('ajax_query_persona/', views.ajax_query_view_persona, name='ajax_query_persona'),
    path('ajax_query_equipo/', views.ajax_query_view_equipo, name='ajax_query_equipo'),
]
