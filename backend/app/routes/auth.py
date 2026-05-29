from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import AuthResponse, RefreshTokenRequest, TokenResponse, UserCreate, UserLogin
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    user = auth_service.register_user(db, payload)
    access_token, refresh_token = auth_service.create_token_pair(db, user)
    return AuthResponse(user=user, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=AuthResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> AuthResponse:
    user = auth_service.authenticate_user(db, payload)
    access_token, refresh_token = auth_service.create_token_pair(db, user)
    return AuthResponse(user=user, access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_auth(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = auth_service.rotate_refresh_token(db, payload)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
