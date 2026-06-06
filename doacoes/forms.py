from django import forms
from .models import Doacao, ComissaoResgate
from liderancas.models import Regiao, Cidade


class DoacaoForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all(),
        label='Região',
        required=False,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = Doacao
        fields = [
            'doador_nome', 'doador_cpf', 'doador_telefone', 'doador_email',
            'valor', 'data', 'forma_pagamento', 'status',
            'comprovante', 'apoiador', 'coordenador',
            'cidade', 'observacoes',
        ]
        widgets = {
            'doador_nome': forms.TextInput(attrs={'class': 'form-input'}),
            'doador_cpf': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'}),
            'doador_telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'doador_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'valor': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'data': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'forma_pagamento': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'comprovante': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'apoiador': forms.Select(attrs={'class': 'form-input'}),
            'coordenador': forms.Select(attrs={'class': 'form-input'}),
            'cidade': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']
        if self.instance.pk and self.instance.regiao:
            self.fields['regiao'].initial = self.instance.regiao
            self.fields['cidade'].queryset = Cidade.objects.filter(regiao=self.instance.regiao)
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()


class ComissaoResgateForm(forms.ModelForm):
    class Meta:
        model = ComissaoResgate
        fields = ['tipo', 'coordenador', 'apoiador', 'valor', 'status', 'nota_fiscal', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'coordenador': forms.Select(attrs={'class': 'form-input'}),
            'apoiador': forms.Select(attrs={'class': 'form-input'}),
            'valor': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'nota_fiscal': forms.ClearableFileInput(attrs={'class': 'form-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
