# Security, Privacy and SEO Operations

SEO work often touches production, analytics, logs and customer data. Follow least privilege.

- Never print secret values, cookies, authorization headers, API tokens, private customer records or environment values.
- Redact query strings if they can contain personal data, session identifiers or tokens.
- Treat robots.txt as public, not as an access-control mechanism.
- Do not expose private staging pages or internal search results through sitemaps or structured data.
- Validate user-controlled URL inputs before crawling; defend against SSRF, local-network access, redirects to private IPs and unbounded resource use.
- Rate-limit crawlers and respect service constraints.
- Do not send data to external SEO vendors without authorization and privacy review.
- Consent, analytics and personalization changes require privacy/legal review where applicable.
- Never use cloaking, hidden content, doorway pages, spam or fabricated structured data.
- Obtain explicit approval before production deploys, DNS changes, external account actions or paid activity.
