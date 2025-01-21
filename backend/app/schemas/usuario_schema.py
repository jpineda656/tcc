from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List
from app.schemas.rol_schema import RoleResponse

class UserBase(BaseModel):
    nombre: str = Field(..., example="Juan")
    apellido: str = Field(..., example="Pérez")
    correo: EmailStr = Field(..., example="juan@example.com")
    
    @field_validator("nombre", "apellido", "correo")
    def validate_non_empty(cls, value):
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="contraseñaSegura123")

class UserUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None

class UserResponse(UserBase):
    id: int
    roles: List[RoleResponse] = []

    class Config:
        from_attributes = True
