from django.db import models
from joinville.models import Usuario # Importando seu modelo principal de usuário

class ChatRoom(models.Model):
    """
    Representa uma sala de chat única entre um usuário padrão e uma empresa.
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='chat_rooms_como_usuario',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.USUARIO}
    )
    empresa = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='chat_rooms_como_empresa',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.EMPRESA}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'empresa')
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat entre {self.usuario.username} e {self.empresa.nome_empresa or self.empresa.username}"


class Message(models.Model):
    """
    Representa uma única mensagem dentro de uma ChatRoom.
    """
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Msg de {self.sender.username} em {self.timestamp.strftime('%d/%m %H:%M')}"