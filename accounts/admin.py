from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "tenant", "guiche", "is_global_master", "ativo")
    list_filter = ("is_global_master", "ativo", "tenant")
    fieldsets = UserAdmin.fieldsets + (
        ("Contexto SaaS", {"fields": ("tenant", "cargo", "telefone", "ativo", "is_global_master", "guiche")}),
    )

