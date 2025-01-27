import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UserCreate, UserUpdate
from app.services.auth_service import get_password_hash
from app.services.rol_service import get_role_by_name

logger = logging.getLogger(__name__)

def create_user(db: Session, user_data: UserCreate) -> Usuario:
    logger.info(f"Creando usuario con correo: {user_data.correo}")
    if db.query(Usuario).filter(Usuario.correo == user_data.correo).first():
        logger.warning(f"Intento de registro duplicado para correo: {user_data.correo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado."
        )
    hashed_password = get_password_hash(user_data.password)
    new_user = Usuario(
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        correo=user_data.correo,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Usuario creado exitosamente: ID {new_user.id}")
    return new_user

def get_all_users(db: Session) -> list[Usuario]:
    usuarios = db.query(Usuario).all()
    logger.info(f"Recuperados {len(usuarios)} usuarios de la base de datos.")
    return usuarios

def update_user(db: Session, usuario_id: int, user_update: UserUpdate) -> Usuario:
    logger.info(f"Actualizando usuario ID: {usuario_id}")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: ID {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(usuario, field, value)
    db.commit()
    db.refresh(usuario)
    logger.info(f"Usuario actualizado: ID {usuario_id}")
    return usuario

def delete_user(db: Session, usuario_id: int) -> None:
    logger.info(f"Eliminando usuario ID: {usuario_id}")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado para eliminar: ID {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    db.delete(usuario)
    db.commit()
    logger.info(f"Usuario eliminado: ID {usuario_id}")

def assign_role_to_user(db: Session, usuario_id: int, nombre_rol: str) -> Usuario:
    logger.info(f"Asignando rol '{nombre_rol}' al usuario ID {usuario_id}")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: ID {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    rol = get_role_by_name(db, nombre_rol)
    if not rol:
        logger.warning(f"Rol no encontrado: {nombre_rol}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol '{nombre_rol}' no existe."
        )

    if rol not in usuario.roles:
        usuario.roles.append(rol)
        db.commit()
        db.refresh(usuario)
        logger.info(f"Rol '{nombre_rol}' asignado al usuario ID {usuario_id}")
    else:
        logger.info(f"El usuario ID {usuario_id} ya tiene el rol '{nombre_rol}'")

    return usuario

def remove_role_from_user(db: Session, usuario_id: int, nombre_rol: str) -> Usuario:
    logger.info(f"Removiendo rol '{nombre_rol}' del usuario ID {usuario_id}")
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        logger.warning(f"Usuario no encontrado: ID {usuario_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    rol = get_role_by_name(db, nombre_rol)
    if not rol:
        logger.warning(f"Rol no encontrado: {nombre_rol}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol '{nombre_rol}' no existe."
        )

    if rol in usuario.roles:
        usuario.roles.remove(rol)
        db.commit()
        db.refresh(usuario)
        logger.info(f"Rol '{nombre_rol}' removido del usuario ID {usuario_id}")
    else:
        logger.info(f"El usuario ID {usuario_id} no posee el rol '{nombre_rol}'")

    return usuario
