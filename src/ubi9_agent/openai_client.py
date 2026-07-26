from __future__ import annotations

import os

from .util import extract_json


class AIClient:
    def __init__(self, model: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "Install the project dependencies to enable AI mode: pip install -e ."
            ) from exc
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-5")

    def json(self, instructions: str, payload: str) -> dict:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=payload,
        )
        return extract_json(response.output_text)
