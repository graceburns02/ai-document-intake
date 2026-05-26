# Architecture

## System Diagram

```text
Upload -> Preview -> OCR (pdfplumber/pytesseract) -> LLM extraction (OpenAI) ->
Pydantic schema -> Validation engine -> Human review UI -> JSON/CSV export
```

## Module Responsibilities
- `app.py`: Streamlit UI orchestration and session state
- `src/ocr.py`: document text extraction + preview generation
- `src/extraction.py`: OpenAI structured extraction
- `src/schemas.py`: invoice and line item schema
- `src/validation.py`: business/data-quality checks
- `src/export.py`: JSON/CSV outputs
- `src/utils.py`: parsing helpers

## Data Flow
1. User uploads invoice.
2. Preview rendered for trust and QA.
3. OCR text extracted.
4. LLM maps text to target schema.
5. User edits extracted fields/line items.
6. Validation checks produce warnings.
7. Clean reviewed output exported.

## Failure Modes
- OCR fails due to low-quality scans.
- API key missing or invalid.
- LLM returns partial/incorrect fields.
- Date/amount reconciliation mismatches.
