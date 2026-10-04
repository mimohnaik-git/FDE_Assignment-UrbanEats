import copy

import pytest
from test_notification import initial, shared

NOW = "2026-10-04T00:00:02Z"
# Real n8n 2.3 Slack response shape; channel identity sanitized for public fixtures.
SLACK = {"ok": True, "channel": "mock-channel",
         "message": {"ts": "1791058142.501809"},
         "message_timestamp": "1791058142.501809"}


def receipt(prepared, channel, value):
    return shared("f.notificationReceipt(v.initial,v.channel,v.receipt,1,v.now)",
                  {"initial": prepared, "channel": channel, "receipt": value, "now": NOW})


@pytest.mark.parametrize("mode", ["top", "nested", "missing", "blank", "false", "channel", "ts_only"])
def test_slack_native_shape(mode):
    value = copy.deepcopy(SLACK)
    if mode == "nested":
        del value["message_timestamp"]
    elif mode == "missing":
        del value["message_timestamp"]
        del value["message"]["ts"]
    elif mode == "blank":
        value["message_timestamp"] = " "
    elif mode == "false":
        value["ok"] = False
    elif mode == "channel":
        value["channel"] = " "
    elif mode == "ts_only":
        value = {"ok": True, "channel": "mock-channel", "ts": "1791058142.501809"}
    row = receipt(initial(), "slack", value)
    assert row["slack_delivery_state"] == ("SUCCESS" if mode in {"top", "nested"} else "UNKNOWN")
    assert row["slack_attempts"] == 1 and row["retry_allowed"] is False


def test_disabled_gmail_exact_pass_through():
    prepared = {**initial(), "id": "native-audit-row-id"}
    gmail = receipt(prepared, "gmail", copy.deepcopy(prepared))
    assert gmail["gmail_attempts"] == 0 and gmail["gmail_delivery_state"] == "UNKNOWN"
    assert gmail["event_type"] == "delivery_not_sent"
    assert gmail["delivery_error_category"] == "CHANNEL_NOT_SENT" and not gmail["retry_allowed"]
    slack = receipt(prepared, "slack", SLACK)
    result = shared("f.completeNotification(v.initial,v.rows,v.now)",
                    {"initial": prepared, "rows": [slack, gmail], "now": NOW})
    assert result["event_type"] == "notification_unverified"
    assert result["slack_delivery_state"] == "SUCCESS" and result["gmail_attempts"] == 0
    # A receipt/error is not a pass-through, even if it contains the upstream fields.
    altered = {**prepared, "error": "ambiguous local error"}
    assert receipt(prepared, "gmail", altered)["gmail_attempts"] == 1


def test_normal_gmail_receipt_unchanged():
    row = receipt(initial(), "gmail", {"id": "mock-gmail-receipt"})
    assert row["gmail_delivery_state"] == "SUCCESS" and row["gmail_attempts"] == 1
