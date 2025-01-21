from fastapi import APIRouter, BackgroundTasks, Depends
from utils.entrenamiento_modelo import train_gesture_recognition_model
from app.models.usuario_model import User
from app.core.rol_auth import require_role


router = APIRouter(
    prefix="/entrenamiento",
    tags=["Entrenamiento"]
)

@router.post("/", summary="Ejecuta el entrenamiento del modelo LSTM")
async def start_training(background_tasks: BackgroundTasks,
                        current_user: User = Depends(require_role("admin"))):
    """
    Endpoint para iniciar el entrenamiento del modelo.
    """
    background_tasks.add_task(train_gesture_recognition_model)
    return {"message": "El entrenamiento del modelo ha sido iniciado en segundo plano."}
