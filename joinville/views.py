# joinville/views.py

from rest_framework import viewsets, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Q
from datetime import datetime, timedelta
from .models import (
    Usuario, Categoria, Evento, FotosEvento,
    Comentario, Avaliacao, Denuncia, Favorito,
    FollowEmpresa, AvaliacaoEmpresa, InteresseEvento
)
from .serializers import (
    UsuarioSerializer, CategoriaSerializer, EventoSerializer, EventoReadSerializer,
    FotosEventoSerializer, ComentarioSerializer, AvaliacaoSerializer,
    DenunciaSerializer, FavoritoSerializer,
    UsuarioRegisterSerializer, EmpresaRegisterSerializer,
    EmpresaPublicProfileSerializer, FollowEmpresaSerializer,
    AvaliacaoEmpresaSerializer, InteresseEventoSerializer,
    DashboardAnalyticsSerializer
)

# JWT
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# ========== LOGIN CUSTOMIZADO ==========

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UsuarioSerializer(self.user).data
        return data


class CustomLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


# ========== REGISTRO ==========

class UsuarioRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UsuarioRegisterSerializer


class EmpresaRegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = [AllowAny]
    serializer_class = EmpresaRegisterSerializer


# ========== USUÁRIOS ==========

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna ou atualiza o usuário autenticado."""
        user = request.user

        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == "PATCH":
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def public_profile(self, request, pk=None):
        """Retorna perfil público completo de uma empresa"""
        try:
            empresa = self.get_object()
            if empresa.tipo_usuario != Usuario.TipoUsuario.EMPRESA:
                return Response(
                    {"error": "Este usuário não é uma empresa"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = EmpresaPublicProfileSerializer(
                empresa, 
                context={'request': request}
            )
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Empresa não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Seguir uma empresa"""
        if request.user.tipo_usuario != Usuario.TipoUsuario.USUARIO:
            return Response(
                {"error": "Apenas usuários podem seguir empresas"},
                status=status.HTTP_403_FORBIDDEN
            )

        empresa = self.get_object()
        if empresa.tipo_usuario != Usuario.TipoUsuario.EMPRESA:
            return Response(
                {"error": "Você só pode seguir empresas"},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow, created = FollowEmpresa.objects.get_or_create(
            usuario=request.user,
            empresa=empresa
        )

        if created:
            return Response(
                {"message": "Agora você está seguindo esta empresa"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Você já segue esta empresa"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        """Deixar de seguir uma empresa"""
        empresa = self.get_object()
        
        try:
            follow = FollowEmpresa.objects.get(
                usuario=request.user,
                empresa=empresa
            )
            follow.delete()
            return Response(
                {"message": "Você deixou de seguir esta empresa"},
                status=status.HTTP_204_NO_CONTENT
            )
        except FollowEmpresa.DoesNotExist:
            return Response(
                {"error": "Você não segue esta empresa"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def following(self, request):
        """Lista empresas que o usuário segue"""
        follows = FollowEmpresa.objects.filter(usuario=request.user)
        serializer = FollowEmpresaSerializer(follows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def dashboard_analytics(self, request):
        """Retorna estatísticas para o dashboard da empresa"""
        if request.user.tipo_usuario != Usuario.TipoUsuario.EMPRESA:
            return Response(
                {"error": "Apenas empresas têm acesso ao dashboard"},
                status=status.HTTP_403_FORBIDDEN
            )

        eventos = Evento.objects.filter(empresa=request.user)
        
        analytics = {
            'total_events': eventos.count(),
            'active_events': eventos.filter(ativo=True).count(),
            'total_participants': InteresseEvento.objects.filter(
                evento__empresa=request.user
            ).count(),
            'total_followers': FollowEmpresa.objects.filter(
                empresa=request.user
            ).count(),
            'avg_rating': AvaliacaoEmpresa.objects.filter(
                empresa=request.user
            ).aggregate(Avg('nota'))['nota__avg'] or 0,
            'total_views': eventos.aggregate(
                total=Count('visualizacoes')
            )['total'] or 0,
            'recent_activities': self._get_recent_activities(request.user)
        }

        serializer = DashboardAnalyticsSerializer(analytics)
        return Response(serializer.data)

    def _get_recent_activities(self, empresa):
        """Gera lista de atividades recentes para o dashboard"""
        activities = []
        
        # Novos seguidores (últimos 7 dias)
        recent_follows = FollowEmpresa.objects.filter(
            empresa=empresa,
            data_seguido__gte=datetime.now() - timedelta(days=7)
        ).select_related('usuario')[:5]
        
        for follow in recent_follows:
            activities.append({
                'id': follow.id,
                'type': 'follow',
                'icon': 'user-plus',
                'message': f'{follow.usuario.first_name or follow.usuario.username} começou a seguir você',
                'time': follow.data_seguido.isoformat()
            })

        # Novos interesses em eventos
        recent_interests = InteresseEvento.objects.filter(
            evento__empresa=empresa,
            data_interesse__gte=datetime.now() - timedelta(days=7)
        ).select_related('usuario', 'evento')[:5]
        
        for interest in recent_interests:
            activities.append({
                'id': interest.id,
                'type': 'interest',
                'icon': 'check-circle',
                'message': f'{interest.usuario.first_name or interest.usuario.username} demonstrou interesse em "{interest.evento.nome}"',
                'time': interest.data_interesse.isoformat()
            })

        # Novas avaliações
        recent_reviews = AvaliacaoEmpresa.objects.filter(
            empresa=empresa,
            data_avaliacao__gte=datetime.now() - timedelta(days=7)
        ).select_related('usuario')[:5]
        
        for review in recent_reviews:
            activities.append({
                'id': review.id,
                'type': 'review',
                'icon': 'star',
                'message': f'{review.usuario.first_name or review.usuario.username} avaliou sua empresa com {review.nota} estrelas',
                'time': review.data_avaliacao.isoformat()
            })

        # Ordena por data (mais recente primeiro)
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        return activities[:10]


# ========== CATEGORIAS ==========

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]


# ========== EVENTOS ==========

class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'my_events']:
            return EventoReadSerializer
        return EventoSerializer

    def retrieve(self, request, *args, **kwargs):
        """Incrementa visualizações ao buscar detalhes do evento"""
        instance = self.get_object()
        instance.visualizacoes += 1
        instance.save(update_fields=['visualizacoes'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        """Lista eventos da empresa logada"""
        eventos_da_empresa = Evento.objects.filter(empresa=request.user)
        page = self.paginate_queryset(eventos_da_empresa)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(eventos_da_empresa, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def show_interest(self, request, pk=None):
        """Registra interesse do usuário em um evento"""
        if request.user.tipo_usuario != Usuario.TipoUsuario.USUARIO:
            return Response(
                {"error": "Apenas usuários podem demonstrar interesse"},
                status=status.HTTP_403_FORBIDDEN
            )

        evento = self.get_object()
        interesse, created = InteresseEvento.objects.get_or_create(
            evento=evento,
            usuario=request.user
        )

        if created:
            return Response(
                {"message": "Interesse registrado com sucesso"},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "Você já demonstrou interesse neste evento"},
            status=status.HTTP_200_OK
        )


# ========== FOTOS DE EVENTOS ==========

class FotosEventoViewSet(viewsets.ModelViewSet):
    queryset = FotosEvento.objects.all()
    serializer_class = FotosEventoSerializer


# ========== COMENTÁRIOS ==========

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.all()
    serializer_class = ComentarioSerializer


# ========== AVALIAÇÕES DE EVENTOS ==========

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer


# ========== DENÚNCIAS ==========

class DenunciaViewSet(viewsets.ModelViewSet):
    queryset = Denuncia.objects.all()
    serializer_class = DenunciaSerializer


# ========== FAVORITOS ==========

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
        return Response(
            {"detail": "Favorito removido"}, 
            status=status.HTTP_204_NO_CONTENT
        )


# ========== AVALIAÇÕES DE EMPRESAS ==========

class AvaliacaoEmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = AvaliacaoEmpresaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtra avaliações por empresa se fornecido como query param"""
        queryset = AvaliacaoEmpresa.objects.all()
        empresa_id = self.request.query_params.get('empresa', None)
        
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        return queryset

    def perform_create(self, serializer):
        """Valida e cria avaliação"""
        if self.request.user.tipo_usuario != Usuario.TipoUsuario.USUARIO:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Apenas usuários podem avaliar empresas")
        
        empresa = serializer.validated_data.get('empresa')
        if empresa.tipo_usuario != Usuario.TipoUsuario.EMPRESA:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Você só pode avaliar empresas")
        
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Lista avaliações feitas pelo usuário logado"""
        avaliacoes = AvaliacaoEmpresa.objects.filter(usuario=request.user)
        serializer = self.get_serializer(avaliacoes, many=True)
        return Response(serializer.data)