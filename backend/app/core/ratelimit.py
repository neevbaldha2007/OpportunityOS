import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings


def get_rate_limit_key(request: Request) -> str:
    """Extract user identifier from JWT Bearer token if present, else fallback to client IP."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_exp": False},
            )
            sub = payload.get("sub")
            if sub:
                return f"user:{sub}"
        except Exception:
            pass
    return get_remote_address(request) or "127.0.0.1"


limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["120/minute"],
)
