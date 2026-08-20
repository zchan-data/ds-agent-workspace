"""Time-series cross-validation that does not leak.

Random K-fold on temporal data trains on the future to predict the past. The
only sanctioned split is walk-forward: train on a prefix, test on the block that
follows, advance, repeat.

There is a second, subtler leak that a naive walk-forward still has. If the label
at time t is a *forward-looking* window (e.g. the return from t to t+h), then the
last h training rows carry labels computed from data inside the test block. The
fix is **purging**: drop those rows from the training set. `WalkForwardSplit`
makes you declare `label_horizon` so the decision is never silently skipped.

    from shared.utils import WalkForwardSplit

    # target = 5-period forward return -> purge 5 dates at each fold boundary
    for train_idx, test_idx in WalkForwardSplit(label_horizon=5).split(df):
        ...
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np
import pandas as pd

__all__ = ["WalkForwardSplit"]


@dataclass
class WalkForwardSplit:
    """Expanding- or rolling-window walk-forward split over a time column.

    Anchored on a **minimum training window** rather than the end of the sample:
    train on the first `min_train_size` periods, test the next `test_size`, then
    advance by `test_size` and repeat to the end of the data. Every period after
    the initial window is therefore tested exactly once, which is what gives an
    out-of-sample series long enough to have statistical power. (An end-anchored
    split that produces one short test block is the classic way to report a
    result that evaporates on a longer sample.)

    Args:
        label_horizon: how many periods **beyond** t the label at t depends on.
            0 for a contemporaneous label, 1 for a next-period label, h for an
            h-period forward return. This many periods are purged from the end
            of every training block. Required — there is no safe default, and
            getting it wrong is invisible in the metrics.
        test_size: periods per test block (also the retrain cadence).
        min_train_size: periods before the first test block. The first training
            block holds ``min_train_size - label_horizon`` of them, the rest
            being purged.
        max_train_size: ``None`` for an expanding window; an int for a fixed
            rolling window of that length.
        n_splits: ``None`` walks to the end of the data; an int caps the folds.
        time_col: the column holding the time index.

    Yields:
        ``(train_idx, test_idx)`` pairs of pandas Index objects into `df`.
    """

    label_horizon: int
    test_size: int = 63
    min_train_size: int = 756
    max_train_size: int | None = None
    n_splits: int | None = None
    time_col: str = "date"

    def __post_init__(self) -> None:
        if self.label_horizon < 0:
            raise ValueError("label_horizon must be >= 0")
        if self.test_size < 1 or self.min_train_size < 1:
            raise ValueError("test_size and min_train_size must be >= 1")

    def split(self, df: pd.DataFrame) -> Iterator[tuple[pd.Index, pd.Index]]:
        periods = np.sort(df[self.time_col].unique())
        n = len(periods)
        if n <= self.min_train_size + self.test_size:
            raise ValueError(
                f"Not enough distinct periods ({n}) for min_train_size="
                f"{self.min_train_size} + test_size={self.test_size}."
            )

        folds = 0
        test_start = self.min_train_size
        while test_start < n:
            if self.n_splits is not None and folds >= self.n_splits:
                break
            test_end = min(test_start + self.test_size, n)

            # Purge: a training row at position i has a label that is only
            # knowable at i + label_horizon, so it must satisfy
            # i + label_horizon < test_start.
            train_hi = test_start - self.label_horizon
            train_lo = (
                0 if self.max_train_size is None else max(0, train_hi - self.max_train_size)
            )
            if train_hi <= train_lo:
                raise ValueError(
                    f"label_horizon={self.label_horizon} purges the entire training "
                    f"block at fold {folds}; increase min_train_size."
                )

            train_periods = set(periods[train_lo:train_hi])
            test_periods = set(periods[test_start:test_end])
            yield (
                df.index[df[self.time_col].isin(train_periods)],
                df.index[df[self.time_col].isin(test_periods)],
            )
            folds += 1
            test_start = test_end
