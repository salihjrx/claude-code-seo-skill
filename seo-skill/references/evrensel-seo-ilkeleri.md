# Evrensel SEO İlkeleri (kullanıcının sağladığı "universal-seo" skill metni)

Kaynak: kullanıcının `seo nedir` klasöründeki SKILL.md. Çalışma modları, P0–P3 öncelik, kanıt disiplini, e-ticaret (§8), yerel (§9), uluslararası (§10), taşıma/canlıya alma (§14), doğrulama (§15), rapor formatları (§16) ve resmi kaynaklar (§17) burada. Ana SKILL.md bu dosyaya atıf yapar. İngilizce metin olduğu gibi korunmuştur.

---


# Universal SEO Skill

## Mission

Make every relevant website discoverable, crawlable, indexable,
understandable, useful to searchers, and measurable. Apply SEO during
planning and implementation---not as a final checklist. Adapt
recommendations to the site's purpose, stack, audience, geography, and
business goals.

**Core rule:** inspect the actual project and verify the actual output.
Do not assume a framework, CMS, route structure, deployment setup,
analytics provider, or existing SEO implementation. Never claim a task
is complete without evidence.

SEO cannot guarantee indexing, rankings, rich results, traffic, or a
particular position. Prioritize user value and technical correctness
over tricks.

## Operating modes

Infer the mode from the request: - **Build mode:** design SEO into a new
site or feature before implementation. - **Audit mode:** inspect an
existing site/repository and report evidence-based findings. - **Fix
mode:** correct identified SEO issues with minimal regressions. -
**Content mode:** research search intent, plan pages, and create useful
content. - **Migration mode:** protect existing URLs, rankings,
redirects, canonicals, and tracking during a redesign/domain/CMS
change. - **Review mode:** verify completed work and produce a test
report.

If the request is broad, start by inspecting the project. Ask a question
only when a missing decision materially affects implementation.
Otherwise make a reasonable, explicitly stated assumption and proceed.

## Non-negotiable workflow

1.  **Discover the project**
    -   Inspect repository files, package manifests, framework, routing,
        rendering strategy, CMS/data model, deployment configuration,
        existing metadata, sitemap, robots file, analytics, and tests.
    -   Identify public pages versus authenticated, private,
        transactional, duplicate, filtered, or utility URLs.
    -   Determine primary audience, language, country/region, conversion
        goal, competitors if relevant, and the type of site.
    -   If a live URL is supplied and browsing is available, inspect
        representative URLs and official documentation. Do not invent
        crawl results or analytics.
2.  **Establish a baseline**
    -   List current URLs/routes and templates.
    -   Check crawlability, indexability, status codes, redirects,
        canonical tags, titles, descriptions, headings, internal links,
        structured data, images, rendering, mobile layout, performance,
        and content quality.
    -   Preserve existing good URLs and traffic-producing pages unless
        there is a justified reason to change them.
3.  **Prioritize**
    -   P0: site accidentally blocked/noindexed, broken domain/HTTPS,
        widespread 5xx/404, wrong canonical host, critical rendering or
        deployment failures.
    -   P1: important pages undiscoverable, wrong status codes,
        duplicate/canonical conflicts, missing key templates, broken
        internal links, migration errors.
    -   P2: page-level metadata, content gaps, structured data, images,
        performance and UX improvements.
    -   P3: incremental content improvements, tests, monitoring, and
        low-impact polish.
    -   Rank by impact, confidence, affected URLs, effort, and risk.
        Explain trade-offs.
4.  **Implement**
    -   Follow the existing architecture and conventions. Avoid
        unnecessary dependencies or rewrites.
    -   Use shared metadata helpers/layouts where appropriate, but allow
        page-specific values.
    -   Generate metadata and structured data from validated source
        data, not brittle string hacks.
    -   Keep private, admin, account, checkout, internal search, and
        other non-search landing pages out of the index when
        appropriate.
5.  **Verify**
    -   Run available tests, lint, type checks, builds, and route
        checks.
    -   Inspect rendered HTML and HTTP responses, not just source
        JSX/templates.
    -   Test representative pages and edge cases, including missing
        fields, unusual characters, empty results, pagination, variants,
        and error states.
    -   Confirm production base URLs, environment variables, redirects,
        robots directives, canonical URLs, sitemap URLs, and structured
        data are correct.
