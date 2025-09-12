import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  
django.setup()

from joinville.models import Categoria  

categorias = [
    "Gastronomia",
    "Clássicos de Joinville",
    "Festas e shows",
    "Esportes",
    "Atividades ao ar livre",
    "Cultura"
]

for nome in categorias:
    if not Categoria.objects.filter(nome=nome).exists():
        Categoria.objects.create(nome=nome)
        print(f"Categoria '{nome}' criada!")
    else:
        print(f"Categoria '{nome}' já existe.")
