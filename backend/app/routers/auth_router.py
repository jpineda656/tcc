from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.coneccion import get_db
from app.models.usuario_model import User
from app.services.auth_service import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Flujo de autenticación:
      - Recibe 'username' y 'password'.
      - Verifica credenciales.
      - Genera y retorna un token JWT.
    """
    # Se asume que 'username' es el correo
    user = db.query(User).filter(User.correo == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos")

    # Generar token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.correo, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
