"""HTTP contract: envelope shape, parsing, and failure modes."""

import asyncio
import json

import pytest
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.errors import _http_error, _validation_error
from app.services.quote_service import _decimal_places, build_quote
from decimal import Decimal


HEADERS = {"Content-Type": "application/json"}


def test_health_and_tariffs(client):
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["success"] is True
    assert health.json()["data"]["status"] == "up"

    tariffs = client.get("/api/v1/tariffs")
    body = tariffs.json()
    assert body["success"] is True
    assert body["data"]["base_fee"] == "5.00"
    assert body["data"]["weight_bands"][0]["rate_per_kg"] == "2.00"
    assert body["data"]["weight_bands"][1]["rate_per_kg"] == "4.00"
    assert body["data"]["client_types"][2]["code"] == "VIP"
    assert body["data"]["shipping_types"][1]["surcharge_rate"] == "0.25"


def test_numeric_json_keeps_exact_decimals(client):
    response = client.post(
        "/api/v1/quotes",
        content=b'{"weight_kg": 0.01, "client_type": "NUEVO", "shipping_type": "ESTANDAR"}',
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["data"]["total"] == "5.02"
    assert response.json()["data"]["weight_kg"] == "0.01"


def test_comma_decimal_and_accented_shipping_are_normalized(client):
    response = client.post(
        "/api/v1/quotes",
        json={"weight_kg": "2,50", "client_type": " vip ", "shipping_type": "estándar"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data"]["weight_kg"] == "2.50"
    assert body["data"]["client_type"] == "VIP"
    assert body["data"]["shipping_type"] == "ESTANDAR"
    assert body["data"]["total"] == "8.00"


def test_missing_fields_list_every_error(client):
    response = client.post("/api/v1/quotes", json={})
    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    fields = {item["field"] for item in body["errors"]}
    assert fields == {"weight_kg", "client_type", "shipping_type"}


def test_malformed_and_empty_json(client):
    malformed = client.post("/api/v1/quotes", content=b"{", headers=HEADERS)
    assert malformed.status_code == 400
    assert malformed.json()["code"] == "INVALID_JSON"
    assert malformed.json()["success"] is False

    empty = client.post("/api/v1/quotes", content=b"   ", headers=HEADERS)
    assert empty.status_code == 400
    assert empty.json()["code"] == "INVALID_JSON"


def test_not_found_and_method_not_allowed(client):
    missing = client.get("/api/v1/no-such-lane")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"
    assert missing.json()["success"] is False

    method = client.get("/api/v1/quotes")
    assert method.status_code == 405
    assert method.json()["code"] == "METHOD_NOT_ALLOWED"


def test_internal_error_does_not_leak_the_exception(client, monkeypatch):
    def boom(_payload):
        raise RuntimeError("secret-boom")

    monkeypatch.setattr("app.api.routes.build_quote", boom)
    response = client.post(
        "/api/v1/quotes",
        json={"weight_kg": "1.00", "client_type": "NUEVO", "shipping_type": "ESTANDAR"},
    )
    assert response.status_code == 500
    assert response.json()["code"] == "INTERNAL_ERROR"
    assert response.json()["success"] is False
    assert "secret-boom" not in response.text


def test_non_object_json(client):
    response = client.post("/api/v1/quotes", content=b"[1, 2]", headers=HEADERS)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_weight_boolean_float_and_exponent_are_rejected():
    with pytest.raises(Exception) as boolean_error:
        build_quote({"weight_kg": True, "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert boolean_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as float_error:
        build_quote({"weight_kg": 1.25, "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert float_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as exponent_error:
        build_quote({"weight_kg": "1e2", "client_type": "NUEVO", "shipping_type": "EXPRESS"})
    assert exponent_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as mixed_error:
        build_quote({"weight_kg": "1,234.50", "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert mixed_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as blank_error:
        build_quote({"weight_kg": "   ", "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert blank_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as nan_error:
        build_quote({"weight_kg": Decimal("NaN"), "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert nan_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as type_error:
        build_quote({"weight_kg": {"kg": 1}, "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert type_error.value.code == "INVALID_WEIGHT"

    with pytest.raises(Exception) as client_error:
        build_quote({"weight_kg": "1.00", "client_type": 1, "shipping_type": "ESTANDAR"})
    assert client_error.value.code == "VALIDATION_ERROR"


def test_integer_weight_uses_the_exact_decimal_path():
    quote = build_quote({"weight_kg": 2, "client_type": "NUEVO", "shipping_type": "ESTANDAR"})
    assert quote["weight_kg"] == "2.00"
    assert quote["total"] == "9.00"


def test_decimal_places_for_non_finite_token():
    assert _decimal_places(Decimal("NaN")) == 99


def test_framework_validation_and_other_http_errors_use_the_envelope():
    validation = asyncio.run(
        _validation_error(
            None,
            RequestValidationError([{"loc": ("body", "weight_kg"), "msg": "bad", "type": "value_error"}]),
        )
    )
    validation_body = json.loads(validation.body)
    assert validation.status_code == 422
    assert validation_body["errors"][0]["field"] == "weight_kg"

    other = asyncio.run(_http_error(None, StarletteHTTPException(status_code=403)))
    other_body = json.loads(other.body)
    assert other.status_code == 403
    assert other_body["code"] == "HTTP_ERROR"
    assert other_body["success"] is False
