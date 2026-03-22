from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import UserForm
from accounts.models import User
from core.mixins import TenantContextMixin, TenantManagementRequiredMixin


def login_view(request):
    from django.contrib.auth import authenticate, login
    from accounts.forms import LoginForm

    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            return redirect("dashboard:home")
        messages.error(request, "Credenciais invalidas.")
    return render(request, "accounts/login.html", {"form": form})


class SaaSLogoutView(LogoutView):
    pass


class UserListView(TenantManagementRequiredMixin, TenantContextMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = User.objects.select_related("tenant", "guiche")
        if self.request.user.is_global_master:
            return queryset.order_by("tenant__nome", "username")
        return queryset.filter(tenant=self.request.user.tenant).order_by("username")


class UserCreateView(TenantManagementRequiredMixin, TenantContextMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.get_tenant()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        if not self.request.user.is_global_master:
            form.instance.tenant = self.request.user.tenant
        messages.success(self.request, "Usuario criado com sucesso.")
        return super().form_valid(form)


class UserUpdateView(TenantManagementRequiredMixin, TenantContextMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:list")

    def get_queryset(self):
        queryset = User.objects.select_related("tenant", "guiche")
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
        messages.success(self.request, "Usuario atualizado com sucesso.")
        return super().form_valid(form)


class UserDeleteView(TenantManagementRequiredMixin, TenantContextMixin, DeleteView):
    model = User
    template_name = "components/confirm_delete.html"
    success_url = reverse_lazy("accounts:list")

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.user.is_global_master:
            return queryset.exclude(pk=self.request.user.pk)
        return queryset.filter(tenant=self.request.user.tenant).exclude(pk=self.request.user.pk)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Usuario removido com sucesso.")
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Excluir usuario"
        context["cancel_url"] = reverse_lazy("accounts:list")
        return context


@login_required
def start_common_preview(request):
    user = request.user
    if request.method == "POST" and user.is_staff and not user.is_global_master and user.tenant_id:
        request.session["staff_preview_mode"] = "common"
        guiche_id = request.POST.get("guiche_id")
        guiche = user.tenant.guiches.filter(pk=guiche_id).first() if guiche_id else None
        if guiche:
            request.session["staff_preview_guiche_id"] = guiche.pk
        elif user.guiche_id:
            request.session["staff_preview_guiche_id"] = user.guiche_id
        else:
            request.session.pop("staff_preview_guiche_id", None)
        messages.info(request, "Pre-visualizacao de operador ativada.")
    return redirect(request.POST.get("next") or "dashboard:home")


@login_required
def stop_common_preview(request):
    if request.method == "POST":
        request.session.pop("staff_preview_mode", None)
        request.session.pop("staff_preview_guiche_id", None)
        messages.info(request, "Pre-visualizacao de operador desativada.")
    return redirect(request.POST.get("next") or "dashboard:home")

