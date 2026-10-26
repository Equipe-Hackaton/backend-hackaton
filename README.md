# Join-Ville · Backend

API REST do **Join-Ville**, uma plataforma que reúne e divulga os eventos de Joinville. Foi desenvolvida no Hackathon do IFC Campus Araquari.

🔗 **Aplicação:** [join-ville-dusky.vercel.app](https://join-ville-dusky.vercel.app/) · **Frontend:** [Equipe-Hackaton/Join-ville](https://github.com/Equipe-Hackaton/Join-ville)

## Funcionalidades

- Dois tipos de conta: **usuário** e **empresa**. Só empresas cadastram eventos.
- **Eventos** com categoria, datas, endereço, descrição e fotos
- **Categorias** (Gastronomia, Clássicos de Joinville, Festas e Shows, Esportes, Atividades ao ar livre, Cultura)
- **Comentários, avaliações e denúncias** de eventos
- **Favoritos** e marcação de **interesse** em eventos
- **Seguir empresas** e avaliá-las
- **Chat** em tempo real com Django Channels
- Autenticação com **JWT** (login, refresh e cadastro separado para usuário e empresa)

## Tecnologias

- Python 3.10
- Django 5.2
- Django REST Framework
- SimpleJWT
- Django Channels + Daphne (WebSocket) e channels-redis
- Pillow (upload de imagens)
- django-cors-headers
- Gunicorn + WhiteNoise
- PDM (gerenciador de pacotes)

## Como rodar

```bash
git clone https://github.com/Equipe-Hackaton/backend-hackaton.git
cd backend-hackaton
pdm install
pdm migrate
python popular_categorias.py   # cria as categorias iniciais
pdm createsuperuser
pdm dev
```

A API sobe em `http://127.0.0.1:8000/api/`. Para o chat via WebSocket, use `pdm daphne`.

## Endpoints principais

| Rota | Descrição |
|---|---|
| `POST /api/auth/login/` | Login (retorna access e refresh token) |
| `POST /api/auth/refresh/` | Renova o access token |
| `POST /api/auth/register/user/` | Cadastro de usuário |
| `POST /api/auth/register/company/` | Cadastro de empresa |
| `/api/eventos/` | Eventos |
| `/api/categorias/` | Categorias |
| `/api/fotos-eventos/` | Fotos dos eventos |
| `/api/comentarios/` | Comentários |
| `/api/avaliacoes/` | Avaliações de eventos |
| `/api/avaliacoes-empresas/` | Avaliações de empresas |
| `/api/denuncias/` | Denúncias |
| `/api/favoritos/` | Favoritos do usuário |
| `/api/usuarios/` | Usuários |

## Estrutura

```
config/      # settings, urls, asgi e wsgi
joinville/   # models, serializers e views do domínio (eventos, empresas, avaliações...)
chat/        # salas e mensagens do chat em tempo real
```

## Equipe

- [Arthur Lanznaster](https://github.com/arthurlanz)
- [Gabriel Sombrio](https://github.com/gaSombrio)
