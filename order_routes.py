from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Usuario, ItemPedido
from schemas import PedidoSchema
from dependencies import pegar_sessao, verificar_token
from models import Pedido
from schemas import ItemPedidoSchema

order_router = APIRouter(prefix="/pedidos", tags=["pedidos"], dependencies=[Depends(verificar_token)])

@order_router.get("/")
async def pedidos():
    """
    Essa é a rota padrão de pedidos do nosso sistema. Todas as rotas dos pedidos precisam de autenticação.
    """
    return {"message": "Lista de pedidos"}

@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao)):
    novo_pedido = Pedido(usuario_id=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"message": f"Pedido criado com sucesso para o produto {novo_pedido.id}"} 


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    pedido.status = "CANCELADO"
    session.commit()
    return {"message": f"Pedido {pedido.id} cancelado com sucesso",
            "pedido": pedido}


@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    pedidos = session.query(Pedido).all()
    return {
        "pedidos": pedidos
        }


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int, 
                                item_pedido_schema: ItemPedidoSchema, 
                                session: Session = Depends(pegar_sessao), 
                                usuario: Usuario = Depends(verificar_token)):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    elif not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    item_pedido = ItemPedido(
    pedido_id=id_pedido,
    quantidade=item_pedido_schema.quantidade,
    sabor=item_pedido_schema.sabor,
    tamanho=item_pedido_schema.tamanho,
    preco=item_pedido_schema.preco
    )
    session.add(item_pedido)
    pedido.calcular_preco()  # depois do add: o autoflush inclui o novo item em pedido.itens
    session.commit()
    return {"message": f"Item adicionado com sucesso ao pedido {pedido.id}",
            "item_id": item_pedido.id,
            "pedido_preco": pedido.preco
            }
