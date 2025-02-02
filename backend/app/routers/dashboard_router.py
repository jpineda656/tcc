# app/routers/dashboard_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.coneccion import get_db
from app.core.auth import get_current_user
from app.models.usuario_model import Usuario
from app.models.meta_captura_model import MetadatosCaptura
from app.models.meta_entrenamiento_model import MetadatosEntrenamiento

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/data")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Retorna información resumida para el dashboard:
      - Cantidad total de capturas del usuario logueado
      - Cantidad total de entrenamientos del usuario logueado
    """
    capture_count = db.query(MetadatosCaptura)\
                      .filter(MetadatosCaptura.usuario_id == current_user.id)\
                      .count()
    training_count = db.query(MetadatosEntrenamiento)\
                       .filter(MetadatosEntrenamiento.usuario_id == current_user.id)\
                       .count()

    return {
        "capture_count": capture_count,
        "training_count": training_count
    }


@router.get("/captures", response_model=List[dict])
def get_capture_logs(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Retorna el historial de capturas del usuario logueado, con paginación.
    - page: Número de página (1 en adelante)
    - limit: Máximo de registros por página (10 por defecto)
    """

    offset = (page - 1) * limit

    # Query con offset/limit
    logs_query = (db.query(MetadatosCaptura)
                    .filter(MetadatosCaptura.usuario_id == current_user.id)
                    .order_by(MetadatosCaptura.id.desc())
                    .offset(offset)
                    .limit(limit))

    logs = logs_query.all()

    # Convertir a dict si no tienes un schema pydantic
    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "label": log.palabra,
            "frames_count": log.cant_fotogramas,
            "created_at": log.fecha_creacion
        })

    return result


@router.get("/trainings", response_model=List[dict])
def get_training_logs(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Retorna el historial de entrenamientos del usuario logueado, con paginación.
    - page: Número de página
    - limit: Máximo de registros por página
    """
    offset = (page - 1) * limit

    logs_query = (db.query(MetadatosEntrenamiento)
                    .filter(MetadatosEntrenamiento.usuario_id == current_user.id)
                    .order_by(MetadatosEntrenamiento.id.desc())
                    .offset(offset)
                    .limit(limit))

    logs = logs_query.all()

    result = []
    for log in logs:
        result.append({
            "id": log.id,
            "status": log.estado,
            "started_at": log.hora_inicio,
            "finished_at": log.hora_fin,
            "accuracy": log.exactitud
        })

    return result
