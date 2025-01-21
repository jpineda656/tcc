from sqlalchemy import Column, Integer, String
from app.models.clase_base import Base

class Role(Base):
    """
    Modelo que representa un rol en el sistema.
    Ejemplos: 'admin', 'user', 'manager', etc.
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role(name='{self.name}')>"
