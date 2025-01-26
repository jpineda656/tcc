from fastapi import APIRouter, BackgroundTasks,Depends
import os
import logging
from utils.procesamiento import preprocess_all_files
from app.core.rol_auth import require_role
from app.models.usuario_model import User



logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/procesamiento",
    tags=["Procesamiento y normalización"]
)

# Directorios de entrada, salida y almacenamiento
INPUT_DIR = "data/capturas"
OUTPUT_DIR = "data/procesados"
DATASET_DIR = "dataset"

@router.post("/", summary = "Ejecuta la normalización de los puntos de referencia")
async def trigger_preprocessing(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_role("admin"))
    ):
    """
    Endpoint para activar el preprocesamiento en segundo plano.
    """
    if not os.path.exists(INPUT_DIR):
        logger.error(f"El directorio de entrada no existe: {INPUT_DIR}")
        return {"error": f"El directorio de entrada no existe: {INPUT_DIR}"}

    logger.info("Solicitando preprocesamiento en segundo plano.")
    background_tasks.add_task(preprocess_all_files, INPUT_DIR, OUTPUT_DIR, DATASET_DIR)

    return {"message": "El preprocesamiento ha sido activado en segundo plano."}
