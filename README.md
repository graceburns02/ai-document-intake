# AI Document Intake

**AI Document Intake is a Streamlit app that turns invoices into validated, reviewable structured data ready for export.**

## Problem Statement
Manual invoice processing is slow, error-prone, and difficult to scale across varied vendor formats.

## Target Users
- Accounts payable specialists
- Finance ops teams
- SMB operators without full invoice automation stacks

## Product Workflow
1. Upload invoice document (PDF/PNG/JPG)
2. Preview document
3. Extract raw text with OCR/PDF parsing
4. Run OpenAI structured extraction into invoice schema
5. Human review/edit fields and line items
6. Run validation checks
7. Export clean JSON and CSV

## Features
- Multi-format invoice upload
- OCR + text extraction fallback path
- OpenAI schema-aligned extraction
- Editable review UI for key fields and line items
- Validation warnings for reconciliation and data quality
- JSON and CSV export options

## Screenshots / Demo
- Add screenshots here after running locally.
- Suggested captures: upload state, extracted review state, validation warnings, export buttons.

## Architecture Diagram
```text
[Invoice Upload]
      |
      v
[Preview + OCR/pdf text extraction]
      |
      v
[OpenAI Structured Extraction]
      |
      v
[Pydantic Schema Validation]
      |
      v
[Human Review UI]
      |
      v
[Business Validation Rules]
      |
      v
[JSON/CSV Export]
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Environment Variables
Set in `.env`:
- `OPENAI_API_KEY`: OpenAI API key used for structured extraction.

## Example Output JSON
```json
{
  "vendor_name": "Acme Supplies LLC",
  "customer_name": "Northwind Logistics",
  "invoice_number": "INV-2026-0142",
  "invoice_date": "2026-05-01",
  "due_date": "2026-05-31",
  "subtotal": 1500.0,
  "tax": 120.0,
  "total": 1620.0,
  "payment_terms": "Net 30",
  "line_items": [
    {
      "description": "Warehouse Labels",
      "quantity": 100,
      "unit_price": 10.0,
      "line_total": 1000.0
    }
  ]
}
```


## Extraction Reliability
- The extraction prompt enforces **JSON-only** responses (no markdown/code fences).
- Model responses are cleaned before validation by stripping markdown fences, selecting the first JSON object, and normalizing common placeholders (`""`, `"N/A"`, `"unknown"`) to `null`.
- `line_items` is always normalized to an array (`[]` when missing).
- If schema validation fails, the app shows a portfolio-friendly warning, reveals raw model output in a debug expander, and still opens the manual review editor so users can continue without crashes.
- A one-time repair retry asks the model to convert its prior output into valid schema JSON.

## AI Product Tradeoffs
- **OCR quality limitations:** Low-resolution scans and skew can degrade extraction quality.
- **Hallucination risk:** LLMs can infer plausible-but-wrong values from ambiguous text.
- **Schema-constrained extraction:** Strong schemas improve reliability but may drop uncertain fields.
- **Human-in-the-loop review:** Needed for production trust and auditability.
- **Latency/cost considerations:** OCR + LLM inference introduces variable cost and response time.

## Evaluation Plan
See `docs/eval_plan.md` for metric definitions, dataset design, and iterative quality loop.

## Roadmap
- Batch upload
- Vendor templates
- Duplicate detection
- QuickBooks/NetSuite export
- Eval dashboard
- Confidence scoring

## Sample Data
Use your own invoice files, or create sample invoices in `sample_data/` for demos.
