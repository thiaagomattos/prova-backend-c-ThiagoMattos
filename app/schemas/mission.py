from datetime import datetime

from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    status: str = Field(min_length=1, max_length=30)
    drone_model: str = Field(min_length=2, max_length=100)
    image_count: int = Field(ge=0)
    area_hectares: float = Field(gt=0)


class MissionResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    drone_model: str
    image_count: int
    area_hectares: float

    model_config = {
        "from_attributes": True
    }