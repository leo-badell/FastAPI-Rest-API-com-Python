import email
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario
from schemas import UsuarioSchema, LoginSchema
from dependencies import pegar_sessao
from main import bcrypt_context

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])

def criar_token(email):
    token = f"fnpoisdfnjjkapodif784{email}"
    return token

@auth_router.get("/")
async def autenticar():
    return {"message": "Rota de autenticação"}

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session = Depends(pegar_sessao)): 
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    else:
        hashed_senha = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, hashed_senha)
        session.add(novo_usuario)
        session.commit()
        return {"message": f"Conta criada com sucesso para {usuario_schema.email}"}


@auth_router.post("/login")
async def login(login_schema: LoginSchema,session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==login_schema.email).first()
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado")
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
