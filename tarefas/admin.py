from django.contrib import admin
from .models import Tarefa, Comentario, TarefaHistorico


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ['created_at']


class HistoricoInline(admin.TabularInline):
    model = TarefaHistorico
    extra = 0
    readonly_fields = ['usuario', 'campo', 'valor_anterior', 'valor_novo', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fase', 'prioridade', 'responsavel', 'regiao', 'prazo', 'excluida_em']
    list_filter = ['fase', 'prioridade', 'tipo', 'regiao']
    search_fields = ['titulo']
    readonly_fields = ['created_at', 'updated_at', 'cadastrado_por', 'atualizado_por', 'excluida_em', 'excluida_por']
    date_hierarchy = 'created_at'
    inlines = [ComentarioInline, HistoricoInline]


@admin.register(TarefaHistorico)
class TarefaHistoricoAdmin(admin.ModelAdmin):
    list_display = ['tarefa', 'usuario', 'campo', 'valor_anterior', 'valor_novo', 'created_at']
    list_filter = ['campo']
    readonly_fields = ['tarefa', 'usuario', 'campo', 'valor_anterior', 'valor_novo', 'created_at']
    date_hierarchy = 'created_at'
