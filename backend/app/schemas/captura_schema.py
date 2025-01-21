from pydantic import BaseModel, Field
from typing import List, Optional

class Landmark(BaseModel):
    x: float = Field(..., example=0.123)
    y: float = Field(..., example=0.456)
    z: float = Field(..., example=0.789)

class FrameData(BaseModel):
    pose: Optional[List[Landmark]] = None
    leftHand: Optional[List[Landmark]] = None
    rightHand: Optional[List[Landmark]] = None
    face: Optional[List[Landmark]] = None

class CaptureData(BaseModel):
    framesData: List[FrameData]
    label: str

class CaptureRequest(BaseModel):
    framesData: List[FrameData] = Field(
        ...,
        example=[
            {
                "pose": [{"x": 0.444, "y": 0.555, "z": 0.666}],
                "leftHand": [{"x": 0.111, "y": 0.222, "z": 0.333}],
                "rightHand": [{"x": 0.123, "y": 0.456, "z": 0.789}],
                "face": [{"x": 0.987, "y": 0.654, "z": 0.321}]
            }
        ]
    )
    label: str = Field(..., example="HOLA")
