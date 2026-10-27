"""Parse a quote request and call the tariff engine."""

import unicodedata
from decimal import Decimal, InvalidOperation

from app.domain.catalog import tariff_snapshot
from app.domain.constants import ClientType, ShippingType
from app.domain.errors import QuoteError
from app.domain.money import money_str
from app.domain.quote_engine import QuoteBreakdown, calculate_shipping_quote

REQUIRED_FIELDS = ("weight_kg", "client_type", "shipping_type")


def build_quote(payload: object) -> dict:
    data = _require_object(payload)
    weight = _parse_weight(data["weight_kg"])
    client_type = _parse_client(data["client_type"])
    shipping_type = _parse_shipping(data["shipping_type"])
    breakdown = calculate_shipping_quote(weight, client_type, shipping_type)
    return _serialize(breakdown)


def build_tariffs() -> dict:
    return tariff_snapshot()


def _require_object(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise QuoteError(
            "VALIDATION_ERROR",
            "La solicitud debe ser un objeto JSON.",
            field="body",
        )
    errors: list[dict[str, str]] = []
    for key in payload:
        if key not in REQUIRED_FIELDS:
            errors.append(
                {"field": str(key), "message": "Este campo no forma parte de la cotización."}
            )
    for key in REQUIRED_FIELDS:
        if key not in payload:
            errors.append({"field": key, "message": "Este campo es obligatorio."})
    if errors:
        raise QuoteError(
            "VALIDATION_ERROR",
            "No se pudo calcular la cotización: revise los campos marcados.",
            errors=errors,
        )
    return payload


def _parse_weight(value: object) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise QuoteError(
            "INVALID_WEIGHT",
            "El peso es obligatorio y debe ser un número decimal.",
            field="weight_kg",
        )
    if isinstance(value, float):
        raise QuoteError(
            "INVALID_WEIGHT",
            "El peso debe enviarse como decimal exacto, no como punto flotante.",
            field="weight_kg",
        )
    if isinstance(value, str):
        text = value.strip().replace(" ", "")
        if not text:
            raise QuoteError(
                "INVALID_WEIGHT",
                "El peso es obligatorio y debe ser un número decimal.",
                field="weight_kg",
            )
        if "," in text and "." in text:
            raise QuoteError(
                "INVALID_WEIGHT",
                "El peso debe ser un número decimal.",
                field="weight_kg",
            )
        if "e" in text.lower():
            raise QuoteError(
                "INVALID_WEIGHT",
                "El peso debe ser un número decimal.",
                field="weight_kg",
            )
        text = text.replace(",", ".")
        try:
            parsed = Decimal(text)
        except InvalidOperation:
            raise QuoteError(
                "INVALID_WEIGHT",
                "El peso debe ser un número decimal.",
                field="weight_kg",
            ) from None
    elif isinstance(value, int):
        parsed = Decimal(value)
    elif isinstance(value, Decimal):
        parsed = value
    else:
        raise QuoteError(
            "INVALID_WEIGHT",
            "El peso debe ser un número decimal.",
            field="weight_kg",
        )

    if not parsed.is_finite():
        raise QuoteError(
            "INVALID_WEIGHT",
            "El peso debe ser un número decimal.",
            field="weight_kg",
        )
    scale = _decimal_places(parsed)
    if scale > 2:
        raise QuoteError(
            "INVALID_WEIGHT_PRECISION",
            "El peso admite como máximo dos decimales.",
            field="weight_kg",
        )
    return parsed


def _decimal_places(value: Decimal) -> int:
    exponent = value.normalize().as_tuple().exponent
    if not isinstance(exponent, int):
        return 99
    return max(0, -exponent)


def _fold(value: object, field: str, message: str) -> str:
    if not isinstance(value, str):
        raise QuoteError("VALIDATION_ERROR", message, field=field)
    folded = unicodedata.normalize("NFD", value.strip())
    without_marks = "".join(char for char in folded if not unicodedata.combining(char))
    return without_marks.upper()


def _parse_client(value: object) -> ClientType:
    message = "Tipo de cliente no válido. Los valores aceptados son NUEVO, FRECUENTE y VIP."
    code = _fold(value, "client_type", message)
    try:
        return ClientType(code)
    except ValueError:
        raise QuoteError("INVALID_CLIENT_TYPE", message, field="client_type") from None


def _parse_shipping(value: object) -> ShippingType:
    message = "Tipo de envío no válido. Los valores aceptados son ESTANDAR y EXPRESS."
    code = _fold(value, "shipping_type", message)
    try:
        return ShippingType(code)
    except ValueError:
        raise QuoteError("INVALID_SHIPPING_TYPE", message, field="shipping_type") from None


def _serialize(quote: QuoteBreakdown) -> dict:
    return {
        "weight_kg": money_str(quote.weight_kg),
        "rate_per_kg": money_str(quote.rate_per_kg),
        "base_fee": money_str(quote.base_fee),
        "weight_charge": money_str(quote.weight_charge),
        "subtotal": money_str(quote.subtotal),
        "client_type": quote.client_type.value,
        "discount_rate": money_str(quote.discount_rate),
        "shipping_type": quote.shipping_type.value,
        "surcharge_rate": money_str(quote.surcharge_rate),
        "surcharge_amount": money_str(quote.surcharge_amount),
        "gross_amount": money_str(quote.gross_amount),
        "discount_amount": money_str(quote.discount_amount),
        "total": money_str(quote.total),
        "currency": quote.currency,
    }
