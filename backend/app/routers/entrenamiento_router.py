from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.models.meta_entrenamiento_model import MetadatosEntrenamiento
from utils.entrenamiento_modelo import train_gesture_recognition_model
from utils.generar_label_map import create_label_map_from_folders
from app.models.usuario_model import Usuario
from app.core.rol_auth import require_role
from app.db.coneccion import get_db

router = APIRouter(
    prefix="/entrenamiento",
    tags=["Entrenamiento"]
)

@router.post("/", summary="Ejecuta el entrenamiento del modelo LSTM")
async def start_training(background_tasks: BackgroundTasks,
                        db: Session = Depends(get_db),
                        current_user: Usuario = Depends(require_role("admin"))):
    """
    Endpoint para iniciar el entrenamiento del modelo.
    """
    #genera el label map de forma automática
    create_label_map_from_folders("dataset", "models/label_map.json")
    
        # Crear registro
    nuevo_meta_entrenamiento = MetadatosEntrenamiento(
        usuario_id=current_user.id,
        estado="started"
    )
    db.add(nuevo_meta_entrenamiento)
    db.commit()
    db.refresh(nuevo_meta_entrenamiento)
    
    background_tasks.add_task(train_gesture_recognition_model, nuevo_meta_entrenamiento.id)
    return {"message": "El entrenamiento del modelo ha sido iniciado en segundo plano."}
