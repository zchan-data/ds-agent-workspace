# Data Science AI Workspace

## Purpose

This is a multi-project data science hub. It contains shared playbooks, reusable templates, utilities, and individual project folders. The goal is to give Claude enough context to assist with any stage of the data science lifecycle — from raw data to deployed product.

Primary language: **Python**. SQL is preferred for data extraction and heavy aggregations. Streamlit or Dash for dashboards. FastAPI for model serving.

---

## Folder Structure

```
data-science-ai/
├── CLAUDE.md               ← you are here
├── playbooks/              ← how-to guides for each workflow stage
│   ├── 00-data-acquisition/
│   │   ├── README.md       ← which acquisition method to use
│   │   ├── apis.md
│   │   ├── scraping.md
│   │   └── files-databases.md
│   ├── 01-data-cleaning.md
│   ├── 02-eda.md
│   ├── 03-feature-engineering.md
│   ├── 04-modeling/
│   │   ├── README.md       ← when to use which approach
│   │   ├── classification.md
│   │   ├── regression.md
│   │   ├── time-series.md  ← read first for any temporal data
│   │   └── deep-learning.md
│   ├── 05-deployment/
│   │   ├── README.md
│   │   ├── api.md
│   │   ├── dashboard.md
│   │   └── reporting.md
│   └── 06-analytics.md
├── templates/              ← scaffolding to copy into new projects
│   ├── project-skeleton/   ← copy this to start a project
│   ├── notebooks/          ← starter .ipynb files per workflow stage
│   ├── scripts/            ← standalone Python scripts
│   └── configs/            ← config files (requirements, pyproject, .env.example)
├── projects/               ← one subfolder per project (see layout below)
└── shared/                 ← reusable Python modules across projects
    ├── README.md           ← index of what's available
    ├── utils/              ← leakage, validation, stats, panel
    └── tests/              ← `pytest` from the workspace root
```

---

## Playbooks

Playbooks are the primary instructions for how Claude should approach each workflow stage. Before starting any stage of work, read the relevant playbook. If a playbook has sub-pages (e.g., `playbooks/modeling/`), read the `README.md` first to determine which sub-page applies.

| Stage | Playbook |
|---|---|
| Data acquisition (APIs, scraping, ingestion) | [playbooks/00-data-acquisition/README.md](playbooks/00-data-acquisition/README.md) |
| Data cleaning | [playbooks/01-data-cleaning.md](playbooks/01-data-cleaning.md) |
| Exploratory data analysis | [playbooks/02-eda.md](playbooks/02-eda.md) |
| Feature engineering | [playbooks/03-feature-engineering.md](playbooks/03-feature-engineering.md) |
| Model selection & training | [playbooks/04-modeling/README.md](playbooks/04-modeling/README.md) |
| Time series & forecasting | [playbooks/04-modeling/time-series.md](playbooks/04-modeling/time-series.md) |
| Deployment | [playbooks/05-deployment/README.md](playbooks/05-deployment/README.md) |
| SQL analytics | [playbooks/06-analytics.md](playbooks/06-analytics.md) |

---

## Working Agreements

How work gets done here, independent of which stage you're in.

**Record decisions as you make them.** Every project README has a `Key Decisions`
section. Append a dated entry whenever you choose an approach, change a metric,
or get a result — what changed, what it did to the number, what you concluded,
and the caveats. This log *is* the experiment tracking (see Tooling below); it
is also the fastest way for anyone, including Claude, to get oriented later.

**Report results honestly, including bad ones.** A negative result is a result:
write it up with the same care as a positive one. If a number reverses after a
methodology fix, say so and explain why the old one was wrong — don't quietly
replace it. If a result rests on a short window, a lucky configuration, or an
assumption that may not hold, state that next to the number. Never present the
best of N runs as *the* result.

**Test the things that fail silently.** Bugs in analysis code usually don't
crash — they produce a plausible wrong number. So test the invariants, not the
outputs: no look-ahead in features, no future data in a training fold, correct
cost accounting, transforms fitted only on training data. Put them in the
project's `tests/`, run them on every change, and use `shared/utils` for the
machinery. Add a regression test whenever you find a bug by hand.

