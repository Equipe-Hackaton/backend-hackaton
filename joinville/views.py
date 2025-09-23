from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Usuario, Categoria, Evento, FotosEvento,
    Comentario, Avaliacao, Denuncia, Favorito
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, EventoSerializer,
    FotosEventoSerializer, ComentarioSerializer, AvaliacaoSerializer,
    DenunciaSerializer, FavoritoSerializer,
    UsuarioRegisterSerializer, EmpresaRegisterSerializer
)


# JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# ---------- LOGIN CUSTOMIZADO ----------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)  # gera access e refresh
        data['user'] = UsuarioSerializer(self.user).data  # adiciona dados do usuário
        return data


class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


# ---------- REGISTRO ----------
class UsuarioRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UsuarioRegisterSerializer


class EmpresaRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EmpresaRegisterSerializer


# ---------- USUÁRIOS (apenas leitura) ----------
class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna o usuário autenticado"""
        user = request.user
        serializer = UsuarioSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------- OUTROS VIEWSETS ----------
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

class FotosEventoViewSet(viewsets.ModelViewSet):
    queryset = FotosEvento.objects.all()
    serializer_class = FotosEventoSerializer

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer

class DenunciaViewSet(viewsets.ModelViewSet):
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer

class FavoritoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=["delete"])
    def remove(self, request, pk=None):
        favorito = self.get_object()
        favorito.delete()
        return Response({"detail": "Favorito removido"}, status=status.HTTP_204_NO_CONTENT)
