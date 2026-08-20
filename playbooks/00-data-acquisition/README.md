# Playbook: Data Acquisition — Overview

Read this first to determine how to bring data into a project. This is the stage *before* cleaning — its job is to land raw data in `data/raw/` with its provenance recorded, then hand off to [01-data-cleaning.md](../01-data-cleaning.md).

## Method Selection (try in this order)

Always prefer the most stable, lowest-effort source. Scraping is a last resort, not a first instinct.

| Priority | Source | Sub-playbook |
|---|---|---|
| 1 | Official API or data export exists | [apis.md](apis.md) |
| 2 | Data is in files or a database you can query | [files-databases.md](files-databases.md) |
| 3 | Data is only on web pages, no API | [scraping.md](scraping.md) |

## General Principles (apply to all)

1. **Raw means raw.** Write acquired data to `data/raw/` exactly as received — no parsing, no cleaning. Transformation is a cleaning concern, not an acquisition one.
2. **Record provenance.** For every dataset, log the source (URL / endpoint / file path), the extraction date, and any query params or filters used. A short note in the project `README.md` or a `data/raw/SOURCES.md` is enough.
3. **Make it reproducible.** Prefer a script over manual download where feasible, so the acquisition can be re-run.
4. **Never commit secrets.** API keys and credentials go in environment variables / `.env` (gitignored), never in code or notebooks.
5. **Cache during development.** Don't re-hit a source on every run — cache raw responses locally and work from the cache.

Once data has landed in `data/raw/`, proceed to [01-data-cleaning.md](../01-data-cleaning.md).
