import uuid
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.core.security import decode_access_token
from app.core.errors import AppError

security = HTTPBearer(auto_error=False)


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency to extract and authenticate the current user via JWT bearer token."""
    token = None
    if auth and auth.credentials:
        token = auth.credentials
    elif authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]

    if not token:
        raise AppError("UNAUTHORIZED", "Missing or invalid authorization header", 401)

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AppError("UNAUTHORIZED", "Invalid token payload", 401)

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AppError("UNAUTHORIZED", "Invalid user ID format in token", 401)

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user or not user.is_active:
        raise AppError("UNAUTHORIZED", "User not found or inactive", 401)

    return user
