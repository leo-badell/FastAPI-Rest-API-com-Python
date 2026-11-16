from fastapi import APIRouter, Depends
from schemas import PedidoSchema
from dependencies import pegar_sessao

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"])

@order_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação.
    """
    return {"message": "Lista de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session = Depends(pegar_sessao)):
    """
    Essa é a rota para criar um novo pedido no nosso sistema. Todas as rotas dos pedidos precisam de autenticação.
    """
    return {"message": "Pedido criado com sucesso"}