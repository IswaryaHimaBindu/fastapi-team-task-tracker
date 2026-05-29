from __future__ import annotations

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class GlobalExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except RequestValidationError as exc:
            return self._handle_validation_error(exc)
        except StarletteHTTPException as exc:
            return self._handle_http_exception(exc)
        except Exception:
            return self._handle_internal_error()

    @staticmethod
    def _handle_validation_error(exc: RequestValidationError) -> JSONResponse:
        errors = exc.errors()
        message = "Validation failed"
        if errors:
            message = errors[0].get("msg", message)
        return JSONResponse(
            status_code=400,
            content={
                "status": 400,
                "code": "VALIDATION_ERROR",
                "message": message,
            },
        )

    @staticmethod
    def _handle_http_exception(exc: StarletteHTTPException) -> JSONResponse:
        status_code = exc.status_code
        detail = exc.detail
        message = detail if isinstance(detail, str) else str(detail)
        if status_code == 401:
            error_code = "AUTHENTICATION_ERROR"
        elif status_code == 403:
            error_code = "PERMISSION_DENIED"
        elif status_code == 422:
            error_code = "VALIDATION_ERROR"
        else:
            error_code = "HTTP_ERROR"
        return JSONResponse(
            status_code=status_code,
            content={
                "status": status_code,
                "code": error_code,
                "message": message,
            },
        )

    @staticmethod
    def _handle_internal_error() -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "status": 500,
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
        )
