from typing import Optional

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiration,
)
from app.models import RefreshToken, RoleEnum, User
from app.schemas.auth import UserCreate, UserLogin


class AuthService:
    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def register_user(self, db: Session, payload: UserCreate) -> User:
        if self.get_user_by_email(db, payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            hashed_password=self._hash_password(payload.password),
            role=RoleEnum.MEMBER,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, payload: UserLogin) -> User:
        user = self.get_user_by_email(db, payload.email)
        if not user or not self._verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def create_refresh_token_record(self, db: Session, user: User, token: str) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user.id,
            token=token,
            expires_at=get_refresh_token_expiration(),
            revoked=False,
        )
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        return refresh_token

    def create_token_pair(self, db: Session, user: User) -> tuple[str, str]:
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))
        self.create_refresh_token_record(db, user, refresh_token)
        return access_token, refresh_token
