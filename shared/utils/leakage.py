"""Look-ahead detection for time-indexed feature pipelines.

The general test for look-ahead bias needs no domain knowledge and no labels:

    A feature computed at time t from information available at time t must be
    **identical** whether or not data after t exists in the input.

So build the features twice — once on full history, once on history truncated at
a cutoff — and compare the rows before the cutoff. Anything that differs is
peeking forward. This catches centered rolling windows, full-sample scalers,
`bfill`, sorting bugs, and target contamination in one shot, across every column
at once, without having to reason about each transform individually.

Provenance: developed for a cross-sectional forecasting project built in this
workspace, where it was validated against a 158-feature panel, then generalized.

    from shared.utils import assert_no_lookahead

    assert_no_lookahead(build_features, prices, cutoff="2023-06-30",
                        key_cols=("date", "ticker"))
"""
from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import pandas as pd

__all__ = ["lookahead_columns", "assert_no_lookahead"]


def lookahead_columns(
    full: pd.DataFrame,
    truncated: pd.DataFrame,
    cutoff,
    cols: Sequence[str] | None = None,
    *,
    time_col: str = "date",
    key_cols: Sequence[str] | None = None,
    exclude: Sequence[str] = (),
    rtol: float = 1e-7,
    atol: float = 1e-10,
    min_rows: int = 100,
    min_coverage: float = 0.5,
) -> list[str]:
    """Return the columns whose pre-cutoff values change when the future is removed.

    Args:
        full: features built from the complete history.
        truncated: features built from the same data cut at `cutoff`.
        cutoff: the truncation point; only rows at or before it are compared.
        cols: columns to check. Defaults to every numeric column not in
            `key_cols` or `exclude`.
        time_col: the time column used for the cutoff comparison.
        key_cols: columns identifying a row (e.g. ``("date", "ticker")`` for a
            panel). Defaults to ``(time_col,)``.
        exclude: columns to skip — put your **target** here. A forward-looking
            label legitimately depends on the future and will always be flagged.
        rtol, atol: float comparison tolerances. Loose enough to absorb
            floating-point noise from differing input lengths, far tighter than
            any real leak.
        min_rows, min_coverage: guards that fail the check outright if the
            comparison window is too small or too NaN-heavy to be meaningful.

    Returns:
        Sorted list of offending column names — empty means no look-ahead.
    """
    keys = list(key_cols) if key_cols else [time_col]
    skip = set(keys) | set(exclude)

    a = full[full[time_col] <= cutoff].set_index(keys).sort_index()
    b = truncated[truncated[time_col] <= cutoff].set_index(keys).sort_index()

    if cols is None:
        cols = [
            c
            for c in a.columns
            if c not in skip and pd.api.types.is_numeric_dtype(a[c])
        ]
    else:
        cols = [c for c in cols if c not in skip]
    if not cols:
        raise ValueError("no columns left to check after applying key_cols/exclude")

    missing = sorted(set(cols) - set(b.columns))
    if missing:
        raise ValueError(f"columns absent from the truncated build: {missing}")

    common = a.index.intersection(b.index)
    if len(common) < min_rows:
        raise AssertionError(
            f"only {len(common)} overlapping rows before the cutoff (need "
            f"{min_rows}) — the comparison window is too thin to be meaningful; "
            "move the cutoff later or lengthen the input"
        )
    a, b = a.loc[common], b.loc[common]

    # An all-NaN window would make the check pass vacuously.
    x_all = a[cols].to_numpy(dtype=float)
    coverage = 1.0 - float(np.isnan(x_all).mean())
    if coverage < min_coverage:
        raise AssertionError(
            f"only {coverage:.0%} of compared values are non-NaN (need "
            f"{min_coverage:.0%}) — lookback windows have not filled, so the "
            "check would pass vacuously"
        )

    bad = []
    for c in cols:
        x = a[c].to_numpy(dtype=float)
        y = b[c].to_numpy(dtype=float)
        both_nan = np.isnan(x) & np.isnan(y)
        if not np.allclose(
            np.where(both_nan, 0.0, x),
            np.where(both_nan, 0.0, y),
            rtol=rtol,
            atol=atol,
        ):
            bad.append(c)
    return sorted(bad)


def assert_no_lookahead(
    build: Callable[[pd.DataFrame], pd.DataFrame],
    data: pd.DataFrame,
    cutoff,
    *,
    time_col: str = "date",
    key_cols: Sequence[str] | None = None,
    cols: Sequence[str] | None = None,
    exclude: Sequence[str] = (),
    **kwargs,
) -> None:
    """Build features on full and truncated history; raise if any feature peeks.

    `build` must be a pure function of its input frame — if it reads a cached
    panel or a global, the truncation has no effect and the check is vacuous.

    Raises:
        AssertionError: naming the offending columns.
    """
    full = build(data)
    truncated = build(data[data[time_col] <= cutoff])

    bad = lookahead_columns(
        full,
        truncated,
        cutoff,
        cols,
        time_col=time_col,
        key_cols=key_cols,
        exclude=exclude,
        **kwargs,
    )
    if bad:
        raise AssertionError(
            f"{len(bad)} column(s) change before {cutoff} when later data is "
            f"removed, i.e. they use future information: {bad}"
        )
