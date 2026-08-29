from fastapi import FastAPI

from app.routes import health, missions, auth, processing
from app.db.database import Base, engine
from app.models.mission import Mission
from app.models.processing import ProcessingHistory
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Challenge IPM API")

app.include_router(health.router)
app.include_router(missions.router)
app.include_router(auth.router)
app.include_router(processing.router)