from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class LineItem(BaseModel):
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


class InvoiceData(BaseModel):
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


class ValidationIssue(BaseModel):
    severity: str
    code: str
    message: str
