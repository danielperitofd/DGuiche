from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import UserForm
from accounts.models import User
from core.mixins import TenantContextMixin


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


class UserListView(TenantContextMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        queryset = User.objects.select_related("tenant", "guiche")
        if self.request.user.is_global_master:
            return queryset.order_by("tenant__nome", "username")
        return queryset.filter(tenant=self.request.user.tenant).order_by("username")


class UserCreateView(TenantContextMixin, CreateView):
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


class UserUpdateView(TenantContextMixin, UpdateView):
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


class UserDeleteView(TenantContextMixin, DeleteView):
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

