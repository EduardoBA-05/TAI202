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

# Endpoint con parámetro obligatorio
@app.get("/programador") 
async def programador(nombre: str): 
    if not nombre.strip(): # revisa si está vacío o solo espacios 
        return {"mensaje": "No especificaste tu nombre"}
        return {"mensaje": f"Hola programador {nombre}, bienvenido a la API"}

#Endpoint con parámetros opcionales
@app.get("/usuario")
async def usuario(nombre: str = "Invitado", edad: int | None = None):
    if edad:
        return {"mensaje": f"Hola {nombre}, tu edad es {edad}"}
    return {"mensaje": f"Hola {nombre}, no especificaste edad"}

