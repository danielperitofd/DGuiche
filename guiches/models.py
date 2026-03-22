from django.db import models


class Guiche(models.Model):
    class Situacao(models.TextChoices):
        LIVRE = "livre", "Livre"
        CHAMANDO = "chamando", "Chamando"
        EM_ATENDIMENTO = "em_atendimento", "Em atendimento"
        INATIVO = "inativo", "Inativo"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="guiches")
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=30)
    ativo = models.BooleanField(default=True)
    situacao = models.CharField(max_length=20, choices=Situacao.choices, default=Situacao.LIVRE)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["codigo", "nome"]
        unique_together = ("tenant", "codigo")

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

