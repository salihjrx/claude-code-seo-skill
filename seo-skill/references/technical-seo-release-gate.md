# Technical SEO Release Gate

A release should not be called SEO-verified until applicable checks pass.

## Critical
- Production not accidentally noindex/blocked.
- Preferred host and HTTPS work; redirects have no loops.
- Revenue-critical URLs return correct statuses.
- Canonicals point to intended canonical URLs.
- Important content and links render.
- No staging/preview URLs leaked into sitemap or canonical output.

## Important
- Titles/descriptions are unique by template and page.
- Sitemap contains only canonical indexable URLs.
- Robots and X-Robots-Tag match intended policy.
- Internal links do not point to errors or redirect chains.
- Structured data matches visible data and validates.
- Locale alternate annotations are reciprocal where applicable.
- Tracking and key conversion events still work.

## Report
Record test URL, expected result, observed result, date, tool, status, and any limitation. If no production access exists, mark production validation pending rather than passed.
