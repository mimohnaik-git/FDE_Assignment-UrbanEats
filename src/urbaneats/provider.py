"""Optional hosted formatter; disabled by default and always disabled in TEST_MODE."""

import json
import os
import time

import httpx

from .briefing import fact_sentences


class HostedFormatter:
    def __init__(self, transport=None):
        self.name = os.getenv("LLM_PROVIDER", "")
        self.model = os.getenv("LLM_MODEL", "")
        self.key = os.getenv("LLM_API_KEY", "")
        self.transport = transport
        self.attempts = 0

    def generate(self, evidence):
        if os.getenv("TEST_MODE", "true").lower() != "false":
            raise ValueError("test_mode")
        if self.name != "openai-compatible" or not self.model or not self.key:
            raise ValueError("provider_not_configured")
        # Explicit local configuration chooses a compatible provider. Never follow redirects.
        url = os.getenv("LLM_BASE_URL", "").rstrip("/")
        if not url.startswith("https://"):
            raise ValueError("https_provider_url_required")
        canonical = [
            {
                "evidence_id": f["evidence_id"],
                "text": fact_sentences(evidence)[f["evidence_id"]],
                "action_ids": f["approved_action_ids"],
            }
            for f in evidence["facts"]
        ]
        prompt = {
            "evidence": evidence,
            "approved_actions": evidence["approved_actions"],
            "required_output_schema": {"items": canonical},
            "instruction": "Return JSON items. Reorder canonical sentences only; "
            "copy all items exactly. Do not add prose or change facts.",
        }
        with httpx.Client(timeout=15, transport=self.transport, follow_redirects=False) as client:
            for attempt in range(1, 4):
                self.attempts = attempt
                try:
                    response = client.post(
                        url + "/chat/completions",
                        headers={"Authorization": "Bearer " + self.key},
                        json={
                            "model": self.model,
                            "temperature": 0,
                            "response_format": {"type": "json_object"},
                            "messages": [{"role": "user", "content": json.dumps(prompt)}],
                        },
                    )
                    response.raise_for_status()
                    return json.loads(response.json()["choices"][0]["message"]["content"])
                except (httpx.TimeoutException, httpx.NetworkError):
                    if attempt == 3:
                        raise ValueError("provider_transport_failed") from None
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code not in {429, 500, 502, 503, 504} or attempt == 3:
                        raise ValueError("provider_http_failed") from None
                time.sleep(attempt)


def configured_provider():
    if os.getenv("TEST_MODE", "true").lower() != "false" or not os.getenv("LLM_PROVIDER"):
        return None
    return HostedFormatter()
