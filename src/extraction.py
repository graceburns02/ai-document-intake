from __future__ import annotations

import json
import os

from openai import OpenAI
from pydantic import ValidationError

from src.schemas import InvoiceData


SYSTEM_PROMPT = (
    "You extract invoice data into strict JSON. "
    "If missing, return null for scalar fields and [] for line_items."
)


def extract_structured_invoice(text: str) -> InvoiceData:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your environment.")

    client = OpenAI(api_key=api_key)

    # Tradeoff: lower temperature reduces creative hallucination but may miss edge fields.
    response = client.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Extract invoice fields and line items from the text below. "
                    "Return only valid JSON with keys matching the schema exactly.\n\n"
                    f"{text}"
                ),
            },
        ],
    )

    raw_text = response.output_text
    try:
        parsed = json.loads(raw_text)
        return InvoiceData.model_validate(parsed)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(
            "Model response could not be parsed into invoice schema. "
            "Try cleaner text or review/edit manually."
        ) from exc
