# joinville/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator, MinValueValidator, MaxValueValidator

class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        USUARIO = 'USUARIO', 'Usuário'
        EMPRESA = 'EMPRESA', 'Empresa'

    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(max_length=10, choices=TipoUsuario.choices, default=TipoUsuario.USUARIO)
    nome_empresa = models.CharField(max_length=200, blank=True, null=True)
    cnpj = models.CharField(
        max_length=14, unique=True, null=True, blank=True,
        validators=[RegexValidator(r'^\d{14}$', 'CNPJ deve conter 14 dígitos.')]
    )
    telefone = models.CharField(max_length=20, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="usuarios/avatares/", blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    interesses = models.JSONField(blank=True, null=True)
    
    # 🆕 NOVOS CAMPOS PARA EMPRESAS
    website = models.URLField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="empresas/covers/", blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Evento(models.Model):
    empresa = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'tipo_usuario': 'EMPRESA'})
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    nome = models.CharField(max_length=200)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    endereco = models.CharField(max_length=200)
    descricao = models.TextField()
    foto = models.ImageField(
        upload_to="eventos/capas/",
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])]
    )
    ativo = models.BooleanField(default=True)
    # 🆕 CAMPO PARA CONTABILIZAR VISUALIZAÇÕES
    visualizacoes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.data_inicio.strftime('%d/%m/%Y')} - {self.data_fim.strftime('%d/%m/%Y')})"


class FotosEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="fotos")
    foto = models.ImageField(
        upload_to="eventos/fotos/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])]
    )

    def __str__(self):
        return f"Foto do evento: {self.evento.nome}"


class Comentario(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()
    data_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} comentou em '{self.evento.nome}'"


class Avaliacao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="avaliacoes")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nota}★ - {self.usuario.username} em '{self.evento.nome}'"


class Denuncia(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.ForeignKey(Comentario, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.TextField()
    data_denuncia = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Denúncia de {self.usuario.username} no evento '{self.evento.nome}'"


class Favorito(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="favoritos")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="favoritos")
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["evento", "usuario"], name="unique_favorito")
        ]

    def __str__(self):
        return f"{self.usuario.username} favoritou '{self.evento.nome}'"


# 🆕 NOVO MODELO: SISTEMA DE SEGUIR EMPRESAS
class FollowEmpresa(models.Model):
    """Permite que usuários sigam empresas"""
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='seguindo',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.USUARIO}
    )
    empresa = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='seguidores',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.EMPRESA}
    )
    data_seguido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'empresa')
        ordering = ['-data_seguido']

    def __str__(self):
        return f"{self.usuario.username} segue {self.empresa.nome_empresa or self.empresa.username}"


# 🆕 NOVO MODELO: AVALIAÇÕES DE EMPRESAS
class AvaliacaoEmpresa(models.Model):
    """Permite que usuários avaliem empresas"""
    empresa = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='avaliacoes_recebidas',
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.EMPRESA}
    )
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        limit_choices_to={'tipo_usuario': Usuario.TipoUsuario.USUARIO}
    )
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('empresa', 'usuario')
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"{self.nota}★ - {self.usuario.username} avaliou {self.empresa.nome_empresa}"


# 🆕 NOVO MODELO: INTERESSE EM EVENTOS
class InteresseEvento(models.Model):
    """Registra quando usuários demonstram interesse em eventos"""
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="interessados")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="eventos_interesse")
    data_interesse = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evento', 'usuario')
        ordering = ['-data_interesse']

    def __str__(self):
        return f"{self.usuario.username} tem interesse em {self.evento.nome}"