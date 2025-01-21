import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario_model import User
from app.schemas.usuario_schema import UserCreate, UserUpdate
from app.services.auth_service import get_password_hash
from app.services.rol_service import get_role_by_name

logger = logging.getLogger(__name__)

def create_user(db: Session, user_data: UserCreate) -> User:
    logger.info(f"Creando usuario con correo: {user_data.correo}")
    if db.query(User).filter(User.correo == user_data.correo).first():
        logger.warning(f"Intento de registro duplicado para correo: {user_data.correo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado."
        )
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
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

def get_all_users(db: Session) -> list[User]:
    users = db.query(User).all()
    logger.info(f"Recuperados {len(users)} usuarios de la base de datos.")
    return users

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    logger.info(f"Actualizando usuario ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuario no encontrado: ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    logger.info(f"Usuario actualizado: ID {user_id}")
    return user

def delete_user(db: Session, user_id: int) -> None:
    logger.info(f"Eliminando usuario ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuario no encontrado para eliminar: ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    db.delete(user)
    db.commit()
    logger.info(f"Usuario eliminado: ID {user_id}")

def assign_role_to_user(db: Session, user_id: int, role_name: str) -> User:
    logger.info(f"Asignando rol '{role_name}' al usuario ID {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuario no encontrado: ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    role = get_role_by_name(db, role_name)
    if not role:
        logger.warning(f"Rol no encontrado: {role_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol '{role_name}' no existe."
        )

    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
        logger.info(f"Rol '{role_name}' asignado al usuario ID {user_id}")
    else:
        logger.info(f"El usuario ID {user_id} ya tiene el rol '{role_name}'")

    return user

def remove_role_from_user(db: Session, user_id: int, role_name: str) -> User:
    logger.info(f"Removiendo rol '{role_name}' del usuario ID {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuario no encontrado: ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )

    role = get_role_by_name(db, role_name)
    if not role:
        logger.warning(f"Rol no encontrado: {role_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El rol '{role_name}' no existe."
        )

    if role in user.roles:
        user.roles.remove(role)
        db.commit()
        db.refresh(user)
        logger.info(f"Rol '{role_name}' removido del usuario ID {user_id}")
    else:
        logger.info(f"El usuario ID {user_id} no posee el rol '{role_name}'")

    return user
