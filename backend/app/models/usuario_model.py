from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.clase_base import Base
from app.models.usuario_rol_model import usuario_roles

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False) 

    # Relación Muchos a Muchos con Roles
    roles = relationship(
        "Rol",
        secondary=usuario_roles,
        backref="usuarios"
    )
    
     # Relación con MetadatosCaptura
    metadatos_captura = relationship(
        "MetadatosCaptura", 
        back_populates="usuario", 
        cascade="all, delete-orphan")

    meta_entrenamiento = relationship(
        "MetadatosEntrenamiento",
        back_populates="usuario", 
        cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(nombre='{self.nombre}', correo='{self.correo}')>"
