from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Max 
from .models import ChatRoom, Message
from .serializers import (
    ChatRoomSerializer,
    MessageSerializer,
    ChatRoomCreateSerializer
)
from joinville.models import Usuario

class ChatRoomViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def get_queryset(self):
        return ChatRoom.objects.filter(Q(usuario=user) | Q(empresa=user)).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-created_at') # Ordena pela última mensagem. Fallback para created_at.

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        empresa_id = serializer.validated_data['empresa_id']
        
        if request.user.tipo_usuario != Usuario.TipoUsuario.USUARIO:
            return Response(
                {"error": "Apenas usuários padrão podem iniciar um chat."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        empresa = Usuario.objects.get(id=empresa_id)
        
        room, created = ChatRoom.objects.get_or_create(
            usuario=request.user,
            empresa=empresa
        )
        
        response_serializer = ChatRoomSerializer(room, context={'request': request})
        http_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(response_serializer.data, status=http_status)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        chatroom = self.get_object()
        messages = chatroom.messages.order_by('timestamp')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)