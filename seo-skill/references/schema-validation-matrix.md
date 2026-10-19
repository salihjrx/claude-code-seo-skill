# Structured Data Validation Matrix

Structured data can enable eligibility for certain search features; it does not guarantee display or rankings.

| Page type | Candidate types | Critical visible-data alignment | Common risk |
|---|---|---|---|
| Product | Product, Offer, AggregateRating/Review when eligible | title, price, currency, availability, variant, reviews | fabricated or hidden claims |
| Article | Article/BlogPosting | headline, author, dates, image | misleading dates/authors |
| Organization | Organization / subtype | legal/public identity, logo, official URLs | unsupported identity claims |
| Local business | LocalBusiness subtype | name, address, phone, hours, service details | virtual or inaccurate location |
| Breadcrumb | BreadcrumbList | actual navigational hierarchy | unrelated breadcrumb labels |
| Event | Event | real dates, venue, ticket/attendance facts | stale or invented event facts |
| Video | VideoObject | visible video, thumbnail, dates and duration | inaccessible or misleading media |
| Job posting | JobPosting | real job, employer, location, salary if supplied | expired/ghost vacancies |
| Recipe | Recipe | actual ingredients, instructions, times and media | missing or false recipe data |

## Validation sequence
1. Parse JSON-LD syntax.
2. Validate required and recommended properties against current official documentation.
3. Compare all material values with visible page content and source data.
4. Confirm page is accessible and not unintentionally blocked.
5. Test representative URLs in the appropriate official rich-result/structured-data tools.
6. Validate template coverage and edge cases in CI.
7. After deployment, inspect real search reports where available; eligibility is not guaranteed display.

Do not add every schema type to every page. Prefer accurate, specific markup over maximal markup.
