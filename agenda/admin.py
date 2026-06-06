from django.contrib import admin
from .models import Compromisso, Roteiro, RoteiroPonto


class RoteiroPontoInline(admin.TabularInline):
    model = RoteiroPonto
    extra = 1


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
