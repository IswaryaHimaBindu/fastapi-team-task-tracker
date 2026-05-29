import uuid
from datetime import datetime
from typing import Optional

import bcrypt
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.security import (
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiration,
)
from app.models import RefreshToken, RoleEnum, User
from app.schemas.auth import RefreshTokenRequest, UserCreate, UserLogin


class AuthService:
    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_refresh_token_record(self, db: Session, user_id: int, token_id: str) -> Optional[RefreshToken]:
        return (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.token_id == token_id)
            .first()
        )

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

    def rotate_refresh_token(self, db: Session, payload: RefreshTokenRequest) -> tuple[str, str]:
        try:
            decoded = jwt.decode(payload.refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(decoded.get("sub"))
        token_id = decoded.get("jti")
        if not token_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        refresh_token_record = self.get_refresh_token_record(db, user_id, token_id)
        if not refresh_token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if refresh_token_record.revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if refresh_token_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self._verify_refresh_token(payload.refresh_token, refresh_token_record.token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token mismatch.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        refresh_token_record.revoked = True
        db.add(refresh_token_record)
        db.commit()

        user = db.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found for refresh token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self.create_token_pair(db, user)

    def _hash_refresh_token(self, refresh_token: str) -> str:
        return bcrypt.hashpw(refresh_token.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_refresh_token(self, refresh_token: str, hashed_token: str) -> bool:
        return bcrypt.checkpw(refresh_token.encode("utf-8"), hashed_token.encode("utf-8"))

    def create_refresh_token_record(self, db: Session, user: User, token_id: str, token: str) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user.id,
            token_id=token_id,
            token=self._hash_refresh_token(token),
            expires_at=get_refresh_token_expiration(),
            revoked=False,
        )
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        return refresh_token

    def create_token_pair(self, db: Session, user: User) -> tuple[str, str]:
        token_id = str(uuid.uuid4())
        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id), token_id=token_id)
        self.create_refresh_token_record(db, user, token_id, refresh_token)
        return access_token, refresh_token
