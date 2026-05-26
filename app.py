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

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.25rem; padding-bottom: 2.0rem;}
        .section-card {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1rem 0.75rem 1rem;
            margin-bottom: 0.85rem;
        }
        .section-header {
            font-size: 1.05rem;
            font-weight: 650;
            letter-spacing: 0.01em;
            margin-bottom: 0.25rem;
        }
        .muted-note {color: #475569; font-size: 0.92rem;}
        .pipeline-pill {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-left: 0.35rem;
        }
        .pill-done {background: #dcfce7; color: #166534;}
        .pill-pending {background: #f1f5f9; color: #475569;}
        .pill-fail {background: #fee2e2; color: #991b1b;}
        .warning-box {
            border-left: 4px solid #f59e0b;
            background: #fffbeb;
            border-radius: 6px;
            padding: 0.55rem 0.75rem;
            margin-bottom: 0.45rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("AI Document Intake")
    st.caption("Operations-ready invoice extraction and review")
    st.markdown("---")
    st.markdown("### App Overview")
    st.markdown(
        "Upload an invoice, run OCR + AI extraction, validate results, then export clean structured data for downstream workflows."
    )
    st.markdown("### Supported File Types")
    st.markdown("- PDF\n- PNG\n- JPG/JPEG")
    st.markdown("### Architecture Summary")
    st.markdown("1. OCR parses document content\n2. LLM extracts structured invoice JSON\n3. Validation flags business rule issues\n4. Human reviewer edits and exports")
    st.markdown("### GitHub")
    st.markdown("[Project Repository](https://github.com/)")

st.title("AI Document Intake")
st.caption("Invoice extraction pipeline with human-in-the-loop validation and export.")

uploaded = st.file_uploader("Upload Invoice", type=["pdf", "png", "jpg", "jpeg"])

if uploaded:
    col1, col2 = st.columns([1.15, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">Document Preview</div>', unsafe_allow_html=True)
        st.markdown('<p class="muted-note">Review the source file before extraction.</p>', unsafe_allow_html=True)
        try:
            previews = load_preview_images(uploaded)
            for img in previews:
                st.image(img, use_container_width=True)
        except Exception as exc:
            st.warning(f"Preview unavailable: {exc}")

    with col2:
        st.markdown('<div class="section-header">Extraction Pipeline</div>', unsafe_allow_html=True)
        st.markdown('<p class="muted-note">Run OCR and AI extraction, then inspect status and diagnostics.</p>', unsafe_allow_html=True)

        pipeline_state = st.session_state.get("pipeline_state", {"ocr": "pending", "extract": "pending", "validate": "pending"})

        if st.button("Run OCR + AI Extraction", type="primary", use_container_width=True):
            pipeline_state = {"ocr": "pending", "extract": "pending", "validate": "pending"}
            try:
                raw_text = extract_text_from_file(uploaded)
                pipeline_state["ocr"] = "done"
                st.session_state["raw_text"] = raw_text

                result = extract_invoice_with_fallback(raw_text)
                if result.invoice is not None:
                    st.session_state["invoice"] = result.invoice.model_dump()
                    pipeline_state["extract"] = "done"
                    pipeline_state["validate"] = "done"
                    st.success("Extraction complete — review and refine details below.")
                else:
                    st.session_state["invoice"] = InvoiceData().model_dump()
                    pipeline_state["extract"] = "fail"
                    pipeline_state["validate"] = "pending"
                    st.error(result.error or "Extraction failed. You can still complete review manually.")

                with st.expander("Debug details", expanded=False):
                    st.markdown("**Raw OCR text**")
                    st.text(raw_text[:8000])
                    st.markdown("**Raw model output**")
                    st.code(result.raw_output or "(none)", language="json")
                    st.markdown("**Parsed JSON used for validation**")
                    st.code(result.parsed_output or {}, language="json")
                    st.markdown("**Unknown keys stripped before validation**")
                    st.code(result.unknown_keys or [], language="json")
                    st.markdown("**Validation error**")
                    st.code(result.validation_error or "(none)")
            except Exception as exc:
                pipeline_state["ocr"] = "fail"
                st.error(f"Pipeline failed: {exc}")

            st.session_state["pipeline_state"] = pipeline_state

        pipeline_state = st.session_state.get("pipeline_state", pipeline_state)
        statuses = {"done": ("Completed", "pill-done"), "pending": ("Pending", "pill-pending"), "fail": ("Failed", "pill-fail")}

        for step, label in [("ocr", "OCR"), ("extract", "AI Extraction"), ("validate", "Validation & Parse")]:
            text, css = statuses[pipeline_state.get(step, "pending")]
            st.markdown(
                f'<div class="section-card"><span class="section-header">{label}</span><span class="pipeline-pill {css}">{text}</span></div>',
                unsafe_allow_html=True,
            )

        if "raw_text" in st.session_state:
            with st.expander("Raw extracted text", expanded=False):
                st.text(st.session_state["raw_text"][:8000])

if "invoice" in st.session_state:
    st.divider()
    st.markdown('<div class="section-header">Human Review & Edit</div>', unsafe_allow_html=True)
    st.markdown('<p class="muted-note">Confirm metadata, adjust line items, and export finalized outputs.</p>', unsafe_allow_html=True)
    state = st.session_state["invoice"]

    fields = ["vendor_name", "customer_name", "invoice_number", "invoice_date", "due_date", "payment_terms"]
    cols = st.columns(3, gap="medium")
    for i, field_name in enumerate(fields):
        state[field_name] = cols[i % 3].text_input(field_name.replace("_", " ").title(), value=state.get(field_name) or "")

    money_fields = ["subtotal", "tax", "total"]
    money_cols = st.columns(3, gap="medium")
    for i, field_name in enumerate(money_fields):
        value = state.get(field_name)
        state[field_name] = money_cols[i].text_input(field_name.title(), value="" if value is None else str(value))

    st.markdown("#### Line Items")
    items = state.get("line_items", [])
    df = pd.DataFrame(items or [{"description": "", "quantity": 0, "unit_price": 0, "line_total": 0}])
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "description": st.column_config.TextColumn("Description", help="Item/service description", required=True),
            "quantity": st.column_config.NumberColumn("Qty", min_value=0, step=1),
            "unit_price": st.column_config.NumberColumn("Unit Price", min_value=0.0, format="%.2f"),
            "line_total": st.column_config.NumberColumn("Line Total", min_value=0.0, format="%.2f"),
        },
    )

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

    normalized = {**state, "subtotal": to_decimal(state.get("subtotal")), "tax": to_decimal(state.get("tax")), "total": to_decimal(state.get("total"))}

    invoice = InvoiceData.model_validate(normalized)
    issues = validate_invoice(invoice)

    st.markdown("#### Validation")
    if issues:
        for issue in issues:
            st.markdown(f'<div class="warning-box">⚠️ <strong>[{issue.code}]</strong> {issue.message}</div>', unsafe_allow_html=True)
    else:
        st.success("No validation warnings. This invoice is ready to export.")

    st.markdown("#### Export")
    export_cols = st.columns(3, gap="small")
    export_cols[0].download_button("Download JSON", data=invoice_to_json(invoice), file_name="invoice.json", use_container_width=True)
    export_cols[1].download_button(
        "Download Summary CSV", data=invoice_summary_csv(invoice), file_name="invoice_summary.csv", use_container_width=True
    )
    export_cols[2].download_button(
        "Download Line Items CSV", data=line_items_to_csv(invoice), file_name="line_items.csv", use_container_width=True
    )
