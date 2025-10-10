# joinville/serializers.py

from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Usuario, Categoria, Evento, FotosEvento, 
    Comentario, Avaliacao, Denuncia, Favorito,
    FollowEmpresa, AvaliacaoEmpresa, InteresseEvento
)


# ========== USUÁRIO - REGISTRO E AUTENTICAÇÃO ==========

class UsuarioRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registrar um usuário comum"""
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            tipo_usuario='USUARIO'
        )
        return user


class EmpresaRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registrar uma empresa"""
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'nome_empresa', 'cnpj', 'telefone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            tipo_usuario='EMPRESA',
            nome_empresa=validated_data.get('nome_empresa'),
            cnpj=validated_data.get('cnpj'),
            telefone=validated_data.get('telefone')
        )
        return user


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer padrão para exibir/editar dados de usuários"""
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'tipo_usuario',
            'nome_empresa', 'cnpj', 'telefone', 'descricao', 'avatar',
            'data_nascimento', 'interesses', 'website', 'cover_image'
        ]
        read_only_fields = ['email', 'tipo_usuario']


# ========== PERFIL PÚBLICO DE EMPRESA ==========

class EmpresaPublicProfileSerializer(serializers.ModelSerializer):
    """Serializer completo para perfil público de empresas com estatísticas"""
    total_events = serializers.SerializerMethodField()
    active_events = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'nome_empresa', 'email', 'telefone', 'descricao', 
            'avatar', 'cover_image', 'website', 'cnpj',
            'total_events', 'active_events', 'followers_count', 
            'rating', 'total_reviews', 'is_following'
        ]

    def get_total_events(self, obj):
        """Total de eventos criados pela empresa"""
        return obj.evento_set.count()

    def get_active_events(self, obj):
        """Total de eventos ativos"""
        return obj.evento_set.filter(ativo=True).count()

    def get_followers_count(self, obj):
        """Número de seguidores da empresa"""
        return obj.seguidores.count()

    def get_rating(self, obj):
        """Avaliação média da empresa"""
        avg = obj.avaliacoes_recebidas.aggregate(Avg('nota'))['nota__avg']
        return round(avg, 1) if avg else 0

    def get_total_reviews(self, obj):
        """Total de avaliações recebidas"""
        return obj.avaliacoes_recebidas.count()

    def get_is_following(self, obj):
        """Verifica se o usuário logado segue esta empresa"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FollowEmpresa.objects.filter(
                usuario=request.user, 
                empresa=obj
            ).exists()
        return False


# ========== CATEGORIAS ==========

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


# ========== EVENTOS ==========

class EventoReadSerializer(serializers.ModelSerializer):
    """Serializer para leitura de eventos com dados completos"""
    categoria = CategoriaSerializer()
    empresa = serializers.SerializerMethodField()
    total_interessados = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = '__all__'

    def get_empresa(self, obj):
        """Retorna dados essenciais da empresa organizadora"""
        if obj.empresa:
            return {
                "id": obj.empresa.id,
                "nome_empresa": obj.empresa.nome_empresa or obj.empresa.username,
                "avatar": obj.empresa.avatar.url if obj.empresa.avatar else None,
                "tipo_usuario": obj.empresa.tipo_usuario,
                "descricao": obj.empresa.descricao,
            }
        return None

    def get_total_interessados(self, obj):
        """Total de usuários interessados no evento"""
        return obj.interessados.count()


class EventoSerializer(serializers.ModelSerializer):
    """Serializer para criação/edição de eventos"""
    class Meta:
        model = Evento
        fields = '__all__'
        read_only_fields = ['empresa', 'visualizacoes', 'created_at']


# ========== FOTOS DE EVENTOS ==========

class FotosEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotosEvento
        fields = '__all__'


# ========== COMENTÁRIOS ==========

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'


# ========== AVALIAÇÕES DE EVENTOS ==========

class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = '__all__'


# ========== DENÚNCIAS ==========

class DenunciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denuncia
        fields = '__all__'


# ========== FAVORITOS ==========

class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorito
        fields = '__all__'


# ========== FOLLOW DE EMPRESAS ==========

class FollowEmpresaSerializer(serializers.ModelSerializer):
    """Serializer para sistema de seguir empresas"""
    empresa_nome = serializers.CharField(source='empresa.nome_empresa', read_only=True)
    empresa_avatar = serializers.ImageField(source='empresa.avatar', read_only=True)

    class Meta:
        model = FollowEmpresa
        fields = ['id', 'empresa', 'empresa_nome', 'empresa_avatar', 'data_seguido']
        read_only_fields = ['usuario', 'data_seguido']


# ========== AVALIAÇÕES DE EMPRESAS ==========

class AvaliacaoEmpresaSerializer(serializers.ModelSerializer):
    """Serializer para avaliações de empresas"""
    usuario_nome = serializers.CharField(source='usuario.first_name', read_only=True)
    usuario_avatar = serializers.ImageField(source='usuario.avatar', read_only=True)

    class Meta:
        model = AvaliacaoEmpresa
        fields = [
            'id', 'empresa', 'usuario', 'usuario_nome', 'usuario_avatar',
            'nota', 'comentario', 'data_avaliacao'
        ]
        read_only_fields = ['usuario', 'data_avaliacao']


# ========== INTERESSE EM EVENTOS ==========

class InteresseEventoSerializer(serializers.ModelSerializer):
    """Serializer para registrar interesse em eventos"""
    class Meta:
        model = InteresseEvento
        fields = ['id', 'evento', 'usuario', 'data_interesse']
        read_only_fields = ['usuario', 'data_interesse']


# ========== DASHBOARD ANALYTICS ==========

class DashboardAnalyticsSerializer(serializers.Serializer):
    """Serializer para estatísticas do dashboard da empresa"""
    total_events = serializers.IntegerField()
    active_events = serializers.IntegerField()
    total_participants = serializers.IntegerField()
    total_followers = serializers.IntegerField()
    avg_rating = serializers.FloatField()
    total_views = serializers.IntegerField()
    recent_activities = serializers.ListField()