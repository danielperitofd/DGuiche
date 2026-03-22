from django.contrib import admin

from atendimento.models import Atendimento, HistoricoAtendimento


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "documento", "tipo_servico", "tenant", "data_referencia", "hora_agendada", "status", "classificacao_fila", "guiche")
    list_filter = ("tenant", "status", "classificacao_fila", "guiche")
    search_fields = ("nome", "documento", "email", "telefone", "observacao")


@admin.register(HistoricoAtendimento)
class HistoricoAtendimentoAdmin(admin.ModelAdmin):
    list_display = ("atendimento", "acao", "usuario", "criado_em")
    list_filter = ("tenant", "acao")
