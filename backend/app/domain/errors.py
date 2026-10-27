"""Domain and validation errors returned as a stable envelope."""


class QuoteError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        errors: list[dict[str, str]] | None = None,
        field: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        if errors is None:
            errors = [{"field": field or "body", "message": message}] if field or message else []
        self.errors = errors
