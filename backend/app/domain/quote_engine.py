"""Core tariff algorithm for FastExpress.

The control-flow graph of ``calculate_shipping_quote`` is the white-box
subject. Decisions, in source order:

1. weight < 0.01 kg
2. weight > 20.00 kg
3. weight <= 5.00 kg
4. client is NUEVO
5. client is FRECUENTE
6. shipping is EXPRESS

Cyclomatic complexity V(G) = 7 (six predicates plus one).
"""

from dataclasses import dataclass
from decimal import Decimal

from app.domain.constants import (
    BASE_FEE,
    CURRENCY,
    DISCOUNT_FRECUENTE,
    DISCOUNT_VIP,
    HEAVY_RATE,
    LIGHT_LIMIT,
    LIGHT_RATE,
    MAX_WEIGHT,
    MIN_WEIGHT,
    SURCHARGE_EXPRESS,
    ClientType,
    ShippingType,
)
from app.domain.errors import QuoteError
from app.domain.money import money


@dataclass(frozen=True)
class QuoteBreakdown:
    weight_kg: Decimal
    rate_per_kg: Decimal
    base_fee: Decimal
    weight_charge: Decimal
    subtotal: Decimal
    client_type: ClientType
    discount_rate: Decimal
    shipping_type: ShippingType
    surcharge_rate: Decimal
    surcharge_amount: Decimal
    gross_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    currency: str = CURRENCY


def calculate_shipping_quote(
    weight_kg: Decimal,
    client_type: ClientType,
    shipping_type: ShippingType,
) -> QuoteBreakdown:
    if weight_kg < MIN_WEIGHT:
        raise QuoteError(
            "WEIGHT_BELOW_MINIMUM",
            "El peso debe estar entre 0.01 kg y 20.00 kg.",
            field="weight_kg",
        )
    if weight_kg > MAX_WEIGHT:
        raise QuoteError(
            "WEIGHT_LIMIT_EXCEEDED",
            "Envío rechazado. Límite excedido: el peso máximo es 20.00 kg.",
            field="weight_kg",
        )

    if weight_kg <= LIGHT_LIMIT:
        rate_per_kg = LIGHT_RATE
    else:
        rate_per_kg = HEAVY_RATE

    weight_charge = money(weight_kg * rate_per_kg)
    subtotal = money(BASE_FEE + weight_charge)

    if client_type == ClientType.NUEVO:
        discount_rate = Decimal("0.00")
    elif client_type == ClientType.FRECUENTE:
        discount_rate = DISCOUNT_FRECUENTE
    else:
        discount_rate = DISCOUNT_VIP

    if shipping_type == ShippingType.EXPRESS:
        surcharge_rate = SURCHARGE_EXPRESS
    else:
        surcharge_rate = Decimal("0.00")

    surcharge_amount = money(subtotal * surcharge_rate)
    gross_amount = money(subtotal + surcharge_amount)
    discount_amount = money(gross_amount * discount_rate)
    total = money(gross_amount - discount_amount)

    return QuoteBreakdown(
        weight_kg=money(weight_kg),
        rate_per_kg=rate_per_kg,
        base_fee=BASE_FEE,
        weight_charge=weight_charge,
        subtotal=subtotal,
        client_type=client_type,
        discount_rate=discount_rate,
        shipping_type=shipping_type,
        surcharge_rate=surcharge_rate,
        surcharge_amount=surcharge_amount,
        gross_amount=gross_amount,
        discount_amount=discount_amount,
        total=total,
    )
