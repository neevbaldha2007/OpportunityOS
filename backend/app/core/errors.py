import uuid
from typing import Any, Optional, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi.errors import RateLimitExceeded
from app.core.logging import logger


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


def build_error_response(
    code: str,
    message: str,
    status_code: int,
    details: Optional[Any] = None,
    request_id: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
) -> JSONResponse:
    req_id = request_id or str(uuid.uuid4())
    content = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": req_id,
        }
    }
    headers = {"X-Request-ID": req_id}
    if extra_headers:
        headers.update(extra_headers)

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers,
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return build_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        request_id=request_id,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    details = []
    for err in exc.errors():
        loc_parts = list(err.get("loc", []))
        if loc_parts and loc_parts[0] in ("body", "query", "path"):
            loc_parts = loc_parts[1:]
        field = ".".join(str(p) for p in loc_parts) or "body"
        details.append({"field": field, "issue": err.get("msg")})

    return build_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=422,
        details=details,
        request_id=request_id,
    )


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    retry_after = "60"
    return build_error_response(
        code="RATE_LIMITED",
        message=f"Rate limit exceeded: {exc.detail}",
        status_code=429,
        details=None,
        request_id=request_id,
        extra_headers={"Retry-After": retry_after},
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "ERROR")
    headers = {}
    if exc.status_code == 429:
        headers["Retry-After"] = "60"

    return build_error_response(
        code=code,
        message=str(exc.detail),
        status_code=exc.status_code,
        request_id=request_id,
        extra_headers=headers if headers else None,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    logger.error(f"Unhandled server exception [req_id={request_id}]: {exc}", exc_info=True)
    return build_error_response(
        code="INTERNAL_ERROR",
        message="An unexpected internal server error occurred",
        status_code=500,
        request_id=request_id,
    )
