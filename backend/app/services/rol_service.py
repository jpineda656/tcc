import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.rol_model import Rol
from app.schemas.rol_schema import RoleCreate, RoleUpdate

logger = logging.getLogger(__name__)

def create_role(db: Session, role_data: RoleCreate) -> Rol:
    if db.query(Rol).filter(Rol.nombre_rol == role_data.nombre_rol).first():
        logger.warning(f"Intento de crear rol existente: {role_data.nombre_rol}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol ya existe."
        )
    new_role = Rol(nombre_rol=role_data.nombre_rol)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    logger.info(f"Rol creado exitosamente: {new_role.nombre_rol}")
    return new_role

def update_role(db: Session, rol_id: int, role_update: RoleUpdate) -> Rol:
    logger.info(f"Actualizando rol ID: {rol_id}")
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        logger.warning(f"Rol no encontrado: ID {rol_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    for field, value in role_update.dict(exclude_unset=True).items():
        setattr(rol, field, value)
    db.commit()
    db.refresh(rol)
    logger.info(f"Rol actualizado: ID {rol_id}")
    return rol

def get_all_roles(db: Session) -> list[Rol]:
    roles = db.query(Rol).all()
    logger.info(f"Se recuperaron {len(roles)} roles de la base de datos.")
    return roles

def delete_role(db: Session, rol_id: int) -> None:
    rol = db.query(Rol).filter(Rol.id == rol_id).first()
    if not rol:
        logger.warning(f"Rol con ID {rol_id} no encontrado para eliminación.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    db.delete(rol)
    db.commit()
    logger.info(f"Rol con ID {rol_id} eliminado exitosamente.")

def get_role_by_name(db: Session, nombre_rol: str) -> Rol | None:
    return db.query(Rol).filter(Rol.nombre_rol == nombre_rol).first()
