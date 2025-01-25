from pydantic import BaseModel, Field, field_validator

class RoleBase(BaseModel):
    name: str = Field(..., example="admin")

    @field_validator("name")
    def validate_non_empty(cls, value):
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value

class RoleCreate(RoleBase):
    name: str = Field(..., min_length=6, example="supervisor")
    
class RoleUpdate(BaseModel):
    name: str | None = None

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True
