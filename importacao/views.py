from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View

from importacao.forms import ImportacaoDetailFilterForm, ImportacaoPlanilhaForm
from importacao.models import ImportacaoPlanilha
from importacao.services import create_import_from_temp, preview_import_file, reprocessar_importacao, save_temp_upload


class ImportacaoListView(LoginRequiredMixin, ListView):
    model = ImportacaoPlanilha
    template_name = "importacao/importacao_list.html"
    context_object_name = "importacoes"

    def get_queryset(self):
        return ImportacaoPlanilha.objects.filter(tenant=self.request.user.tenant).order_by("-criado_em")


class ImportacaoCreateView(LoginRequiredMixin, View):
    template_name = "importacao/importacao_form.html"
    success_url = reverse_lazy("importacao:list")

    def get(self, request):
        form = ImportacaoPlanilhaForm(initial={"action": "preview"})
        return render(request, self.template_name, {"form": form, "preview": None})

    def post(self, request):
        form = ImportacaoPlanilhaForm(request.POST, request.FILES)
        preview = None
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "preview": preview})

        action = form.cleaned_data.get("action") or "preview"
        if action == "preview":
            try:
                temp_file = save_temp_upload(form.cleaned_data["arquivo"])
                preview = preview_import_file(temp_file)
                form = ImportacaoPlanilhaForm(
                    initial={
                        "temp_file": temp_file,
                        "data_referencia": preview["metadata"].get("agenda_data"),
                        "action": "confirm",
                    }
                )
                return render(request, self.template_name, {"form": form, "preview": preview})
            except Exception as exc:
                messages.error(request, f"Falha ao analisar a planilha: {exc}")
                form = ImportacaoPlanilhaForm(initial={"action": "preview"})
                return render(request, self.template_name, {"form": form, "preview": None})

        try:
            importacao = create_import_from_temp(
                temp_file=form.cleaned_data["temp_file"],
                tenant=request.user.tenant,
                user=request.user,
                data_referencia=form.cleaned_data["data_referencia"],
            )
            messages.success(request, f"Planilha importada com sucesso. Inseridos: {importacao.inseridos}, atualizados: {importacao.atualizados}, preservados: {importacao.preservados}, ignorados: {importacao.ignorados}.")
            return redirect("importacao:detail", pk=importacao.pk)
        except Exception as exc:
            messages.error(request, f"Falha ao concluir a importacao: {exc}")
            return render(request, self.template_name, {"form": form, "preview": None})


class ImportacaoDetailView(LoginRequiredMixin, DetailView):
    model = ImportacaoPlanilha
    template_name = "importacao/importacao_detail.html"
    context_object_name = "importacao"

    def get_queryset(self):
        return ImportacaoPlanilha.objects.filter(tenant=self.request.user.tenant).prefetch_related("registros")

    def dispatch(self, request, *args, **kwargs):
        self.filter_form = ImportacaoDetailFilterForm(request.GET or None)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registros = self.object.registros.all()
        if self.filter_form.is_valid():
            nome = self.filter_form.cleaned_data.get("nome")
            resultado = self.filter_form.cleaned_data.get("resultado")
            linha = self.filter_form.cleaned_data.get("linha")
            if nome:
                registros = registros.filter(nome__icontains=nome)
            if resultado:
                registros = registros.filter(resultado=resultado)
            if linha:
                registros = registros.filter(linha=linha)
        context["filter_form"] = self.filter_form
        context["registros"] = registros
        context["resumo_resultados"] = self.object.registros.values("resultado").annotate(total=Count("id")).order_by("resultado")
        return context


class ImportacaoReprocessView(LoginRequiredMixin, View):
    def post(self, request, pk):
        origem = ImportacaoPlanilha.objects.filter(tenant=request.user.tenant).get(pk=pk)
        nova = reprocessar_importacao(origem, request.user)
        messages.success(request, f"Importacao reprocessada. Nova execucao #{nova.pk} criada com inseridos={nova.inseridos}, atualizados={nova.atualizados}, preservados={nova.preservados}, ignorados={nova.ignorados}.")
        return redirect("importacao:detail", pk=nova.pk)
