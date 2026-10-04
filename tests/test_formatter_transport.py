import json

import httpx
import pytest

from urbaneats.briefing import generate_briefing
from urbaneats.provider import FORMATTER_SCHEMA, HostedFormatter
from urbaneats.service import Runtime


@pytest.fixture
def groq(monkeypatch):
    monkeypatch.setenv("TEST_MODE", "false")
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_MODEL", "openai/gpt-oss-20b")
    monkeypatch.setenv("GROQ_BASE_URL", "https://formatter.invalid/v1")
    monkeypatch.setenv("GROQ_API_KEY", "mock-local-credential")
    monkeypatch.setattr("urbaneats.provider.time.sleep", lambda _: None)


def valid_content(request):
    prompt = json.loads(json.loads(request.content)["messages"][0]["content"])
    return {"choices": [{"message": {"content": json.dumps(prompt["required_output_schema"])}}]}


def test_strict_groq_request_and_acceptance(groq, config, batch):
    def handle(request):
        body = json.loads(request.content)
        assert body["temperature"] == 0
        assert body["include_reasoning"] is False and "reasoning_format" not in body
        fmt = body["response_format"]
        assert fmt["type"] == "json_schema" and fmt["json_schema"]["strict"] is True
        assert fmt["json_schema"]["schema"] == FORMATTER_SCHEMA
        schema = fmt["json_schema"]["schema"]
        for obj in [schema, schema["properties"]["items"]["items"]]:
            assert obj["additionalProperties"] is False
            assert set(obj["required"]) == set(obj["properties"])
        return httpx.Response(200, json=valid_content(request))
    result = Runtime(config, HostedFormatter(httpx.MockTransport(handle))).process(batch)
    assert result["briefing"]["formatter"]["provider_status"] == "VALIDATED"


@pytest.mark.parametrize("mode,reason,attempts", [
    ("4xx", "PROVIDER_HTTP_FAILED", 1),
    ("5xx", "PROVIDER_HTTP_FAILED", 3),
    ("transport", "PROVIDER_TRANSPORT_FAILED", 3),
    ("envelope", "PROVIDER_RESPONSE_MALFORMED", 1),
    ("json", "PROVIDER_RESPONSE_MALFORMED", 1),
    ("schema", "PROVIDER_OUTPUT_REJECTED", 1),
    ("unsupported", "PROVIDER_OUTPUT_REJECTED", 1),
])
def test_safe_diagnostics_and_fallback(groq, config, batch, mode, reason, attempts):
    secret = "private-provider-detail"
    def handle(request):
        if mode == "transport":
            raise httpx.ReadTimeout(secret, request=request)
        if mode in {"4xx", "5xx"}:
            return httpx.Response(400 if mode == "4xx" else 503, text=secret,
                                  headers={"x-secret": secret})
        if mode == "envelope":
            return httpx.Response(200, json={"unexpected": secret})
        content = valid_content(request)
        if mode == "json":
            content["choices"][0]["message"]["content"] = secret
        else:
            output = json.loads(content["choices"][0]["message"]["content"])
            if mode == "schema":
                output = {"items": "invalid"}
            else:
                output["items"][0]["text"] += " invented cause"
            content["choices"][0]["message"]["content"] = json.dumps(output)
        return httpx.Response(200, json=content)
    provider = HostedFormatter(httpx.MockTransport(handle))
    result = Runtime(config, provider).process(batch)
    trace = result["briefing"]["formatter"]
    assert trace["provider_status"] == "FALLBACK" and trace["reason"] == reason
    assert trace["attempts"] == attempts and result["routing_status"] == "RED_ALERT"
    public = json.dumps(result)
    assert secret not in public and "mock-local-credential" not in public
    assert "Authorization" not in public and "invented cause" not in public


def test_recovery_retry(groq, config, batch):
    calls = []
    def handle(request):
        calls.append(1)
        return httpx.Response(503) if len(calls) < 3 else httpx.Response(200, json=valid_content(request))
    result = Runtime(config, HostedFormatter(httpx.MockTransport(handle))).process(batch)
    assert result["briefing"]["formatter"]["provider_status"] == "VALIDATED"
    assert result["briefing"]["formatter"]["attempts"] == 3


@pytest.mark.parametrize("route", ["red", "green", "failure"])
def test_portable_presentation_and_spacing(runtime, batch, route):
    if route == "green":
        batch["orders"] = batch["orders"][:4]
    result = runtime.process({} if route == "failure" else batch)
    messages = [result["briefing"]["text"], *result["briefing"]["channels"].values()]
    if route != "failure":
        assert "no production-quality claim. [evidence:KPI-BATCH]" in result["briefing"]["text"]
        assert "Current batch:" in result["briefing"]["channels"]["gmail_text"]
        assert "Currentbatch:" not in result["briefing"]["channels"]["gmail_text"]
        assert "no production-quality claim.[evidence:KPI-BATCH]" not in result["briefing"]["text"]
    else:
        assert "DATA_FAILURE" in result["briefing"]["channels"]["gmail_subject"]
    for text in messages:
        assert text.isascii()
        assert ".[evidence:" not in text
        assert "claim. [evidence:" in text or "claim" not in text


def test_unknown_provider_exception_is_safe(runtime, batch):
    class Broken:
        def generate(self, evidence):
            raise RuntimeError("private-provider-detail")
    evidence = runtime.process(batch)["evidence"]
    briefing = generate_briefing(evidence, Broken())
    assert briefing["formatter"]["reason"] == "PROVIDER_UNAVAILABLE"
    assert "private-provider-detail" not in json.dumps(briefing)
