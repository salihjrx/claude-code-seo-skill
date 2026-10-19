# Ecommerce Catalog, Variants and Faceted Navigation

## Entity model
Define relationships among brand, product family, sellable SKU, variant, category, collection, merchant offer, inventory location and locale. Keep stable IDs separate from mutable titles/slugs.

## Product page decisions
- Use a distinct URL for a variant only when it has meaningful user/search value and stable inventory/selection behavior.
- Ensure selected variant, image, SKU, price, stock, shipping and structured data agree.
- Canonicalize true duplicates, not genuinely different products.
- Keep discontinued, temporarily unavailable, permanently retired and replaced products on separate policies.
- Preserve useful historical pages when they help users; redirect only to a close equivalent.
- Never invent scarcity, reviews, stock or discount claims.

## Facet eligibility rubric
A facet landing page may be index-worthy when it has:
- demonstrated search demand or a validated customer need;
- a stable and comprehensible URL;
- sufficient available inventory;
- distinct content and utility beyond a filter list;
- unique title/H1/canonical and meaningful internal links;
- an owner and maintenance policy.
No single factor alone guarantees indexation.

## Feed and page consistency
Reconcile product landing pages, structured data and merchant feeds for:
- price and currency;
- availability;
- condition;
- variant IDs and GTIN/MPN/brand where accurate;
- shipping/returns information;
- sale price timing;
- image and landing URL;
- locale, language and market eligibility.

## Catalog QA
Automate checks for orphan products, empty categories, duplicate titles, missing image alt, inconsistent variants, stale stock, invalid canonical targets, parameter explosion, redirecting sitemap URLs and broken internal product links.
