import os

os.environ.setdefault("SECRET_KEY", "chave-de-teste")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import bcrypt_context
from dependencies import pegar_sessao
from main import app
from models import Base, Usuario

# banco em memória: os testes nunca tocam no banco.db
engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessaoTeste = sessionmaker(bind=engine)


def sessao_teste():
    session = SessaoTeste()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[pegar_sessao] = sessao_teste
client = TestClient(app)


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def criar_usuario(email, admin=False, ativo=True):
    with SessaoTeste() as s:
        s.add(Usuario("Teste", email, bcrypt_context.hash("senha"), ativo=ativo, admin=admin))
        s.commit()


def tokens(email):
    r = client.post("/Autenticar/login", json={"email": email, "senha": "senha"})
    assert r.status_code == 200, r.text
    return r.json()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_criar_conta_nao_aceita_admin():
    r = client.post("/Autenticar/criar_conta", json={"nome": "X", "email": "x@t.com", "senha": "senha", "admin": True})
    assert r.status_code == 200
    r = client.get("/pedidos/listar", headers=auth(tokens("x@t.com")["access_token"]))
    assert r.status_code == 401


def test_preco_do_pedido_e_status():
    criar_usuario("a@t.com")
    h = auth(tokens("a@t.com")["access_token"])

    assert client.post("/pedidos/pedido", json={"id_usuario": 1}, headers=h).status_code == 200
    item = {"quantidade": 1, "sabor": "Napolitana", "tamanho": "media", "preco": 45}
    client.post("/pedidos/pedido/adicionar-item/1", json=item, headers=h)
    r = client.post("/pedidos/pedido/adicionar-item/1", json={**item, "quantidade": 2, "preco": 30}, headers=h)
    assert r.json()["pedido_preco"] == 105

    r = client.post("/pedidos/pedido/remover-item/1", headers=h)
    assert r.json() == {"message": "Item removido com sucesso do pedido 1", "quantidade_itens_pedido": 1, "pedido_preco": 60}

    r = client.get("/pedidos/pedido/1", headers=h)  # quebrava com 500 quando o pedido tinha itens
    assert r.status_code == 200
    assert r.json()["itens"][0]["preco"] == 30

    assert client.post("/pedidos/pedido/adicionar-item/1", json={**item, "preco": -45}, headers=h).status_code == 422
    assert client.post("/pedidos/pedido/adicionar-item/1", json={**item, "quantidade": 0}, headers=h).status_code == 422

    assert client.post("/pedidos/pedido/finalizar/1", headers=h).status_code == 200
    assert client.post("/pedidos/pedido/adicionar-item/1", json=item, headers=h).status_code == 400
    assert client.post("/pedidos/pedido/remover-item/2", headers=h).status_code == 400


def test_permissoes():
    criar_usuario("a@t.com")
    criar_usuario("b@t.com")
    h_a = auth(tokens("a@t.com")["access_token"])
    h_b = auth(tokens("b@t.com")["access_token"])

    assert client.post("/pedidos/pedido", json={"id_usuario": 2}, headers=h_a).status_code == 401
    client.post("/pedidos/pedido", json={"id_usuario": 1}, headers=h_a)
    assert client.get("/pedidos/pedido/1", headers=h_b).status_code == 401


def test_tipos_de_token_e_usuario_inativo():
    criar_usuario("a@t.com")
    t = tokens("a@t.com")

    assert client.get("/pedidos/pedidos", headers=auth(t["refresh_token"])).status_code == 401
    assert client.get("/Autenticar/refresh", headers=auth(t["access_token"])).status_code == 401
    assert client.get("/Autenticar/refresh", headers=auth(t["refresh_token"])).status_code == 200

    with SessaoTeste() as s:
        s.query(Usuario).update({"ativo": False})
        s.commit()
    assert client.get("/pedidos/pedidos", headers=auth(t["access_token"])).status_code == 401
    r = client.post("/Autenticar/login", json={"email": "a@t.com", "senha": "senha"})
    assert r.status_code == 400
