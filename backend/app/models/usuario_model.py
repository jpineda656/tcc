from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.clase_base import Base
from app.models.usuario_rol_model import user_roles

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False) 

    # Relación Muchos a Muchos con Roles
    roles = relationship(
        "Role",
        secondary=user_roles,
        backref="users"
    )
    
     # Relación con MetadatosCaptura
    metadatos_captura = relationship(
        "MetadatosCaptura", 
        back_populates="user", 
        cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(nombre='{self.nombre}', correo='{self.correo}')>"
