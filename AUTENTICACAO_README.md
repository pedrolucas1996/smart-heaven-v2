# 🔐 Sistema de Autenticação - Smart Heaven v2

## ✅ IMPLEMENTAÇÃO COMPLETA

O sistema de login e senha foi **totalmente implementado** no Smart Heaven v2!

## 📋 O que foi implementado

### Backend (FastAPI)
- ✅ Modelo de usuário (`User`) com SQLAlchemy
- ✅ Schemas Pydantic para validação (`UserCreate`, `UserLogin`, `Token`, etc.)
- ✅ Serviço de autenticação (`AuthService`) com:
  - Hash de senhas usando bcrypt
  - Geração e validação de tokens JWT
  - Autenticação de usuários
  - Criação de novos usuários
- ✅ Rotas de autenticação (`/api/v1/auth/`):
  - `POST /register` - Cadastro de novos usuários
  - `POST /login` - Login com usuário e senha
  - `GET /me` - Obter dados do usuário autenticado
- ✅ Middleware de proteção de rotas
- ✅ Migration do Alembic para criar tabela `users`

### Frontend (React + TypeScript)
- ✅ Context API para gerenciamento de autenticação (`AuthContext`)
- ✅ Página de Login/Registro (`LoginPage`)
- ✅ Componente de proteção de rotas (`ProtectedRoute`)
- ✅ Integração com API via axios
- ✅ Persistência de token no localStorage
- ✅ Redirecionamento automático para login quando não autenticado

## 🚀 Como usar (quando o banco voltar)

### 1. Criar tabela de usuários no banco

Quando o banco MySQL em `192.168.31.153` estiver online novamente, execute:

```sql
-- Opção 1: Usar o script SQL direto
mysql -u pedro -p -h 192.168.31.153 smartheaven < create_users_table.sql

-- Opção 2: Usar Alembic (recomendado)
cd backend
alembic upgrade head
```

### 2. Iniciar o backend

```bash
cd H:\vscode\smart-heaven-v2\backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Iniciar o frontend

```bash
cd H:\vscode\smart-heaven-v2\frontend
npm install  # Se ainda não instalou
npm run dev
```

### 4. Acessar o sistema

1. Abra o navegador em `http://localhost:5173`
2. Você será redirecionado para a página de login
3. Clique em "Não tem conta? Cadastre-se"
4. Crie sua conta com:
   - Usuário (mínimo 3 caracteres)
   - Email válido
   - Senha (mínimo 6 caracteres)
5. Após criar, você será automaticamente logado!

## 🔑 Endpoints da API

### Registro de usuário
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "seu_usuario",
  "email": "seu@email.com",
  "password": "sua_senha"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: multipart/form-data

username=seu_usuario
password=sua_senha
```

Retorna:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Obter dados do usuário atual
```http
GET /api/v1/auth/me
Authorization: Bearer <seu_token>
```

## 🛡️ Segurança implementada

- ✅ Senhas hasheadas com bcrypt (não são armazenadas em texto puro)
- ✅ Tokens JWT com expiração de 30 minutos (configurável)
- ✅ Secret key segura gerada aleatoriamente
- ✅ Validação de dados com Pydantic
- ✅ Proteção contra SQL injection (SQLAlchemy ORM)
- ✅ CORS configurado para permitir apenas origens confiáveis
- ✅ Verificação de usuário ativo antes de autenticar

## 📝 Estrutura de arquivos criados/modificados

```
backend/
├── src/
│   ├── models/
│   │   └── user.py                    # Modelo de usuário
│   ├── schemas/
│   │   └── user.py                    # Schemas de validação
│   ├── services/
│   │   └── auth_service.py            # Lógica de autenticação
│   ├── namespaces/
│   │   └── auth/
│   │       └── controller.py          # Rotas de autenticação
│   ├── core/
│   │   ├── config.py                  # Configurações (SECRET_KEY, etc)
│   │   └── dependencies.py            # Dependências FastAPI
│   └── main.py                        # Registro das rotas
├── alembic/
│   └── versions/
│       └── 001_add_users_table.py     # Migration da tabela users
├── .env                               # Variáveis de ambiente
└── create_users_table.sql             # Script SQL alternativo

frontend/
├── src/
│   ├── contexts/
│   │   └── AuthContext.tsx            # Context de autenticação
│   ├── pages/
│   │   └── LoginPage.tsx              # Página de login/registro
│   ├── components/
│   │   └── ProtectedRoute.tsx         # Proteção de rotas
│   └── main.tsx                       # Configuração de rotas
```

## 🎨 Interface do usuário

A página de login tem:
- ✨ Design moderno e responsivo
- 🌙 Tema escuro (combina com o resto do app)
- 🔄 Alternância entre Login e Cadastro
- ⚠️ Mensagens de erro amigáveis
- ⏳ Indicador de carregamento
- 🔒 Validação de formulário

## ⚙️ Configurações

Todas as configurações estão no arquivo `.env`:

```env
# Segurança
SECRET_KEY=<chave-gerada-automaticamente>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Testar a API com curl

```bash
# Registrar usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@smartheaven.com","password":"admin123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=admin" \
  -F "password=admin123"

# Usar o token (substitua <TOKEN>)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <TOKEN>"
```

## 📌 Próximos passos (opcionais)

- [ ] Adicionar "Esqueci minha senha"
- [ ] Implementar refresh tokens
- [ ] Adicionar níveis de permissão (admin, user)
- [ ] Adicionar perfil de usuário editável
- [ ] Implementar autenticação de 2 fatores
- [ ] Adicionar logs de acesso

## ❓ Troubleshooting

**Erro: "Could not validate credentials"**
- Verifique se o token está sendo enviado no header Authorization
- Confirme que o token não expirou (30 minutos)

**Erro: "Username already exists"**
- Esse usuário já foi cadastrado, tente outro nome

**Erro: "Incorrect username or password"**
- Verifique se o usuário e senha estão corretos
- Confirme que o usuário está ativo (is_active = true)

---

**Implementado por**: Sistema de IA
**Data**: 09/12/2025
**Status**: ✅ COMPLETO - Aguardando banco de dados online para testar
