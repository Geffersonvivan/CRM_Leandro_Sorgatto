import re
from django import forms
from .models import CoordenadorRegional, CaboEleitoral, Apoiador, Voluntario, Cidade, Regiao, InteracaoLog


class DuplicateCheckMixin:
    """Verifica duplicatas por telefone e email no clean."""

    def _normalize_phone(self, phone):
        return re.sub(r'\D', '', phone) if phone else ''

    def _check_duplicates(self, model):
        telefone = self.cleaned_data.get('telefone', '')
        email = self.cleaned_data.get('email', '')
        phone_digits = self._normalize_phone(telefone)

        qs = model.objects.all()
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if phone_digits and len(phone_digits) >= 10:
            for existing in qs.values_list('telefone', 'nome'):
                if self._normalize_phone(existing[0]) == phone_digits:
                    self.add_error('telefone', f'Telefone já cadastrado para: {existing[1]}')
                    break

        if email:
            dup = qs.filter(email__iexact=email).first()
            if dup:
                self.add_error('email', f'Email já cadastrado para: {dup.nome}')


class CoordenadorRegionalForm(DuplicateCheckMixin, forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all(),
        label='Região',
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = CoordenadorRegional
        fields = [
            'nome', 'telefone', 'email',
            'cidade_base', 'instagram',
            'prioridade', 'frequencia_relacionamento',
            'observacoes',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'cidade_base': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'instagram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@usuario'}),
            'prioridade': forms.Select(attrs={'class': 'form-input'}),
            'frequencia_relacionamento': forms.Select(attrs={'class': 'form-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.cidade_base_id:
            self.fields['regiao'].initial = self.instance.cidade_base.regiao_id
            self.fields['cidade_base'].queryset = Cidade.objects.filter(
                regiao=self.instance.cidade_base.regiao
            )
        else:
            regiao_id = self.data.get('regiao') if self.data else None
            if regiao_id:
                self.fields['cidade_base'].queryset = Cidade.objects.filter(regiao_id=regiao_id)
            else:
                self.fields['cidade_base'].queryset = Cidade.objects.none()

    def clean(self):
        super().clean()
        self._check_duplicates(CoordenadorRegional)

        cidade = self.cleaned_data.get('cidade_base')
        regiao = self.cleaned_data.get('regiao')
        if cidade and regiao and cidade.regiao_id != regiao.pk:
            self.add_error('cidade_base', 'A cidade base selecionada não pertence à região informada.')

        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.regiao = self.cleaned_data['regiao']
        if commit:
            instance.save()
        return instance


class CaboEleitoralForm(DuplicateCheckMixin, forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all(),
        label='Região',
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = CaboEleitoral
        fields = [
            'nome', 'telefone', 'email',
            'cidade', 'instagram',
            'prioridade', 'frequencia_relacionamento',
            'observacoes',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'cidade': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'instagram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@usuario'}),
            'prioridade': forms.Select(attrs={'class': 'form-input'}),
            'frequencia_relacionamento': forms.Select(attrs={'class': 'form-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.cidade_id:
            self.fields['regiao'].initial = self.instance.cidade.regiao_id
            self.fields['cidade'].queryset = Cidade.objects.filter(
                regiao=self.instance.cidade.regiao
            )
        else:
            regiao_id = self.data.get('regiao') if self.data else None
            if regiao_id:
                self.fields['cidade'].queryset = Cidade.objects.filter(regiao_id=regiao_id)
            else:
                self.fields['cidade'].queryset = Cidade.objects.none()

    def clean(self):
        super().clean()
        self._check_duplicates(CaboEleitoral)

        cidade = self.cleaned_data.get('cidade')
        regiao = self.cleaned_data.get('regiao')
        if cidade and regiao and cidade.regiao_id != regiao.pk:
            self.add_error('cidade', 'A cidade selecionada não pertence à região informada.')

        return self.cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        cidade = self.cleaned_data['cidade']
        coord = CoordenadorRegional.objects.filter(regiao=cidade.regiao).first()
        if coord:
            instance.coordenador = coord
        if commit:
            instance.save()
        return instance


class ApoiadorForm(DuplicateCheckMixin, forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all(),
        label='Região',
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )

    class Meta:
        model = Apoiador
        fields = [
            'nome', 'telefone', 'email', 'cidade',
            'tipo', 'origem_contato', 'instagram',
            'prioridade', 'grau_influencia',
            'frequencia_relacionamento',
            'status', 'observacoes',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'cidade': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'origem_contato': forms.TextInput(attrs={'class': 'form-input'}),
            'instagram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@usuario'}),
            'prioridade': forms.Select(attrs={'class': 'form-input'}),
            'grau_influencia': forms.Select(attrs={'class': 'form-input'}),
            'frequencia_relacionamento': forms.Select(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if self.instance.pk and self.instance.cidade_id:
            self.fields['regiao'].initial = self.instance.cidade.regiao_id

        if user:
            if hasattr(user, 'coordenacao'):
                self.fields['regiao'].queryset = Regiao.objects.filter(
                    pk=user.coordenacao.regiao_id
                )
                self.fields['regiao'].initial = user.coordenacao.regiao_id
                self.fields['cidade'].queryset = Cidade.objects.filter(
                    regiao=user.coordenacao.regiao
                )
            elif hasattr(user, 'cabo_eleitoral'):
                self.fields['regiao'].queryset = Regiao.objects.filter(
                    pk=user.cabo_eleitoral.cidade.regiao_id
                )
                self.fields['regiao'].initial = user.cabo_eleitoral.cidade.regiao_id
                self.fields['cidade'].queryset = Cidade.objects.filter(
                    pk=user.cabo_eleitoral.cidade_id
                )
            else:
                regiao_id = self.data.get('regiao') if self.data else None
                if regiao_id:
                    self.fields['cidade'].queryset = Cidade.objects.filter(regiao_id=regiao_id)
                elif self.instance.pk and self.instance.cidade_id:
                    self.fields['cidade'].queryset = Cidade.objects.filter(
                        regiao=self.instance.cidade.regiao
                    )
                else:
                    self.fields['cidade'].queryset = Cidade.objects.none()
        else:
            self.fields['cidade'].queryset = Cidade.objects.none()

    def clean(self):
        super().clean()
        self._check_duplicates(Apoiador)

        cidade = self.cleaned_data.get('cidade')
        regiao = self.cleaned_data.get('regiao')
        if cidade and regiao and cidade.regiao_id != regiao.pk:
            self.add_error('cidade', 'A cidade selecionada não pertence à região informada.')

        return self.cleaned_data


class VoluntarioForm(forms.ModelForm):
    regiao = forms.ModelChoiceField(
        queryset=Regiao.objects.all().order_by('sigla'),
        label='Região',
        required=False,
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'id_regiao'}),
    )
    disponibilidades = forms.MultipleChoiceField(
        choices=Voluntario.DISPONIBILIDADE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        label='Disponibilidade',
    )

    class Meta:
        model = Voluntario
        fields = ['nome', 'telefone', 'cidade', 'endereco', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(00) 00000-0000'}),
            'cidade': forms.Select(attrs={'class': 'form-input', 'id': 'id_cidade'}),
            'endereco': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Rua, nº, bairro...'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

    field_order = ['nome', 'telefone', 'regiao', 'cidade', 'endereco', 'disponibilidades', 'observacoes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            if self.instance.regiao_id:
                self.fields['regiao'].initial = self.instance.regiao_id
            if self.instance.cidade_id:
                self.fields['cidade'].queryset = Cidade.objects.filter(
                    regiao=self.instance.cidade.regiao
                )
            if self.instance.disponibilidades:
                self.fields['disponibilidades'].initial = self.instance.disponibilidades

        regiao_id = self.data.get('regiao') if self.data else None
        if regiao_id:
            try:
                self.fields['cidade'].queryset = Cidade.objects.filter(regiao_id=int(regiao_id)).order_by('nome')
            except (ValueError, TypeError):
                self.fields['cidade'].queryset = Cidade.objects.none()
        elif not (self.instance.pk and self.instance.cidade_id):
            self.fields['cidade'].queryset = Cidade.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.regiao = self.cleaned_data.get('regiao')
        instance.disponibilidades = self.cleaned_data['disponibilidades']
        if commit:
            instance.save()
        return instance


class InteracaoLogForm(forms.ModelForm):
    class Meta:
        model = InteracaoLog
        fields = ['tipo', 'descricao', 'data']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descreva a interação...'}),
            'data': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
        }
