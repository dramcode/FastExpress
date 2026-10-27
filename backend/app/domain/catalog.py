"""Public tariff board. Values come from the same constants as the engine."""

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
)
from app.domain.money import money_str


def tariff_snapshot() -> dict:
    heavy_min = LIGHT_LIMIT + Decimal("0.01")
    return {
        "currency": CURRENCY,
        "base_fee": money_str(BASE_FEE),
        "max_weight_kg": money_str(MAX_WEIGHT),
        "min_weight_kg": money_str(MIN_WEIGHT),
        "weight_bands": [
            {
                "min_kg": money_str(MIN_WEIGHT),
                "max_kg": money_str(LIGHT_LIMIT),
                "rate_per_kg": money_str(LIGHT_RATE),
            },
            {
                "min_kg": money_str(heavy_min),
                "max_kg": money_str(MAX_WEIGHT),
                "rate_per_kg": money_str(HEAVY_RATE),
            },
        ],
        "client_types": [
            {"code": "NUEVO", "label": "Nuevo", "discount_rate": "0.00"},
            {"code": "FRECUENTE", "label": "Frecuente", "discount_rate": money_str(DISCOUNT_FRECUENTE)},
            {"code": "VIP", "label": "VIP", "discount_rate": money_str(DISCOUNT_VIP)},
        ],
        "shipping_types": [
            {"code": "ESTANDAR", "label": "Estándar", "surcharge_rate": "0.00"},
            {"code": "EXPRESS", "label": "Express", "surcharge_rate": money_str(SURCHARGE_EXPRESS)},
        ],
    }
