# SEO Acceptance Test Catalog

Adapt commands to the actual stack; do not assume a tool exists.

## HTML and metadata
- Every indexable canonical page has a meaningful title and a single clear primary heading.
- Canonical URL is absolute, expected, stable and not a redirect/error.
- No accidental `noindex`; robots meta and X-Robots-Tag agree with policy.
- Description is useful and page-specific where feasible; it is not a ranking guarantee.
- Open Graph/social metadata does not contradict page identity.

## Discovery
- Important pages have crawlable internal links.
- Sitemap contains only intended canonical, successful URLs.
- Sitemap `lastmod` reflects meaningful changes, not every deployment.
- No critical orphan URLs without a discovery path.
- Pagination and facets follow documented policy.

## International
- Locale page is in the expected language.
- hreflang links to equivalent live pages and is reciprocal.
- Canonical and hreflang strategy are consistent.
- Locale switcher preserves equivalent content when available.

## Structured data
- JSON parses.
- Type is appropriate and supported.
- Required properties exist for the target feature.
- Values match visible content and source-of-truth data.
- No fake reviews, prices, availability or dates.

## Commerce
- Page, feed and schema agree on price, currency, availability and variant.
- Product IDs are stable and correctly mapped.
- Out-of-stock and discontinued behavior follows policy.
- Faceted URL space is bounded and intentional.

## Performance and UX
- Use field data when available; lab data is diagnostic, not a substitute.
- Measure LCP, INP and CLS with the appropriate current methodology.
- Test mobile layouts, consent flows, image dimensions and third-party scripts.
- Do not regress accessibility or conversion in pursuit of a single score.

## Safety
- No secret or customer data appears in reports.
- No production action occurs without authorization.
- Tests use bounded request counts and respect rate limits.
