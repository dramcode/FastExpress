"""Tariff constants from the FastExpress business rules."""

from decimal import Decimal
from enum import Enum


class ClientType(str, Enum):
    NUEVO = "NUEVO"
    FRECUENTE = "FRECUENTE"
    VIP = "VIP"


class ShippingType(str, Enum):
    ESTANDAR = "ESTANDAR"
    EXPRESS = "EXPRESS"


BASE_FEE = Decimal("5.00")
MIN_WEIGHT = Decimal("0.01")
LIGHT_LIMIT = Decimal("5.00")
MAX_WEIGHT = Decimal("20.00")
LIGHT_RATE = Decimal("2.00")
HEAVY_RATE = Decimal("4.00")
DISCOUNT_FRECUENTE = Decimal("0.10")
DISCOUNT_VIP = Decimal("0.20")
SURCHARGE_EXPRESS = Decimal("0.25")
CURRENCY = "USD"
