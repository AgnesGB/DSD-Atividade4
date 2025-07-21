# 🎮 DSD-Atividade4 - Jogo da Velha com API Gateway REST/SOAP

Este projeto implementa um **jogo da velha online** utilizando uma arquitetura de microserviços com API Gateway que integra serviços REST e SOAP.

## 🏗️ Arquitetura

A arquitetura implementa o padrão **API Gateway**, onde todas as requisições dos clientes são processadas por um gateway central que roteia para os serviços internos apropriados.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Cliente   │────│ API Gateway │────│ Serviço     │
│    Web      │    │  (Django)   │    │ REST        │
└─────────────┘    │             │    │ (Django)    │
                   │    :8000    │    │   :8001     │
┌─────────────┐    │             │    └─────────────┘
│ Cliente     │────│             │    ┌─────────────┐
│ Externo     │    │             │────│ Serviço     │
└─────────────┘    └─────────────┘    │ SOAP        │
                                      │ (Spyne)     │
                                      │   :8002     │
                                      └─────────────┘
```

## 🚀 Como Executar

### 📋 Pré-requisitos

- **Python 3.8+** 🐍
- **pip** (gerenciador de pacotes Python)

### ⚡ Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/AgnesGB/DSD-Atividade4.git
cd DSD-Atividade4

# 2. Instale as dependências 
pip install -r requirements.txt drf-yasg

# 3. Configure os bancos de dados
cd rest_service/tictactoe
python manage.py makemigrations
python manage.py migrate

cd ../../api_gateway/gateway
python manage.py migrate

# 4. Execute os serviços (em terminais separados)
```

### 🖥️ Executando os Serviços

**Terminal 1: Serviço REST (Jogo da Velha)**
```bash
cd rest_service/tictactoe
python manage.py runserver 8001
```

**Terminal 2: API Gateway**
```bash
cd api_gateway/gateway
python manage.py runserver 8000
```

**Terminal 3: (Opcional) Serviço SOAP**
```bash
cd soap_server
python server.py  # ⚠️ Requer Python < 3.12 devido ao spyne
```

### 🎯 Testando a API

Após executar os serviços, você pode testar:

**📱 Interfaces Web:**
- **Swagger UI**: http://localhost:8000/ (Documentação interativa)
- **API Gateway**: http://localhost:8000/api/games/
- **Serviço REST**: http://localhost:8001/api/

**🔧 Testando via curl:**

```bash
# Listar jogos
curl http://localhost:8000/api/games/

# Criar novo jogo
curl -X POST http://localhost:8001/api/games/ \
  -H "Content-Type: application/json" \
  -d '{"player_x": "Jogador1"}'

# Fazer uma jogada
curl -X POST http://localhost:8001/api/games/{game_id}/move/ \
  -H "Content-Type: application/json" \
  -d '{"position": 0, "player": "X"}'
```

## 🧩 Componentes

### 🛡️ API Gateway (porta 8000)
- **Framework**: Django REST Framework
- **Funcionalidades**:
  - Roteamento central de requisições
  - Implementação de HATEOAS
  - Documentação automática via Swagger
  - Integração com serviços REST e SOAP

### 🎮 Serviço REST (porta 8001)
- **Framework**: Django REST Framework
- **Funcionalidades**:
  - Lógica completa do jogo da velha
  - Gerenciamento de partidas
  - Validação de movimentos
  - API RESTful com CRUD completo

### 🌐 Serviço SOAP (porta 8002)
- **Framework**: Spyne
- **Funcionalidades**:
  - Gerenciamento de jogadores
  - Estatísticas de partidas
  - Geração automática de WSDL
  - ⚠️ **Nota**: Atualmente incompatível com Python 3.12+

## 📚 Endpoints da API

### 🎯 API Gateway (localhost:8000)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/games/` | Lista todos os jogos (com HATEOAS) |
| `POST` | `/api/games/` | Cria novo jogo |
| `GET` | `/api/games/{id}/` | Detalhes de um jogo específico |
| `POST` | `/api/games/{id}/join/` | Entra em um jogo |
| `POST` | `/api/games/{id}/move/` | Faz uma jogada |
| `GET` | `/api/players/` | Lista jogadores |
| `GET` | `/swagger/` | Documentação Swagger |

