from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.extraction import extract_invoice_with_fallback
from src.export import invoice_summary_csv, invoice_to_json, line_items_to_csv
from src.ocr import extract_text_from_file, load_preview_images
from src.schemas import InvoiceData, LineItem
from src.utils import to_decimal
from src.validation import validate_invoice

load_dotenv()

st.set_page_config(page_title="AI Document Intake", layout="wide")
st.title("AI Document Intake")
st.caption("Upload an invoice, extract structured data with AI, review, validate, and export.")

uploaded = st.file_uploader("Upload invoice", type=["pdf", "png", "jpg", "jpeg"])

if uploaded:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Document Preview")
        try:
            previews = load_preview_images(uploaded)
            for img in previews:
                st.image(img, use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not render preview: {exc}")

    with col2:
        st.subheader("Extraction Pipeline")
        if st.button("Run OCR + AI Extraction", type="primary"):
            try:
                raw_text = extract_text_from_file(uploaded)
                st.session_state["raw_text"] = raw_text
                result = extract_invoice_with_fallback(raw_text)
                if result.invoice is not None:
                    st.session_state["invoice"] = result.invoice.model_dump()
                    st.success("Extraction complete. Review and edit below.")
                else:
                    st.session_state["invoice"] = InvoiceData().model_dump()
                    st.warning(result.error or "Extraction failed. You can still review/edit manually.")
                    if result.raw_output:
                        with st.expander("Debug: raw model output", expanded=False):
                            st.code(result.raw_output, language="json")
            except Exception as exc:
                st.error(str(exc))

        if "raw_text" in st.session_state:
            with st.expander("Raw extracted text", expanded=False):
                st.text(st.session_state["raw_text"][:8000])

if "invoice" in st.session_state:
    st.divider()
    st.subheader("Human Review & Edit")
    state = st.session_state["invoice"]

    fields = [
        "vendor_name",
        "customer_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "payment_terms",
    ]
    cols = st.columns(3)
    for i, f in enumerate(fields):
        state[f] = cols[i % 3].text_input(f.replace("_", " ").title(), value=state.get(f) or "")

    money_fields = ["subtotal", "tax", "total"]
    mcols = st.columns(3)
    for i, f in enumerate(money_fields):
        value = state.get(f)
        state[f] = mcols[i].text_input(f.title(), value="" if value is None else str(value))

    st.markdown("#### Line Items")
    items = state.get("line_items", [])
    df = pd.DataFrame(items or [{"description": "", "quantity": 0, "unit_price": 0, "line_total": 0}])
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    parsed_items = []
    for row in edited_df.to_dict(orient="records"):
        if not str(row.get("description", "")).strip():
            continue
        parsed_items.append(
            LineItem(
                description=str(row.get("description", "")).strip(),
                quantity=to_decimal(row.get("quantity")) or Decimal("0"),
                unit_price=to_decimal(row.get("unit_price")) or Decimal("0"),
                line_total=to_decimal(row.get("line_total")) or Decimal("0"),
            ).model_dump()
        )
    state["line_items"] = parsed_items

    normalized = {
        **state,
        "subtotal": to_decimal(state.get("subtotal")),
        "tax": to_decimal(state.get("tax")),
        "total": to_decimal(state.get("total")),
    }

    invoice = InvoiceData.model_validate(normalized)
    issues = validate_invoice(invoice)

    st.markdown("#### Validation")
    if issues:
        for issue in issues:
            st.warning(f"[{issue.code}] {issue.message}")
    else:
        st.success("No validation warnings.")

    st.markdown("#### Export")
    st.download_button("Download JSON", data=invoice_to_json(invoice), file_name="invoice.json")
    st.download_button("Download Summary CSV", data=invoice_summary_csv(invoice), file_name="invoice_summary.csv")
    st.download_button("Download Line Items CSV", data=line_items_to_csv(invoice), file_name="line_items.csv")
