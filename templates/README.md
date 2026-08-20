# Templates

Reusable scaffolding for new projects.

| Item | Purpose |
|---|---|
| [project-skeleton/](project-skeleton/) | Copy to `projects/<name>/` to start a new project. Mechanical structure + config stubs only — no opinionated code. |
| `notebooks/` | Reusable notebook snippets / starter cells. Grows over time. |
| `scripts/` | Standalone reusable Python scripts. Grows over time. |
| `configs/` | Shared config files (linting, formatting, CI). Grows over time. |

## Starting a New Project

```bash
cp -r templates/project-skeleton projects/<your-project>
```

Then fill in `projects/<your-project>/README.md` (goal + data sources) before doing any other work.

`notebooks/`, `scripts/`, and `configs/` are intentionally sparse — the plan is to **harvest** proven patterns here (and reusable helpers into `shared/utils/`) after building the first real project, rather than guessing them up front.
