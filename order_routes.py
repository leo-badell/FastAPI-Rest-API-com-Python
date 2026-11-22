from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from dependencies import pegar_sessao, verificar_token
from models import Usuario, Pedido, ItemPedido
from schemas import PedidoSchema, ItemPedidoSchema, ResponsePedidoSchema

order_router = APIRouter(prefix="/pedidos", tags=["Pedidos"], dependencies=[Depends(verificar_token)])


def pegar_pedido(id_pedido, session, usuario):
    pedido = session.query(Pedido).filter(Pedido.id == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if not usuario.admin and usuario.id != pedido.usuario_id:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    return pedido


def exigir_pendente(pedido):
    if pedido.status != "Pendente":
        raise HTTPException(status_code=400, detail=f"Pedido {pedido.id} está {pedido.status} e não pode ser alterado")


@order_router.post("/pedido")
async def criar_pedido(pedido_schema: PedidoSchema, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin and usuario.id != pedido_schema.id_usuario:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    novo_pedido = Pedido(usuario_id=pedido_schema.id_usuario)
    session.add(novo_pedido)
    session.commit()
    return {"message": f"Pedido {novo_pedido.id} criado com sucesso"}


@order_router.post("/pedido/cancelar/{id_pedido}")
async def cancelar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = pegar_pedido(id_pedido, session, usuario)
    pedido.status = "Cancelado"
    session.commit()
    return {"message": f"Pedido {pedido.id} cancelado com sucesso",
            "pedido": pedido}


@order_router.get("/listar")
async def listar_pedidos(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    if not usuario.admin:
        raise HTTPException(status_code=401, detail="Acesso não autorizado")
    return {"pedidos": session.query(Pedido).all()}


@order_router.post("/pedido/adicionar-item/{id_pedido}")
async def adicionar_item_pedido(id_pedido: int,
                                item_pedido_schema: ItemPedidoSchema,
                                session: Session = Depends(pegar_sessao),
                                usuario: Usuario = Depends(verificar_token)):
    pedido = pegar_pedido(id_pedido, session, usuario)
    exigir_pendente(pedido)
    item_pedido = ItemPedido(
        pedido_id=id_pedido,
        quantidade=item_pedido_schema.quantidade,
        sabor=item_pedido_schema.sabor,
        tamanho=item_pedido_schema.tamanho,
        preco=item_pedido_schema.preco
    )
    pedido.itens.append(item_pedido)  # via relação: o item entra em pedido.itens e na sessão
    pedido.calcular_preco()
    session.commit()
    return {"message": f"Item adicionado com sucesso ao pedido {pedido.id}",
            "item_id": item_pedido.id,
            "pedido_preco": pedido.preco
            }


@order_router.post("/pedido/remover-item/{id_item_pedido}")
async def remover_item_pedido(id_item_pedido: int,
                              session: Session = Depends(pegar_sessao),
                              usuario: Usuario = Depends(verificar_token)):
    item_pedido = session.query(ItemPedido).filter(ItemPedido.id == id_item_pedido).first()
    if not item_pedido:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")
    pedido = pegar_pedido(item_pedido.pedido_id, session, usuario)
    exigir_pendente(pedido)
    pedido.itens.remove(item_pedido)  # tira da lista para o preço não contar o item removido
    session.delete(item_pedido)
    pedido.calcular_preco()
    session.commit()
    return {"message": f"Item removido com sucesso do pedido {pedido.id}",
            "quantidade_itens_pedido": len(pedido.itens),
            "pedido_preco": pedido.preco
            }


@order_router.post("/pedido/finalizar/{id_pedido}")
async def finalizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    pedido = pegar_pedido(id_pedido, session, usuario)
    exigir_pendente(pedido)
    pedido.status = "Finalizado"
    session.commit()
    return {"message": f"Pedido {pedido.id} finalizado com sucesso",
            "pedido": pedido}


@order_router.get("/pedido/{id_pedido}", response_model=ResponsePedidoSchema)
async def visualizar_pedido(id_pedido: int, session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    return pegar_pedido(id_pedido, session, usuario)


# Todos os pedidos do usuário logado
@order_router.get("/pedidos", response_model=List[ResponsePedidoSchema])
async def visualizar_pedidos_usuario(session: Session = Depends(pegar_sessao), usuario: Usuario = Depends(verificar_token)):
    # selectinload: busca os itens de todos os pedidos numa consulta só
    return session.query(Pedido).options(selectinload(Pedido.itens)).filter(Pedido.usuario_id == usuario.id).all()
