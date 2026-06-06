from django import forms
from liderancas.models import Apoiador, Cidade, Regiao, Voluntario
from doacoes.models import Doacao
from usuarios.models import Usuario


class ApoiadorPWAForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        label='Região',
        widget=forms.Select(attrs={'class': 'pwa-input', 'id': 'id_regiao'}),
    )
    tipo = forms.ChoiceField(
        choices=[c for c in Apoiador.TIPO_CHOICES if c[0] != 'pwa'],
        widget=forms.RadioSelect(attrs={'class': 'pwa-radio'}),
    )

    class Meta:
        model = Apoiador
        fields = ['nome', 'tipo', 'cidade', 'telefone', 'instagram', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': 'Nome completo'}),
            'cidade': forms.Select(attrs={'class': 'pwa-input', 'id': 'id_cidade'}),
            'telefone': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': '(00) 00000-0000'}),
            'instagram': forms.TextInput(attrs={'class': 'pwa-input pwa-input-at', 'placeholder': 'usuario'}),
            'observacoes': forms.Textarea(attrs={'class': 'pwa-input', 'placeholder': 'Observações...', 'rows': 3}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Se POST, popular cidades pela região enviada
        data = args[0] if args else None
        if data and data.get('regiao'):
            try:
                regiao_id = int(data.get('regiao'))
                self.fields['cidade'].queryset = Cidade.objects.filter(
                    regiao_id=regiao_id
                ).order_by('nome')
            except (ValueError, TypeError):
                self.fields['cidade'].queryset = Cidade.objects.none()
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()

    field_order = ['nome', 'tipo', 'regiao', 'cidade', 'telefone', 'instagram', 'observacoes']


class ReplicadorForm(forms.Form):
    nome = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': 'Nome completo'}),
    )
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        label='Região',
        widget=forms.Select(attrs={'class': 'pwa-input', 'id': 'id_regiao'}),
    )
    cidade = forms.ModelChoiceField(
        queryset=Cidade.objects.none(),
        label='Cidade',
        widget=forms.Select(attrs={'class': 'pwa-input', 'id': 'id_cidade'}),
    )
    telefone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': '(00) 00000-0000'}),
    )
    instagram = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'pwa-input pwa-input-at', 'placeholder': 'usuario'}),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        data = args[0] if args else None
        if data and data.get('regiao'):
            try:
                regiao_id = int(data.get('regiao'))
                self.fields['cidade'].queryset = Cidade.objects.filter(
                    regiao_id=regiao_id
                ).order_by('nome')
            except (ValueError, TypeError):
                self.fields['cidade'].queryset = Cidade.objects.none()
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()

    def save(self, convidado_por):
        dados = self.cleaned_data
        nome_parts = dados['nome'].strip().split(' ', 1)
        first_name = nome_parts[0]
        last_name = nome_parts[1] if len(nome_parts) > 1 else ''

        # Gerar username único a partir do telefone ou nome
        telefone = dados.get('telefone', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if telefone:
            username = telefone
            n = 1
            while Usuario.objects.filter(username=username).exists():
                username = f'{telefone}_{n}'
                n += 1
        else:
            base = dados['nome'].lower().replace(' ', '.')
            username = base
            n = 1
            while Usuario.objects.filter(username=username).exists():
                username = f'{base}{n}'
                n += 1

        # Senha: últimos 4 dígitos do telefone + primeiro nome minúsculo
        if len(telefone) >= 4:
            senha = telefone[-4:] + first_name.lower()
        else:
            senha = first_name.lower() + '2026'

        user = Usuario.objects.create_user(
            username=username,
            password=senha,
            first_name=first_name,
            last_name=last_name,
            telefone=dados.get('telefone', ''),
            instagram=dados.get('instagram', ''),
            cidade=dados['cidade'],
            vinculo='replicador',
            perfil='operador',
            convidado_por=convidado_por,
        )
        return user, senha


class VoluntarioPWAForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        label='Região',
        widget=forms.Select(attrs={'class': 'pwa-input', 'id': 'id_regiao'}),
    )
    disponibilidades = forms.MultipleChoiceField(
        choices=Voluntario.DISPONIBILIDADE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'pwa-check'}),
        label='Disponibilidade',
    )

    class Meta:
        model = Voluntario
        fields = ['nome', 'telefone', 'cidade', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': 'Nome completo'}),
            'telefone': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': '(00) 00000-0000'}),
            'cidade': forms.Select(attrs={'class': 'pwa-input', 'id': 'id_cidade'}),
            'observacoes': forms.Textarea(attrs={'class': 'pwa-input', 'placeholder': 'Observações...', 'rows': 3}),
        }

    field_order = ['nome', 'telefone', 'regiao', 'cidade', 'disponibilidades', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = args[0] if args else None
        if data and data.get('regiao'):
            try:
                regiao_id = int(data.get('regiao'))
                self.fields['cidade'].queryset = Cidade.objects.filter(regiao_id=regiao_id).order_by('nome')
            except (ValueError, TypeError):
                self.fields['cidade'].queryset = Cidade.objects.none()
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()


class DoacaoPWAForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        label='Região',
        required=False,
        widget=forms.Select(attrs={'class': 'pwa-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = Doacao
        fields = [
            'doador_nome', 'doador_cpf', 'doador_telefone', 'doador_email',
            'valor', 'forma_pagamento', 'cidade', 'observacoes',
        ]
        widgets = {
            'doador_nome': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': 'Nome completo do doador'}),
            'doador_cpf': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': '000.000.000-00'}),
            'doador_telefone': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': '(00) 00000-0000'}),
            'doador_email': forms.EmailInput(attrs={'class': 'pwa-input', 'placeholder': 'email@exemplo.com'}),
            'valor': forms.TextInput(attrs={'class': 'pwa-input', 'placeholder': 'R$ 0,00', 'inputmode': 'numeric', 'id': 'id_valor'}),
            'forma_pagamento': forms.Select(attrs={'class': 'pwa-input'}),
            'cidade': forms.Select(attrs={'class': 'pwa-input', 'id': 'id_cidade'}),
            'observacoes': forms.Textarea(attrs={'class': 'pwa-input', 'placeholder': 'Observações...', 'rows': 3}),
        }

    field_order = ['doador_nome', 'doador_cpf', 'doador_telefone', 'doador_email', 'valor', 'forma_pagamento', 'regiao', 'cidade', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = args[0] if args else None
        if data and data.get('regiao'):
            try:
                regiao_id = int(data.get('regiao'))
                self.fields['cidade'].queryset = Cidade.objects.filter(regiao_id=regiao_id).order_by('nome')
            except (ValueError, TypeError):
                self.fields['cidade'].queryset = Cidade.objects.none()
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()
