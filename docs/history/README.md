# Historical assignment and engineering snapshots

These files preserve the original assignment narrative and earlier engineering decisions.
Their commands, filenames, node counts and readiness statements describe the system at
the time of each snapshot.

The current accepted system is the **23-node canonical n8n workflow** with the saved-model
placement API, grounded briefings, independent outage reporting and audited channel
policy. The earlier 22-node design was superseded. Use the [project README](../../README.md),
[runtime documentation](../RUNTIME.md), [automation contract](../LIVE_AUTOMATION.md) and
[canonical workflow documentation](../../workflows/n8n/README.md) for current behavior.

| Snapshot | Historical purpose |
|---|---|
| [README_PRE_3B1.md](README_PRE_3B1.md) | Preserved original assignment narrative and earlier README; unchanged snapshot |
| [RUNTIME_PHASE2_3.md](RUNTIME_PHASE2_3.md) | Earlier runtime setup and contracts |
| [LIVE_AUTOMATION_PHASE3_3A.md](LIVE_AUTOMATION_PHASE3_3A.md) | Earlier automation and outage design |
| [REMEDIATION_PLAN_PHASE1_3.md](REMEDIATION_PLAN_PHASE1_3.md) | Original audit/remediation reasoning |
| [PHASE3_3A_REPORT.md](PHASE3_3A_REPORT.md) | Earlier deployment/outage verification |
| [AUDIT_PHASE1_3.md](AUDIT_PHASE1_3.md) | Original assignment and prediction-contract audit |

Historical results remain under [evaluation/results](../../evaluation/results/), and
datasets/notebooks retain their provenance paths. Earlier workflow graphs are in the
[workflow archive](../../workflows/n8n/history/README.md). Final isolated verification is
recorded in the [24-case native evidence](../../evaluation/results/final_native_verification.json)
and [canonical GREEN/RED/DATA_FAILURE execution evidence](../../evaluation/results/final_n8n_execution_verification.json).

Historical snapshots are retained as evidence; their contents are not rewritten to match
the present architecture.
