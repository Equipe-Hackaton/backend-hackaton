# config/urls.py

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from joinville.views import (
    UsuarioViewSet, CategoriaViewSet, EventoViewSet,
    FotosEventoViewSet, ComentarioViewSet, AvaliacaoViewSet,
    DenunciaViewSet, FavoritoViewSet,
    # Importando as novas views de registro
    UsuarioRegisterView, EmpresaRegisterView
)
from django.conf import settings
from django.conf.urls.static import static

# Importando as views do Simple JWT para login
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
# REMOVIDO: router.register(r'empresas', EmpresaViewSet)
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
    
    # --- ADICIONADO: Novas Rotas de Autenticação ---
    # Rota para Login (enviar email e senha, receber tokens)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Rota para renovar o token de acesso usando o token de refresh
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Rota para Registrar Usuário Comum
    path('api/auth/register/user/', UsuarioRegisterView.as_view(), name='register_user'),
    # Rota para Registrar Empresa
    path('api/auth/register/company/', EmpresaRegisterView.as_view(), name='register_company'),

    path('', lambda request: redirect('/api/')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)