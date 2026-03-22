from django import forms

from guiches.models import Guiche


class GuicheForm(forms.ModelForm):
    class Meta:
        model = Guiche
        fields = ["tenant", "nome", "codigo", "ativo", "situacao"]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop("tenant", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields["tenant"].queryset = self.fields["tenant"].queryset.filter(pk=tenant.pk)
            self.fields["tenant"].initial = tenant
        if user and not user.is_global_master:
            self.fields["tenant"].queryset = self.fields["tenant"].queryset.filter(pk=user.tenant_id)
            self.fields["tenant"].initial = user.tenant
            self.fields["tenant"].disabled = True

