import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.base_class import Base
from app.db.connection import engine
from app.initial_data import initialize_data
from app.routers import (
    preprocessing_router,
    user_router,
    auth_router,
    role_router,
    capture_router,
    training_router,
    prediction_router
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
    description="API para la gestión de usuarios y roles."
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
    user_router.router,
    role_router.router,
    capture_router.router,
    preprocessing_router.router,
    training_router.router,
    prediction_router.router
]
for r in routers:
    app.include_router(r)

@app.get("/ping", tags=["Health"])
def ping():
    return {"message": "pong"}
