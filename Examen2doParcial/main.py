from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from typing import Optional
from pydantic import BaseModel,Field 
from fastapi.security import HTTPBasic, HTTPBasicCredentials

#Instancia del servidor
app = FastAPI(
    title= "Mi primer API",
    description= "Eduardo Badillo Arreola",
    version="1.0"
)


#TB ficticia
reservas=[
    {"id":1,"cliente":"Fany","edad":21,"fecha_inicio":"2026-10-10","fecha_fin":"2026-10-15","hora_inicio":"09:00","hora_fin":"17:00","numero_personas":2},
    {"id":2,"cliente":"Aly","edad":21,"fecha_inicio":"2026-10-11","fecha_fin":"2026-10-16","hora_inicio":"10:00","hora_fin":"17:00","numero_personas":2},
    {"id":3,"cliente":"Dulce","edad":21,"fecha_inicio":"2026-10-12","fecha_fin":"2026-10-17","hora_inicio":"10:00","hora_fin":"17:00","numero_personas":2}

]


class crear_reserva(BaseModel):
   #Con validaciones
   id: int = Field(..., gt=0, description="Identificador de reserva (mayor que 0)") 
   cliente: str = Field(..., min_length=3)
   edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123 años")
   fecha_inicio: str = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
   fecha_fin: str = Field(..., description="Fecha de fin en formato YYYY-MM-DD")
   hora_inicio: str = Field(..., description="Hora de inicio en formato HH:MM")
   hora_fin: str = Field(..., description="Hora de fin en formato HH:MM")
   numero_personas: int = Field(..., ge=1, le=10, description="Número de personas válido entre 1 y 10")

@app.get("/v1/parametroOb/{id}",tags=['Parametro Obligatorio'])
async def consultauno(id:int):
    return {"mensaje":"reserva encontrada",
            "reserva":id,
            "status":"200" }






