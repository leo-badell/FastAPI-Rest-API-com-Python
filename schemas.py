from pydantic import BaseModel, Field, AliasChoices
from typing import List


class UsuarioSchema(BaseModel):
    nome: str
    email: str
    senha: str

    class Config:
        from_attributes = True

class LoginSchema(BaseModel):
    email: str
    senha: str

    class Config:
        from_attributes = True

class PedidoSchema(BaseModel):
    id_usuario: int

    class Config:
        from_attributes = True


class ItemPedidoSchema(BaseModel):
    quantidade: int = Field(gt=0)
    sabor: str
    tamanho: str
    # "preco" no JSON da requisição; "preco_unitario" ao ler do model ItemPedido
    preco: float = Field(gt=0, validation_alias=AliasChoices("preco", "preco_unitario"))

    class Config:
        from_attributes = True


class ResponsePedidoSchema(BaseModel):
    id: int
    status: str
    preco: float
    itens: List[ItemPedidoSchema]

    class Config:
        from_attributes = True
