# SEO Prioritization Model

Use scoring to structure judgment, not to manufacture certainty.

Score each factor from 1–5:
- **Reach**: number/value of affected pages or journeys;
- **Impact**: plausible effect on eligibility, usefulness or conversion;
- **Confidence**: strength of evidence;
- **Urgency**: time sensitivity / risk if left unresolved;
- **Effort**: engineering/editorial/coordination cost;
- **Risk**: probability and severity of regressions.

Optional planning heuristic:
`priority = (reach × impact × confidence × urgency) / (effort × risk)`
Define scales locally and keep the raw values visible. Do not call the result an official Google metric or a precise forecast.

Prioritization guardrails:
- Security, privacy and release blockers override scores.
- Fix broad template defects before isolated page polish when evidence supports it.
- Prefer reversible, testable changes.
- Avoid duplicate tickets for the same root cause.
- Include dependencies and an explicit acceptance test.
