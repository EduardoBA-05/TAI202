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

# GET (id): Lee un usuario específico por su ID
@router.get("/{id}")
async def leer_usuario_por_id(id: int, db: Session = Depends(get_db)):
    usr_db = db.query(dbUsuario).filter(dbUsuario.id == id).first()
    if not usr_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "status": "200",
        "usuario": usr_db
    }


# POST: Crea usuarios verificando primero que el id no esté en la BD
@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuarioP: crear_usuario, db: Session = Depends(get_db)): 
    nuevoU = dbUsuario(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)

    return {
        "mensaje": "Usuario Agregado",
        "Usuario": nuevoU # Retornamos nuevoU para que incluya el ID generado por la BD
    }

# PUT: Actualizar un usuario completo (Reemplaza todos los datos)
@router.put("/{id}")
async def actualizar_usuario(id: int, usuario_actualizado: crear_usuario, db: Session = Depends(get_db)):
    usr_db = db.query(dbUsuario).filter(dbUsuario.id == id).first()
    
    if not usr_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para actualizar")
    
    # Actualizamos los campos
    usr_db.nombre = usuario_actualizado.nombre
    usr_db.edad = usuario_actualizado.edad
    
    db.commit()
    db.refresh(usr_db)
    
    return {
        "mensaje": "Usuario actualizado correctamente",
        "datos_nuevos": usr_db,
        "status": "200"
    }


# PATCH: Actualización parcial (Solo modifica los campos enviados)
@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def actualizar_parcial_usuario(id: int, usuario_parcial: dict, db: Session = Depends(get_db)):
    usr_db = db.query(dbUsuario).filter(dbUsuario.id == id).first()
    
    if not usr_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para modificar")
    
    # Verificamos qué llaves vienen en el diccionario y actualizamos
    if "nombre" in usuario_parcial:
        usr_db.nombre = usuario_parcial["nombre"]
    if "edad" in usuario_parcial:
        usr_db.edad = usuario_parcial["edad"]
        
    db.commit()
    db.refresh(usr_db)
    
    return {
        "mensaje": "Usuario modificado parcialmente",
        "datos_nuevos": usr_db,
        "status": "200"
    }

# DELETE: Eliminar un usuario
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, db: Session = Depends(get_db), usuarioAuth: str = Depends(verificar_peticion)):
    usr_db = db.query(dbUsuario).filter(dbUsuario.id == id).first()
    
    if not usr_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado para eliminar")
    
    db.delete(usr_db)
    db.commit()
    
    return {
        "mensaje": f"Usuario eliminado por {usuarioAuth}",
        "status": "200"
    }