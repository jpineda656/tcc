import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.coneccion import get_db
from app.schemas.rol_schema import RoleCreate, RoleResponse
from app.services.rol_service import create_role, get_all_roles, delete_role
from app.core.rol_auth import require_role
from app.models.usuario_model import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

@router.post("/", response_model=RoleResponse, summary="Crear un nuevo rol")
def create_role_endpoint(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Crea un nuevo rol en el sistema.
    - name: Nombre único del rol. Ejemplo: 'admin'.
    """
    logger.info(f"Usuario {current_user.correo} intenta crear un nuevo rol: {role_data.name}")
    return create_role(db, role_data)

@router.get("/", response_model=list[RoleResponse], summary="Listar todos los roles")
def get_all_roles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Retorna la lista de todos los roles registrados.
    """
    logger.info(f"Usuario {current_user.correo} solicita la lista de roles")
    return get_all_roles(db)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un rol")
def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Elimina un rol por su ID.
    - role_id: ID del rol a eliminar.
    """
    logger.info(f"Usuario {current_user.correo} intenta eliminar el rol con ID {role_id}")
    delete_role(db, role_id)
    return
