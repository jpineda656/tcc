from pydantic import BaseModel, Field, field_validator

class RoleBase(BaseModel):
    name: str = Field(..., example="admin")

    @field_validator("name")
    def validate_non_empty(cls, value):
        if not value.strip():
            raise ValueError("Este campo no puede estar vacío.")
        return value

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True
