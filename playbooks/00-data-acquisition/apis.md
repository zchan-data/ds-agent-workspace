# Playbook: APIs & Official Exports

The preferred way to acquire data: stable schemas, documented contracts, and explicitly permitted use. Always check whether a source offers an API or bulk export before considering scraping.

## Tooling

| Need | Tool |
|---|---|
| Simple HTTP requests | `requests` |
| Async / HTTP-2 / high throughput | `httpx` |
| Retries with backoff | `tenacity` |
| Bulk / official exports | provider CLI or SDK (e.g., cloud `gsutil`, `aws s3`) |

## Auth Patterns

- **API keys**: load from environment / `.env` (`os.environ["API_KEY"]`), never hardcode.
- **OAuth**: use the provider's SDK to handle token refresh; store refresh tokens securely.
- Send a descriptive `User-Agent` and any required headers.

## Pagination & Rate Limits

- Paginate to completion — don't stop at the first page. Common schemes: page/offset, cursor/`next` token, link headers.
- Respect the documented rate limit. Add backoff on `429` / `503` responses with `tenacity` (exponential backoff + jitter).
- Honor `Retry-After` headers when present.

## Checklist

- [ ] Confirm the API's terms permit your intended use
- [ ] Load credentials from env vars / `.env`, never hardcoded
- [ ] Paginate fully; verify total record count against the API's reported total
- [ ] Add retries with exponential backoff for transient failures
- [ ] Cache raw JSON responses to `data/raw/` (avoid re-hitting the API on every run)
- [ ] Record endpoint, query params, and extraction date as provenance
- [ ] Hand cleaned-up parsing to the cleaning stage — store raw payloads as-is

## Notes

<!-- Add project-specific notes here -->
