from django.db import models
from django.utils import timezone

from core.utils import compose_import_key, normalize_name


class Atendimento(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO = "aguardando", "Aguardando"
        CHAMADO = "chamado", "Chamado"
        ATENDIDO = "atendido", "Atendido"
        AUSENTE = "ausente", "Ausente"

    class Classificacao(models.TextChoices):
        NO_HORARIO = "no_horario", "No horario"
        ATRASADO = "atrasado", "Atrasado"
        ENCAIXE = "encaixe", "Encaixe"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="atendimentos")
    nome = models.CharField(max_length=180)
    nome_normalizado = models.CharField(max_length=180, editable=False)
    documento = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=80, blank=True)
    tipo_servico = models.CharField(max_length=120, blank=True)
    data_referencia = models.DateField(default=timezone.localdate)
    hora_agendada = models.TimeField(null=True, blank=True)
    hora_chegada = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AGUARDANDO)
    classificacao_fila = models.CharField(max_length=20, choices=Classificacao.choices, default=Classificacao.NO_HORARIO)
    guiche = models.ForeignKey("guiches.Guiche", on_delete=models.PROTECT, related_name="atendimentos", null=True, blank=True)
    observacao = models.TextField(blank=True)
    origem_importacao = models.ForeignKey("importacao.ImportacaoPlanilha", on_delete=models.SET_NULL, related_name="atendimentos", null=True, blank=True)
    import_key = models.CharField(max_length=255, editable=False)
    chamado_em = models.DateTimeField(null=True, blank=True)
    atendido_em = models.DateTimeField(null=True, blank=True)
    ausente_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["hora_agendada", "hora_chegada", "nome"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "import_key"], name="uniq_atendimento_import_key_por_tenant"),
        ]

    def save(self, *args, **kwargs):
        self.nome_normalizado = normalize_name(self.nome)
        self.import_key = compose_import_key(self.nome, self.hora_agendada, self.data_referencia)
        super().save(*args, **kwargs)

    @property
    def servico_visual(self):
        nome = normalize_name(self.tipo_servico)
        if "transfer" in nome:
            return {"label": "Servico prioritario", "badge": "text-bg-danger"}
        if "revisa" in nome or "alist" in nome:
            return {"label": "Servico preferencial", "badge": "text-bg-success"}
        if "certid" in nome:
            return {"label": "Servico simples", "badge": "text-bg-secondary"}
        if nome:
            return {"label": "Servico padrao", "badge": "text-bg-primary"}
        return {"label": "Sem servico", "badge": "text-bg-light"}

    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"


class HistoricoAtendimento(models.Model):
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE, related_name="historicos")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, related_name="historicos_atendimento")
    usuario = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=80)
    descricao = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.acao} - {self.atendimento.nome}"
