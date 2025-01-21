import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.coneccion import get_db
from app.core.rol_auth import require_role
from app.schemas.usuario_schema import UserCreate, UserUpdate, UserResponse
from app.core.auth import get_current_user
from app.models.usuario_model import User
from app.services import usuario_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Usuarios"]
)

@router.post("/", response_model=UserResponse, summary="Crear un nuevo usuario")
def create_user_endpoint(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    logger.info(f"Creación de usuario: {user_data.correo}")
    return usuario_service.create_user(db, user_data)

@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar un usuario existente")
def update_user_endpoint(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db)
):
    logger.info(f"Actualización del usuario ID: {user_id}")
    return usuario_service.update_user(db, user_id, user_update)

@router.get("/", response_model=list[UserResponse], summary="Listar todos los usuarios")
def get_all_users_endpoint(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Usuario administrador {current_user.correo} solicita listado de usuarios")
    return usuario_service.get_all_users(db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un usuario")
def delete_user_endpoint(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Solicitud para eliminar usuario ID: {user_id}")
    usuario_service.delete_user(db, user_id)
    return

@router.post("/{user_id}/roles/{role_name}", response_model=UserResponse, summary="Asignar un rol a un usuario")
def assign_role_to_user_endpoint(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Usuario administrador {current_user.correo} asigna rol '{role_name}' al usuario ID {user_id}")
    return usuario_service.assign_role_to_user(db, user_id, role_name)

@router.delete("/{user_id}/roles/{role_name}", response_model=UserResponse, summary="Remover un rol de un usuario")
def remove_role_from_user_endpoint(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    logger.info(f"Usuario administrador {current_user.correo} remueve rol '{role_name}' del usuario ID {user_id}")
    return usuario_service.remove_role_from_user(db, user_id, role_name)
