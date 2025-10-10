# config/urls.py

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from joinville.views import (
    UsuarioViewSet, CategoriaViewSet, EventoViewSet,
    FotosEventoViewSet, ComentarioViewSet, AvaliacaoViewSet,
    DenunciaViewSet, FavoritoViewSet, AvaliacaoEmpresaViewSet,
    UsuarioRegisterView, EmpresaRegisterView, CustomLoginView
)
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# Router principal
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'fotos-eventos', FotosEventoViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)
router.register(r'denuncias', DenunciaViewSet)
router.register(r'favoritos', FavoritoViewSet, basename='favorito')
# 🆕 NOVA ROTA: Avaliações de empresas
router.register(r'avaliacoes-empresas', AvaliacaoEmpresaViewSet, basename='avaliacao-empresa')

urlpatterns = [
    path('admin/', admin.site.urls),          
    path('api/', include(router.urls)),
    
    # --- AUTENTICAÇÃO ---
    path('api/auth/login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/user/', UsuarioRegisterView.as_view(), name='register_user'),
    path('api/auth/register/company/', EmpresaRegisterView.as_view(), name='register_company'),
    
    # 🆕 CHAT (inclui todas as rotas do chat)
    path('api/', include('chat.urls')),
    
    # Redirect raiz para API
    path('', lambda request: redirect('/api/')),
]

# Serve arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)