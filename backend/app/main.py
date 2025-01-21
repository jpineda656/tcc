import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.clase_base import Base
from app.db.coneccion import engine
from app.initial_data import initialize_data
from app.routers import (
    procesamiento_router,
    usuario_router,
    auth_router,
    rol_router,
    captura_router,
    entrenamiento_router,
    evaluacion_router
)

# Configuración centralizada de logging
logging_config = {
    "version": 1,
    "formatters": {
        "default": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": logging.INFO
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "level": logging.INFO
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": logging.INFO
    }
}

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Crear la aplicación con configuración centralizada
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API para captura, procesamiento y entrenamiento de puntos de referencias aplicando redes neuronales LSTM."
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Ajustar según sea necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos (considerar migraciones en producción)
Base.metadata.create_all(bind=engine)

# Inicializar datos (roles y usuario admin)
initialize_data()

# Registrar routers de forma modular
routers = [
    auth_router.router,
    usuario_router.router,
    rol_router.router,
    captura_router.router,
    procesamiento_router.router,
    entrenamiento_router.router,
    evaluacion_router.router
]
for r in routers:
    app.include_router(r)

