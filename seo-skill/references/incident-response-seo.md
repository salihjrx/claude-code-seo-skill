# SEO Incident Response

## Severity
- **SEV-1**: broad critical-site deindexing, accidental sitewide noindex/robots block, domain/DNS outage, broken canonical/redirect affecting most valuable URLs, security compromise.
- **SEV-2**: major template or locale affected, product feeds broadly wrong, significant crawl/render failure, large migration mapping errors.
- **SEV-3**: limited URL cluster defect, localized schema/content/metadata regression.
- **SEV-4**: isolated low-impact issue or optimization opportunity.

Severity should reflect user/business impact and scope, not the drama of a single ranking screenshot.

## First 30 minutes
1. Confirm the event and timestamp with independent evidence.
2. Check availability, deploys, DNS/CDN, robots, noindex, canonicals, redirects, sitemap, rendering and tracking.
3. Determine scope by template, locale, device and URL cohort.
4. Stop risky rollout or roll back if evidence supports it and authority permits.
5. Preserve logs, diffs, screenshots, URL samples and timeline.
6. Assign incident owner and communication cadence.

## Diagnosis discipline
Separate cause from correlation. Search demand, seasonality, SERP changes, competitors, stock, pricing, analytics consent, tracking failures and site changes can look similar in a traffic chart.

## Recovery
Fix the cause, test affected templates, deploy with approval, verify representative URLs and monitor leading indicators. Document root cause, detection gap, prevention and follow-up owner.
