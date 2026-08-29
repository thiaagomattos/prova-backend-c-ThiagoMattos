from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.database import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    drone_model = Column(String(100), nullable=False)
    image_count = Column(Integer, nullable=False)
    area_hectares = Column(Float, nullable=False)