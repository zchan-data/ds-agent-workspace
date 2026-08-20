# Playbook: File & Database Ingestion

Acquiring data from files (delivered exports, uploads) or by querying a database/warehouse.

## File Formats

| Format | Loader | Notes |
|---|---|---|
| CSV | `pandas.read_csv` / `polars.read_csv` | Watch encoding and delimiter; specify `dtype` to avoid silent mis-parsing |
| Excel | `pandas.read_excel` | Specify `sheet_name`; beware merged cells and header rows |
| Parquet | `pandas.read_parquet` / `polars.read_parquet` | Preferred for large data — typed, compressed, columnar |
| JSON / JSONL | `pandas.read_json` / `json` | Use JSONL (line-delimited) for streaming large files |

- Prefer **Parquet** over CSV for anything large or reused — it preserves dtypes and is far faster.
- Use **polars** over pandas when files are large or memory is tight.

## Database & Warehouse Pulls

| Context | Tool |
|---|---|
| Local files as SQL | `duckdb` (query CSV/Parquet directly) |
| Relational DB | `sqlalchemy` + `pandas.read_sql` |
| Cloud warehouse | provider connector (Snowflake, BigQuery, Redshift) |

For query conventions (CTEs, grain checks, validating joins), see [06-analytics.md](../06-analytics.md). Store query results to `data/raw/` (or `data/processed/` if the query already does meaningful transformation).

## Checklist

- [ ] Validate schema on load: column names, dtypes, row count vs. expected
- [ ] Check encoding (CSV) and the correct sheet/header (Excel)
- [ ] For DB pulls, confirm the query grain and check for duplicates after joins
- [ ] Save acquired data to `data/raw/`; record source path/query and extraction date
- [ ] Prefer Parquet when persisting large intermediate data

## Notes

<!-- Add project-specific notes here -->
