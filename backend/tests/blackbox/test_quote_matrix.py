"""Black-box matrix through the public quote endpoint."""

import json

import pytest

HEADERS = {"Content-Type": "application/json"}


def post_quote(client, payload: dict):
    return client.post("/api/v1/quotes", content=json.dumps(payload), headers=HEADERS)


def assert_total(client, payload: dict, total: str, rate: str):
    response = post_quote(client, payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["code"] == "QUOTE_CALCULATED"
    assert body["message"] == "Cotización calculada correctamente."
    assert body["errors"] == []
    assert body["data"]["total"] == total
    assert body["data"]["rate_per_kg"] == rate
    assert body["data"]["currency"] == "USD"
    assert body["data"]["base_fee"] == "5.00"


def assert_rejected(client, payload: dict, code: str):
    response = post_quote(client, payload)
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["code"] == code
    assert body["data"] is None
    assert body["errors"]


@pytest.mark.parametrize(
    ("weight", "total", "rate"),
    [
        ("2.50", "10.00", "2.00"),
        ("10.00", "45.00", "4.00"),
    ],
)
def test_equivalence_valid_weight_partitions(client, weight, total, rate):
    assert_total(
        client,
        {"weight_kg": weight, "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
        total,
        rate,
    )


def test_equivalence_weight_below_minimum_interior(client):
    assert_rejected(
        client,
        {"weight_kg": "-5.00", "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
        "WEIGHT_BELOW_MINIMUM",
    )


def test_equivalence_weight_above_maximum_interior(client):
    assert_rejected(
        client,
        {"weight_kg": "25.00", "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
        "WEIGHT_LIMIT_EXCEEDED",
    )


def test_equivalence_weight_not_numeric(client):
    assert_rejected(
        client,
        {"weight_kg": "abc", "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
        "INVALID_WEIGHT",
    )


def test_equivalence_weight_too_many_decimals(client):
    assert_rejected(
        client,
        {"weight_kg": "1.234", "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
        "INVALID_WEIGHT_PRECISION",
    )


@pytest.mark.parametrize(
    ("weight", "code", "total", "rate"),
    [
        ("0.00", "WEIGHT_BELOW_MINIMUM", None, None),
        ("0.01", None, "5.02", "2.00"),
        ("5.00", None, "15.00", "2.00"),
        ("5.01", None, "25.04", "4.00"),
        ("20.00", None, "85.00", "4.00"),
        ("20.01", "WEIGHT_LIMIT_EXCEEDED", None, None),
    ],
)
def test_bva_weight_and_resulting_amount(client, weight, code, total, rate):
    payload = {"weight_kg": weight, "client_type": "NUEVO", "shipping_type": "ESTANDAR"}
    if code:
        assert_rejected(client, payload, code)
        assert post_quote(client, payload).json()["data"] is None
        return
    assert_total(client, payload, total, rate)


@pytest.mark.parametrize(
    ("client_type", "shipping_type", "total"),
    [
        ("NUEVO", "ESTANDAR", "7.00"),
        ("NUEVO", "EXPRESS", "8.75"),
        ("FRECUENTE", "ESTANDAR", "6.30"),
        ("FRECUENTE", "EXPRESS", "7.87"),
        ("VIP", "ESTANDAR", "5.60"),
        ("VIP", "EXPRESS", "7.00"),
    ],
)
def test_decision_table_client_and_shipping(client, client_type, shipping_type, total):
    assert_total(
        client,
        {"weight_kg": "1.00", "client_type": client_type, "shipping_type": shipping_type},
        total,
        "2.00",
    )


def test_invalid_client_and_shipping_are_outside_the_decision_table(client):
    assert_rejected(
        client,
        {"weight_kg": "1.00", "client_type": "REGULAR", "shipping_type": "ESTANDAR"},
        "INVALID_CLIENT_TYPE",
    )
    assert_rejected(
        client,
        {"weight_kg": "1.00", "client_type": "NUEVO", "shipping_type": "URGENTE"},
        "INVALID_SHIPPING_TYPE",
    )


def test_amount_is_not_an_input_field(client):
    response = post_quote(
        client,
        {
            "weight_kg": "1.00",
            "client_type": "NUEVO",
            "shipping_type": "ESTANDAR",
            "monto": "10.00",
        },
    )
    body = response.json()
    assert response.status_code == 422
    assert body["success"] is False
    assert body["code"] == "VALIDATION_ERROR"
    assert any(item["field"] == "monto" for item in body["errors"])
