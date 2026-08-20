# Playbook: Data Cleaning

> Stub — fill in with your preferred conventions, gotchas, and checklists as you build them up.

## Goals
- Arrive at a clean, well-typed DataFrame (or equivalent) ready for EDA and feature engineering.
- Preserve raw data untouched in `data/raw/`; write outputs to `data/processed/`.

## Checklist

- [ ] Inspect shape, dtypes, missing value counts (`df.info()`, `df.isnull().sum()`)
- [ ] Identify and document duplicates
- [ ] Handle missing values (drop, impute, or flag — document the choice)
- [ ] Fix dtypes (parse dates, cast categoricals, correct numeric strings)
- [ ] Standardize column names (snake_case, no spaces)
- [ ] Check for outliers and decide handling strategy
- [ ] Validate against expectations (row counts, value ranges, referential integrity)
- [ ] Save cleaned data to `data/processed/` with a versioned filename or timestamp

## Notes

<!-- Add project-specific conventions here as you encounter them -->
