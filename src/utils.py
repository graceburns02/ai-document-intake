from __future__ import annotations

from decimal import Decimal, InvalidOperation


def to_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None


def money(value: Decimal | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"
