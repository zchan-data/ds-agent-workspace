# Playbook: Web Scraping

> Every site is different, so the *selectors and per-site code* are never reusable. The *process* below is. This playbook captures the durable decisions — method choice, the ethics gate, resilience patterns, and the output contract — not site-specific parsing.

## Decision Framework (before writing any code)

1. **Is there an API or data export?** If yes, stop — use [apis.md](apis.md) instead. Scraping is a last resort.
2. **Is the data in static HTML or JS-rendered?** View page source (or disable JS): if the data is in the initial HTML, you don't need a browser. If it's loaded by JavaScript, check the network tab for a backing JSON endpoint you can hit directly (often there is one — that's effectively an undocumented API and far more stable than scraping the DOM).
3. **Only if both above fail**, render the page with a headless browser.

## Legal / Ethics Gate (do not skip)

- [ ] Check `robots.txt` (`https://site.com/robots.txt`) and honor its disallow rules
- [ ] Read the site's Terms of Service — scraping may be prohibited
- [ ] Never scrape personal data (PII) or content behind authentication/paywalls without explicit permission
- [ ] Send a descriptive `User-Agent` identifying your bot and a contact
- [ ] Rate-limit yourself — never hammer a server; you are a guest

If any of these can't be satisfied, don't scrape. Find another source.

## Tooling (standard Python stack)

| Situation | Tool |
|---|---|
| Static HTML | `requests` (fetch) + `BeautifulSoup` (parse) |
| Backing JSON endpoint found | `requests` / `httpx` directly — skip HTML parsing |
| JS-rendered pages | `Playwright` (headless browser) |
| Large multi-page crawls | `Scrapy` (built-in concurrency, retries, throttling) |
| Retries with backoff | `tenacity` |

## Resilience Patterns

- **Polite delays**: sleep between requests with random jitter to avoid a fixed signature and reduce server load.
- **Retries with backoff**: wrap fetches with `tenacity` (exponential backoff) for transient `429`/`5xx` errors.
- **Cache raw responses**: save fetched HTML/JSON to `data/raw/` and develop your parser against the cache — never re-hit the site on every run.
- **Fail loudly on layout change**: if an expected element is missing, raise rather than silently writing empty data. Layout drift is the #1 cause of silent scraper breakage.

## Output Contract

- Write **raw** scraped payloads (HTML, JSON) to `data/raw/`, untouched.
- Parsing into tidy rows and normalization is a **cleaning** concern — see [01-data-cleaning.md](../01-data-cleaning.md). Keep scraping and cleaning separate so a parser bug doesn't force a re-scrape.
- Record provenance: source URLs, scrape date, pagination range.

## Anti-Patterns (avoid)

- Reaching for a headless browser (Selenium/Playwright) when `requests` + `BeautifulSoup` would do — slower, heavier, more fragile.
- No rate limiting / no delays — gets you blocked and is abusive.
- Brittle absolute XPath/CSS paths (`div > div > div:nth-child(3)`) — prefer stable attributes (`id`, `data-*`, semantic classes).
- Scraping when a documented API exists.
- Parsing inside the fetch loop — separate fetch (acquisition) from parse (cleaning).

## Checklist

- [ ] Confirmed no API/export exists (step 1 of decision framework)
- [ ] Checked for a backing JSON endpoint before parsing HTML
- [ ] Passed the legal/ethics gate (robots.txt, ToS, no PII, User-Agent)
- [ ] Chose the lightest tool that works (requests > Playwright > Scrapy by need)
- [ ] Added delays + jitter and retries with backoff
- [ ] Cached raw responses to `data/raw/`
- [ ] Parser fails loudly on missing expected elements
- [ ] Recorded provenance (URLs, date, pagination)

## Notes

<!-- Add project-specific notes here -->
