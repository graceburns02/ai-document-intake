import json

import pytest

from src.extraction import _clean_json_candidate, _extract_first_json_object


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


def test_invalid_json_fallback_raises_decode_error():
    with pytest.raises(json.JSONDecodeError):
        _extract_first_json_object("not-json-output")
