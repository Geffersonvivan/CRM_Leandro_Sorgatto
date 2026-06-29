from django.contrib import admin
from .models import Regiao, Cidade, Lideranca, InteracaoLog, Egresso, Lassberg


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


@admin.register(Lideranca)
class LiderancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'papel', 'telefone', 'email', 'cidade', 'coordenador_responsavel', 'tipo', 'cargo', 'status', 'prioridade', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'email']
    list_filter = ['papel', 'tipo', 'cargo', 'status', 'prioridade', 'grau_influencia', 'cidade__regiao', 'is_active']
    raw_id_fields = ['cidade', 'regiao', 'coordenador_responsavel']
    ordering = ['nome']


@admin.register(Egresso)
class EgressoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'cidade_nome', 'estado', 'curso', 'instituicao', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'email', 'cidade_nome', 'curso']
    list_filter = ['estado', 'instituicao', 'is_active']
    raw_id_fields = ['cidade']
    ordering = ['nome']


@admin.register(Lassberg)
class LassbergAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'cidade_nome', 'estado', 'is_active', 'created_at']
    search_fields = ['nome', 'telefone', 'cidade_nome']
    list_filter = ['estado', 'is_active']
    raw_id_fields = ['cidade']
    ordering = ['nome']


@admin.register(InteracaoLog)
class InteracaoLogAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'tipo', 'data', 'registrado_por', 'created_at']
    search_fields = ['descricao', 'lideranca__nome', 'egresso__nome', 'lassberg__nome']
    list_filter = ['tipo', 'data']
    raw_id_fields = ['lideranca', 'egresso', 'lassberg']
    ordering = ['-data']
