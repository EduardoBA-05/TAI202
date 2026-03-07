#importaciones
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import asyncio
from pydantic import BaseModel, Field

#Instancia del servidor
app = FastAPI(
    title= "Mi primer API con JWT",
    description= "Eduardo Badillo Arreola - API con autenticación OAuth2 + JWT",
    version="1.0"
)

#Configuración JWT
CLAVE_SECRETA = "clave_ultra_secreta"
ALGORITMO = "HS256"
MINUTOS_EXPIRACION_TOKEN_ACCESO = 30

#Contexto para encriptar contraseñas
contexto_contraseñas = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Esquema OAuth2
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")

#Base de datos ficticia de usuarios con contraseñas
base_datos_usuarios = {
    "fany": {
        "nombre_usuario": "fany",
        "nombre_completo": "Fany Martinez",
        "correo": "fany@example.com",
        "contraseña_encriptada": contexto_contraseñas.hash("password123"),
        "desactivado": False
    },
    "aly": {
        "nombre_usuario": "aly",
        "nombre_completo": "Aly Rodriguez",
        "correo": "aly@example.com",
        "contraseña_encriptada": contexto_contraseñas.hash("password123"),
        "desactivado": False
    }
}

#Lista ficticia de usuarios
lista_usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Aly","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

#Modelos para autenticación
class Token(BaseModel):
    token_acceso: str
    tipo_token: str

class DatosToken(BaseModel):
    nombre_usuario: Optional[str] = None

class Usuario(BaseModel):
    nombre_usuario: str
    correo: Optional[str] = None
    nombre_completo: Optional[str] = None
    desactivado: Optional[bool] = None

class UsuarioBD(Usuario):
    contraseña_encriptada: str

# CORRECCIÓN 1: Cambiamos el nombre de la clase a mayúscula (CrearUsuario)
class CrearUsuario(BaseModel):
   #Con validaciones
   id: int = Field(..., gt=0, description="Identificador de usuario (mayor que 0)") 
   nombre: str = Field(..., min_length=3, max_length=50, example="Juanita")
   edad: int = Field(..., ge=1, le=123, description="Edad válida entre 1 y 123 años")

#Funciones de autenticación
def verificar_contraseña(contraseña_plana, contraseña_encriptada):
    return contexto_contraseñas.verify(contraseña_plana, contraseña_encriptada)

def encriptar_contraseña(contraseña):
    return contexto_contraseñas.hash(contraseña)

def obtener_usuario(base_datos, nombre_usuario: str):
    if nombre_usuario in base_datos:
        datos_usuario = base_datos[nombre_usuario]
        return UsuarioBD(**datos_usuario)

def autenticar_usuario(base_datos, nombre_usuario: str, contraseña: str):
    usuario = obtener_usuario(base_datos, nombre_usuario)
    if not usuario:
        return False
    if not verificar_contraseña(contraseña, usuario.contraseña_encriptada):
        return False
    return usuario

def crear_token_acceso(datos: dict, tiempo_expiracion: Optional[timedelta] = None):
    datos_para_codificar = datos.copy()
    if tiempo_expiracion:
        expiracion = datetime.utcnow() + tiempo_expiracion
    else:
        expiracion = datetime.utcnow() + timedelta(minutes=15)
    datos_para_codificar.update({"exp": expiracion})
    token_codificado = jwt.encode(datos_para_codificar, CLAVE_SECRETA, algorithm=ALGORITMO)
    return token_codificado

async def obtener_usuario_actual(token: str = Depends(esquema_oauth2)):
    excepcion_credenciales = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CLAVE_SECRETA, algorithms=[ALGORITMO])
        nombre_usuario: str = payload.get("sub")
        if nombre_usuario is None:
            raise excepcion_credenciales
        datos_token = DatosToken(nombre_usuario=nombre_usuario)
    except JWTError:
        raise excepcion_credenciales
    usuario = obtener_usuario(base_datos_usuarios, nombre_usuario=datos_token.nombre_usuario)
    if usuario is None:
        raise excepcion_credenciales
    return usuario

