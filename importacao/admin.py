from django.contrib import admin

from importacao.models import ImportacaoPlanilha, RegistroImportado


@admin.register(ImportacaoPlanilha)
class ImportacaoPlanilhaAdmin(admin.ModelAdmin):
    list_display = ("tenant", "data_referencia", "importado_por", "inseridos", "atualizados", "preservados", "ignorados", "criado_em")
    list_filter = ("tenant", "data_referencia")


@admin.register(RegistroImportado)
class RegistroImportadoAdmin(admin.ModelAdmin):
    list_display = ("importacao", "linha", "nome", "resultado", "detalhe")
    list_filter = ("resultado",)

