# chat/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import (
    ChatRoomSerializer, MessageSerializer, ChatRoomCreateSerializer
)
from joinville.models import Usuario


class ChatRoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar salas de chat entre usuários e empresas
    """
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna apenas as salas de chat que o usuário participa
        """
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(usuario=user) | Q(empresa=user)
        ).select_related('usuario', 'empresa').prefetch_related('messages')

    def create(self, request, *args, **kwargs):
        """
        Cria ou retorna uma sala de chat existente entre usuário e empresa
        """
        serializer = ChatRoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        empresa_id = serializer.validated_data['empresa_id']
        
        # Valida que o solicitante é um USUARIO
        if request.user.tipo_usuario != Usuario.TipoUsuario.USUARIO:
            return Response(
                {"error": "Apenas usuários podem iniciar conversas com empresas"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Busca ou cria a sala de chat
        try:
            empresa = Usuario.objects.get(
                id=empresa_id, 
                tipo_usuario=Usuario.TipoUsuario.EMPRESA
            )
        except Usuario.DoesNotExist:
            return Response(
                {"error": "Empresa não encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verifica se já existe uma sala de chat
        chat_room, created = ChatRoom.objects.get_or_create(
            usuario=request.user,
            empresa=empresa
        )
        
        response_serializer = ChatRoomSerializer(chat_room)
        
        if created:
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def messages(self, request, pk=None):
        """
        Lista todas as mensagens de uma sala de chat específica
        """
        chat_room = self.get_object()
        
        # Verifica se o usuário tem permissão para ver as mensagens
        if chat_room.usuario != request.user and chat_room.empresa != request.user:
            return Response(
                {"error": "Você não tem permissão para ver estas mensagens"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        messages = chat_room.messages.all().select_related('sender')
        serializer = MessageSerializer(messages, many=True)
        
        # Marca as mensagens como lidas se o usuário não é o remetente
        messages.exclude(sender=request.user).update(read=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def unread_count(self, request):
        """
        Retorna o número total de mensagens não lidas do usuário
        """
        user = request.user
        
        # Conta mensagens não lidas em todas as salas que o usuário participa
        unread = Message.objects.filter(
            Q(room__usuario=user) | Q(room__empresa=user)
        ).exclude(sender=user).filter(read=False).count()
        
        return Response({"unread_count": unread})