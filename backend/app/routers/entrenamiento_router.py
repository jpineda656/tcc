# backend/app/routers/entrenamiento_router.py

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.models.meta_entrenamiento_model import MetadatosEntrenamiento
from utils.entrenamiento_modelo import train_gesture_recognition_model
from utils.generar_label_map import create_label_map_from_folders
from app.models.usuario_model import Usuario
from app.core.rol_auth import require_role
from app.db.coneccion import get_db

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
    prefix="/entrenamiento",
    tags=["Entrenamiento"]
)

# Estado global simple para entrenamiento
TRAIN_STATE = {
    "status": "idle"  # "idle", "running", "completed", "failed"
}

@router.post("/", summary="Ejecuta el entrenamiento del modelo LSTM")
async def start_training(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role("admin"))
):
    """
    Inicia el entrenamiento en segundo plano.
    """
    if TRAIN_STATE["status"] == "running":
        raise HTTPException(status_code=400, detail="Ya hay un entrenamiento en curso.")

    # Generar label_map
    create_label_map_from_folders("dataset", "models/label_map.json")

    # Crear registro en DB
    nuevo_meta = MetadatosEntrenamiento(
        usuario_id=current_user.id,
        estado="started"
    )
    db.add(nuevo_meta)
    db.commit()
    db.refresh(nuevo_meta)

    # setear estado a 'running'
    TRAIN_STATE["status"] = "running"
    logger.info("Iniciando entrenamiento en segundo plano.")

    # Lanza la tarea real en background
    background_tasks.add_task(real_training_task, nuevo_meta.id)

    return {"message": "El entrenamiento ha sido iniciado en segundo plano."}

@router.get("/status", summary="Retorna el estado actual del entrenamiento")
def get_training_status():
    """
    Devuelve el estado actual: 'running', 'completed', 'failed', 'idle'
    """
    return {"status": TRAIN_STATE["status"]}

def real_training_task(entrenamiento_id: int):
    """
    Llama la función real 'train_gesture_recognition_model'.
    Si todo ok => TRAIN_STATE['status']='completed'
    si falla => 'failed'
    """
    from app.db.coneccion import SessionLocal
    db = SessionLocal()
    try:
        train_gesture_recognition_model(entrenamiento_id)
        TRAIN_STATE["status"] = "completed"
        logger.info("Entrenamiento completado con éxito.")
    except Exception as e:
        TRAIN_STATE["status"] = "failed"
        logger.exception(f"Error en entrenamiento: {str(e)}")
        # Actualiza en DB si quieres
    finally:
        db.close()
