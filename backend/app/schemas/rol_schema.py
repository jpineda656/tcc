from pydantic import BaseModel, Field, field_validator

class RoleBase(BaseModel):
    nombre_rol: str = Field(..., example="admin")

    @field_validator("nombre_rol")
    def validate_non_empty(cls, value):
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value

class RoleCreate(RoleBase):
    nombre_rol: str = Field(..., min_length=4, example="supervisor")
    
class RoleUpdate(BaseModel):
    nombre_rol: str | None = None

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True
