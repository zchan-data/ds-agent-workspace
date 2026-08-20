# Playbook: SQL Analytics

## When SQL (not Python)

- Aggregations over millions of rows that live in a database or data warehouse
- Joins across multiple tables before pulling data into Python
- Ad-hoc exploration directly in a warehouse (Snowflake, BigQuery, Redshift)
- Reporting queries that business users might run themselves

## Stack

| Context | Tool |
|---|---|
| Local files (CSV, Parquet) | DuckDB |
| Cloud warehouse | Snowflake / BigQuery / Redshift |
| Python integration | `duckdb` Python package, `sqlalchemy`, `pandas.read_sql` |

## Conventions

- Write queries in `.sql` files under `src/queries/`, not embedded as strings in Python
- Use CTEs over subqueries for readability
- Comment non-obvious business logic in SQL (e.g., why a filter value was chosen)
- Always include a `LIMIT` during exploration; remove it for final exports
- Validate row counts before and after joins (unexpected fan-out is a common bug)

## DuckDB Quick Start

```python
import duckdb

con = duckdb.connect()
df = con.execute("SELECT * FROM read_parquet('data/processed/*.parquet')").df()
```

## Checklist

- [ ] Confirm grain of the table before aggregating (what is one row?)
- [ ] Check for duplicates after joins
- [ ] Validate NULLs in key columns
- [ ] Save final query results to `data/processed/` or `outputs/`

## Notes

<!-- Add project-specific notes here -->
