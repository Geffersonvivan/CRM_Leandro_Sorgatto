from django.contrib import admin
from .models import Regiao, Cidade, CoordenadorRegional, CaboEleitoral, Apoiador, InteracaoLog


@admin.register(Regiao)
class RegiaoAdmin(admin.ModelAdmin):
    list_display = ['sigla', 'nome', 'populacao', 'eleitores', 'meta_votos']
    search_fields = ['nome', 'sigla']
    ordering = ['sigla']


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'regiao', 'populacao', 'eleitores', 'prefeito_nome', 'prefeito_partido']
    search_fields = ['nome', 'codigo_ibge']
    list_filter = ['regiao']
    ordering = ['nome']


@admin.register(CoordenadorRegional)
class CoordenadorRegionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'regiao', 'cidade_base', 'prioridade', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'email']
    list_filter = ['regiao', 'prioridade', 'frequencia_relacionamento', 'is_active']
    raw_id_fields = ['cidade_base']
    ordering = ['nome']


@admin.register(CaboEleitoral)
class CaboEleitoralAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'cidade', 'coordenador', 'prioridade', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'email']
    list_filter = ['cidade__regiao', 'prioridade', 'frequencia_relacionamento', 'is_active']
    raw_id_fields = ['cidade', 'coordenador']
    ordering = ['nome']


@admin.register(Apoiador)
class ApoiadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'cidade', 'tipo', 'status', 'prioridade', 'grau_influencia', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'email']
    list_filter = ['tipo', 'status', 'prioridade', 'grau_influencia', 'cidade__regiao', 'is_active']
    raw_id_fields = ['cidade']
    ordering = ['nome']


@admin.register(InteracaoLog)
class InteracaoLogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tipo', 'data', 'registrado_por', 'created_at']
    search_fields = ['descricao', 'coordenador__nome', 'cabo__nome', 'apoiador__nome']
    list_filter = ['tipo', 'data']
    raw_id_fields = ['coordenador', 'cabo', 'apoiador']
    ordering = ['-data']
