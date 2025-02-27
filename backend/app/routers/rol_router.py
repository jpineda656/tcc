# backend/app/routers/rol_router.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.coneccion import get_db
from app.schemas.rol_schema import RoleCreate, RoleResponse, RoleUpdate
from app.services.rol_service import create_role,update_role,  get_all_roles, delete_role
from app.core.rol_auth import require_role
from app.models.usuario_model import Usuario

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.post("/", response_model=RoleResponse, summary="Crear un nuevo rol")
def create_role_endpoint(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin"))
):
    """
    Crea un nuevo rol en el sistema.
    - name: Nombre único del rol. Ejemplo: 'admin'.
    """
    logger.info(f"Usuario {current_user.correo} intenta crear un nuevo rol: {role_data.nombre_rol}")
    return create_role(db, role_data)

@router.put("/{rol_id}", response_model=RoleResponse, summary="Actualizar un Rol existente")
def update_role_endpoint(
    rol_id: int, 
    role_update: RoleUpdate, 
    db: Session = Depends(get_db)
):
    logger.info(f"Actualización del Rol ID: {rol_id}")
    return update_role(db, rol_id, role_update)

@router.get("/", response_model=list[RoleResponse], summary="Listar todos los roles")
def get_all_roles_endpoint(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin"))
):
    """
    Retorna la lista de todos los roles registrados.
    """
    logger.info(f"Usuario {current_user.correo} solicita la lista de roles")
    return get_all_roles(db)

@router.delete("/{rol_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un rol")
def delete_role_endpoint(
    rol_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin"))
):
    """
    Elimina un rol por su ID.
    - role_id: ID del rol a eliminar.
    """
    logger.info(f"Usuario {current_user.correo} intenta eliminar el rol con ID {rol_id}")
    delete_role(db, rol_id)
    return
