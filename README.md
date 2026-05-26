# AI Document Intake

AI-powered document intake workflow for extracting, validating, reviewing, and exporting structured invoice data from PDFs and images.

## Live Demo

[https://YOUR-STREAMLIT-APP.streamlit.app](https://ai-document-intake.streamlit.app/)

## GitHub Repository

https://github.com/graceburns02/ai-document-intake

---

## Overview

AI Document Intake is a production-style AI workflow application that combines OCR, structured LLM extraction, schema validation, and human review to transform unstructured invoices into structured exportable data.

The application demonstrates practical AI workflow design patterns including:
- OCR + document ingestion
- structured extraction using LLMs
- schema-constrained outputs
- validation and reconciliation checks
- human-in-the-loop review workflows
- structured export pipelines

This project was built as an applied AI product workflow demonstration focused on operational reliability rather than fully autonomous processing.

---

## Features

- PDF and image invoice upload
- OCR-based text extraction
- Structured invoice field extraction
- Line item parsing
- Schema validation
- Validation and reconciliation checks
- Human review/edit workflow
- CSV and JSON export
- Error handling and extraction fallback workflows

---

## Screenshots

### Upload & Extraction Workflow

Upload invoice PDFs or images and extract structured invoice fields using OCR and LLM-based extraction.

![Upload & Extraction](screenshots/upload-extraction.png)

---

### Human Review & Validation

Review extracted invoice data, edit fields manually, and validate totals before export.

![Human Review](screenshots/human-review-validation.png)

---

### Structured Export

Export reviewed invoice data into structured CSV format for downstream workflows.

![CSV Export](screenshots/csv-export.png)

---

## Architecture

```text
Upload Document
        ↓
OCR/Text Extraction
        ↓
LLM Structured Extraction
        ↓
Schema Validation
        ↓
Human Review Workflow
        ↓
Structured Export
```

### Core Components

- Streamlit frontend for workflow orchestration and document review
- OCR pipeline for PDF/image text extraction
- OpenAI-powered structured extraction workflow
- Pydantic schema validation layer
- Validation and reconciliation engine
- Human review/edit workflow
- CSV/JSON export utilities

---

## AI Product Tradeoffs

This application intentionally uses a human-in-the-loop workflow rather than fully autonomous extraction.

Key considerations:
- OCR quality varies significantly across invoice formats and scan quality
- LLM extraction can omit or hallucinate fields
- Schema-constrained outputs improve reliability but do not eliminate extraction failures
- Validation and reconciliation checks help identify extraction inconsistencies
- Human review is critical for high-confidence financial workflows
- Structured outputs improve downstream integrations and automation reliability

The application prioritizes operational reliability and reviewability over fully autonomous processing.

---

## Validation Workflow

The application includes multiple validation layers to improve extraction reliability:

- Required field validation
- Invoice total reconciliation
- Date format validation
- Numeric normalization
- Line item structure validation
- Human review/edit workflow for correction and approval

When schema validation fails, the application gracefully falls back to manual review instead of failing the workflow.

---

## Example Workflow

1. Upload invoice PDF or image
2. Extract OCR text from the document
3. Run structured LLM extraction
4. Validate extracted fields
5. Review/edit invoice data manually if needed
6. Export structured CSV or JSON output

---

## Example Output

```json
{
  "vendor_name": "Cypress North",
  "customer_name": "Beatty-Hegmann",
  "invoice_number": "INV-00001",
  "invoice_date": "2019-06-03",
  "due_date": "2019-06-18",
  "subtotal": 1375.00,
  "tax": 120.31,
  "total": 1495.31,
  "payment_terms": "15 Days",
  "line_items": [
    {
      "description": "Fee",
      "quantity": 2.0,
      "unit_price": 100.00,
      "line_total": 200.00
    }
  ]
}
```

---

## Local Development

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

---

## Environment Variables

Create a `.streamlit/secrets.toml` file locally or configure the following secret in Streamlit Community Cloud:

```toml
OPENAI_API_KEY="your_api_key"
```

---

## Deployment

The application is deployed using Streamlit Community Cloud.

System dependencies required for OCR/PDF support:

- tesseract-ocr
- poppler-utils

---

## Repository Structure

```text
ai-document-intake/
│
├── app.py
├── requirements.txt
├── packages.txt
├── README.md
│
├── screenshots/
│   ├── upload-extraction.png
│   ├── human-review-validation.png
│   └── csv-export.png
│
├── src/
│   ├── extraction.py
│   ├── ocr.py
│   ├── schemas.py
│   ├── validation.py
│   ├── export.py
│   └── utils.py
│
├── tests/
│   ├── test_validation.py
│   └── test_schemas.py
│
└── docs/
    ├── architecture.md
    ├── eval_plan.md
    └── product_brief.md
```

---

## Evaluation Considerations

Key evaluation metrics for production deployment would include:

- Header field extraction accuracy
- Line item extraction accuracy
- Total reconciliation accuracy
- OCR extraction reliability
- Average processing latency
- Human review correction rate

Additional evaluation improvements could include:
- confidence scoring
- benchmark datasets
- extraction drift monitoring
- vendor-specific evaluation workflows

---

## Roadmap

- Batch invoice processing
- Confidence scoring
- Vendor-specific extraction templates
- Duplicate invoice detection
- Audit logging
- QuickBooks / NetSuite export
- Evaluation dashboard
- Feedback-driven extraction improvement
- Multi-document workflow orchestration

---

## Tech Stack

- Python
- Streamlit
- OpenAI API
- Pydantic
- pandas
- pytesseract
- pdf2image
- Pillow

---

## Why This Project

This project was built to demonstrate practical applied AI workflow design patterns relevant to enterprise AI systems, including:
- OCR ingestion pipelines
- schema-constrained LLM extraction
- operational validation workflows
- human-in-the-loop review systems
- structured export pipelines
- production-oriented error handling

The focus was on building a realistic AI operations workflow rather than a simple chatbot or prompt wrapper.

---

## License

MIT License
