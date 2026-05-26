from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @staticmethod
    def _normalize_scalar(value):
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "" or stripped.lower() in {"n/a", "na", "none", "null", "unknown", "-"}:
                return None
            return stripped
        return value

    @classmethod
    def _to_decimal(cls, value):
        value = cls._normalize_scalar(value)
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            try:
                return Decimal(cleaned)
            except InvalidOperation:
                return value
        return value


class LineItem(StrictBaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = Field(default=None, ge=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)
    line_total: Optional[Decimal] = None

    @field_validator("line_total")
    @classmethod
    def ensure_non_negative_total(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        if value is not None and value < 0:
            raise ValueError("line_total cannot be negative")
        return value

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        return cls._normalize_scalar(value)

    @field_validator("quantity", "unit_price", "line_total", mode="before")
    @classmethod
    def normalize_numeric_fields(cls, value):
        return cls._to_decimal(value)


class InvoiceHeader(StrictBaseModel):
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    payment_terms: Optional[str] = None


class InvoiceTotals(StrictBaseModel):
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    total: Optional[Decimal] = None


class InvoiceData(StrictBaseModel):
    vendor_name: Optional[str] = None
    customer_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    total: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    line_items: List[LineItem] = Field(default_factory=list)

    @field_validator(
        "vendor_name",
        "customer_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "payment_terms",
        mode="before",
    )
    @classmethod
    def normalize_text_fields(cls, value):
        return cls._normalize_scalar(value)

    @field_validator("subtotal", "tax", "total", mode="before")
    @classmethod
    def normalize_totals(cls, value):
        return cls._to_decimal(value)

    @field_validator("line_items", mode="before")
    @classmethod
    def normalize_line_items(cls, value):
        if value is None or value == "":
            return []
        return value


class ValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    severity: str
    code: str
    message: str
