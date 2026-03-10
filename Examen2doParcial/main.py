from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel,Field 
from fastapi.security import HTTPBasic, HTTPBasicCredentials

#Instancia del servidor
app = FastAPI(
    title= "Examen 2do Parcial",
    description= "Eduardo Badillo Arreola",
    version="1.0"
)


#TB ficticia
reservas=[
    {"id":1,"cliente":"Fany","edad":21,"fecha_inicio_dia":"Lunes","fecha_fin_dia":"Viernes","hora_inicio":"09:00","hora_fin":"17:00","numero_personas":2,"estado":"confirmada"},
    {"id":2,"cliente":"Aly","edad":21,"fecha_inicio_dia":"Martes","fecha_fin_dia":"Sabado","hora_inicio":"10:00","hora_fin":"17:00","numero_personas":2,"estado":"confirmada"},
    {"id":3,"cliente":"Dulce","edad":21,"fecha_inicio_dia":"Miercoles","fecha_fin_dia":"Viernes","hora_inicio":"10:00","hora_fin":"17:00","numero_personas":2, "estado":"confirmada"}

]


class crear_reserva(BaseModel):
   #Con validaciones
   id: int = Field(..., gt=0, description="Identificador de reserva (mayor que 0)") 
   cliente: str = Field(..., min_length=3)
   edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123 años")
   fecha_inicio_dia: str = Field(..., not_equal="Domingo", description="Domingo no se puede reservar")
   fecha_fin_dia: str = Field(..., not_equal="Domingo", description="Domingo no se puede reservar")
   hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM")
   hora_fin: str = Field(..., description="Hora de fin en formato HH:MM")
   numero_personas: int = Field(..., ge=1, le=10, description="Número de personas válido entre 1 y 10")
   estado: str = Field(..., description="Estado de la reserva")


class Usuario(BaseModel):
    nombre: str = Field(..., description="Nombre del usuario")
    contrasena: str = Field(..., description="Contraseña del usuario")

usuarios= [
    Usuario(nombre="admin", contrasena="rest123")
]


#GET: Busca una reserva por ID
@app.get("/v1/parametroOb/{id}",tags=['Parametro Obligatorio'])
async def consultauno(id:int):
    return {"mensaje":"reserva encontrada",
            "reserva":id,
            "status":"200" }


#GET: Lista todas las reservas con autenticación
@app.get("/v1/reservas/", tags=['HTTP CRUD'])
async def listar_reservas(usuario: Usuario):
    if usuario.nombre != "admin" or usuario.contrasena != "rest123":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return{
        "total":len(reservas), 
        "reservas": reservas,
        "status":"200"
    }

#POST: Crea una nueva reserva
@app.post("/v1/reservas/", tags=['HTTP CRUD'])
async def crear_reserva(reserva: crear_reserva):
    reservas.append(reserva)
    return{
        "mensaje":"reserva creada",
        "reserva": reserva,
        "status":"201"
    }

#Confirmar reserva
@app.post("/v1/reservas/confirmar/{id}", tags=['HTTP CRUD'])
async def confirmar_reserva(id: int):
    return{
        "mensaje":"reserva confirmada",
        "reserva": id,
        "status":"200",
        "estado":"confirmada"
    }


#Cancelar reserva si esta confirmada con autenticación usando el usuario y contraseña
@app.post("/v1/reservas/cancelar/{id}", tags=['HTTP CRUD'])
async def cancelar_reserva(id: int, usuario: Usuario):
    if usuario.nombre != "admin" or usuario.contrasena != "rest123":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return{
        "mensaje":"reserva cancelada",
        "reserva": id,
        "status":"200",
        "estado":"cancelada"
    }


#comando para ejecutar el servidor
#uvicorn main:app --reload

#endpoints de la api en postman
#GET: /v1/parametroOb/{id}
#GET: /v1/reservas/
#POST: /v1/reservas/
#POST: /v1/reservas/confirmar/{id}
#POST: /v1/reservas/cancelar/{id}