6.  **Report**
    -   Summarize what changed, files touched, tests run, observed
        results, unresolved risks, and any manual steps.
    -   Separate verified facts from assumptions and recommendations.
    -   Never report "SEO score," indexing, rich results, or ranking
        success without a real measurement source.

## 1. Technical SEO baseline

### Crawlability and indexability

For every important public page, confirm: - It returns the intended HTTP
status (normally `200` for a valid page). - It can be discovered through
crawlable links using real `<a href="...">` elements. - Important
content and links are available to search engines after rendering. - No
accidental `noindex`, `X-Robots-Tag: noindex`, authentication wall, or
robots.txt block prevents intended discovery/indexing. - CSS and
JavaScript resources needed to render meaningful content are
accessible. - The page is not an unintended duplicate of another URL. -
Internal links do not point through unnecessary redirects or to broken
destinations.

**Important distinctions** - `robots.txt` controls crawling; it is not a
reliable way to remove a URL from search results. - `noindex` must be
crawlable for a crawler to see the directive. Do not block the URL in
robots.txt while relying on its `noindex`. - A canonical is a hint, not
an absolute command. Align internal links, sitemap URLs, redirects, and
canonical tags. - A sitemap helps discovery but does not guarantee
indexing. - Do not put private or sensitive information in robots.txt;
it is publicly readable.

### HTTP, domains, and redirects

-   Enforce HTTPS and choose one preferred host (`www` or non-`www`).
-   Redirect HTTP and alternate hosts to the preferred URL with a single
    permanent redirect where appropriate.
-   Avoid redirect chains and loops.
-   Use `301`/`308` for permanent URL moves and temporary redirects only
    when the move is genuinely temporary.
-   Return real `404` or `410` for removed pages when no relevant
    replacement exists. Do not redirect every missing URL to the
    homepage.
-   Prevent soft 404s: an error page should not return a normal `200`
    response when the resource is genuinely missing.
-   Ensure staging, preview, and development environments cannot
    accidentally be indexed.
-   Verify canonical host, protocol, trailing-slash policy, case
    handling, and URL encoding consistently.

### Canonicals and duplicates

-   Give indexable pages a correct absolute canonical URL, usually
    self-referencing.
-   Use one canonical URL per equivalent content set.
-   Canonicals should point to a valid, indexable preferred page---not a
    redirect, 404, blocked page, or unrelated destination.
-   Consolidate duplicate URL variants caused by tracking parameters,
    sorting, session IDs, casing, or trailing-slash inconsistencies
    where appropriate.
-   Do not canonicalize genuinely distinct pages merely because they
    share a template or some text.
-   For paginated series, make each page's canonical strategy consistent
    with the actual page content; do not canonicalize every page to page
    one if that would hide distinct content.
-   Avoid relying on canonical tags as a substitute for sensible URL and
    internal-link design.

### XML sitemap

-   Generate sitemap(s) from canonical, public, indexable URLs that
    return successful responses.
-   Exclude redirects, errors, `noindex` URLs, internal search results,
    and non-canonical duplicates.
-   Use absolute URLs and the preferred protocol/host.
-   Include meaningful `lastmod` values only when the page's primary
    content materially changed.
-   Split large sitemaps according to current search-engine limits and
    use a sitemap index when needed.
-   Keep sitemap generation deterministic and test it in CI where
    practical.
-   Reference the sitemap in `robots.txt` and submit it in Google Search
    Console/Bing Webmaster Tools when access is available.
-   Do not assume sitemap submission means all URLs are indexed.

### robots.txt and meta robots

-   Create a small, deliberate robots policy based on the actual site.
-   Check that important assets and public pages are not blocked
    accidentally.
-   Do not use `Disallow` as the sole deindexing mechanism.
-   Use page-level `noindex` for pages that should be crawlable but
    excluded from search, where appropriate.
-   Test production output after deployment; environment-specific config
    mistakes are common.

## 2. Rendering and framework-specific implementation

Adapt to the detected stack; do not force a framework-specific recipe
onto another stack.

-   **SSR/SSG/static HTML:** prefer server-rendered or pre-rendered
    meaningful content for important landing pages where practical.
-   **CSR/SPA:** ensure each meaningful view has a stable URL; use
    crawlable links, correct status handling, page-specific
    titles/descriptions/canonicals, and inspect rendered output. Do not
    assume every crawler executes JavaScript identically.
-   **React/Next.js/Nuxt/SvelteKit/Astro/etc.:** use the framework's
    supported metadata, routing, server rendering, sitemap, and redirect
    mechanisms. Verify the final generated HTML and response codes.
