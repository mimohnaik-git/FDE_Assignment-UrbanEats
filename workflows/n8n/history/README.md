# Historical workflow exports — do not import for current operation

- urbaneats_core_scaffold.json: inactive Phase-2 minimal API scaffold; retained for history
  and a sanitization regression test.
- urbaneats_phase3a.json: inactive sanitized 79-node outage implementation superseded by
  the accepted 22-node Phase-3B architecture. Kept as a provenance snapshot, not a builder.

The only canonical current export is ../urbaneats_live.json. Earlier node counts/branches
here are historical. Never activate these exports or the root assignment workflow.
