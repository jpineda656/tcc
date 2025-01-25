import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.rol_model import Role
from app.schemas.rol_schema import RoleCreate, RoleUpdate

logger = logging.getLogger(__name__)

def create_role(db: Session, role_data: RoleCreate) -> Role:
    if db.query(Role).filter(Role.name == role_data.name).first():
        logger.warning(f"Intento de crear rol existente: {role_data.name}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol ya existe."
        )
    new_role = Role(name=role_data.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    logger.info(f"Rol creado exitosamente: {new_role.name}")
    return new_role

def update_role(db: Session, role_id: int, role_update: RoleUpdate) -> Role:
    logger.info(f"Actualizando rol ID: {role_id}")
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.warning(f"Rol no encontrado: ID {role_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    for field, value in role_update.dict(exclude_unset=True).items():
        setattr(role, field, value)
    db.commit()
    db.refresh(role)
    logger.info(f"Rol actualizado: ID {role_id}")
    return role

def get_all_roles(db: Session) -> list[Role]:
    roles = db.query(Role).all()
    logger.info(f"Se recuperaron {len(roles)} roles de la base de datos.")
    return roles

def delete_role(db: Session, role_id: int) -> None:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        logger.warning(f"Rol con ID {role_id} no encontrado para eliminación.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado."
        )
    db.delete(role)
    db.commit()
    logger.info(f"Rol con ID {role_id} eliminado exitosamente.")

def get_role_by_name(db: Session, role_name: str) -> Role | None:
    return db.query(Role).filter(Role.name == role_name).first()
