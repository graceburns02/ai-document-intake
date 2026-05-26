from __future__ import annotations

import json
import os
import re
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.schemas import InvoiceData

SYSTEM_PROMPT = (
    "You extract invoice data into strict JSON. "
    "Return ONLY a single JSON object that matches the invoice schema exactly. "
    "No markdown, no code fences, no extra commentary. "
    "Use null for unknown scalar fields, [] for line_items, and numeric JSON values (or null) for money/quantities."
)


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    invoice: InvoiceData | None
    raw_output: str | None = None
    parsed_output: dict[str, Any] | None = None
    unknown_keys: list[str] = Field(default_factory=list)
    validation_error: str | None = None
    error: str | None = None


def _extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        raise json.JSONDecodeError("No JSON object found", text, 0)

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    raise json.JSONDecodeError("Unterminated JSON object", text, start)


def _clean_json_candidate(raw_text: str) -> dict[str, Any]:
    cleaned = re.sub(r"```(?:json)?", "", raw_text, flags=re.IGNORECASE).strip()
    cleaned = _extract_first_json_object(cleaned)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise json.JSONDecodeError("Top-level JSON must be object", cleaned, 0)

    def normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "" or stripped.lower() in {"n/a", "na", "none", "null", "unknown", "-"}:
                return None
        return value

    normalized = normalize(data)

    for field in ("subtotal", "tax", "total"):
        value = normalized.get(field)
        if isinstance(value, str):
            cleaned_num = value.replace(",", "").replace("$", "").strip()
            try:
                normalized[field] = float(cleaned_num)
            except ValueError:
                pass

    for item in normalized.get("line_items", []) if isinstance(normalized.get("line_items"), list) else []:
        if not isinstance(item, dict):
            continue
        for field in ("quantity", "unit_price", "line_total"):
            value = item.get(field)
            if isinstance(value, str):
                cleaned_num = value.replace(",", "").replace("$", "").strip()
                try:
                    item[field] = float(cleaned_num)
                except ValueError:
                    pass

    if normalized.get("line_items") is None or not isinstance(normalized.get("line_items"), list):
        normalized["line_items"] = []
    return normalized


def _strip_unknown_keys(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    allowed_root = set(InvoiceData.model_fields.keys())
    allowed_line_item = set(InvoiceData.model_fields["line_items"].annotation.__args__[0].model_fields.keys())

    stripped = {}
    unknown: list[str] = []
    for key, value in payload.items():
        if key not in allowed_root:
            unknown.append(key)
            continue
        stripped[key] = value

    line_items = stripped.get("line_items")
    if isinstance(line_items, list):
        cleaned_items = []
        for i, item in enumerate(line_items):
            if not isinstance(item, dict):
                cleaned_items.append(item)
                continue
            cleaned = {}
            for key, value in item.items():
                if key not in allowed_line_item:
                    unknown.append(f"line_items[{i}].{key}")
                    continue
                cleaned[key] = value
            cleaned_items.append(cleaned)
        stripped["line_items"] = cleaned_items

    return stripped, unknown


def _response_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    return text if text else str(response)


def _create_response(client: OpenAI, prompt: str, schema: dict[str, Any] | None = None) -> Any:
    kwargs: dict[str, Any] = {
        "model": "gpt-4.1-mini",
        "temperature": 0,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }

    if schema is not None:
        kwargs["text"] = {
            "format": {
                "type": "json_schema",
                "name": "invoice_data",
                "schema": schema,
                "strict": True,
            }
        }
    else:
        kwargs["text"] = {"format": {"type": "json_object"}}

    return client.responses.create(**kwargs)


def extract_invoice_with_fallback(text: str) -> ExtractionResult:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your environment.")

    client = OpenAI(api_key=api_key)
    schema = InvoiceData.model_json_schema()
    base_prompt = (
        "Extract invoice fields and line items from the text below. "
        "Return only valid JSON with keys matching the schema exactly. "
        "Return null for unknown fields. Return numbers without currency symbols. "
        "Return line_items as [] if no items are found. Use exactly the schema field names.\n\n"
        f"{text}"
    )

    raw_text = ""
    try:
        try:
            response = _create_response(client, base_prompt, schema=schema)
        except Exception:
            response = _create_response(client, base_prompt, schema=None)
        raw_text = _response_text(response)
        parsed = _clean_json_candidate(raw_text)
        stripped, unknown_keys = _strip_unknown_keys(parsed)
        invoice = InvoiceData.model_validate(stripped)
        return ExtractionResult(invoice=invoice, raw_output=raw_text, parsed_output=stripped, unknown_keys=unknown_keys)
    except (json.JSONDecodeError, ValidationError, TypeError):
        repair_prompt = (
            "Convert the following content into valid JSON matching the invoice schema exactly. "
            "Return only JSON. Ensure line_items is an array and numeric fields are numbers or null.\n\n"
            f"{raw_text}"
        )
        try:
            try:
                repair_response = _create_response(client, repair_prompt, schema=schema)
            except Exception:
                repair_response = _create_response(client, repair_prompt, schema=None)
            repaired_text = _response_text(repair_response)
            repaired = _clean_json_candidate(repaired_text)
            stripped, unknown_keys = _strip_unknown_keys(repaired)
            invoice = InvoiceData.model_validate(stripped)
            return ExtractionResult(invoice=invoice, raw_output=repaired_text, parsed_output=stripped, unknown_keys=unknown_keys)
        except Exception as exc:
            return ExtractionResult(
                invoice=None,
                raw_output=raw_text or None,
                validation_error=str(exc),
                error="Schema validation failed for model output. You can still review/edit invoice fields manually.",
            )


def extract_structured_invoice(text: str) -> InvoiceData:
    result = extract_invoice_with_fallback(text)
    if result.invoice is None:
        raise ValueError(result.error or "Extraction failed")
    return result.invoice
