from app.models.usuario_model import Base
from app.db.coneccion import engine

# Crear tablas en la base de datos (solo ejecutar cuando sea necesario actualizar el schema)
Base.metadata.create_all(bind=engine)