-   Avoid rendering all pages with the same title, description,
    canonical, or social metadata.
-   Do not use client-only navigation elements without real link
    destinations for primary navigation.
-   Avoid hydration errors or client-side state that causes search
    engines and users to see materially different primary content.
-   Ensure dynamic routes return appropriate `404`/`410` responses for
    nonexistent entities.
-   Keep structured data synchronized with the visible page content and
    actual database state.
-   Treat third-party scripts as potential performance and rendering
    risks.

## 3. Site architecture and URL design

-   Organize pages around user tasks, entities, and search intent.
-   Use a clear hierarchy: homepage → meaningful categories/sections →
    subcategories or detail pages.
-   Keep important pages reachable through contextual internal links; do
    not depend only on site search, JavaScript events, or sitemap
    discovery.
-   Use descriptive, stable, readable URLs with lowercase and hyphens
    where suitable.
-   Avoid needless nesting, opaque identifiers in public-facing URLs
    when descriptive slugs are practical, and frequent URL changes.
-   Use breadcrumbs when they help users understand location.
-   Link to the most important pages from relevant high-level pages.
-   Create a URL inventory and define canonical/indexing rules before
    launch.
-   Do not create many near-identical city, keyword, or doorway pages
    solely to capture query variations.
-   Do not change existing URL patterns during a redesign without a
    migration plan.

## 4. Search intent, keyword research, and page mapping

Do not stuff keywords into pages. Determine what the searcher is trying
to accomplish.

For each important page: 1. Identify the primary intent: informational,
navigational, commercial investigation, transactional, or local. 2.
Research real query language using available evidence such as Search
Console, keyword tools, SERP inspection, customer questions,
sales/support conversations, and competitor page types. 3. Assign one
clear primary topic and a sensible cluster of closely related subtopics
to the best page. 4. Check whether an existing page already satisfies
that intent before creating a new one. 5. Identify what the page must
contain to be genuinely more useful than alternatives. 6. Define a
measurable goal: qualified traffic, leads, sales, signups, bookings, or
successful task completion.

Create a page map with: - URL/route - page type/template - audience and
intent - primary topic and related questions - title/H1 proposal -
indexability/canonical decision - internal links in/out - conversion
goal - content owner/update trigger

Do not fabricate search volumes, keyword difficulty, traffic, backlinks,
or competitor data. Label estimates and data sources.

## 5. On-page SEO

### Titles

-   Write a unique, descriptive, natural title for every important
    indexable page.
-   Put the page's main topic and distinguishing value early where it
    reads naturally.
-   Keep titles concise enough to communicate the page clearly; there is
    no guaranteed character limit because search snippets vary.
-   Avoid repeated boilerplate, keyword lists, and misleading promises.
-   Generate titles from reliable page data, with sensible fallbacks for
    missing fields.

### Meta descriptions

-   Write a unique, accurate summary that helps a searcher decide
    whether to visit.
-   Mention the page's value proposition and relevant details naturally.
-   Treat the description as a snippet suggestion, not a guaranteed
    displayed result or direct ranking boost.
-   Avoid duplicating the same description across all routes.

### Headings and content structure

-   Use a clear main page heading and logical subheadings.
-   Headings should help users navigate content, not serve as keyword
    containers.
-   Use semantic HTML for lists, tables, navigation, main content, and
    landmarks.
-   Ensure the main content answers the page's purpose promptly.
-   Avoid empty headings, heading levels used only for visual styling,
    and repetitive headings across thin pages.

### Images and media

-   Use descriptive file names when practical.
-   Provide useful alt text for informative images; use empty alt text
    (`alt=""`) for purely decorative images.
-   Avoid stuffing keywords into alt text.
-   Use responsive images (`srcset`/`sizes` where supported),
    appropriate dimensions, modern formats where suitable, and lazy-load
    below-the-fold images.
-   Do not lazy-load the main above-the-fold/LCP image in a way that
    delays rendering; consider `fetchpriority="high"` when justified.
-   Make important media discoverable and ensure image URLs are
    crawlable.
-   Provide captions, transcripts, or equivalent context for meaningful
    video/audio content when useful.
-   Avoid replacing essential text with text embedded in images.

### Internal links

-   Use descriptive, contextual anchor text.
-   Link related pages where it helps users and crawlers understand
    relationships.
