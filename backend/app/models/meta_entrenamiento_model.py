# app/models/meta_entrenamiento_model.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.clase_base import Base

class MetadatosEntrenamiento(Base):
    __tablename__ = "meta_entrenamiento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    
    # Fecha/hora de inicio
    hora_inicio = Column(DateTime, default=datetime.utcnow)
    
    # Fecha/hora de fin (puede ser null hasta que termine)
    hora_fin = Column(DateTime, nullable=True)
    
    # Estado del entrenamiento (started, completed, failed, etc.)
    estado = Column(String(50), default="started")

    # (Opcional) Métricas o hiperparámetros
    exactitud = Column(String(50), nullable=True)
    perdida = Column(String(50), nullable=True)

    # Relación con el usuario
    usuario = relationship("Usuario", back_populates="meta_entrenamiento")
