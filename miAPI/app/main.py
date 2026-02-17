#importaciones
from fastapi import FastAPI, status, HTTPException
import asyncio
from typing import Optional

#Instancia del servidor
app = FastAPI(
    title= "Mi primer API",
    description= "Eduardo Badillo Arreola",
    version="1.0"
)

#TB ficticia
usuarios=[
    {"id":1,"nombre":"Fany","edad":21},
    {"id":2,"nombre":"Aly","edad":21},
    {"id":3,"nombre":"Dulce","edad":21},
]

#Endpoints
@app.get("/")
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
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return{"mensaje":"usuario encontrado","usuario":usuarioK}
        return{"mensaje":"usuario no encontrado","status":"200"}
    else:
        return {"mensaje":"No se proporciono id","status":"200"}

#GET: Lee los usuarios mostrados en la BD
@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return{
        "total":len(usuarios), 
        "usuarios": usuarios,
        "status":"200"
    }

# POST: Crea usuarios verificando primero que el id no esté en la BD
@app.post("/v1/usuarios/", tags=['HTTP CRUD'])
async def agregar_usuarios(usuario:dict):
    for usr in usuarios: 
        if usr ["id"] == usuario.get("id"):
            raise HTTPException(
                status_code=400,
                detail= "El id ya existe"
            )
    usuarios.append(usuario)
    return{
        "mensaje":"Usuario Creado",
        "Datos nuevos": usuario
    }

# PUT: Actualizar un usuario completo (Reemplaza todos los datos)
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_usuario(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            # Nos aseguramos que el ID del objeto coincida con el de la URL
            usuario_actualizado["id"] = id
            # Reemplazamos el objeto completo en la lista
            usuarios[index] = usuario_actualizado
            return {
                "mensaje": "Usuario actualizado correctamente",
                "datos_anteriores": usr, # Opcional: para ver qué cambió
                "datos_nuevos": usuario_actualizado,
                "status": "200"
            }
    
    # Si termina el ciclo y no encontró el ID
    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para actualizar"
    )

# PATCH: Actualización parcial (Solo modifica los campos enviados)
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def actualizar_parcial_usuario(id: int, usuario_parcial: dict):
    for usr in usuarios:
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

# DELETE: Eliminar un usuario
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD'])
async def eliminar_usuario(id: int):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return {
                "mensaje": "Usuario eliminado exitosamente",
                "usuario_eliminado": usr,
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para eliminar"
    )