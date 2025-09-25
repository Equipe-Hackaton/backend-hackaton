from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Usuario, Categoria, Evento, FotosEvento,
    Comentario, Avaliacao, Denuncia, Favorito
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, EventoSerializer, EventoReadSerializer,
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
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    # Altera a action 'me' para permitir GET e PATCH
    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna ou atualiza o usuário autenticado."""
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "PATCH":
            # partial=True permite que apenas alguns campos sejam enviados
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
# ---------- OUTROS VIEWSETS ----------
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer # Padrão para escrita

    # NOVO MÉTODO para escolher o serializer correto
    def get_serializer_class(self):
        # Para ações de leitura, usa o serializer com detalhes
        if self.action in ['list', 'retrieve', 'my_events']:
            return EventoReadSerializer
        # Para ações de escrita, usa o serializer simples
        return EventoSerializer

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        eventos_da_empresa = Evento.objects.filter(empresa=request.user)
        page = self.paginate_queryset(eventos_da_empresa)
        if page is not None:
            # Usa o get_serializer que agora é dinâmico
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(eventos_da_empresa, many=True)
        return Response(serializer.data)
    
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
