from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import TenantContextMixin, TenantManagementRequiredMixin
from guiches.forms import GuicheForm
from guiches.models import Guiche


class GuicheListView(TenantManagementRequiredMixin, TenantContextMixin, ListView):
    model = Guiche
    template_name = "guiches/guiche_list.html"
    context_object_name = "guiches"

    def get_queryset(self):
        queryset = Guiche.objects.select_related("tenant")
        if self.request.user.is_global_master:
            return queryset.order_by("tenant__nome", "codigo")
        return queryset.filter(tenant=self.request.user.tenant).order_by("codigo")


class GuicheCreateView(TenantManagementRequiredMixin, TenantContextMixin, CreateView):
    model = Guiche
    form_class = GuicheForm
    template_name = "guiches/guiche_form.html"
    success_url = reverse_lazy("guiches:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.get_tenant()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_global_master:
            form.instance.tenant = self.request.user.tenant
        messages.success(self.request, "Guiche criado com sucesso.")
        return super().form_valid(form)


class GuicheUpdateView(TenantManagementRequiredMixin, TenantContextMixin, UpdateView):
    model = Guiche
    form_class = GuicheForm
    template_name = "guiches/guiche_form.html"
    success_url = reverse_lazy("guiches:list")

    def get_queryset(self):
        queryset = Guiche.objects.select_related("tenant")
        if self.request.user.is_global_master:
            return queryset
        return queryset.filter(tenant=self.request.user.tenant)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.get_tenant()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_global_master:
            form.instance.tenant = self.request.user.tenant
        messages.success(self.request, "Guiche atualizado com sucesso.")
        return super().form_valid(form)


class GuicheDeleteView(TenantManagementRequiredMixin, TenantContextMixin, DeleteView):
    model = Guiche
    template_name = "components/confirm_delete.html"
    success_url = reverse_lazy("guiches:list")

    def get_queryset(self):
        queryset = Guiche.objects.all()
        if self.request.user.is_global_master:
            return queryset
        return queryset.filter(tenant=self.request.user.tenant)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Guiche removido com sucesso.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir guiche"
        context["cancel_url"] = reverse_lazy("guiches:list")
        return context