async def obtener_usuario_activo(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    if usuario_actual.desactivado:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return usuario_actual

#Endpoints
@app.post("/token", response_model=Token, tags=['Autenticación'])
async def login_para_token_acceso(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticar_usuario(base_datos_usuarios, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tiempo_expiracion_token = timedelta(minutes=MINUTOS_EXPIRACION_TOKEN_ACCESO)
    
    # CORRECCIÓN 2: Uso correcto de los parámetros "datos" y "tiempo_expiracion"
    token_acceso = crear_token_acceso(
        datos={"sub": usuario.nombre_usuario}, tiempo_expiracion=tiempo_expiracion_token
    )
    return {"token_acceso": token_acceso, "tipo_token": "bearer"}

@app.get("/users/me", response_model=Usuario, tags=['Autenticación'])
async def leer_usuario_actual(usuario_actual: Usuario = Depends(obtener_usuario_activo)):
    return usuario_actual

@app.get("/", tags=['General'])
async def holamundo():
    return {"mensaje":"Hola Mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {
        "mensaje":"Bienvenido a FastAPI",
        "estatus":"200",
    }

@app.get("/v1/parametroOb/{id}",tags=['Parametro Obligatorio'])
async def consultauno(id:int):
    return {"mensaje":"usuario encontrado",
            "usuario":id,
            "status":"200" }

@app.get("/v1/parametroOp/",tags=['Parametro Opcional'])
async def consultatodos(id:Optional[int]=None):
    if id is not None:
        for usuarioK in lista_usuarios:
            if usuarioK["id"] == id:
                return{"mensaje":"usuario encontrado","usuario":usuarioK}
        return{"mensaje":"usuario no encontrado","status":"200"}
    else:
        return {"mensaje":"No se proporciono id","status":"200"}

#GET: Lee los usuarios mostrados en la BD
@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return{
        "total":len(lista_usuarios), 
        "usuarios": lista_usuarios,
        "status":"200"
    }

# POST: Crea usuarios verificando primero que el id no esté en la BD
@app.post("/v1/usuarios/", tags=['HTTP CRUD'] ,status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: CrearUsuario): # CORRECCIÓN 3: Referenciamos la clase con mayúscula
    for usr in lista_usuarios:
        if usr ["id"] == usuario.id: 
            raise HTTPException(
                status_code=400,
                detail= "El id ya existe"
            )
    
    # CORRECCIÓN 4: Transformamos el objeto Pydantic a diccionario antes de guardarlo en la lista
    lista_usuarios.append(usuario.dict()) 
    return{
        "mensaje":"Usuario Creado",
        "Datos nuevos": usuario
    }

# PUT: Actualizar un usuario completo (Reemplaza todos los datos) - PROTEGIDO
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict, usuario_actual: Usuario = Depends(obtener_usuario_activo)):
    for index, usr in enumerate(lista_usuarios):
        if usr["id"] == id:
            # Nos aseguramos que el ID del objeto coincida con el de la URL
            usuario_actualizado["id"] = id
            # Reemplazamos el objeto completo en la lista
            lista_usuarios[index] = usuario_actualizado
            return {
                "mensaje": "Usuario actualizado correctamente",
                "datos_anteriores": usr, 
                "datos_nuevos": usuario_actualizado,
                "status": "200",
                "actualizado_por": usuario_actual.nombre_usuario
            }
    
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para actualizar"
    )

# PATCH: Actualización parcial (Solo modifica los campos enviados)
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_parcial: dict):
    for usr in lista_usuarios:
        if usr["id"] == id:
            # El método .update() de python actualiza solo las llaves que vienen en el dict
            usr.update(usuario_parcial)
            # Aseguramos que el ID no cambie aunque lo envíen en el body
            usr["id"] = id 
            return {
                "mensaje": "Usuario modificado parcialmente",
                "datos_nuevos": usr,
                "status": "200"
            }
            
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para modificar"
    )

# DELETE: Eliminar un usuario - PROTEGIDO
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def eliminar_usuario(id: int, usuario_actual: Usuario = Depends(obtener_usuario_activo)):
    for usr in lista_usuarios:
        if usr["id"] == id:
            lista_usuarios.remove(usr)
            return {
                "mensaje": "Usuario eliminado exitosamente",
                "usuario_eliminado": usr,
                "status": "200",
                "eliminado_por": usuario_actual.nombre_usuario
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para eliminar"
    )