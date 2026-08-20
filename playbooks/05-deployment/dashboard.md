# Playbook: Dashboard Deployment

## Stack

| Use case | Tool |
|---|---|
| Quick internal tool, prototype | Streamlit |
| Complex interactivity, multi-page | Dash (Plotly) |
| BI / non-technical stakeholders | Metabase, Superset, or Tableau |

## Checklist

- [ ] Separate data loading from display logic — use `@st.cache_data` / `@st.cache_resource` in Streamlit
- [ ] Keep heavy computation out of the render loop (precompute, cache, or offload to API)
- [ ] Add input validation and user-friendly error messages
- [ ] Test with realistic data volumes — Streamlit can choke on large DataFrames in the browser
- [ ] Pin all dependencies
- [ ] Document how to run locally in `app/README.md`

## Streamlit Conventions

- One `app.py` at the root of `app/`; split into pages under `app/pages/` for multi-page apps
- Load model/data with `@st.cache_resource` so it survives reruns
- Use `st.secrets` for credentials, never hardcode

## Notes

<!-- Add project-specific notes here -->
