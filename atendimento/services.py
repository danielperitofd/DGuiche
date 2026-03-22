from datetime import datetime, timedelta

from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone

from atendimento.models import Atendimento, HistoricoAtendimento
from guiches.models import Guiche


def classificar_chegada(atendimento):
    if atendimento.classificacao_fila == Atendimento.Classificacao.ENCAIXE:
        return Atendimento.Classificacao.ENCAIXE
    if not atendimento.hora_chegada or not atendimento.hora_agendada:
        return Atendimento.Classificacao.NO_HORARIO
    base = datetime.combine(timezone.localdate(), atendimento.hora_agendada)
    chegada = datetime.combine(timezone.localdate(), atendimento.hora_chegada)
    if chegada <= base + timedelta(minutes=15):
        return Atendimento.Classificacao.NO_HORARIO
    return Atendimento.Classificacao.ATRASADO


def registrar_historico(atendimento, usuario, acao, descricao=""):
    HistoricoAtendimento.objects.create(
        atendimento=atendimento,
        tenant=atendimento.tenant,
        usuario=usuario,
        acao=acao,
        descricao=descricao,
    )


def registrar_chegada(atendimento, hora_chegada, usuario):
    atendimento.hora_chegada = hora_chegada
    atendimento.classificacao_fila = classificar_chegada(atendimento)
    atendimento.save(update_fields=["hora_chegada", "classificacao_fila", "atualizado_em"])
    registrar_historico(atendimento, usuario, "checkin", f"Chegada registrada às {hora_chegada}.")
    return atendimento


def fila_inteligente_queryset(tenant):
    return (
        Atendimento.objects.filter(tenant=tenant, status=Atendimento.Status.AGUARDANDO)
        .filter(Q(hora_chegada__isnull=False) | Q(classificacao_fila=Atendimento.Classificacao.ENCAIXE))
        .annotate(
            prioridade=Case(
                When(classificacao_fila=Atendimento.Classificacao.NO_HORARIO, then=Value(0)),
                When(classificacao_fila=Atendimento.Classificacao.ATRASADO, then=Value(1)),
                When(classificacao_fila=Atendimento.Classificacao.ENCAIXE, then=Value(2)),
                default=Value(9),
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "hora_agendada", "hora_chegada", "criado_em")
    )


def chamar_proximo(usuario):
    guiche = usuario.guiche
    if not guiche:
        raise ValueError("Usuário sem guichê vinculado.")
    guiche.situacao = Guiche.Situacao.CHAMANDO
    guiche.save(update_fields=["situacao", "atualizado_em"])
    atendimento = fila_inteligente_queryset(usuario.tenant).first()
    if not atendimento:
        return None
    atendimento.guiche = guiche
    atendimento.status = Atendimento.Status.CHAMADO
    atendimento.chamado_em = timezone.now()
    atendimento.save(update_fields=["guiche", "status", "chamado_em", "atualizado_em"])
    registrar_historico(atendimento, usuario, "chamar", f"Chamado para {guiche}.")
    return atendimento


def concluir_atendimento(atendimento, usuario):
    if not atendimento.guiche_id:
        raise ValueError("Não é possível concluir um atendimento sem guichê vinculado.")
    atendimento.status = Atendimento.Status.ATENDIDO
    atendimento.atendido_em = timezone.now()
    atendimento.save(update_fields=["status", "atendido_em", "atualizado_em"])
    atendimento.guiche.situacao = Guiche.Situacao.LIVRE
    atendimento.guiche.save(update_fields=["situacao", "atualizado_em"])
    registrar_historico(atendimento, usuario, "concluir", "Atendimento concluído.")
    return atendimento


def marcar_ausente(atendimento, usuario):
    atendimento.status = Atendimento.Status.AUSENTE
    atendimento.ausente_em = timezone.now()
    atendimento.save(update_fields=["status", "ausente_em", "atualizado_em"])
    if atendimento.guiche_id:
        atendimento.guiche.situacao = Guiche.Situacao.LIVRE
        atendimento.guiche.save(update_fields=["situacao", "atualizado_em"])
    registrar_historico(atendimento, usuario, "ausente", "Atendimento marcado como ausente.")
    return atendimento

