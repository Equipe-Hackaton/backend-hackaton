import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from joinville.models import Usuario
from django.db import models

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['conv_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Validação: Checa se o usuário pertence à sala de chat
        is_participant = await self.check_user_in_room()
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']

        new_message = await self.save_message(message_content)
        sender_data = {
            'id': self.user.id,
            'username': self.user.username,
            'nome_empresa': self.user.nome_empresa,
            'avatar': self.user.avatar.url if self.user.avatar else None,
            'tipo_usuario': self.user.tipo_usuario
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.content,
                'sender': sender_data,
                'timestamp': new_message.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        # 🔑 CORREÇÃO: Envia a mensagem com a chave 'content'
        await self.send(text_data=json.dumps({
            'content': event['message'], # Renomeado para 'content'
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))
    @database_sync_to_async
    def save_message(self, message_content):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=self.user, content=message_content)
    
    @database_sync_to_async
    def check_user_in_room(self):
        return ChatRoom.objects.filter(id=self.room_id).filter(
            models.Q(usuario=self.user) | models.Q(empresa=self.user)
        ).exists()