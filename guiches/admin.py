from django.contrib import admin

from guiches.models import Guiche


@admin.register(Guiche)
class GuicheAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "tenant", "situacao", "ativo")
    list_filter = ("tenant", "ativo", "situacao")
    search_fields = ("codigo", "nome")

