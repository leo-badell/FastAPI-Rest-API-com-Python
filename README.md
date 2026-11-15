# FastAPI Project — API de Pedidos

API em FastAPI desenvolvida durante o curso: cadastro de usuários e base para um sistema de pedidos (pizzaria), com banco SQLite gerenciado por SQLAlchemy e migrações via Alembic.

## O que foi implementado até agora

### Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | Cria o app FastAPI, carrega o `.env` (`SECRET_KEY`), configura o `bcrypt_context` (hash de senhas com passlib/bcrypt) e registra os routers. |
| `models.py` | Modelos do banco (SQLAlchemy) e conexão com `sqlite:///banco.db`. |
| `schemas.py` | Schemas Pydantic de validação do corpo das requisições. |
| `dependencies.py` | `pegar_sessao()`: dependência que abre e fecha a sessão do banco a cada requisição. |
| `auth_routes.py` | Rotas de autenticação/cadastro (`/Autenticar`). |
| `order_routes.py` | Rotas de pedidos (`/pedidos`). |
| `alembic/` + `alembic.ini` | Migrações do banco (migração inicial já criada). |

### Banco de dados (tabelas)

- **usuarios**: `id`, `nome`, `email` (único), `senha` (hash bcrypt), `ativo`, `admin`
- **pedidos**: `id`, `status` (padrão `Pendente`), `usuario_id` → usuarios, `preco`
- **itens_pedido**: `id`, `quantidade`, `sabor`, `tamanho`, `preco`, `pedido_id` → pedidos

### Rotas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/Autenticar/` | Rota padrão de autenticação. |
| POST | `/Autenticar/criar_conta` | Cria um usuário. Recebe JSON (`UsuarioSchema`), salva a senha com hash bcrypt e retorna erro 400 se o e-mail já existir. |
| GET | `/pedidos/` | Rota padrão de pedidos (lista ainda fixa). |

Exemplo de corpo para `/Autenticar/criar_conta`:

```json
{
  "nome": "Fulano",
  "email": "fulano@exemplo.com",
  "senha": "minhasenha",
  "ativo": true,
  "admin": false
}
```

## Como rodar (Windows / PowerShell)

### 1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Se o PowerShell bloquear o script de ativação, rode uma vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### 2. Instalar as dependências

```powershell
pip install -r requirements.txt
```

### 3. Criar o arquivo `.env`

Crie um arquivo `.env` na raiz com a variável abaixo (ele está no `.gitignore` e **não** deve ser commitado):

```
SECRET_KEY=coloque_uma_chave_aleatoria_aqui
```

Para gerar uma chave aleatória:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Criar/atualizar o banco de dados (Alembic)

```powershell
alembic upgrade head
```

Quando alterar algo em `models.py`, gere uma nova migração e aplique:

```powershell
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

### 5. Subir o servidor

```powershell
uvicorn main:app --reload
```

Se a porta 8000 estiver ocupada: `uvicorn main:app --reload --port 8001`

### 6. Acessar a documentação

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Para parar o servidor: `Ctrl + C`.
