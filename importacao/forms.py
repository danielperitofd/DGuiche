from django import forms

from importacao.models import RegistroImportado


class ImportacaoPlanilhaForm(forms.Form):
    arquivo = forms.FileField(required=False)
    data_referencia = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    temp_file = forms.CharField(required=False, widget=forms.HiddenInput)
    action = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned = super().clean()
        action = cleaned.get("action") or "preview"
        arquivo = cleaned.get("arquivo")
        temp_file = cleaned.get("temp_file")
        data_referencia = cleaned.get("data_referencia")
        if action == "preview" and not arquivo:
            self.add_error("arquivo", "Selecione um arquivo para pre-visualizar.")
        if action == "confirm":
            if not temp_file:
                raise forms.ValidationError("Arquivo temporario nao encontrado. Reenvie a planilha.")
            if not data_referencia:
                self.add_error("data_referencia", "Informe a data de referencia para concluir a importacao.")
        return cleaned


class ImportacaoDetailFilterForm(forms.Form):
    nome = forms.CharField(required=False)
    resultado = forms.ChoiceField(required=False, choices=[("", "Todos")] + list(RegistroImportado.Resultado.choices))
    linha = forms.IntegerField(required=False, min_value=1)
