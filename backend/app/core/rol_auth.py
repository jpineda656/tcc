from fastapi import Depends, HTTPException, status
from app.core.auth import get_current_user
from app.models.usuario_model import Usuario

def require_role(nombre_rol: str):
    """
    Devuelve una función que verifica si el usuario tiene el rol especificado.
    """
    def role_checker(current_user: Usuario = Depends(get_current_user)):
        if not any(r.nombre_rol == nombre_rol for r in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso."
            )
        return current_user
    return role_checker