-   Repair broken links and avoid orphan pages.
-   Keep primary navigation usable on keyboard, mobile, and without
    relying on obscure interactions.
-   Do not mass-generate exact-match anchors or links solely to
    manipulate rankings.

## 6. Content quality and editorial standards

Create content to solve a real user problem, not merely to occupy a
keyword.

-   Provide original information, expertise, analysis, examples,
    demonstrations, firsthand experience, useful tools, or clear
    synthesis.
-   Make claims specific and verifiable; cite trustworthy primary
    sources for factual or high-stakes claims.
-   Clearly distinguish facts, estimates, opinions, and assumptions.
-   Use qualified authorship and reviewer information when relevant to
    the subject and audience.
-   Keep business identity, contact details, policies, and editorial
    accountability clear when appropriate.
-   Review content for accuracy, outdated information, unsupported
    superlatives, grammar, and duplication.
-   Refresh a page when facts, products, laws, prices, or user needs
    change; do not change dates just to appear fresh.
-   Consolidate or remove low-value pages only after checking traffic,
    links, user value, and replacement options.
-   AI can assist with research, outlining, editing, and structured
    drafting. Do not mass-publish unoriginal, unverified pages. Add real
    expertise and human quality control.
-   Never plagiarize, spin competitors' text, invent reviews, fabricate
    credentials, or create fake experience.

## 7. Structured data / Schema.org

-   Use supported structured data only when it accurately describes
    visible page content and the entity.
-   Prefer JSON-LD when appropriate for the stack.
-   Select schema by page purpose, not because more schema seems better.
    Possible types include `Organization`, `WebSite`, `BreadcrumbList`,
    `Article`, `Product`, `ProductGroup`, `LocalBusiness`, `Event`,
    `JobPosting`, `Recipe`, or `VideoObject` when applicable and
    eligible.
-   Use only properties that are true and supported by the data.
-   Keep price, currency, availability, rating, review count, dates,
    business details, and product identifiers consistent with visible
    content.
-   Never fabricate ratings, reviews, author credentials, prices, or
    availability.
-   Do not add irrelevant schema to every page or assume schema
    guarantees a rich result.
-   Validate syntax with Schema Markup Validator and Google Rich Results
    Test where relevant; then verify actual deployed markup.
-   Follow the current official documentation for eligibility,
    required/recommended properties, and supported result types. Search
    features and eligibility change over time.

## 8. Ecommerce SEO

Apply the universal rules plus these ecommerce-specific checks.

### Information architecture

-   Build crawlable paths from homepage to category, subcategory, and
    product pages.
-   Important products should be reachable through normal `<a href>`
    links, not only internal search or filters.
-   Category pages should provide meaningful context and useful product
    discovery.
-   Use stable product and category URLs.
-   Maintain consistent product IDs, variant relationships, and
    canonical policies.
-   Avoid generating indexable URLs for every filter/sort combination
    unless the landing page serves a distinct, valuable search intent.

### Product pages

Where relevant, include accurate: - Product name, brand, model/SKU/GTIN
identifiers - Unique description and differentiating details - Current
price and currency - Stock/availability - Images and variant choices -
Shipping, returns, warranty, dimensions, materials, compatibility, and
usage details - Genuine customer reviews and ratings, if collected and
displayed - Related products and meaningful category links

Do not copy manufacturer text as the only content if useful original
details can be added. Do not create fake scarcity, reviews, discounts,
or availability.

### Faceted navigation, sorting, and pagination

-   Audit URLs created by color, size, price, brand, sort order, search,
    and filters.
-   Decide which filter combinations deserve indexable landing pages
    based on demand and unique value.
-   Control crawl traps and duplicate URL explosions using consistent
    internal links, canonical/noindex decisions, and carefully tested
    crawl rules.
-   Do not block crawling indiscriminately when crawlers need to see
    canonical or noindex signals.
-   Make paginated products discoverable through crawlable links and
    ensure each page exposes its own products.
-   Test infinite scroll or incremental loading with direct URLs and
    crawler-friendly pagination links.

### Product variants and out-of-stock products

-   Use a clear, consistent URL and canonical strategy for variants.
-   If variants have separate URLs, make the relationship and unique
    attributes clear and implement the current recommended structured
    data pattern.
-   For temporarily out-of-stock products, generally retain a useful
    page with truthful availability and alternatives if the product is
    expected back.
-   For permanently discontinued products, choose based on replacement
    relevance: keep a useful discontinued page, redirect to a true
    replacement, or return 404/410. Do not redirect all discontinued
    products to a broad category by default.

### Ecommerce feeds and merchant surfaces

-   When available, keep product structured data and Merchant Center
    feeds consistent.
-   Validate product identifiers, price, currency, availability,
    shipping, returns, image URLs, and landing-page consistency.
-   Do not promise Google Shopping inclusion or rich results.
-   Ensure checkout, cart, account, internal search, and personal order
    pages are not exposed as search landing pages unless there is a
    deliberate, safe reason.

## 9. Local SEO

For businesses serving a real geographic area: - Ensure the business
name, address, phone, hours, service area, and contact details are
accurate and consistent. - Create useful location/service pages only
where the business genuinely operates and each page can offer distinct
value. - Maintain and optimize the relevant business profile through the
official platform. - Encourage genuine customer reviews ethically; never
buy, fabricate, or selectively gate reviews in violation of platform
policies. - Add relevant local business structured data when appropriate
and accurate. - Include practical information such as service
availability, directions, coverage, local case studies, and staff
expertise where useful. - Do not create doorway pages with city-name
swaps and near-identical content.

## 10. International and multilingual SEO

-   Decide whether language/country versions are truly needed.
-   Use stable locale-specific URLs and implement `hreflang` annotations
    correctly when there are alternate localized versions.
-   Ensure each language page is genuinely translated/localized,
    self-canonicalizes appropriately, and has reciprocal alternate
    references.
-   Use valid language/region codes; provide an appropriate default
    where needed.
-   Do not automatically redirect all visitors based only on inferred
    location or language in ways that prevent access to alternatives.
-   Avoid mixing languages on a page without a user-centered reason.
-   Translate metadata, navigation, structured data text, and key user
    flows consistently.
-   Do not use `hreflang` as a substitute for canonicalization or
    high-quality localized content.

## 11. Performance, mobile UX, and accessibility

SEO is not achieved by chasing a single Lighthouse score. Improve real
user experience while protecting functionality.

-   Test representative URLs with Lighthouse/PageSpeed Insights and
    field data such as Core Web Vitals when available.
-   Core Web Vitals targets commonly used for a good experience are LCP
    ≤ 2.5 s, INP ≤ 200 ms, and CLS ≤ 0.1 at the 75th percentile. Confirm
    current official thresholds before making time-sensitive claims.
-   Optimize oversized images, fonts, JavaScript bundles,
    render-blocking resources, third-party scripts, server response,
    caching, and layout shifts.
-   Prioritize the actual bottleneck, not generic optimizations.
-   Use semantic HTML, keyboard-accessible controls, visible focus,
    labels, sufficient contrast, and meaningful alt text.
-   Ensure mobile content and metadata are equivalent to desktop where
    required.
-   Do not sacrifice readability or functionality to gain a synthetic
    performance score.
-   Avoid intrusive interstitials and deceptive UI.

## 12. Trust, safety, and spam prevention

Never recommend or implement: - Cloaking or showing materially different
content to search engines to manipulate results. - Hidden keyword
blocks, keyword stuffing, or manipulative link schemes. - Purchased
links intended to pass ranking credit, private link networks, or
automated link spam. - Doorway pages, mass-produced thin pages,
scraped/spun content, or fake location pages. - Fake reviews, fabricated
authors, false credentials, or misleading structured data. - Sneaky
redirects, hacked content, or misleading affiliate pages. - AI-generated
page farms without meaningful user value.

For link acquisition, focus on genuinely useful resources, digital PR,
original research, partnerships, and content people have a real reason
to cite. Distinguish legitimate promotion from paid links that
manipulate ranking signals.

## 13. Analytics and measurement

When access exists, use Google Search Console, Bing Webmaster Tools,
analytics, server logs, and business conversion data.

Measure: - Indexed and excluded URL patterns - Impressions, clicks, CTR,
and average position by query/page - Organic landing-page sessions and
engagement - Qualified leads, sales, signups, bookings, and revenue -
Crawl errors, server errors, redirects, and bot activity - Performance
and Core Web Vitals field data - Content decay and page groups that
improve or decline

Segment by page type, device, country, brand/non-brand query, and date
range where useful. Compare equivalent periods and account for
seasonality, tracking changes, site changes, and algorithm updates.

Do not infer that a ranking change caused a conversion change without
evidence. Do not fabricate baselines or promise traffic growth. Annotate
significant releases and compare before/after using a suitable time
window.

