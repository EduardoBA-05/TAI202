from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.models.usuario import crear_usuario
from app.data.database import usuarios
from app.security.auth import verificar_peticion

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import usuario as dbUsuario



router= APIRouter(
    prefix="/v1/usuarios",
    tags=["HTTP CRUD"]
)

#*********************
# Usuario CRUD
#*********************


#GET: Lee los usuarios mostrados en la BD
@router.get("/")
async def leer_usuarios(db:Session= Depends(get_db)):
    
    queryUsuarios= db.query(dbUsuario).all()
    

    return{
        "status":"200",
        "total":len(queryUsuarios), 
        "usuarios":queryUsuarios
        
    }

# POST: Crea usuarios verificando primero que el id no esté en la BD
@router.post("/",status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuarioP:crear_usuario,db:Session= Depends(get_db)): #<------- usamos el modelo
    nuevoU= dbUsuario(nombre= usuarioP.nombre, edad= usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)



    return{
        "mensaje":"Usuario Agregado",
        "Usuario": usuarioP
    }

# PUT: Actualizar un usuario completo (Reemplaza todos los datos)
@router.put("/{id}")
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
@router.patch("/{id}",status_code=status.HTTP_200_OK)
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
@router.delete("/{id}",status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int,usuarioAuth:str= Depends(verificar_peticion)):
    for usr in usuarios:
        if usr["id"] == id:
            usuarios.remove(usr)
            return {
                "mensaje": f"Usuario eliminado por {usuarioAuth}",
                "usuario_eliminado": usr,
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado para eliminar"
    )