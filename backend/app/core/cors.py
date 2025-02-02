# backend/app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    """
    Función para configurar CORS en la aplicación FastAPI.
    """
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5173/login",
        # Aquí agregas más orígenes si lo requieres
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Usar lista de orígenes especificados
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
