from django.contrib import admin

from .models import Oportunidade


@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'prioridade', 'score', 'status', 'cidade', 'criada_em')
    list_filter = ('tipo', 'prioridade', 'status', 'fonte')
    search_fields = ('titulo', 'cidade__nome', 'dedup_key')
    autocomplete_fields = ('cidade', 'atribuida_a', 'compromisso')
    readonly_fields = ('criada_em', 'atualizada_em', 'vista_em', 'resolvida_em')
