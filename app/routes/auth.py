from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse
from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    # if data.username != "admin" or data.password != "123456":
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid username or password"
    #     )

    expiration = datetime.now(timezone.utc) + timedelta(hours=1)

    token = jwt.encode(
        {
            "sub": data.username,
            "exp": expiration
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }