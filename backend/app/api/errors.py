"""Translate domain and framework errors into the API envelope."""

import json
import logging
from decimal import Decimal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.envelope import envelope
from app.domain.errors import QuoteError

logger = logging.getLogger("fastexpress")

DOMAIN_STATUS = {
    "VALIDATION_ERROR": 422,
    "INVALID_WEIGHT": 422,
    "INVALID_WEIGHT_PRECISION": 422,
    "WEIGHT_BELOW_MINIMUM": 422,
    "WEIGHT_LIMIT_EXCEEDED": 422,
    "INVALID_CLIENT_TYPE": 422,
    "INVALID_SHIPPING_TYPE": 422,
}


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(QuoteError, _quote_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(Exception, _unexpected_error)


def _decimal_from_token(token: str) -> Decimal:
    return Decimal(token)


async def read_json_object(request: Request) -> object:
    raw = await request.body()
    if not raw or not raw.strip():
        raise QuoteError(
            "INVALID_JSON",
            "El cuerpo de la solicitud no es JSON válido.",
            field="body",
        )
    try:
        return json.loads(raw.decode("utf-8"), parse_float=_decimal_from_token, parse_int=_decimal_from_token)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise QuoteError(
            "INVALID_JSON",
            "El cuerpo de la solicitud no es JSON válido.",
            field="body",
        ) from None


async def _quote_error(_request: Request, exc: QuoteError) -> JSONResponse:
    status_code = 400 if exc.code == "INVALID_JSON" else DOMAIN_STATUS.get(exc.code, 422)
    return envelope(
        success=False,
        message=exc.message,
        code=exc.code,
        errors=exc.errors,
        status_code=status_code,
    )


async def _validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for item in exc.errors():
        location = [str(part) for part in item.get("loc", []) if part not in {"body", "query", "path"}]
        field = ".".join(location) or "body"
        errors.append({"field": field, "message": "El valor enviado no es válido."})
    return envelope(
        success=False,
        message="No se pudo calcular la cotización: revise los campos marcados.",
        code="VALIDATION_ERROR",
        errors=errors,
        status_code=422,
    )


async def _http_error(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        code = "NOT_FOUND"
        message = "No existe ese recurso."
    elif exc.status_code == 405:
        code = "METHOD_NOT_ALLOWED"
        message = "Método no permitido para este recurso."
    else:
        code = "HTTP_ERROR"
        message = "No se pudo completar la solicitud."
    return envelope(success=False, message=message, code=code, status_code=exc.status_code)


async def _unexpected_error(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled quote error", exc_info=exc)
    return envelope(
        success=False,
        message="Ocurrió un error interno al calcular la cotización.",
        code="INTERNAL_ERROR",
        status_code=500,
    )
