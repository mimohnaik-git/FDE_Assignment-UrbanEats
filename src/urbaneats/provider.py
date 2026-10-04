"""Optional hosted formatter; disabled by default and always disabled in TEST_MODE."""

import json
import os
import time

import httpx

from .briefing import ProviderFailure, canonical_items, render

FORMATTER_SCHEMA = {
    "type": "object",
    "properties": {"items": {
        "type": "array", "items": {
            "type": "object",
            "properties": {
                "evidence_id": {"type": "string"},
                "text": {"type": "string"},
                "action_ids": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["evidence_id", "text", "action_ids"],
            "additionalProperties": False,
        },
    }},
    "required": ["items"],
    "additionalProperties": False,
}


class HostedFormatter:
    def __init__(self, transport=None):
        self.name = os.getenv("LLM_PROVIDER", "")
        groq = self.name == "groq"
        self.model = os.getenv("GROQ_MODEL" if groq else "LLM_MODEL", "")
        self.key = os.getenv("GROQ_API_KEY" if groq else "LLM_API_KEY", "")
        self.base_url = os.getenv("GROQ_BASE_URL" if groq else "LLM_BASE_URL", "")
        self.transport = transport
        self.attempts = 0

    def generate(self, evidence):
        if os.getenv("TEST_MODE", "true").lower() != "false":
            raise ValueError("test_mode")
        if self.name not in {"openai-compatible", "groq"} or not self.model or not self.key:
            raise ValueError("provider_not_configured")
        # Explicit local configuration chooses a compatible provider. Never follow redirects.
        url = self.base_url.rstrip("/")
        if not url.startswith("https://"):
            raise ValueError("https_provider_url_required")
        canonical = canonical_items(evidence)
        prompt = {
            "evidence": {key: evidence[key] for key in (
                "routing_status", "facts", "approved_actions", "run_id", "source_batch_id",
                "source_mode", "generated_at", "model_version") if key in evidence},
            "approved_actions": evidence["approved_actions"],
            "deterministic_briefing": render(evidence, canonical),
            "required_output_schema": {"items": canonical},
            "instruction": "Return JSON items. Reorder cited canonical sentences only; "
            "copy all items exactly including citations and action IDs. Do not add prose, "
            "metrics, causes, recommendations, readiness claims or change facts/provenance.",
        }
        payload = {
            "model": self.model, "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": json.dumps(prompt)}],
        }
        if self.name == "groq" and self.model in {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}:
            payload["response_format"] = {
                "type": "json_schema", "json_schema": {
                    "name": "urbaneats_formatter", "strict": True, "schema": FORMATTER_SCHEMA,
                },
            }
            # GPT-OSS does not support reasoning_format; never request reasoning output.
            payload["include_reasoning"] = False
        with httpx.Client(timeout=15, transport=self.transport, follow_redirects=False) as client:
            for attempt in range(1, 4):
                self.attempts = attempt
                try:
                    response = client.post(
                        url + "/chat/completions",
                        headers={"Authorization": "Bearer " + self.key},
                        json=payload,
                    )
                    response.raise_for_status()
                    try:
                        return json.loads(response.json()["choices"][0]["message"]["content"])
                    except (ValueError, KeyError, IndexError, TypeError):
                        raise ProviderFailure("PROVIDER_RESPONSE_MALFORMED") from None
                except (httpx.TimeoutException, httpx.NetworkError):
                    if attempt == 3:
                        raise ProviderFailure("PROVIDER_TRANSPORT_FAILED") from None
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code not in {429, 500, 502, 503, 504} or attempt == 3:
                        raise ProviderFailure("PROVIDER_HTTP_FAILED") from None
                time.sleep(attempt)


def configured_provider():
    if os.getenv("TEST_MODE", "true").lower() != "false" or not os.getenv("LLM_PROVIDER"):
        return None
    return HostedFormatter()
