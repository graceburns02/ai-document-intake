from __future__ import annotations

import json

import pandas as pd

from src.schemas import InvoiceData


def invoice_to_json(invoice: InvoiceData) -> str:
    return invoice.model_dump_json(indent=2)


def line_items_to_csv(invoice: InvoiceData) -> str:
    rows = [item.model_dump() for item in invoice.line_items]
    if not rows:
        rows = [{"description": "", "quantity": "", "unit_price": "", "line_total": ""}]
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def invoice_summary_csv(invoice: InvoiceData) -> str:
    payload = invoice.model_dump()
    payload["line_items"] = json.dumps(payload["line_items"])
    return pd.DataFrame([payload]).to_csv(index=False)
