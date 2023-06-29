from django.contrib import admin

# from . import models
from .models import Empresa, Sede, Persona, RegEquipo, Equipo


class SedeAdmin(admin.ModelAdmin):
    fields = ["empresa", "nom_sede"]

    list_display = ["empresa", "nom_sede"]


class EquipoAdmin(admin.ModelAdmin):
    fields = ["eq_tipo", "eq_marca", "eq_serie"]

    list_display = ["eq_serie", "eq_marca", "eq_tipo"]

    list_filter = ["eq_marca", "eq_tipo"]

    search_fields = ["eq_serie"]


class PersonaAdmin(admin.ModelAdmin):
    fields = ["id_tipo", "id_num", "nom_persona"]

    list_display = ("nom_persona", "id_tipo", "id_num")

    list_filter = ["id_tipo"]

    search_fields = ["nom_persona", "id_num"]

class RegEquipoAdmin(admin.ModelAdmin):
    fields = ["sede", "equipo", "portador", "ts_ing", "ts_sal"]

    list_display = ("equipo", "portador", "ts_ing", "ts_sal")

    list_filter = ["sede", "ts_ing", ]

    #search_fields = ["nom_persona", "equipo"]


# Register your models here.

admin.site.register(Empresa)
admin.site.register(Sede, SedeAdmin)
admin.site.register(Persona, PersonaAdmin)
admin.site.register(RegEquipo, RegEquipoAdmin)
admin.site.register(Equipo, EquipoAdmin)
