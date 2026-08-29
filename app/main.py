from fastapi import FastAPI

from db.database import Base, engine

app = FastAPI(title="Challenge IPM API")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
