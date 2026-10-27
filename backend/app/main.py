"""FastExpress quote API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_error_handlers
from app.api.routes import router

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="FastExpress Quotes",
        version="1.0.0",
        summary="Shipping quote and discount module.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
