from fastapi import APIRouter

auth_router = APIRouter(prefix="/Autenticar", tags=["Autenticar"])

@auth_router.get("/")
async def autenticar():
    return {"message": "Rota de autenticação"}

