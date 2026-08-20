# <Project Name>

## Goal

<!-- What question does this project answer? What is the target / deliverable?
     One or two sentences. -->

## Data Sources

<!-- Where does the data come from? See data/raw/SOURCES.md for the detailed
     provenance log. Summarize the main sources here. -->

## Key Decisions

<!-- Log notable choices as the project evolves: chosen metric, model family,
     features dropped, assumptions made. Keeps future-you (and Claude) oriented. -->

## How to Run

```bash
# 1. Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch notebooks / run scripts
jupyter lab
```

## Structure

| Path | Contents |
|---|---|
| `data/raw/` | Original source data — never modified (see `SOURCES.md`) |
| `data/processed/` | Cleaned / transformed data ready for modeling |
| `data/external/` | Third-party reference data, lookups |
| `notebooks/` | Jupyter notebooks, numbered by stage (`01_eda.ipynb`) |
| `src/` | Production-quality Python modules for this project |
| `tests/` | Invariant tests — leakage, splits, accounting (`pytest`) |
| `models/` | Serialized model artifacts |
| `outputs/` | Reports, figures, predictions, exports |
| `resources/` | Papers, domain notes, dataset docs (see `resources/README.md`) |
| `app/` | Deployment code (API, dashboard) |
