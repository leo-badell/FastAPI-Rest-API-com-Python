from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base


Base = declarative_base()
db = create_engine("sqlite:///banco.db")


# Criar as clases/Tabelas do banco de dados
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, default=True)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, nome, email, senha, ativo=True, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.ativo = ativo
        self.admin = admin

# Pedido

class Pedido(Base):
    __tablename__ = "pedidos"

    # STATUS_PEDIDOS = (
    #     ("Pendente", "Pendente"),
    #     ("Cancelado", "Cancelado"), 
    #     ("Concluído", "Concluído")
    # )
    
    id = Column("id", Integer, primary_key=True, autoincrement=True) # pyright: ignore[reportUnknownVariableType]
    status = Column("status", String, nullable=False) 
    usuario_id = Column("usuario_id", Integer, ForeignKey("usuarios.id"), nullable=False)
    preco = Column("preco", Float, nullable=False)

    def __init__(self, usuario_id, status="Pendente", preco=0):
        self.usuario_id = usuario_id
        self.preco = preco
        self.status = status

# ItensPedido
class ItensPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer, nullable=False)
    sabor = Column("sabor", String, nullable=False)
    tamanho = Column("tamanho", String, nullable=False)
    preco = Column("preco", Float, nullable=False)
    pedido_id = Column("pedido_id", Integer, ForeignKey("pedidos.id"), nullable=False)
    
    

    def __init__(self, pedido_id, sabor, quantidade, preco, tamanho):
        self.pedido_id = pedido_id
        self.sabor = sabor
        self.tamanho = tamanho
        self.quantidade = quantidade
        self.preco = preco

# Executa a criação dos metadados do seu banco (cria efetivamente o banco)
# Base.metadata.create_all(db)