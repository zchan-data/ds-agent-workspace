# Playbook: Deployment — Overview

| Target | Sub-playbook |
|---|---|
| REST API / model endpoint | [api.md](api.md) |
| Interactive web dashboard | [dashboard.md](dashboard.md) |
| Notebook report / PDF | [reporting.md](reporting.md) |

## General Principles

- **Decouple model from app.** Load the serialized artifact at startup; never retrain inside the serving layer.
- **Pin dependencies.** Use `requirements.txt` or `pyproject.toml` with exact versions for production.
- **Validate inputs at the boundary.** Don't trust that incoming data matches training data schema.
- **Log predictions.** Store inputs, outputs, and latency for monitoring and retraining.
- **Test the deployment artifact**, not just the notebook. Run the full pipeline from raw input to prediction output before shipping.
