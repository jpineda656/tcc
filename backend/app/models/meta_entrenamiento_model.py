# app/models/meta_entrenamiento_model.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.clase_base import Base

class MetadatosEntrenamiento(Base):
    __tablename__ = "meta_entrenamiento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Fecha/hora de inicio
    started_at = Column(DateTime, default=datetime.utcnow)
    
    # Fecha/hora de fin (puede ser null hasta que termine)
    finished_at = Column(DateTime, nullable=True)
    
    # Estado del entrenamiento (started, completed, failed, etc.)
    status = Column(String(50), default="started")

    # (Opcional) Métricas o hiperparámetros
    accuracy = Column(String(50), nullable=True)
    loss = Column(String(50), nullable=True)

    # Relación con el usuario
    user = relationship("User", back_populates="meta_entrenamiento")
