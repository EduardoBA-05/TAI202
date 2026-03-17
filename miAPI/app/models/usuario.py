from pydantic import BaseModel,Field 



#****************************
#Modelo de Validación usuario <----- creamos el modelo
#****************************

class crear_usuario(BaseModel):
   #Con validaciones
   id: int = Field(..., gt=0, description="Identificador de usuario (mayor que 0)") 
   nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
   edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123 años")