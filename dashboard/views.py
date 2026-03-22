from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from accounts.forms import LoginForm
from accounts.models import User
from atendimento.models import Atendimento
from atendimento.services import fila_inteligente_queryset
from core.utils import get_staff_preview_state
from guiches.models import Guiche
from importacao.models import ImportacaoPlanilha
from tenants.models import Tenant


class DemoLandingView(TemplateView):
    template_name = "dashboard/demo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = LoginForm()
        context["signup_available"] = Tenant.objects.filter(ativo=True, cadastro_publico_ativo=True).exists()
        return context


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        preview_state = get_staff_preview_state(self.request)

        if user.is_global_master and not preview_state["preview_mode"]:
            context.update(
                {
                    "master_mode": True,
                    "total_tenants": Tenant.objects.count(),
                    "tenants_ativos": Tenant.objects.filter(ativo=True).count(),
                    "total_usuarios": User.objects.count(),
                    "tenants": Tenant.objects.order_by("nome"),
                }
            )
            return context

        tenant = self.request.tenant or user.tenant
        queryset = Atendimento.objects.filter(tenant=tenant)
        fila = fila_inteligente_queryset(tenant)[:8]
        agora_chamando = queryset.filter(status=Atendimento.Status.CHAMADO).select_related("guiche").order_by("-chamado_em").first()

        tempos = []
        for item in queryset.filter(atendido_em__isnull=False, chamado_em__isnull=False):
            tempos.append(item.atendido_em - item.chamado_em)
        media = None
        if tempos:
            media = sum(tempos, timedelta()) / len(tempos)
            total_seconds = int(media.total_seconds())
            media = f"{total_seconds // 60} min"

        context.update(
            {
                "master_mode": False,
                "tenant": tenant,
                "total_importado": queryset.count(),
                "em_atendimento": queryset.filter(status=Atendimento.Status.CHAMADO).count(),
                "chamados": queryset.filter(status=Atendimento.Status.CHAMADO).count(),
                "atendidos": queryset.filter(status=Atendimento.Status.ATENDIDO).count(),
                "guiches_ativos": Guiche.objects.filter(tenant=tenant, ativo=True).count(),
                "tempo_medio": media or "--",
                "fila": fila,
                "agora_chamando": agora_chamando,
                "historico_recente": queryset.select_related("guiche").order_by("-atualizado_em")[:10],
                "guiches": Guiche.objects.filter(tenant=tenant).order_by("codigo"),
                "importacoes": ImportacaoPlanilha.objects.filter(tenant=tenant)[:5],
                "aguardando_checkin": queryset.filter(status=Atendimento.Status.AGUARDANDO, hora_chegada__isnull=True).order_by("hora_agendada")[:8],
                "effective_guiche": preview_state["effective_guiche"],
            }
        )
        return context
