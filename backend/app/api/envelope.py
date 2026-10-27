"""HTTP envelope shared by every endpoint."""

from fastapi.responses import JSONResponse


def envelope(
    *,
    success: bool,
    message: str,
    code: str,
    data: dict | None = None,
    errors: list[dict[str, str]] | None = None,
    status_code: int = 200,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": success,
            "message": message,
            "code": code,
            "data": data,
            "errors": errors or [],
        },
    )
