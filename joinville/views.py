# joinville/views.py

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from .models import (
    Usuario, Categoria, Evento, FotosEvento,
    Comentario, Avaliacao, Denuncia, Favorito
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, EventoSerializer,
    FotosEventoSerializer, ComentarioSerializer, AvaliacaoSerializer,
    DenunciaSerializer, FavoritoSerializer,
    # Importando os novos serializers de registro
    UsuarioRegisterSerializer, EmpresaRegisterSerializer
)

# NOVA VIEW: Para registrar um Usuário comum
class UsuarioRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny] # Permite que qualquer um acesse para se registrar
    serializer_class = UsuarioRegisterSerializer

# NOVA VIEW: Para registrar uma Empresa
class EmpresaRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny] # Permite que qualquer um acesse para se registrar
    serializer_class = EmpresaRegisterSerializer


# ATUALIZADO: Este ViewSet agora é apenas para leitura (GET), mais seguro.
class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


# REMOVIDO: EmpresaViewSet não é mais necessário, já que empresas são usuários.


# ViewSets existentes
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny] # Exemplo: Deixar categorias abertas para todos verem

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    # Por padrão (definido no settings.py), apenas usuários logados podem CRIAR eventos,
    # mas todos podem LER.

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
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer