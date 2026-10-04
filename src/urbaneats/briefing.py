import json
import re

MODEL_LIMITATION = (
    "exploratory, uncalibrated, conditional Delivered-vs-Cancelled model; no production-quality claim"
)


class ProviderFailure(ValueError):
    """Allowlisted public category, never provider response or exception details."""

    def __init__(self, category):
        self.category = category if category in {
            "PROVIDER_HTTP_FAILED", "PROVIDER_TRANSPORT_FAILED", "PROVIDER_RESPONSE_MALFORMED",
        } else "PROVIDER_UNAVAILABLE"
        super().__init__(self.category)


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
    required = required_evidence_ids(packet)

    return (
        bool(cited)
        and set(cited) <= valid
        and required <= set(cited)
        and (
            f"[run:{packet['run_id']}]" in text
            and f"[source:{packet['source_batch_id']}]" in text
            and re.findall(r"\[run:([^\]]+)\]", text) == [packet["run_id"]]
            and re.findall(r"\[source:([^\]]+)\]", text) == [packet["source_batch_id"]]
        )
    )


def validate_formatter_output(output, packet):
    """Accept canonical evidence sentences only with their exact citation.

    Provenance/routing/model text is system-rendered. No free-form metric, action,
    causal statement or model-readiness claim can pass this closed vocabulary.
    """

    if (not isinstance(output, dict) or set(output) != {"items"}
            or not isinstance(output["items"], list) or not output["items"]):
        raise ValueError("Invalid formatter schema")

    sentences = fact_sentences(packet)

    seen = set()

    for item in output["items"]:
        if not isinstance(item, dict) or set(item) != {"evidence_id", "text", "action_ids"}:
            raise ValueError("Invalid formatter item")

        eid = item["evidence_id"]

        if eid not in sentences or eid in seen or item["text"] != sentences[eid] + f" [evidence:{eid}]":
            raise ValueError("Unsupported evidence or wording")

        seen.add(eid)

        fact = next(f for f in packet["facts"] if f["evidence_id"] == eid)

        if item["action_ids"] != fact["approved_action_ids"]:
            raise ValueError("Unsupported actions")

    required = required_evidence_ids(packet)

    if not required <= seen:
        raise ValueError("Required evidence omitted")

    return output


def cited_line(text, evidence_id):
    """Join a rendered sentence and its citation with exactly one separating space."""
    return f"{text.rstrip()} [evidence:{evidence_id}]"


def required_evidence_ids(packet):
    """Batch and supported hotspots must survive formatting and rendering."""
    return {"KPI-BATCH"} | {f["evidence_id"] for f in packet["facts"] if f.get("is_hotspot")}


def canonical_items(packet):
    """Construct the same closed vocabulary for local and hosted formatting."""
    sentences = fact_sentences(packet)
    return [
        {"evidence_id": f["evidence_id"],
         "text": cited_line(sentences[f["evidence_id"]], f["evidence_id"]),
         "action_ids": f["approved_action_ids"]}
        for f in packet["facts"]
    ]


def render(packet, items):

    lines = [
        f"UrbanEats - {packet['source_mode']} - exploratory conditional model",
        f"[run:{packet['run_id']}] [source:{packet['source_batch_id']}]",
        "Observed cancellation metrics unavailable for this placement batch.",
        cited_line(f"{MODEL_LIMITATION}.", "KPI-BATCH"),
    ]

    for item in items:
        citation = f"[evidence:{item['evidence_id']}]"
        lines.append(item["text"] if item["text"].endswith(citation) else f"{item['text']} {citation}")

        for aid in item["action_ids"]:
            action = next(a for a in packet["approved_actions"] if a["action_id"] == aid)

            lines.append(cited_line(f"Action {aid}: {action['description']}", item["evidence_id"]))

    text = "\n".join(lines)

    if not validate_citations(text, packet):
        raise ValueError("Invalid rendered citations")

    return text


def generate_briefing(packet, provider=None):
    items = canonical_items(packet)

    trace = {"mode": "deterministic", "provider_status": "NOT_CONFIGURED"}

    if provider is not None:
        try:
            # Detached copy prevents a provider mutating pipeline truth.

            category = "PROVIDER_UNAVAILABLE"
            output = provider.generate(json.loads(json.dumps(packet)))

            category = "PROVIDER_OUTPUT_REJECTED"
            items = validate_formatter_output(output, packet)["items"]

            trace = {"mode": "provider", "provider_status": "VALIDATED"}

        except Exception as exc:
            trace = {
                "mode": "deterministic",
                "provider_status": "FALLBACK",
                "reason": exc.category if isinstance(exc, ProviderFailure) else category,
            }

    trace.update(
        provider=getattr(provider, "name", "local_stub" if provider else None),
        model=getattr(provider, "model", None),
        attempts=getattr(provider, "attempts", 0),
        fallback_used=trace["provider_status"] == "FALLBACK",
    )

    return {"text": render(packet, items), "formatter": trace}
