
from rest_framework import viewsets
from .models import (
    Empresa, Categoria, Usuario, Evento,
    FotosEvento, Comentario, Avaliacao,
    Denuncia, Favorito
)
from .serializers import (
    EmpresaSerializer, CategoriaSerializer, UsuarioSerializer, EventoSerializer,
    FotosEventoSerializer, ComentarioSerializer, AvaliacaoSerializer,
    DenunciaSerializer, FavoritoSerializer
)

class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


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
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer
