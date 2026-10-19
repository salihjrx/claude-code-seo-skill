# SEO Architecture and URL Governance

## Purpose
Create stable, crawlable, understandable URL systems that reflect information architecture without exposing every internal filter or state as an indexable page.

## URL inventory schema
Maintain one row per URL or normalized URL pattern:
`url | template | locale | status | index_policy | canonical_target | sitemap_eligible | internal_link_depth | organic_clicks | conversions | owner | notes`

## Policy matrix
For every route family, explicitly decide:
- crawl allowed? (robots policy)
- index allowed? (meta robots / X-Robots-Tag)
- canonical target?
- included in sitemap?
- linked internally?
- parameters allowed?
- authentication required?
- analytics classification?

Do not treat these controls as interchangeable. Robots controls crawling; noindex is a page-level indexing directive that must be crawled to be seen; canonical is a hint for duplicate/alternate URLs; sitemap is a discovery signal, not an indexing guarantee.

## Facets and parameters
For each filter, sort, pagination and search parameter:
1. Determine whether it represents a distinct useful search intent.
2. Estimate crawl space growth and parameter combinations.
3. Decide whether a stable, curated landing page is warranted.
4. Keep useful facet URLs crawlable only when they provide distinct value and have a controlled link graph.
5. Avoid generating indexable permutations that differ only by order, tracking parameter, session, sort order or trivial combinations.
6. Preserve user utility even when a URL is excluded from indexing.
7. Test canonical behavior and internal links across combinations.

## Pagination
- Use crawlable links to discover subsequent pages.
- Give each paginated page an appropriate canonical when content is distinct; do not automatically canonicalize every page to page one.
- Ensure products/items are discoverable without requiring infinite-scroll interaction.
- Avoid relying on deprecated or unsupported pagination assumptions.

## URL normalization
Define explicit rules for:
- scheme and host;
- trailing slash;
- casing;
- percent encoding;
- query parameter ordering;
- tracking parameters;
- duplicate slashes;
- Unicode paths;
- legacy slugs;
- locale prefixes.
Test idempotence: normalizing a normalized URL must not change it again.

## Governance
Every new route/template must ship with an indexability policy, canonical behavior, sitemap behavior, internal-link discovery, analytics mapping, localization policy and automated tests.
