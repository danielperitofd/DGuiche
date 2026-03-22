from django import forms

from atendimento.models import Atendimento
from guiches.models import Guiche


class AtendimentoFilterForm(forms.Form):
    nome = forms.CharField(required=False, label="Nome")
    status = forms.ChoiceField(required=False, choices=[("", "Todos")] + list(Atendimento.Status.choices))
    guiche = forms.ModelChoiceField(required=False, queryset=Guiche.objects.none())
    data_inicial = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    data_final = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop("tenant", None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields["guiche"].queryset = tenant.guiches.all()


class CheckInForm(forms.Form):
    hora_chegada = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}), label="Hora de chegada")


class EncaixeForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ["nome", "hora_chegada", "observacao", "guiche"]
        widgets = {
            "hora_chegada": forms.TimeInput(attrs={"type": "time"}),
            "observacao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop("tenant", None)
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields["guiche"].queryset = tenant.guiches.filter(ativo=True)

