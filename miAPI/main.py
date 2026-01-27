#importaciones
from fastapi import FastAPI
import asyncio

#Instancia del servidor
app = FastAPI()

#Endpoints -> ubicación especifica donde los recursos de la API
@app.get("/")
async def holamundo():
    return {"mensaje":"Hola Mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {"mensaje":"Bienvenido Mundo FastAPI",
            "estatus":"200"}