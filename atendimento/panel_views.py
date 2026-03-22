from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from atendimento.models import Atendimento


class ChamadaPainelView(LoginRequiredMixin, TemplateView):
    template_name = "atendimento/painel_chamada.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Atendimento.objects.filter(tenant=self.request.user.tenant).select_related("guiche")
        atual = queryset.filter(status=Atendimento.Status.CHAMADO).order_by("-chamado_em").first()
        recentes = queryset.filter(status=Atendimento.Status.CHAMADO).order_by("-chamado_em")[:6]
        context.update({
            "atual": atual,
            "recentes": recentes,
            "tenant": self.request.user.tenant,
        })
        return context
