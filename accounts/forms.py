from django import forms

from accounts.models import User
from tenants.models import Tenant


class LoginForm(forms.Form):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label="Confirmar senha", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "cargo",
            "telefone",
            "tenant",
            "guiche",
            "ativo",
            "is_staff",
        ]

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop("tenant", None)
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["password1"].help_text = "Preencha apenas se quiser alterar a senha."
        if user and not user.is_global_master:
            self.fields["tenant"].queryset = Tenant.objects.filter(pk=user.tenant_id)
            self.fields["tenant"].initial = user.tenant
            self.fields["tenant"].disabled = True
            self.fields["is_staff"].initial = False
        if tenant:
            self.fields["tenant"].queryset = Tenant.objects.filter(pk=tenant.pk)
            self.fields["tenant"].initial = tenant
        if tenant:
            self.fields["guiche"].queryset = tenant.guiches.all()
        elif user and not user.is_global_master and user.tenant_id:
            self.fields["guiche"].queryset = user.tenant.guiches.all()

    def clean(self):
        cleaned = super().clean()
        tenant = cleaned.get("tenant")
        guiche = cleaned.get("guiche")
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if guiche and tenant and guiche.tenant_id != tenant.id:
            self.add_error("guiche", "O guiche precisa pertencer a mesma tenant do usuario.")
        if self.instance.pk:
            if password1 or password2:
                if password1 != password2:
                    self.add_error("password2", "As senhas nao conferem.")
        else:
            if not password1:
                self.add_error("password1", "Informe a senha do novo usuario.")
            if password1 != password2:
                self.add_error("password2", "As senhas nao conferem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
