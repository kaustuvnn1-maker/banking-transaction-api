import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_var.get() or "N/A"
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None) or "N/A",
        }

        for key in ("method", "path", "status_code", "duration_ms", "query_params", "error"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


logger = logging.getLogger("bankapi")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = logging.FileHandler(os.path.join(logs_dir, "applog.log"), mode="a")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

logger.addFilter(CorrelationIdFilter())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        correlation_id = (
            request.headers.get("x-correlation-id")
            or request.headers.get("correlation_id")
            or str(uuid.uuid4())
        )
        request.state.correlation_id = correlation_id
        token = correlation_id_var.set(correlation_id)

        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
            },
        )

        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
            )
            raise
        finally:
            correlation_id_var.reset(token)
