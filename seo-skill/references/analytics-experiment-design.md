# SEO Measurement and Experiment Design

## KPI tree
Business outcome → qualified organic sessions → landing-page engagement/task completion → leads/orders/revenue → margin/retention where available. Treat impressions, rankings and clicks as diagnostic metrics, not the business outcome itself.

## Segmentation
Segment by market, locale, page template, query intent, device, brand/non-brand, product/category, new/returning user and release cohort when the data supports it. Protect privacy and follow consent rules.

## Annotation ledger
Record deploys, migrations, content changes, campaign activity, outages, consent changes, tracking changes, seasonality and major SERP changes with timestamp, affected URLs, expected effect and owner.

## Experiment discipline
- State hypothesis and mechanism before implementation.
- Define treatment/control or comparison cohort where feasible.
- Choose primary and guardrail metrics in advance.
- Account for seasonality, promotions, stock, SERP volatility and concurrent releases.
- Avoid claiming causality from before/after charts alone.
- Use holdbacks or phased rollout where feasible and safe.
- Record null/negative outcomes and unexpected effects.
- Don't run an experiment that creates a harmful user experience or violates platform policy.

## Attribution caveats
Search Console clicks, analytics sessions and CRM conversions have different definitions and sampling/consent limitations. Reconcile them directionally; do not expect exact equality. Explain timezone, currency, attribution model, filters and data latency in reports.
