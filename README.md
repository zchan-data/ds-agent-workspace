# Data Science Agent Workspace

An opinionated workspace for doing data science with an AI coding agent
([Claude Code](https://claude.com/claude-code), or anything else that reads a
project instruction file).

It is not a library or a framework. It's the surrounding structure: **playbooks**
telling the agent how to approach each stage of the lifecycle, a **project
skeleton** to copy, and a small set of **shared utilities** for the things that
are easy to get silently wrong.

The goal is that "help me with this dataset" produces the same disciplined work
every time, instead of whatever the model felt like doing that day.

---

## What's in here

```
├── CLAUDE.md            ← the agent's entry point: structure, conventions, working agreements
├── playbooks/           ← how to approach each stage, from acquisition to deployment
├── templates/
│   └── project-skeleton/  ← copy this to start a project
├── shared/
│   ├── utils/           ← leakage detection, temporal validation, HAC stats, panel normalization
│   └── tests/
└── projects/            ← your actual work (not tracked in this repo)
```

## Quick start

```bash
git clone https://github.com/<you>/ds-agent-workspace.git
cd ds-agent-workspace

cp -r templates/project-skeleton projects/my-project
cd projects/my-project && git init
```

Fill in the project `README.md` with the goal and data sources before doing
anything else, then point your agent at the workspace. `CLAUDE.md` is loaded
automatically by Claude Code; other tools may need it pointed at explicitly.

Run the shared utility tests from the workspace root:

```bash
pip install pandas numpy scipy pytest
pytest
```

---

## The playbooks

`playbooks/` is the substance of this repo. Each one covers a single stage and is
written to be *followed* rather than read: decision tables for choosing an
approach, checklists for the work itself, and named anti-patterns to avoid.
`CLAUDE.md` directs the agent to the relevant playbook before it starts a stage.

| Stage | What it covers |
|---|---|
| [**00 Data acquisition**](playbooks/00-data-acquisition/README.md) | Getting raw data in and recording where it came from. Sources are tried in order of stability: official API first, then files and databases, then scraping as a last resort. Raw payloads land untouched in `data/raw/` with provenance logged. |
| [**01 Data cleaning**](playbooks/01-data-cleaning.md) | Reaching a typed, validated frame. Dtypes, duplicates, missing values, outliers, and a documented decision for each, with the raw data left untouched. |
| [**02 EDA**](playbooks/02-eda.md) | Univariate through multivariate analysis, class balance, temporal patterns, and projecting high-dimensional data with PCA, UMAP, or t-SNE. Findings get narrated in the notebook, figures saved to `outputs/figures/`. |
| [**03 Feature engineering**](playbooks/03-feature-engineering.md) | Encoding, scaling, interactions, and dimensionality reduction, including a table for picking between PCA, TruncatedSVD, LDA, UMAP, and autoencoders. Everything fitted inside a pipeline so it stays leakage-free. |
| [**04 Modeling**](playbooks/04-modeling/README.md) | Baseline first, tune on cross-validation and never on test, serialize the preprocessor together with the model. Routes to one of four sub-playbooks. |
| [**05 Deployment**](playbooks/05-deployment/README.md) | Decoupling the model from the serving layer, pinning dependencies, validating inputs at the boundary, and logging predictions for monitoring. Routes to one of three targets. |
| [**06 SQL analytics**](playbooks/06-analytics.md) | When to push work into SQL instead of Python, query conventions (CTEs, `.sql` files under `src/queries/`, grain and fan-out checks), and DuckDB for querying local Parquet. |

Three stages have sub-playbooks, and their `README.md` acts as the router:

**Acquisition** splits into `apis.md` (auth patterns, pagination to completion,
rate limits and backoff, response caching), `files-databases.md` (format loaders,
why Parquet beats CSV, warehouse pulls, schema validation on load), and
`scraping.md`, which is the most opinionated of the three: a legal and ethics
gate you cannot skip, a decision framework that pushes you toward a backing JSON
endpoint before you ever parse HTML, and a list of anti-patterns like reaching
for a headless browser when `requests` would do.

**Modeling** splits into `classification.md` and `regression.md` (metric
selection by scenario, and a model progression from a dummy baseline through
linear models to boosted trees), `deep-learning.md` (start from pretrained, plus
a separate checklist for LLM and RAG work), and
[`time-series.md`](playbooks/04-modeling/time-series.md), described below.

**Deployment** splits into `api.md` (FastAPI with Pydantic schemas, model loaded
at startup, health endpoint, per-request logging), `dashboard.md` (Streamlit
versus Dash, caching, testing against realistic data volumes), and
`reporting.md` (`nbconvert` for clean exports, `papermill` for parameterized
reports).

---

## The opinionated parts

Most of this is unremarkable good practice. Four things are deliberate choices
worth knowing about before you adopt it.

**Playbooks are instructions, not documentation.** `CLAUDE.md` directs the agent
to read the relevant playbook *before* starting a stage. They're written as
checklists and decision tables, the format an agent follows well, rather than as
prose explaining concepts it already knows.

**The decision log is the experiment tracker.** Every project README carries a
dated `Key Decisions` section: what changed, what it did to the metric, what you
concluded, and the caveats. MLflow and W&B are better once you're running real
sweeps, but a log the agent maintains as it works beats a tracking server nobody
sets up. Negative results get logged with the same care as positive ones.

**Test invariants, not outputs.** Analysis bugs rarely crash; they produce a
plausible wrong number. So the tests assert properties: no look-ahead in
features, no future data in a training fold, transforms fitted only on training
data. `shared/utils/leakage.py` implements the general version: build features on
full history and on truncated history, then flag every column that changes. One
assertion catches leaks nobody thought to look for.

**Time series is treated as its own discipline.**
[`playbooks/04-modeling/time-series.md`](playbooks/04-modeling/time-series.md)
exists because temporal data is a regression problem *plus* four categories of
leak that silently invalidate results: features that see their own future, labels
that overlap the fold boundary, preprocessing fitted across the split, and a
universe selected on facts known only later. It is the longest and most detailed
file in the repo.

---

## Adapting it

Fork it and edit. The tooling preferences in `CLAUDE.md` (pandas, scikit-learn,
LightGBM, FastAPI, Streamlit, DuckDB) are choices, not requirements. Change the
table and the agent follows. Playbooks marked as stubs are intentionally thin;
fill them in with your own conventions as you hit them.

The one thing worth keeping if you keep nothing else is the working agreements
section of `CLAUDE.md`, plus `time-series.md` if you touch temporal data at all.

## License

MIT. See [LICENSE](LICENSE).
