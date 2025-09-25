from django.contrib import admin
from .models import Usuario, Categoria, Evento, FotosEvento, Comentario, Avaliacao, Denuncia, Favorito

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("email", "tipo_usuario", "nome_empresa", "cnpj", "telefone")
    list_filter = ("tipo_usuario",)
    search_fields = ("email", "nome_empresa", "cnpj")

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "data_inicio", "data_fim", "empresa", "ativo")
    list_filter = ("categoria", "data_inicio", "ativo")
    search_fields = ("nome", "descricao")

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)

@admin.register(FotosEvento)
class FotosEventoAdmin(admin.ModelAdmin):
    list_display = ("evento",)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("evento", "usuario", "data_comentario")
    search_fields = ("comentario",)

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("evento", "usuario", "nota", "data_avaliacao")
    list_filter = ("nota",)

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("evento", "usuario", "data_denuncia")
    search_fields = ("descricao",)

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("evento", "usuario", "data_adicionado")
