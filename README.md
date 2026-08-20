# Data Science AI Workspace

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

Fill in the project `README.md` — goal and data sources — before doing anything
else, then point your agent at the workspace. `CLAUDE.md` is loaded
automatically by Claude Code; other tools may need it pointed at explicitly.

Run the shared utility tests from the workspace root:

```bash
pip install pandas numpy scipy pytest
pytest
```

---

## The opinionated parts

Most of this is unremarkable good practice. Four things are deliberate choices
worth knowing about before you adopt it.

**Playbooks are instructions, not documentation.** `CLAUDE.md` directs the agent
to read the relevant playbook *before* starting a stage. They're written as
checklists and decision tables — the format an agent follows well — rather than
prose explaining concepts it already knows.

**The decision log is the experiment tracker.** Every project README carries a
dated `Key Decisions` section: what changed, what it did to the metric, what you
concluded, and the caveats. MLflow and W&B are better once you're running real
sweeps, but a log the agent maintains as it works beats a tracking server nobody
sets up. Negative results get logged with the same care as positive ones.

**Test invariants, not outputs.** Analysis bugs rarely crash; they produce a
plausible wrong number. So the tests assert properties: no look-ahead in
features, no future data in a training fold, transforms fitted only on training
data. `shared/utils/leakage.py` implements the general version — build features
on full history and on truncated history, and flag every column that changes.
One assertion catches leaks nobody thought to look for.

**Time series is treated as its own discipline.**
[`playbooks/04-modeling/time-series.md`](playbooks/04-modeling/time-series.md)
exists because temporal data is a regression problem *plus* four categories of
leak that silently invalidate results. It's the most expensively-learned file
here — see below.

---

## Where this came from

The methodology isn't invented. It's the residue of a real project built in this
workspace: a cross-sectional equity forecasting model that produced an
encouraging **+1.82 Sharpe ratio**, which turned out to be an artifact of a
105-day evaluation window. Widening it to 1,861 days flipped the sign. Correcting
the cost accounting, averaging over rebalance timing instead of reporting the
best configuration, and applying a HAC correction for overlapping windows left a
final answer of **no tradable edge** — a negative result, and the correct one.

Nothing was wrong with the model. Everything was wrong with how it was measured.

The playbooks and the shared utilities are the parts of that experience worth
keeping, so the next project starts from the corrected version. The project
itself isn't in this repo — only what generalizes.

---

## Adapting it

Fork it and edit. The tooling preferences in `CLAUDE.md` (pandas, scikit-learn,
LightGBM, FastAPI, Streamlit, DuckDB) are choices, not requirements — change the
table and the agent follows. Playbooks marked as stubs are intentionally thin;
fill them in with your own conventions as you hit them.

The one thing worth keeping if you keep nothing else is the working agreements
section of `CLAUDE.md`, plus `time-series.md` if you touch temporal data at all.

## License

MIT — see [LICENSE](LICENSE).
