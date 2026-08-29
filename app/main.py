from fastapi import FastAPI

from app.routes import health, missions
from app.db.database import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Challenge IPM API")

app.include_router(health.router)
app.include_router(missions.router)