### 🎮 Serviço REST (localhost:8001)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/` | API Root (navegável) |
| `GET` | `/api/games/` | Lista jogos |
| `POST` | `/api/games/` | Cria jogo |
| `GET` | `/api/games/{id}/` | Detalhes do jogo |
| `POST` | `/api/games/{id}/move/` | Faz jogada |

## 🎯 Exemplos de Uso

### 🔥 Fluxo Completo de Jogo

```bash
# 1. Criar um novo jogo
GAME=$(curl -s -X POST http://localhost:8001/api/games/ \
  -H "Content-Type: application/json" \
  -d '{"player_x": "Alice"}' | jq -r '.id')

echo "Jogo criado: $GAME"

# 2. Segundo jogador entra
curl -X PATCH http://localhost:8001/api/games/$GAME/ \
  -H "Content-Type: application/json" \
  -d '{"player_o": "Bob"}'

# 3. Alice faz primeira jogada (posição 0)
curl -X POST http://localhost:8001/api/games/$GAME/move/ \
  -H "Content-Type: application/json" \
  -d '{"position": 0}'

# 4. Ver estado atual do jogo
curl -s http://localhost:8001/api/games/$GAME/ | jq .
```

### 🎲 Testando via API Gateway

```bash
# Listar jogos com links HATEOAS
curl -s http://localhost:8000/api/games/ | jq .

# Criar jogo via Gateway (integra SOAP + REST)
curl -X POST http://localhost:8000/api/games/ \
  -H "Content-Type: application/json" \
  -d '{"player_name": "Charlie"}'
```

## 🏗️ Estrutura do Projeto

```
DSD-Atividade4/
├── 📁 api_gateway/gateway/          # API Gateway Django
│   ├── 📁 api/                      # App principal
│   │   ├── 📄 views.py             # Views do gateway
│   │   ├── 📄 clients.py           # Clientes REST/SOAP
│   │   └── 📄 urls.py              # Rotas
│   └── 📁 gateway/                  # Configurações Django
├── 📁 rest_service/tictactoe/       # Serviço REST
│   ├── 📁 game/                     # App do jogo
│   │   ├── 📄 models.py            # Modelo do jogo
│   │   ├── 📄 views.py             # API Views
│   │   └── 📄 serializers.py       # Serializadores
│   └── 📁 tictactoe/               # Configurações Django
├── 📁 soap_server/                  # Serviço SOAP
│   ├── 📄 server.py                # Servidor Spyne
│   └── 📄 test_soap.py             # Testes SOAP
├── 📁 client_web/                   # Cliente Web (futuro)
├── 📄 requirements.txt              # Dependências Python
└── 📄 README.md                     # Este arquivo
```

## 🔧 Desenvolvimento

### 🛠️ Comandos Úteis

```bash
# Verificar se serviços estão rodando
curl -s http://localhost:8000/api/games/ | jq length
curl -s http://localhost:8001/api/ | jq .

# Resetar banco de dados
cd rest_service/tictactoe
rm db.sqlite3
python manage.py migrate

# Ver logs em tempo real
tail -f nohup.out  # se rodando com nohup
```

### 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| **Erro de módulo não encontrado** | `pip install -r requirements.txt drf-yasg` |
| **Porta já em uso** | `pkill -f "runserver 800X"` |
| **SOAP não funciona** | Usar Python < 3.12 ou desabilitar SOAP |
| **Erro de migração** | `python manage.py makemigrations && python manage.py migrate` |

## 🚀 Recursos Implementados

- ✅ **API Gateway** com roteamento inteligente
- ✅ **HATEOAS** (Hypermedia as the Engine of Application State)
- ✅ **Documentação Swagger** automática
- ✅ **Validação** completa do jogo da velha
- ✅ **Detecção de vitória** e empate
- ✅ **API RESTful** completa
- ✅ **Integração REST/SOAP** (SOAP requer Python < 3.12)
- ✅ **Banco de dados** com modelos Django

## 🎓 Conceitos de DSD Demonstrados

1. **Microserviços**: Separação clara de responsabilidades
2. **API Gateway**: Ponto único de entrada
3. **REST**: Protocolo stateless para comunicação
4. **SOAP**: Protocolo baseado em XML (quando disponível)
5. **HATEOAS**: Links dinâmicos para navegação da API
6. **Service Discovery**: Gateway conhece os serviços
7. **Load Balancing**: Distribuição de carga (conceitual)

---

🎮 **Divirta-se jogando e explorando a arquitetura!** 🎯