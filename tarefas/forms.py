from django import forms
from liderancas.models import Regiao, Cidade
from usuarios.models import Usuario
from .models import Tarefa, Comentario


class TarefaForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        required=False,
        label='Região',
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = Tarefa
        fields = [
            'titulo', 'descricao', 'tipo', 'prioridade',
            'responsavel', 'participantes',
            'regiao', 'cidade', 'prazo', 'observacoes',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'prioridade': forms.Select(attrs={'class': 'form-input'}),
            'responsavel': forms.Select(attrs={'class': 'form-input'}),
            'participantes': forms.SelectMultiple(attrs={'class': 'form-input', 'size': 5}),
            'cidade': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'prazo': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

    field_order = [
        'titulo', 'descricao', 'tipo', 'prioridade',
        'responsavel', 'participantes',
        'regiao', 'cidade', 'prazo', 'observacoes',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios_sistema = Usuario.objects.exclude(
            vinculo__in=['coordenador', 'cabo', 'replicador']
        ).order_by('first_name')
        self.fields['responsavel'].queryset = usuarios_sistema
        self.fields['participantes'].queryset = usuarios_sistema

        if self.instance.pk and self.instance.cidade_id:
            self.fields['regiao'].initial = self.instance.cidade.regiao_id
            self.fields['cidade'].queryset = Cidade.objects.filter(
                regiao=self.instance.cidade.regiao
            ).order_by('nome')
        else:
            regiao_id = self.data.get('regiao') if self.data else None
            if regiao_id:
                try:
                    self.fields['cidade'].queryset = Cidade.objects.filter(
                        regiao_id=int(regiao_id)
                    ).order_by('nome')
                except (ValueError, TypeError):
                    self.fields['cidade'].queryset = Cidade.objects.none()
            else:
                self.fields['cidade'].queryset = Cidade.objects.none()


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Escreva um comentário...',
            }),
        }
