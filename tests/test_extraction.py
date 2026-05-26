import json

import pytest

from src.extraction import _clean_json_candidate, _extract_first_json_object, _strip_unknown_keys
from src.schemas import InvoiceData


def test_markdown_wrapped_json_is_parsed():
    raw = """```json
{"vendor_name":"Acme","line_items":[]}
```"""
    data = _clean_json_candidate(raw)
    assert data["vendor_name"] == "Acme"
    assert data["line_items"] == []


def test_numeric_strings_with_dollar_signs_are_normalized_to_numbers():
    raw = '{"subtotal":"$12.00","line_items":[{"quantity":"2","unit_price":"$3.50","line_total":"$7.00"}]}'
    data = _clean_json_candidate(raw)
    assert data["subtotal"] == 12.0
    assert data["line_items"][0]["quantity"] == 2.0
    assert data["line_items"][0]["unit_price"] == 3.5
    assert data["line_items"][0]["line_total"] == 7.0


def test_missing_line_items_defaults_to_array():
    raw = '{"vendor_name":"Acme"}'
    data = _clean_json_candidate(raw)
    assert data["line_items"] == []


def test_empty_and_na_values_are_normalized_to_none():
    raw = '{"vendor_name":"N/A","invoice_number":"","line_items":[]}'
    data = _clean_json_candidate(raw)
    invoice = InvoiceData.model_validate(data)
    assert invoice.vendor_name is None
    assert invoice.invoice_number is None


def test_strip_unknown_keys_removes_extra_fields_and_nested_extras():
    payload = {
        "vendor_name": "Acme",
        "unexpected": "value",
        "line_items": [{"description": "A", "extra": "x"}],
    }
    stripped, unknown = _strip_unknown_keys(payload)
    assert "unexpected" not in stripped
    assert stripped["line_items"][0] == {"description": "A"}
    assert "unexpected" in unknown
    assert "line_items[0].extra" in unknown


def test_null_fields_and_empty_line_items_validate():
    data = {
        "vendor_name": None,
        "customer_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "due_date": None,
        "subtotal": None,
        "tax": None,
        "total": None,
        "payment_terms": None,
        "line_items": [],
    }
    invoice = InvoiceData.model_validate(data)
    assert invoice.line_items == []


def test_invalid_json_fallback_raises_decode_error():
    with pytest.raises(json.JSONDecodeError):
        _extract_first_json_object("not-json-output")
