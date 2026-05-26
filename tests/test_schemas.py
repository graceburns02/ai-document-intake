from decimal import Decimal

from src.schemas import InvoiceData, LineItem


def test_invoice_schema_creation():
    invoice = InvoiceData(
        vendor_name="Vendor",
        invoice_number="INV-1",
        invoice_date="2026-01-01",
        subtotal=Decimal("100.00"),
        tax=Decimal("10.00"),
        total=Decimal("110.00"),
        line_items=[
            LineItem(
                description="Service",
                quantity=Decimal("2"),
                unit_price=Decimal("50.00"),
                line_total=Decimal("100.00"),
            )
        ],
    )
    assert invoice.vendor_name == "Vendor"
    assert len(invoice.line_items) == 1