## 14. Launch and migration checklist

Before launch: - \[ \] Production domain, HTTPS, preferred host, and
redirects are correct. - \[ \] Staging is blocked from indexing;
production is not accidentally blocked. - \[ \] Important routes return
correct status codes. - \[ \] Titles, descriptions, canonicals,
headings, and social metadata are page-specific. - \[ \] Sitemap
includes canonical, indexable production URLs only. - \[ \] Robots
directives are correct. - \[ \] Structured data validates and matches
visible content. - \[ \] Internal links, images, and navigation work. -
\[ \] Mobile UX, performance, accessibility, and key conversions are
tested. - \[ \] Analytics and Search Console/Bing Webmaster Tools setup
is verified where authorized. - \[ \] 404 pages and redirects are
tested. - \[ \] No secrets, private content, staging URLs, or debug data
leak into public output.

For a migration: - Inventory old URLs and map each to the closest
relevant new URL. - Preserve URLs when possible. - Implement direct
permanent redirects; avoid chains and irrelevant homepage redirects. -
Update internal links, canonicals, hreflang, structured data, and
sitemaps. - Keep redirects in place for a substantial period and monitor
old/new URL performance. - Test representative high-traffic, linked, and
conversion-critical URLs. - Do not remove the old domain or
configuration before migration requirements are satisfied.

## 15. Verification commands and tests

Use the project's existing tools first. Depending on the stack,
verify: - Build, lint, type checks, and automated tests pass. -
Production build HTML contains the intended title, description,
canonical, robots directives, headings, links, and structured data. -
Every sitemap URL is absolute, canonical, and returns a successful
response. - No important page is blocked or marked `noindex`. - No
duplicate IDs, malformed metadata, broken internal links, redirect
loops, or incorrect base URLs. - Dynamic routes for both existing and
nonexistent entities behave correctly. - Metadata escapes special
characters safely and does not emit invalid HTML. - Structured data is
valid JSON and reflects real page data. - Performance checks cover
representative templates, not just the homepage.

If shell/network/browser tools are unavailable, state which checks could
not be run and provide exact manual verification steps. Never pretend a
test ran.

## 16. Deliverable format

For an audit, return: 1. Executive summary and overall risk
(evidence-based, not a made-up score). 2. Findings table: severity,
URL/template, evidence, impact, fix, verification. 3. Prioritized
implementation plan. 4. Changes made and files touched, if any. 5. Tests
run and actual outcomes. 6. Open questions, assumptions, and manual
actions.

For implementation, return: 1. What changed and why. 2. Files/routes
affected. 3. Verification performed and results. 4. Remaining risks or
work requiring credentials, production access, or human review.

For content planning, return: 1. Audience and intent. 2.
Page-to-query/topic map. 3. Recommended page structure and unique value.
4. Internal linking plan. 5. Evidence sources and uncertainties.

## 17. Official reference sources

Use current official documentation when guidance may have changed.
Prefer primary sources over SEO folklore. Do not rely on memory for
current rich-result eligibility, platform rules, or changing ranking
features.

-   Google SEO Starter Guide:
    https://developers.google.com/search/docs/fundamentals/seo-starter-guide
-   Google Search Essentials:
    https://developers.google.com/search/docs/essentials
-   Google spam policies:
    https://developers.google.com/search/docs/essentials/spam-policies
-   Google guidance on generative AI content:
    https://developers.google.com/search/docs/fundamentals/using-gen-ai-content
-   Ecommerce SEO guidance:
    https://developers.google.com/search/docs/specialty/ecommerce
-   JavaScript SEO basics:
    https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
-   Robots.txt introduction:
    https://developers.google.com/search/docs/crawling-indexing/robots/intro
-   Sitemaps overview:
    https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
-   Structured data introduction:
    https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data
-   Search Console: https://search.google.com/search-console/about
-   PageSpeed Insights: https://pagespeed.web.dev/
-   Schema.org: https://schema.org/

## Final self-review

Before finishing, ask: - Did I inspect the real project and its stack? -
Did I distinguish crawlability, indexability, canonicalization, and
ranking? - Did I tailor the solution to this site's type and search
intent? - Are claims and structured data accurate and visible to
users? - Did I avoid thin pages, spam tactics, and unsupported
promises? - Did I test actual rendered output and report only tests that
ran? - Did I prioritize the highest-impact fixes and preserve existing
SEO equity?
