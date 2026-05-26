# Evaluation Plan

## Target Metrics
- Field-level precision/recall/F1
- Line-item extraction accuracy
- Reconciliation accuracy (subtotal/tax/total)
- Latency (end-to-end)
- Cost per processed invoice

## Eval Dataset Approach
- Collect a balanced set across vendor formats, scan quality, and complexity.
- Include both machine-readable PDFs and image scans.

## Field-Level Accuracy
Measure exact-match accuracy for entity fields (invoice number, dates, totals, names).

## Line-Item Accuracy
Measure row detection, description quality, quantity/unit/total numeric correctness.

## Reconciliation Accuracy
Track percentage of invoices where totals reconcile automatically.

## Latency/Cost Tracking
Log OCR time, model latency, and estimated token-based cost per run.

## Manual Review Feedback Loop
Capture user edits as weak labels for future prompt/schema tuning and vendor-specific templates.
