# SEO Migration Playbook

## Before launch
- Freeze and export the old URL inventory, status codes, canonical, index directives, traffic, conversions and backlinks where available.
- Map every old URL to the closest relevant new URL; avoid blanket homepage redirects.
- Test redirect coverage, loops, chains, protocol/host normalization and query behavior.
- Preserve content, metadata, internal links, image URLs and structured data where appropriate.
- Confirm new robots, canonicals, hreflang, sitemaps, navigation and analytics.
- Crawl staging with authentication safeguards; prevent staging from being indexed without accidentally carrying noindex into production.
- Prepare rollback, owners, monitoring and communication.

## Launch day
- Test critical templates and high-value URL samples.
- Verify HTTP codes and redirects from outside the app where possible.
- Check robots/noindex/canonical, sitemap, hreflang, schema, internal links and analytics.
- Check CDN/cache behavior and server logs if available.
- Submit updated sitemaps or change-of-address tooling only where applicable and currently supported.

## After launch
- Monitor old URL redirects, new URL indexation, crawl errors, organic landing pages, conversions, logs and server performance.
- Segment by template, locale and device.
- Compare with seasonality and expected migration effects; do not declare failure from a single day's fluctuation.
- Fix discovered mapping errors quickly and preserve redirect mappings long enough to serve users and crawlers.
- Maintain a dated issue log and rollback decision criteria.
