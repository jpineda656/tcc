#backend/app/core/config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde el archivo .env

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "jpineda")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "jpineda")
    DB_NAME: str = os.getenv("DB_NAME", "fastapi_db")

    PROJECT_NAME: str = "FastAPI + MariaDB CRUD"
    PROJECT_VERSION: str = "1.0.0"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRETO")  # Obtiene de .env
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()
