import os
import json
import datetime
import aiofiles
import logging

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.coneccion import get_db
from app.models.metadatos_captura_model import MetadatosCaptura
from app.schemas.captura_schema import CaptureRequest
from app.core.rol_auth import require_role
from app.models.usuario_model import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/captura",
    tags=["Captura de puntos de referencia"]
)

# Directorio donde se guardarán los archivos
DATA_DIR = "data/capturas"
os.makedirs(DATA_DIR, exist_ok=True)  # Crear directorio si no existe

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Capturar datos de referencia")
async def capture_data(
    data: CaptureRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
    ):
    """
    Recibe datos de referencia para una palabra en lenguaje de señas y los guarda en un archivo JSON.
    - **label**: Palabra asociada.
    - **framesData**: Datos de landmarks por fotograma.
    """
    try:
        # Crear el nombre del archivo basado en la palabra y un timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{data.label}_{len(data.framesData)}_{timestamp}.json"
        file_path = os.path.join(DATA_DIR, file_name)

        # Guardar los datos en un archivo JSON de forma asíncrona
        async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
            # Convertir el objeto Pydantic a dict y luego a JSON
            content = json.dumps(data.dict(), ensure_ascii=False, indent=4)
            await file.write(content)

        logger.info(f"Datos capturados y guardados en {file_path}")
        # Guarda metadatos
        frames_count = len(data.framesData)
        nuevos_metadatos = MetadatosCaptura(
            user_id=current_user.id,
            label=data.label,
            frames_count=frames_count
        )
        db.add(nuevos_metadatos)
        db.commit()
        db.refresh(nuevos_metadatos)
        
        return {"message": "Datos capturados y guardados correctamente.", "file": file_name}
    except Exception as e:
        logger.exception(f"Error al guardar los datos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar los datos: {str(e)}"
        )
