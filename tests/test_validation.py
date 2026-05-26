from decimal import Decimal

from src.schemas import InvoiceData, LineItem
from src.validation import validate_invoice


def test_total_validation_warning():
    invoice = InvoiceData(subtotal=Decimal("100"), tax=Decimal("10"), total=Decimal("200"))
    issues = validate_invoice(invoice)
    assert any(i.code == "total_mismatch" for i in issues)


def test_missing_required_fields_warning():
    invoice = InvoiceData()
    issues = validate_invoice(invoice)
    assert any(i.code == "missing_required" for i in issues)


def test_line_item_subtotal_validation():
    invoice = InvoiceData(
        subtotal=Decimal("100"),
        line_items=[
            LineItem(description="A", quantity=Decimal("1"), unit_price=Decimal("20"), line_total=Decimal("20"))
        ],
    )
    issues = validate_invoice(invoice)
    assert any(i.code == "line_items_mismatch" for i in issues)
