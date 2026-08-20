# Playbook: Notebook Reporting

## Goal

Produce a clean, self-contained report from a Jupyter notebook — either as rendered HTML, PDF, or a shared notebook link.

## Checklist

- [ ] Clear all outputs, then re-run the notebook top-to-bottom in a fresh kernel before exporting
- [ ] Move all parameters (dates, thresholds, file paths) to the top cell — makes reruns easy
- [ ] Use markdown cells to narrate findings; figures should be self-labeling (titles, axis labels, units)
- [ ] Hide implementation cells with `# noqa` tags or Jupyter's "hide input" metadata if sharing with non-technical stakeholders
- [ ] Export with `nbconvert`: `jupyter nbconvert --to html --execute notebook.ipynb`
- [ ] Save output to `outputs/reports/`

## Parameterized Reports

Use `papermill` to run notebooks with different parameters programmatically:

```bash
papermill template_notebook.ipynb outputs/reports/report_2024-01.ipynb \
  -p start_date 2024-01-01 -p end_date 2024-01-31
```

## Notes

<!-- Add project-specific notes here -->
