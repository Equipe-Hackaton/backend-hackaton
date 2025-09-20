from django.contrib import admin
from .models import Empresa, Evento

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'telefone')
    search_fields = ('nome', 'cnpj')

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'data_inicio', 'data_fim', 'empresa')
    list_filter = ('categoria', 'data_inicio')
    search_fields = ('nome', 'descricao')
