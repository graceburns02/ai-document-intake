from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.schemas import InvoiceData, ValidationIssue


REQUIRED_FIELDS = ["vendor_name", "invoice_number", "invoice_date", "total"]


def validate_invoice(invoice: InvoiceData) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for field in REQUIRED_FIELDS:
        if getattr(invoice, field) in (None, ""):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="missing_required",
                    message=f"Required field missing: {field}",
                )
            )

    if invoice.subtotal is not None and invoice.tax is not None and invoice.total is not None:
        if invoice.subtotal + invoice.tax != invoice.total:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="total_mismatch",
                    message="Total does not equal subtotal + tax.",
                )
            )

    if invoice.subtotal is not None and invoice.line_items:
        line_sum = sum((item.line_total for item in invoice.line_items), Decimal("0"))
        if line_sum != invoice.subtotal:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    code="line_items_mismatch",
                    message="Line items sum does not match subtotal.",
                )
            )

    if invoice.total is not None and invoice.total <= 0:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="non_positive_total",
                message="Total is zero or negative; review for anomalies.",
            )
        )

    for field in ["invoice_date", "due_date"]:
        value = getattr(invoice, field)
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        code="invalid_date",
                        message=f"Invalid date format for {field}; expected YYYY-MM-DD.",
                    )
                )

    return issues
