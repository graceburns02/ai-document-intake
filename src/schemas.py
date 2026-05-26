from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class LineItem(BaseModel):
    description: str = Field(..., min_length=1)
    quantity: Decimal = Field(..., ge=0)
    unit_price: Decimal = Field(..., ge=0)
    line_total: Decimal = Field(...)

    @field_validator("line_total")
    @classmethod
    def ensure_non_negative_total(cls, value: Decimal) -> Decimal:
        if value < 0:
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
