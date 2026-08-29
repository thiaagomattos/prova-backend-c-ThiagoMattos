from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProcessingHistoryResponse(BaseModel):
    id: int
    mission_id: int
    model_version: str
    status: str
    inference_time: float | None
    predictions: list[dict[str, Any]] | None
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True