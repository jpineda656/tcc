# backend/app/routers/procesamiento_router.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
import os
import logging
from utils.procesamiento import preprocess_all_files
from app.core.rol_auth import require_role
from app.models.usuario_model import Usuario

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/procesamiento",
    tags=["Procesamiento y normalización"]
)

# Directorios de entrada, salida y almacenamiento
INPUT_DIR = "data/capturas"
OUTPUT_DIR = "data/procesados"
DATASET_DIR = "dataset"

# Variable global de estado
PROCESS_STATE = {
    "status": "idle"   # "idle", "running", "completed", "failed"
}

@router.post("/", summary="Ejecuta la normalización de los puntos de referencia")
async def trigger_preprocessing(
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(require_role("admin"))
):
    """
    Endpoint para activar el preprocesamiento en segundo plano.
    """
    if not os.path.exists(INPUT_DIR):
        logger.error(f"El directorio de entrada no existe: {INPUT_DIR}")
        raise HTTPException(status_code=400, detail=f"No existe: {INPUT_DIR}")
    
    if PROCESS_STATE["status"] == "running":
        raise HTTPException(status_code=400, detail="Ya hay un proceso de normalización en curso.")

    # Actualizamos estado a 'running'
    PROCESS_STATE["status"] = "running"
    logger.info("Solicitando preprocesamiento en segundo plano.")

    # Inicia la tarea real en background
    background_tasks.add_task(real_preprocessing_task)

    return {"message": "El preprocesamiento ha sido activado en segundo plano."}


@router.get("/status")
def get_preprocessing_status():
    """
    Retorna el estado actual del proceso de normalización: 
    'idle', 'running', 'completed', o 'failed'
    """
    return {"status": PROCESS_STATE["status"]}


def real_preprocessing_task():
    """
    Ejecuta 'preprocess_all_files' real. 
    Si todo va bien, setea status='completed'.
    Si algo falla, setea status='failed'.
    """
    try:
        preprocess_all_files(INPUT_DIR, OUTPUT_DIR, DATASET_DIR)
        PROCESS_STATE["status"] = "completed"
        logger.info("Preprocesamiento completado.")
    except Exception as e:
        PROCESS_STATE["status"] = "failed"
        logger.exception(f"Error en preprocesamiento: {str(e)}")
