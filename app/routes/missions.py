from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_token

from app.db.database import get_db
from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionResponse
from typing import List

router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
    dependencies=[Depends(verify_token)]
)

@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(mission: MissionCreate,db: Session = Depends(get_db)):
    new_mission = Mission(
        name=mission.name,
        status=mission.status,
        drone_model=mission.drone_model,
        image_count=mission.image_count,
        area_hectares=mission.area_hectares
    )

    db.add(new_mission)
    db.commit()
    db.refresh(new_mission)

    return new_mission

@router.get("/", response_model=List[MissionResponse])
def get_missions(db: Session = Depends(get_db)):
    missions = db.query(Mission).all()
    return missions

@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.put("/{mission_id}", response_model=MissionResponse)
def update_mission(
    mission_id: int,
    mission_data: MissionCreate,
    db: Session = Depends(get_db)
):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()

    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission.name = mission_data.name
    mission.status = mission_data.status
    mission.drone_model = mission_data.drone_model
    mission.image_count = mission_data.image_count
    mission.area_hectares = mission_data.area_hectares

    db.commit()
    db.refresh(mission)

    return mission

@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    db.delete(mission)
    db.commit()
    return {"message": "Mission deleted successfully"}

__all__ = ["router"]