**Commit in logical units.** Commit when a piece of work is coherent and the
tests pass, with a message saying what changed and why. Don't commit data, model
artifacts, or secrets — the `.gitignore` files handle this; don't override them.

Note the repository boundary: **this workspace repo is public and tracks only
the workflow** (playbooks, templates, `shared/`). `projects/` is gitignored here,
and each project is its own separate repo. So run git commands from the directory
that owns what you're committing — playbook and shared-utility changes at the
workspace root, project work inside the project.

**Keep raw data immutable and provenance recorded.** `data/raw/` is never
modified in place, and every dataset gets an entry in `data/raw/SOURCES.md`
(source, extraction date, query/filters used).

---

## Project Layout

Every project under `projects/` follows this structure:

```
projects/my-project/
├── README.md           ← project goal, data sources, key decisions
├── data/
│   ├── raw/            ← original, untouched source data (never modify)
│   ├── processed/      ← cleaned/transformed data ready for modeling
│   └── external/       ← third-party data (reference datasets, lookups)
├── notebooks/          ← Jupyter notebooks (numbered by stage: 01_eda.ipynb)
├── src/                ← production-quality Python modules for this project
├── tests/              ← invariant tests (leakage, splits, accounting)
├── models/             ← serialized model artifacts (.pkl, .pt, .onnx, etc.)
├── outputs/            ← reports, plots, predictions, exports
├── resources/          ← papers, domain notes, dataset docs for THIS project
└── app/                ← deployment code (FastAPI app, Streamlit app, etc.)
```

When starting a new project, copy the skeleton:

```bash
cp -r templates/project-skeleton projects/<your-project>
cd projects/<your-project> && git init    # each project is its own repo
```

Then fill in `projects/<your-project>/README.md` with the project goal and data sources before doing any other work. The skeleton provides the structure above plus `.gitignore`, `.env.example`, `requirements.txt`, a `data/raw/SOURCES.md` provenance log, and a `resources/README.md` index.

---

## Shared Utilities

`shared/utils/` contains reusable Python helpers available to all projects. Add the workspace root to `PYTHONPATH`, then `from shared.utils import ...`. **Before writing new helper code inside a project, check whether a shared utility already exists** — see [shared/README.md](shared/README.md) for the full index.

| Import | Use for |
|---|---|
| `assert_no_lookahead`, `lookahead_columns` | Proving a time-indexed feature pipeline doesn't use future data |
| `WalkForwardSplit` | Temporal train/test splits, with fold-boundary purging |
| `mean_significance`, `newey_west_se`, `effective_sample_size` | Significance testing when observations overlap |
| `neutralize_cross_section` | Within-period normalization of entity × time panels |

Promote code here **after** a project proves it works, not on speculation. Anything promoted needs a test in `shared/tests/` (`pytest` from the workspace root).

---

## Tooling Preferences

| Task | Preferred tool |
|---|---|
| Data manipulation | pandas, polars for large data |
| ML (classical) | scikit-learn |
| ML (deep learning / LLMs) | PyTorch, HuggingFace Transformers |
| Experiment tracking | Dated decision log in the project README (baseline); MLflow or W&B once sweeps outgrow it |
| Testing | pytest — invariant tests per project in `tests/`, shared helpers in `shared/utils` |
| Model serving | FastAPI |
| Dashboards | Streamlit (quick), Dash (complex) |
| SQL | DuckDB (local), Snowflake/BigQuery (cloud) |
| Notebooks | Jupyter (`.ipynb`), nbconvert for reports |
| Visualization | matplotlib, seaborn, plotly |

---

## Resources

Reference material — papers, dataset docs, domain notes, links — lives **inside the project it belongs to**, at `projects/<name>/resources/`. Add a short entry to that folder's `README.md` whenever you drop something in, saying why it mattered, so it stays findable.

There is deliberately no workspace-level `resources/`: in practice reference material is nearly always specific to the question one project is answering, and a general folder just makes it harder to find. Reusable *code* goes in `shared/` (see above); reusable *method* goes in a playbook.
