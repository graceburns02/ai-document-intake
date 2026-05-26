from decimal import Decimal

from src.schemas import InvoiceData, InvoiceHeader, InvoiceTotals, LineItem


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


def test_json_schema_forbids_additional_properties_on_all_objects():
    schema = InvoiceData.model_json_schema()

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False

    line_item_schema = LineItem.model_json_schema()
    totals_schema = InvoiceTotals.model_json_schema()
    header_schema = InvoiceHeader.model_json_schema()

    for model_schema in (line_item_schema, totals_schema, header_schema):
        assert model_schema["type"] == "object"
        assert model_schema["additionalProperties"] is False
