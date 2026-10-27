"""Exact cent rounding for quote amounts."""

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def money_str(value: Decimal) -> str:
    return f"{money(value):.2f}"
