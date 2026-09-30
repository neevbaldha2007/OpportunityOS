import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Union
import bcrypt
import jwt
from app.config import settings
from app.core.errors import AppError


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw password against the bcrypt hashed password."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with 12 salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(user_id: Union[uuid.UUID, str], email: str) -> str:
    """Generate an HS256 JWT access token with user_id and email payload."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email.lower(),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate an HS256 JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise AppError("UNAUTHORIZED", "Invalid token type", 401)
        return payload
    except jwt.ExpiredSignatureError:
        raise AppError("UNAUTHORIZED", "Token has expired", 401)
    except jwt.PyJWTError:
        raise AppError("UNAUTHORIZED", "Could not validate credentials", 401)
    except AppError:
        raise
    except Exception:
        raise AppError("UNAUTHORIZED", "Invalid token", 401)
