from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, View

from atendimento.forms import AtendimentoFilterForm, CheckInForm, EncaixeForm
from atendimento.models import Atendimento
from atendimento.services import chamar_proximo, concluir_atendimento, marcar_ausente, registrar_chegada


class AtendimentoListView(LoginRequiredMixin, ListView):
    model = Atendimento
    template_name = "atendimento/atendimento_list.html"
    context_object_name = "atendimentos"
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.tenant or self.request.user.tenant
        queryset = Atendimento.objects.select_related("tenant", "guiche", "origem_importacao").filter(tenant=tenant)
        form = self.filter_form
        if form.is_valid():
            nome = form.cleaned_data.get("nome")
            status = form.cleaned_data.get("status")
            guiche = form.cleaned_data.get("guiche")
            data_inicial = form.cleaned_data.get("data_inicial")
            data_final = form.cleaned_data.get("data_final")
            if nome:
                queryset = queryset.filter(nome__icontains=nome)
            if status:
                queryset = queryset.filter(status=status)
            if guiche:
                queryset = queryset.filter(guiche=guiche)
            if data_inicial:
                queryset = queryset.filter(data_referencia__gte=data_inicial)
            if data_final:
                queryset = queryset.filter(data_referencia__lte=data_final)
        return queryset.order_by("status", "hora_agendada", "nome")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context

    def dispatch(self, request, *args, **kwargs):
        tenant = request.tenant or request.user.tenant
        self.filter_form = AtendimentoFilterForm(request.GET or None, tenant=tenant)
        return super().dispatch(request, *args, **kwargs)


class CheckInView(LoginRequiredMixin, View):
    def post(self, request, pk):
        atendimento = get_object_or_404(Atendimento, pk=pk, tenant=request.user.tenant)
        form = CheckInForm(request.POST)
        if form.is_valid():
            registrar_chegada(atendimento, form.cleaned_data["hora_chegada"], request.user)
            messages.success(request, f"Chegada registrada para {atendimento.nome}.")
        else:
            messages.error(request, "Nao foi possivel registrar a chegada.")
        return redirect("dashboard:home")


class EncaixeCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    form_class = EncaixeForm
    template_name = "atendimento/encaixe_form.html"
    success_url = reverse_lazy("dashboard:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.user.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.user.tenant
        form.instance.data_referencia = timezone.localdate()
        form.instance.classificacao_fila = Atendimento.Classificacao.ENCAIXE
        form.instance.status = Atendimento.Status.AGUARDANDO
        messages.success(self.request, "Encaixe criado com sucesso.")
        return super().form_valid(form)


class ChamarProximoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            atendimento = chamar_proximo(request.user)
            if atendimento:
                messages.success(request, f"Agora chamando {atendimento.nome}.")
            else:
                messages.info(request, "Nao ha pessoas elegiveis na fila inteligente.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("dashboard:home")


class ConcluirAtendimentoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        atendimento = get_object_or_404(Atendimento, pk=pk, tenant=request.user.tenant)
        try:
            concluir_atendimento(atendimento, request.user)
            messages.success(request, f"Atendimento concluido para {atendimento.nome}.")
        except ValueError as exc:
            messages.error(request, str(exc))
        return redirect("dashboard:home")


class MarcarAusenteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        atendimento = get_object_or_404(Atendimento, pk=pk, tenant=request.user.tenant)
        marcar_ausente(atendimento, request.user)
        messages.warning(request, f"{atendimento.nome} marcado como ausente.")
        return redirect("dashboard:home")
