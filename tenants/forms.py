from django import forms

from tenants.models import Tenant


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ["nome", "slug", "codigo", "descricao", "ativo", "cadastro_publico_ativo"]
        widgets = {"descricao": forms.Textarea(attrs={"rows": 3})}
