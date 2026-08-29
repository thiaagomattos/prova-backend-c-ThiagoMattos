import json
import os
import tempfile
import time

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.database import get_db
from app.models.mission import Mission
from app.models.processing import ProcessingHistory
from app.schemas.processing import ProcessingHistoryResponse
from app.services.ai_service import ai_service
from typing import List

router = APIRouter(
    prefix="/missions",
    tags=["Processing"],
    dependencies=[Depends(verify_token)]
)


@router.post("/{mission_id}/process")
async def process_mission(
    mission_id: int,
    image: UploadFile = File(...),
    confidence_threshold: float = Form(0.5),
    db: Session = Depends(get_db)
):
    mission = (
        db.query(Mission)
        .filter(Mission.id == mission_id)
        .first()
    )

    if not mission:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    contents = await image.read()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    ) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name

    start_time = time.perf_counter()

    try:
        predictions = ai_service.predict(
            temp_path,
            confidence_threshold
        )

        inference_time = time.perf_counter() - start_time

        history = ProcessingHistory(
            mission_id=mission_id,
            model_version=ai_service.model_version,
            status="success",
            inference_time=inference_time,
            predictions=json.dumps(predictions)
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "mission_id": mission_id,
            "filename": image.filename,
            "model_version": ai_service.model_version,
            "confidence_threshold": confidence_threshold,
            "inference_time": round(inference_time, 4),
            "predictions": predictions
        }

    except Exception as e:

        inference_time = time.perf_counter() - start_time

        history = ProcessingHistory(
            mission_id=mission_id,
            model_version=ai_service.model_version,
            status="error",
            inference_time=inference_time,
            error_message=str(e)
        )

        db.add(history)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Error during AI processing"
        )

    finally:
        os.remove(temp_path)

@router.get("/{mission_id}/processing-history", response_model=List[ProcessingHistoryResponse])
def get_processing_history(
    mission_id: int,
    db: Session = Depends(get_db)
):
    mission = (
        db.query(Mission)
        .filter(Mission.id == mission_id)
        .first()
    )

    if not mission:
        raise HTTPException(
            status_code=404,
            detail="Mission not found"
        )

    history = (
        db.query(ProcessingHistory)
        .filter(ProcessingHistory.mission_id == mission_id)
        .order_by(ProcessingHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": record.id,
            "mission_id": record.mission_id,
            "model_version": record.model_version,
            "status": record.status,
            "inference_time": record.inference_time,
            "predictions": (
                json.loads(record.predictions)
                if record.predictions
                else None
            ),
            "error_message": record.error_message,
            "created_at": record.created_at
        }
        for record in history
    ]