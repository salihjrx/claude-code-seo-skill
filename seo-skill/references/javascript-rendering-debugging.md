# JavaScript Rendering Debugging Playbook

## Failure model
Separate these stages:
1. URL discovery;
2. HTTP fetch and response status;
3. HTML parsing;
4. resource access;
5. JavaScript execution/rendering;
6. link discovery after rendering;
7. canonical/robots/schema interpretation;
8. indexing and ranking (not directly proven by local rendering).

## Per-template comparison
For a representative URL, capture:
- raw response HTML;
- rendered DOM/HTML from a browser-capable tool if available;
- screenshot/console/network errors if available;
- status and redirect chain;
- title, description, H1, canonical, robots, hreflang;
- main content and internal links;
- JSON-LD and visible content consistency;
- hydration/runtime errors;
- blocked CSS/JS/API resources.

Do not claim Google renders a page exactly as a local browser does. A local browser render proves local behavior only.

## Debugging sequence
- Confirm primary content and links exist in initial HTML where practical.
- If client-rendered, ensure rendering completes without authentication, consent, geolocation or interaction prerequisites that prevent discovery.
- Test direct navigation and refresh for deep routes.
- Verify canonical and robots values after hydration, and ensure they do not conflict with initial HTML.
- Check API responses, cache variance and user-agent-independent substantive content.
- Avoid lazy-loading primary text/links behind user interaction.
- Confirm images have meaningful alt text where informative and dimensions to reduce layout shift.
- Verify rendered schema matches the visible page.
- Re-run tests after build/minification, not only in development.

## Acceptance tests
A critical page passes only if:
- response is expected and stable;
- primary content is available without interaction;
- crawlable links lead to important related pages;
- no unintended noindex/canonical override appears;
- schema parses and matches visible facts;
- page is usable on mobile and doesn't rely on console-free assumptions.
