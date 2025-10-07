from rest_framework import serializers
from joinville.models import Usuario
from .models import ChatRoom, Message

class ChatUserSerializer(serializers.ModelSerializer):
    """Serializer simplificado para mostrar informações do usuário no chat."""
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nome_empresa', 'avatar', 'tipo_usuario']

class MessageSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de Mensagem."""
    sender = ChatUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp']

class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer para listar as salas de chat."""
    usuario = ChatUserSerializer(read_only=True)
    empresa = ChatUserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'usuario', 'empresa', 'created_at', 'last_message']

    def get_last_message(self, obj):
        """Pega a última mensagem da sala para exibir na lista de conversas."""
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

class ChatRoomCreateSerializer(serializers.Serializer):
    """Serializer usado especificamente para iniciar um novo chat."""
    empresa_id = serializers.IntegerField(write_only=True)

    def validate_empresa_id(self, value):
        """Valida se o ID fornecido corresponde a um usuário do tipo EMPRESA."""
        if not Usuario.objects.filter(id=value, tipo_usuario=Usuario.TipoUsuario.EMPRESA).exists():
            raise serializers.ValidationError("Nenhuma empresa encontrada com este ID.")
        return value