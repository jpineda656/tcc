# backend/app/models/usuario_rol_model.py
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.clase_base import Base

usuario_roles = Table(
    "usuario_roles",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("rol_id", Integer, ForeignKey("roles.id"), primary_key=True),
)
