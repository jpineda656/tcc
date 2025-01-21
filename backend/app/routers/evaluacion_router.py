from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from utils.evaluacion import predict


router = APIRouter(
    prefix="",
    tags=["Evualuación"]
)

class PredictionRequest(BaseModel):
    framesData: List[Dict]    
    
@router.post("/" , summary="Evalua los puntos de refencia y muestra resultado")
async def predict_gesture(request: PredictionRequest):
    """
    Endpoint para realizar predicción de gestos en tiempo real.
    """
    try:
        # Pasa framesData directamente al proceso de predicción
        prediction_result = predict({"framesData": request.framesData})
        return prediction_result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
