# Product Brief: AI Document Intake

## Problem
Finance and operations teams spend significant time manually keying invoice data into downstream systems.

## Users
- AP specialists
- Finance operations analysts
- SMB operators handling invoices without ERP automation

## Pain Points
- Manual data entry errors
- Slow throughput during month-end close
- Inconsistent line-item normalization

## MVP Scope
- Single-document upload (PDF/JPG/PNG)
- OCR + LLM structured extraction
- Human review and edit workflow
- Validation warnings
- JSON/CSV export

## Success Metrics
- Field-level extraction accuracy >= 92%
- Subtotal/total reconciliation pass rate >= 95% after review
- Median processing latency <= 20 seconds per invoice

## Non-Goals
- Fully automated no-human-touch posting
- Native ERP integrations in MVP

## Roadmap
- Batch upload
- Vendor templates
- Duplicate detection
- QuickBooks/NetSuite export
- Confidence scoring and eval dashboard
