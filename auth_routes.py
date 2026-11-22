from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session
from config import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from dependencies import pegar_sessao, verificar_refresh_token
from models import Usuario
from schemas import UsuarioSchema, LoginSchema

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])


def criar_token(id_usuario, tipo="access", duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "tipo": tipo, "exp": data_expiracao}
    return jwt.encode(dic_info, SECRET_KEY, ALGORITHM)


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not usuario.ativo or not bcrypt_context.verify(senha, usuario.senha):
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    return {
        "access_token": criar_token(usuario.id),
        "refresh_token": criar_token(usuario.id, "refresh", timedelta(days=7)),
        "token_type": "bearer"
    }


@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    # ativo/admin ficam no padrão do model: admin só se define direto no banco
    novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, bcrypt_context.hash(usuario_schema.senha))
    session.add(novo_usuario)
    session.commit()
    return {"message": f"Conta criada com sucesso para {usuario_schema.email}"}


# Rota de login usando LoginSchema
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    return autenticar_usuario(login_schema.email, login_schema.senha, session)


# Rota de login usando OAuth2PasswordBearer
@auth_router.post("/login-form")
async def login_form(dados_formulario: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(pegar_sessao)):
    return autenticar_usuario(dados_formulario.username, dados_formulario.password, session)


@auth_router.get("/refresh")
async def refresh_token(usuario: Usuario = Depends(verificar_refresh_token)):
    return {"access_token": criar_token(usuario.id),
            "token_type": "bearer"}
