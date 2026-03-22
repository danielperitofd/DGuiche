from django.contrib import admin

from tenants.models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("nome", "codigo", "slug")

