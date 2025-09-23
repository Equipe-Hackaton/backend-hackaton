# config/urls.py

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from joinville.views import (
    UsuarioViewSet, CategoriaViewSet, EventoViewSet,
    FotosEventoViewSet, ComentarioViewSet, AvaliacaoViewSet,
    DenunciaViewSet, FavoritoViewSet,
    UsuarioRegisterView, EmpresaRegisterView,
    # 🔑 Importa o novo login customizado
    CustomLoginView
)
from django.conf import settings
from django.conf.urls.static import static

# Importando as views do Simple JWT para refresh
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'eventos', EventoViewSet)
router.register(r'fotos-eventos', FotosEventoViewSet)
router.register(r'comentarios', ComentarioViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)
router.register(r'denuncias', DenunciaViewSet)
router.register(r'favoritos', FavoritoViewSet, basename='favorito')

urlpatterns = [
    path('admin/', admin.site.urls),          
    path('api/', include(router.urls)),
    
    # --- AUTENTICAÇÃO ---
    path('api/auth/login/', CustomLoginView.as_view(), name='token_obtain_pair'),  # customizado (retorna user + tokens)
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/user/', UsuarioRegisterView.as_view(), name='register_user'),
    path('api/auth/register/company/', EmpresaRegisterView.as_view(), name='register_company'),

    path('', lambda request: redirect('/api/')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)