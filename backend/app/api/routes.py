"""FastExpress HTTP routes."""

from fastapi import APIRouter, Request

from app.api.envelope import envelope
from app.api.errors import read_json_object
from app.services.quote_service import build_quote, build_tariffs

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return envelope(
        success=True,
        message="Servicio disponible.",
        code="OK",
        data={"status": "up", "service": "fastexpress-quotes"},
    )


@router.get("/tariffs")
async def tariffs() -> dict:
    return envelope(
        success=True,
        message="Tarifario disponible.",
        code="OK",
        data=build_tariffs(),
    )


@router.post("/quotes")
async def create_quote(request: Request):
    payload = await read_json_object(request)
    quote = build_quote(payload)
    return envelope(
        success=True,
        message="Cotización calculada correctamente.",
        code="QUOTE_CALCULATED",
        data=quote,
    )
