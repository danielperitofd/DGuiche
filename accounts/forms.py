from django import forms

from accounts.models import User
from tenants.models import Tenant


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={"placeholder": "Seu usuário", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Sua senha", "autocomplete": "current-password"}),
    )


class PublicSignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Crie uma senha", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmar senha",
        widget=forms.PasswordInput(attrs={"placeholder": "Repita a senha", "autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["tenant", "first_name", "last_name", "username", "email", "telefone"]
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "username": "Usuário",
            "email": "E-mail",
            "telefone": "Telefone",
            "tenant": "Tenant",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Seu nome"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Seu sobrenome"}),
            "username": forms.TextInput(attrs={"placeholder": "Escolha um usuário", "autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"placeholder": "voce@empresa.com", "autocomplete": "email"}),
            "telefone": forms.TextInput(attrs={"placeholder": "(00) 00000-0000", "autocomplete": "tel"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tenant"].queryset = Tenant.objects.filter(ativo=True, cadastro_publico_ativo=True).order_by("nome")

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        tenant = cleaned.get("tenant")
        if tenant and (not tenant.ativo or not tenant.cadastro_publico_ativo):
            self.add_error("tenant", "O cadastro público não está disponível para esta tenant.")
        if not password1:
            self.add_error("password1", "Informe uma senha.")
        if password1 != password2:
            self.add_error("password2", "As senhas não conferem.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = False
        user.is_superuser = False
        user.is_global_master = False
        user.ativo = True
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


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
