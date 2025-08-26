
from django.db import models
from django.core.validators import (
    RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
)


class Empresa(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[RegexValidator(r'^\d{14}$', 'CNPJ deve conter exatamente 14 dígitos numéricos')]
    )
    email = models.EmailField(max_length=200)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nome} (CNPJ: {self.cnpj})"


class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome}"


class Usuario(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    senha = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nome} ({self.email})"


class Evento(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
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
        return f"{self.usuario.nome} comentou em '{self.evento.nome}' em {self.data_comentario.strftime('%d/%m/%Y %H:%M')}"


class Avaliacao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="avaliacoes")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True, null=True)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nota}★ - {self.usuario.nome} em '{self.evento.nome}'"


class Denuncia(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.ForeignKey(Comentario, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.TextField()
    data_denuncia = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Denúncia de {self.usuario.nome} no evento '{self.evento.nome}' em {self.data_denuncia.strftime('%d/%m/%Y %H:%M')}"


class Favorito(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name="favoritos")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="favoritos")
    data_adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["evento", "usuario"], name="unique_favorito")
        ]

    def __str__(self):
        return f"{self.usuario.nome} favoritou '{self.evento.nome}' em {self.data_adicionado.strftime('%d/%m/%Y %H:%M')}"


