# Importaciones necesarias
from fastapi import FastAPI, status, HTTPException
from app.validaciones import Libro, Usuario, Prestamo

# Instancia del servidor
app = FastAPI(
    title="API Biblioteca Digital",
    description="Eduardo Badillo Arreola",
    version="1.0"
)

# Bases de datos ficticias
libros = [
    {
        "id_libro": 1,
        "titulo": "Disparador Cósmico",
        "autor": "Robert Anton Wilson",
        "anio": 1977,
        "paginas": 288,
        "estado": "prestado"  
    },
    {
        "id_libro": 2,
        "titulo": "No me puedes lastimar: Domina tu mente y desafía las probabilidades",
        "autor": "David Goggins",
        "anio": 2022,
        "paginas": 364,
        "estado": "prestado"  
    },
    {
        "id_libro": 3,
        "titulo": "El Matrimonio Perfecto",
        "autor": "Samael Aun Weor",
        "anio": 1950,
        "paginas": 350,
        "estado": "disponible"
    }
]


prestamos = [
    {
        "id_prestamo": 1,
        "id_libro": 1,
        "usuario": {
            "nombre": "Carlos Slim",
            "correo": "carlos@telmex.com"
        }
    },
    {
        "id_prestamo": 2,
        "id_libro": 2,
        "usuario": {
            "nombre": "Ana Gabriela Guevara",
            "correo": "ana.guevara@conade.gob.mx"
        }
    }
]

usuarios = [
    {
        "nombre": "Eduardo Badillo",
        "correo": "eduardo@correo.com"
    },
    {
        "nombre": "Carlos Slim",
        "correo": "carlos@telmex.com"
    },
    {
        "nombre": "Ana Gabriela Guevara",
        "correo": "ana.guevara@conade.gob.mx"
    }
]


#Listar todos los libros disponibles
@app.get("/libros", tags=['Libros'])
async def listar_libros():
    return {"libros_registrados": libros}


#Buscar un libro por su nombre
@app.get("/libros/buscar/{titulo}", tags=['Libros'])
async def buscar_libro(titulo: str):
    # Buscamos coincidencias
    libros_encontrados = []
    for l in libros:
        if titulo.lower() in l["titulo"].lower():
            libros_encontrados.append(l)
            
    if not libros_encontrados:
        raise HTTPException(status_code=404, detail="No se encontraron libros con ese nombre")
        
    return {"libros": libros_encontrados}

#Registrar un libro
@app.post("/libros", status_code=status.HTTP_201_CREATED, tags=['Libros'])
async def registrar_libro(libro: Libro):
    # Verificamos si el ID ya existe usando un for
    for l in libros:
        if l["id_libro"] == libro.id_libro:
            raise HTTPException(status_code=400, detail="El ID del libro ya existe")
    
    # libro.model_dump() convierte el modelo Pydantic a un diccionario normal
    libros.append(libro.model_dump())
    return {"mensaje": "Libro registrado exitosamente", "libro": libro}

#Registrar el préstamo de un libro
@app.post("/prestamos", status_code=status.HTTP_201_CREATED, tags=['Préstamos'])
async def registrar_prestamo(prestamo: Prestamo):
    libro_encontrado = None
    
    #Buscar si el libro existe
    for l in libros:
        if l["id_libro"] == prestamo.id_libro:
            libro_encontrado = l
            break
            
    if not libro_encontrado:
        raise HTTPException(status_code=404, detail="El libro no existe")
        
    #Validar si ya está prestado (Código 409 Conflict)
    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(status_code=409, detail="El libro ya está prestado")
        
    #Si está disponible, cambiamos su estado y guardamos el préstamo
    libro_encontrado["estado"] = "prestado"
    prestamos.append(prestamo.model_dump())
    
    return {"mensaje": "Préstamo registrado con éxito", "prestamo": prestamo}

# Modificar un libro existente (Actualización total)
@app.put("/libros/{id_libro}", tags=['Libros'])
async def actualizar_libro(id_libro: int, libro_actualizado: Libro):
    # Buscamos el libro por el ID que viene en la URL
    for i in range(len(libros)):
        if libros[i]["id_libro"] == id_libro:
            
            # .model_dump() convierte el objeto Pydantic a diccionario
            libros[i] = libro_actualizado.model_dump()
            return {"mensaje": "Libro actualizado correctamente", "libro": libros[i]}
    
    # Si terminamos el ciclo y no encontramos el ID
    raise HTTPException(status_code=404, detail="No se encontró el libro para actualizar")

#Marcar un libro como devuelto
@app.patch("/libros/devolver/{id_libro}", tags=['Préstamos'])
async def devolver_libro(id_libro: int):
    for l in libros:
        if l["id_libro"] == id_libro:
            if l["estado"] == "disponible":
                raise HTTPException(status_code=400, detail="El libro ya se encuentra disponible")
            
            # Cambiamos estado
            l["estado"] = "disponible"
            return {"mensaje": "Libro devuelto exitosamente", "status": "200 OK"}
            
    raise HTTPException(status_code=404, detail="Libro no encontrado")


# Eliminar un libro
@app.delete("/libros/{id_libro}", tags=['Libros'])
async def eliminar_libro(id_libro: int):
    # Buscamos el libro en la lista
    for l in libros:
        if l["id_libro"] == id_libro:
            # Regla de negocio: No borrar si está prestado
            if l["estado"] == "prestado":
                raise HTTPException(
                    status_code=400, 
                    detail="No se puede eliminar el libro porque actualmente está prestado"
                )
            
            # Si está disponible, lo eliminamos
            libros.remove(l)
            return {"mensaje": f"Libro con ID {id_libro} eliminado correctamente"}
            
    # Si no se encuentra el ID
    raise HTTPException(status_code=404, detail="El libro no existe")