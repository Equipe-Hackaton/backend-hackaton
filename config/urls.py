from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from joinville.views import (
    EmpresaViewSet, CategoriaViewSet, UsuarioViewSet, EventoViewSet,
    FotosEventoViewSet, ComentarioViewSet, AvaliacaoViewSet,
    DenunciaViewSet, FavoritoViewSet
)

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'fotos-eventos', FotosEventoViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)
router.register(r'denuncias', DenunciaViewSet)
router.register(r'favoritos', FavoritoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),          
    path('api/', include(router.urls)),
    path('', lambda request: redirect('/api/')),
]
