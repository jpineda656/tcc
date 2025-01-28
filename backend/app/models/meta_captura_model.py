# app/models/metadatos_captura_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.clase_base import Base

class MetadatosCaptura(Base):
    """
    Modelo que representa los metadatos al momento de realizar la captura.
    """
    __tablename__ = "metadatos_captura"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    palabra = Column(String(100), nullable=False)
    cant_fotogramas = Column(Integer, nullable=False, default=0)
    
    
    # Fecha/hora en que se generó la captura
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="metadatos_captura")
    
    def __repr__(self):
        return f"<CaptureLog id={self.id} palabra={self.palabra} usuario_id={self.usuario_id}>" 


