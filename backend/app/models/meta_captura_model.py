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
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    label = Column(String(100), nullable=False)
    frames_count = Column(Integer, nullable=False, default=0)
    
    
    # Fecha/hora en que se generó la captura
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relación con el usuario
    user = relationship("User", back_populates="metadatos_captura")
