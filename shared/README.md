# Shared Utilities

Reusable helpers available to every project. Add the workspace root to
`PYTHONPATH`, then import from the package:

```python
from shared.utils import assert_no_lookahead, WalkForwardSplit
```

Run the tests from the workspace root:

```bash
pytest        # shared/tests
```

## What's here

| Module | Provides | Use it when |
|---|---|---|
| [`utils/leakage.py`](utils/leakage.py) | `assert_no_lookahead`, `lookahead_columns` | Any time-indexed feature pipeline. Builds features on full vs. truncated history and flags every column that changes — one assertion covering leaks you didn't think to check for. |
| [`utils/validation.py`](utils/validation.py) | `WalkForwardSplit` | Splitting temporal data. Expanding or rolling window, and it **purges** the fold boundary so forward-looking labels can't reach into the test block. Requires you to declare `label_horizon`. |
| [`utils/stats.py`](utils/stats.py) | `newey_west_se`, `mean_significance`, `effective_sample_size` | Testing the mean of an autocorrelated series — overlapping-window backtests, rolling metrics. The naive t-stat is inflated; these report both so the gap is visible. |
| [`utils/panel.py`](utils/panel.py) | `neutralize_cross_section` | Normalizing entity × time panels within each period (z-score or rank). Leak-free by construction — no train/test fit to keep straight. |

## The bar for adding something

Promote code here **after** a project has proven it works, not on speculation —
the same rule `templates/` follows. Each module's docstring records where it
came from and what it was worth there. Anything promoted needs a test in
`shared/tests/`.
