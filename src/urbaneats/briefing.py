import json
import re
from typing import Protocol


class FormatterProvider(Protocol):
    """Injectable formatter interface; hosted transport is optional."""

    def generate(self, evidence: dict) -> dict: ...


def fact_sentences(packet):

    sentences = {}

    for fact in packet["facts"]:
        prefix = (
            "Current batch"
            if fact["evidence_id"] == "KPI-BATCH"
            else (f"{fact['restaurant']} / {fact['delivery_zone']}")
        )

        support = (
            " Insufficient support; no hotspot claim."
            if fact.get("support_status") == "INSUFFICIENT_SUPPORT"
            else ""
        )

        sentences[fact["evidence_id"]] = (
            f"{prefix}: {fact['numerator']}/{fact['denominator']} orders model-flagged "
            f"({fact['predicted_risk_rate']:.1%}); this is a predicted-risk fraction, "
            f"not an observed cancellation rate.{support}"
        )

    return sentences


def validate_citations(text, packet):

    valid = {f["evidence_id"] for f in packet["facts"]}

    cited = re.findall(r"\[evidence:([^\]]+)\]", text)

    return (
        bool(cited)
        and set(cited) <= valid
        and (
            f"[run:{packet['run_id']}]" in text
            and f"[source:{packet['source_batch_id']}]" in text
            and re.findall(r"\[run:([^\]]+)\]", text) == [packet["run_id"]]
            and re.findall(r"\[source:([^\]]+)\]", text) == [packet["source_batch_id"]]
        )
    )


def validate_formatter_output(output, packet):
    """Conservative structured formatter: reorder/select canonical sentences only.



    Arbitrary prose cannot be made safe by a numeric/citation regex. Phase 2 therefore

    permits no free-form additions; Phase 3 can extend this under factual validation.

    """

    if not isinstance(output, dict) or set(output) != {"items"} or not output["items"]:
        raise ValueError("Invalid formatter schema")

    sentences = fact_sentences(packet)

    seen = set()

    for item in output["items"]:
        if not isinstance(item, dict) or set(item) != {"evidence_id", "text", "action_ids"}:
            raise ValueError("Invalid formatter item")

        eid = item["evidence_id"]

        if eid not in sentences or eid in seen or item["text"] != sentences[eid]:
            raise ValueError("Unsupported evidence or wording")

        seen.add(eid)

        fact = next(f for f in packet["facts"] if f["evidence_id"] == eid)

        if item["action_ids"] != fact["approved_action_ids"]:
            raise ValueError("Unsupported actions")

    required = {"KPI-BATCH"} | {f["evidence_id"] for f in packet["facts"] if f.get("is_hotspot")}

    if not required <= seen:
        raise ValueError("Required evidence omitted")

    return output


def render(packet, items):

    lines = [
        f"UrbanEats — {packet['source_mode']} — exploratory conditional model",
        f"[run:{packet['run_id']}] [source:{packet['source_batch_id']}]",
        "Observed cancellation metrics unavailable for this placement batch.",
    ]

    for item in items:
        lines.append(f"{item['text']} [evidence:{item['evidence_id']}]")

        for aid in item["action_ids"]:
            action = next(a for a in packet["approved_actions"] if a["action_id"] == aid)

            lines.append(f"Action {aid}: {action['description']} [evidence:{item['evidence_id']}]")

    text = "\n".join(lines)

    if not validate_citations(text, packet):
        raise ValueError("Invalid rendered citations")

    return text


def generate_briefing(packet, provider=None):

    sentences = fact_sentences(packet)

    items = [
        {
            "evidence_id": f["evidence_id"],
            "text": sentences[f["evidence_id"]],
            "action_ids": f["approved_action_ids"],
        }
        for f in packet["facts"]
    ]

    trace = {"mode": "deterministic", "provider_status": "NOT_CONFIGURED"}

    if provider is not None:
        try:
            # Detached copy prevents a provider mutating pipeline truth.

            output = provider.generate(json.loads(json.dumps(packet)))

            items = validate_formatter_output(output, packet)["items"]

            trace = {"mode": "provider", "provider_status": "VALIDATED"}

        except Exception:
            trace = {
                "mode": "deterministic",
                "provider_status": "FALLBACK",
                "reason": "provider_unavailable_or_output_rejected",
            }

    trace.update(
        provider=getattr(provider, "name", "local_stub" if provider else None),
        model=getattr(provider, "model", None),
        attempts=getattr(provider, "attempts", 0),
        fallback_used=trace["provider_status"] == "FALLBACK",
    )

    return {"text": render(packet, items), "formatter": trace}
