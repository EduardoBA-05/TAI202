from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime

# Obtenemos el año actual dinámicamente para la validación del libro
anio_actual = datetime.now().year

class Usuario(BaseModel):
    nombre: str = Field(..., min_length=2, description="Nombre del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico válido") 


class Libro(BaseModel):
    id_libro: int
    
    titulo: str = Field(..., min_length=2, max_length=100)
    
    autor: str
    
    # Mayor a 1450 y menor o igual al año actual
    anio: int = Field(..., gt=1450, le=anio_actual) 
    
    # Entero positivo mayor a 1
    paginas: int = Field(..., gt=1)
    
    # Estado del libro solo puede ser "disponible" o "prestado"
    estado: Literal["disponible", "prestado"] = "disponible"


class Prestamo(BaseModel):
    id_prestamo: int
    id_libro: int
    usuario: Usuario