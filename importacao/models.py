from django.db import models
from django.utils import timezone


class ImportacaoPlanilha(models.Model):
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="importacoes")
    arquivo = models.FileField(upload_to="importacoes/%Y/%m/%d/")
    data_referencia = models.DateField(default=timezone.localdate)
    importado_por = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    inseridos = models.PositiveIntegerField(default=0)
    atualizados = models.PositiveIntegerField(default=0)
    preservados = models.PositiveIntegerField(default=0)
    ignorados = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Importação {self.tenant} - {self.criado_em:%d/%m/%Y %H:%M}"


class RegistroImportado(models.Model):
    class Resultado(models.TextChoices):
        INSERIDO = "inserido", "Inserido"
        ATUALIZADO = "atualizado", "Atualizado"
        PRESERVADO = "preservado", "Preservado"
        IGNORADO = "ignorado", "Ignorado"

    importacao = models.ForeignKey(ImportacaoPlanilha, on_delete=models.CASCADE, related_name="registros")
    linha = models.PositiveIntegerField()
    nome = models.CharField(max_length=180)
    hora = models.TimeField(null=True, blank=True)
    status_origem = models.CharField(max_length=80, blank=True)
    guiche_origem = models.CharField(max_length=80, blank=True)
    observacao = models.TextField(blank=True)
    resultado = models.CharField(max_length=20, choices=Resultado.choices)
    detalhe = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["linha"]

