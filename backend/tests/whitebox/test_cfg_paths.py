"""White-box basis paths for calculate_shipping_quote. V(G) = 7."""

from decimal import Decimal

import pytest

from app.domain.constants import ClientType, ShippingType
from app.domain.errors import QuoteError
from app.domain.quote_engine import calculate_shipping_quote


def _quote(weight: str, client: ClientType, shipping: ShippingType):
    return calculate_shipping_quote(Decimal(weight), client, shipping)


def test_path_1_weight_below_minimum():
    with pytest.raises(QuoteError) as caught:
        _quote("0.00", ClientType.NUEVO, ShippingType.ESTANDAR)
    assert caught.value.code == "WEIGHT_BELOW_MINIMUM"


def test_path_2_weight_above_maximum():
    with pytest.raises(QuoteError) as caught:
        _quote("20.01", ClientType.VIP, ShippingType.EXPRESS)
    assert caught.value.code == "WEIGHT_LIMIT_EXCEEDED"
    assert "Límite excedido" in caught.value.message


def test_path_3_light_nuevo_estandar_boundary():
    quote = _quote("5.00", ClientType.NUEVO, ShippingType.ESTANDAR)
    assert quote.rate_per_kg == Decimal("2.00")
    assert quote.weight_charge == Decimal("10.00")
    assert quote.subtotal == Decimal("15.00")
    assert quote.surcharge_amount == Decimal("0.00")
    assert quote.discount_amount == Decimal("0.00")
    assert quote.total == Decimal("15.00")


def test_path_4_light_frecuente_express_rounds_half_up():
    quote = _quote("5.00", ClientType.FRECUENTE, ShippingType.EXPRESS)
    assert quote.subtotal == Decimal("15.00")
    assert quote.surcharge_rate == Decimal("0.25")
    assert quote.surcharge_amount == Decimal("3.75")
    assert quote.gross_amount == Decimal("18.75")
    assert quote.discount_rate == Decimal("0.10")
    assert quote.discount_amount == Decimal("1.88")
    assert quote.total == Decimal("16.87")


def test_path_5_light_vip_estandar():
    quote = _quote("5.00", ClientType.VIP, ShippingType.ESTANDAR)
    assert quote.discount_rate == Decimal("0.20")
    assert quote.surcharge_rate == Decimal("0.00")
    assert quote.discount_amount == Decimal("3.00")
    assert quote.total == Decimal("12.00")


def test_path_6_heavy_nuevo_estandar_boundary():
    quote = _quote("5.01", ClientType.NUEVO, ShippingType.ESTANDAR)
    assert quote.rate_per_kg == Decimal("4.00")
    assert quote.weight_charge == Decimal("20.04")
    assert quote.subtotal == Decimal("25.04")
    assert quote.total == Decimal("25.04")


def test_path_7_heavy_frecuente_express():
    quote = _quote("5.01", ClientType.FRECUENTE, ShippingType.EXPRESS)
    assert quote.subtotal == Decimal("25.04")
    assert quote.surcharge_amount == Decimal("6.26")
    assert quote.gross_amount == Decimal("31.30")
    assert quote.discount_amount == Decimal("3.13")
    assert quote.total == Decimal("28.17")
