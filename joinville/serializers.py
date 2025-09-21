# joinville/serializers.py

from rest_framework import serializers
from .models import (
    Usuario, Categoria, Evento, FotosEvento, 
    Comentario, Avaliacao, Denuncia, Favorito
)

# NOVO: Serializer para registrar um usuário comum
class UsuarioRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        # username é obrigatório pelo AbstractUser, mas usaremos o email para login
        fields = ['username', 'first_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Usa create_user para garantir que a senha seja criptografada (hashed)
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            tipo_usuario='USUARIO' # Define o tipo de usuário
        )
        return user

# NOVO: Serializer para registrar uma empresa
class EmpresaRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'nome_empresa', 'cnpj', 'telefone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            tipo_usuario='EMPRESA', # Define o tipo de usuário
            nome_empresa=validated_data.get('nome_empresa'),
            cnpj=validated_data.get('cnpj'),
            telefone=validated_data.get('telefone')
        )
        return user

# NOVO: Serializer para exibir dados de usuários com segurança
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        # Lista os campos que podem ser exibidos publicamente (sem senha!)
        fields = ['id', 'username', 'email', 'first_name', 'tipo_usuario', 'nome_empresa', 'cnpj', 'telefone']


# Serializers existentes (sem mudanças, mas mantidos para clareza)
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class EventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = '__all__'
        depth = 1 # Opcional: mostra detalhes dos objetos relacionados

class FotosEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotosEvento
        fields = '__all__'

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'

class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = '__all__'

class DenunciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Denuncia
        fields = '__all__'

class FavoritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorito
        fields = '__all__'