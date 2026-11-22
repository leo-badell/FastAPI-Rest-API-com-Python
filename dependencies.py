from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from sqlalchemy.orm import sessionmaker, Session
from models import db
from models import Usuario
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM

def pegar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()

def verificar_token(token: str = Depends(oauth2_schema), session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = dic_info.get("sub")
    except JWTError as erro:
        print(erro)
        raise HTTPException(status_code=401, detail="Token inválido")
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    return usuario

