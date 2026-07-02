from django.contrib import admin
from .models import Compromisso, Evento, EventoAnexo, Roteiro, RoteiroPonto


class RoteiroPontoInline(admin.TabularInline):
    model = RoteiroPonto
    extra = 1


class EventoAnexoInline(admin.TabularInline):
    model = EventoAnexo
    extra = 1
    readonly_fields = ['enviado_por', 'created_at']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data', 'tipo', 'cidade', 'status', 'relevancia']
    list_filter = ['status', 'relevancia', 'tipo']
    search_fields = ['nome', 'local']
    inlines = [EventoAnexoInline]


@admin.register(Compromisso)
class CompromissoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data_hora_inicio', 'tipo', 'cidade', 'status']
    list_filter = ['tipo', 'status', 'regiao']
    search_fields = ['titulo', 'descricao']


@admin.register(Roteiro)
class RoteiroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'data', 'regiao', 'status']
    list_filter = ['status', 'regiao']
    inlines = [RoteiroPontoInline]
