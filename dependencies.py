from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db, Usuario

SessionLocal = sessionmaker(bind=db)


def pegar_sessao():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def usuario_do_token(token, session, tipo):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    # sem isso o refresh token serviria de access token e vice-versa
    if dic_info.get("tipo") != tipo:
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = session.query(Usuario).filter(Usuario.id == dic_info.get("sub")).first()
    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    return usuario


def verificar_token(token: str = Depends(oauth2_schema), session=Depends(pegar_sessao)):
    return usuario_do_token(token, session, "access")


def verificar_refresh_token(token: str = Depends(oauth2_schema), session=Depends(pegar_sessao)):
    return usuario_do_token(token, session, "refresh")
