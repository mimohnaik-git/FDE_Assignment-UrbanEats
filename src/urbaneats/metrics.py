def current_metrics(predictions):
    total = len(predictions)
    flagged = sum(p["risk_flag"] for p in predictions)
    return {
        "records_evaluated": total,
        "high_risk_count": flagged,
        "predicted_risk_rate": flagged / total,
        "mean_model_score": sum(p["cancellation_probability"] for p in predictions) / total,
        "observed_cancellation_rate": None,
        "observed_metrics_status": "UNAVAILABLE: placement batch has no matured outcomes",
        "interpretation": "Uncalibrated conditional Delivered/Cancelled model scores, not observed rates",
    }
