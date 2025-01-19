from fastapi import APIRouter, BackgroundTasks
import os
import logging
from utils.preprocessing import preprocess_all_files

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/trigger",
    tags=["triggers"]
)

# Directorios de entrada, salida y almacenamiento
INPUT_DIR = "data/captures"
OUTPUT_DIR = "data/processed"
DATASET_DIR = "dataset"

@router.post("/trigger_preprocessing")
async def trigger_preprocessing(background_tasks: BackgroundTasks):
    """
    Endpoint para activar el preprocesamiento en segundo plano.
    """
    if not os.path.exists(INPUT_DIR):
        logger.error(f"El directorio de entrada no existe: {INPUT_DIR}")
        return {"error": f"El directorio de entrada no existe: {INPUT_DIR}"}

    logger.info("Solicitando preprocesamiento en segundo plano.")
    background_tasks.add_task(preprocess_all_files, INPUT_DIR, OUTPUT_DIR, DATASET_DIR)

    return {"message": "El preprocesamiento ha sido activado en segundo plano."}
