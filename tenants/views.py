from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import GlobalMasterRequiredMixin
from tenants.forms import TenantForm
from tenants.models import Tenant


class TenantListView(GlobalMasterRequiredMixin, ListView):
    model = Tenant
    template_name = "tenants/tenant_list.html"
    context_object_name = "tenants"


class TenantCreateView(GlobalMasterRequiredMixin, CreateView):
    model = Tenant
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"
    success_url = reverse_lazy("tenants:list")

    def form_valid(self, form):
        messages.success(self.request, "Tenant criada com sucesso.")
        return super().form_valid(form)


class TenantUpdateView(GlobalMasterRequiredMixin, UpdateView):
    model = Tenant
    form_class = TenantForm
    template_name = "tenants/tenant_form.html"
    success_url = reverse_lazy("tenants:list")

    def form_valid(self, form):
        messages.success(self.request, "Tenant atualizada com sucesso.")
        return super().form_valid(form)


class TenantDeleteView(GlobalMasterRequiredMixin, DeleteView):
    model = Tenant
    template_name = "components/confirm_delete.html"
    success_url = reverse_lazy("tenants:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Tenant removida com sucesso.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir tenant"
        context["cancel_url"] = reverse_lazy("tenants:list")
        return context
