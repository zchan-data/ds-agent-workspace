"""Significance testing for autocorrelated performance series.

The trap this exists for: when you sample a metric daily but each observation is
built from an h-period forward window, consecutive observations share data and
are strongly autocorrelated. A one-sample t-test then **understates the standard
error and inflates the t-stat** — you get a "significant" result out of noise.

The fix is a Newey-West (Bartlett-kernel) HAC standard error with lag ~ h - 1.
Reach for it whenever observations overlap: rolling-window backtest returns,
daily-sampled multi-day forecasts, any metric computed on a sliding window.

Provenance: a forecasting project built in this workspace, where the HAC
correction turned an apparently significant signal into an insignificant one
(t 0.7, p 0.49) and exposed that the headline result rested on ~105
out-of-sample observations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

__all__ = ["newey_west_se", "mean_significance", "effective_sample_size"]


def newey_west_se(x, lags: int) -> float:
    """Newey-West (Bartlett-kernel) HAC standard error of the sample mean.

    ``LRV = γ₀ + 2·Σ_{k=1..L} (1 − k/(L+1))·γ_k``, ``se = √(LRV/n)``.
    Reduces to the plain ``√(γ₀/n)`` at ``lags=0``.

    Args:
        x: the observation series.
        lags: truncation lag L. For an h-period overlapping window use ``h - 1``.
    """
    x = np.asarray(pd.Series(x).dropna(), dtype=float)
    n = x.size
    if n < 2:
        return float("nan")

    e = x - x.mean()
    lrv = e @ e / n  # γ₀
    for k in range(1, min(lags, n - 1) + 1):
        gamma_k = (e[k:] @ e[:-k]) / n
        lrv += 2.0 * (1.0 - k / (lags + 1)) * gamma_k
    lrv = max(lrv, 0.0)  # finite samples can produce a tiny negative LRV
    return float(np.sqrt(lrv / n))


def mean_significance(x, lags: int, periods_per_year: int = 252) -> dict:
    """Mean of `x` with both naive and HAC t-stats, so the gap is visible.

    Always report both. When ``t_HAC`` is materially below ``t_naive``, the naive
    figure was measuring overlap, not signal.
    """
    x = pd.Series(x).dropna()
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if n > 1 else float("nan")

    se_naive = sd / np.sqrt(n) if n > 1 else float("nan")
    se_hac = newey_west_se(x, lags)
    t_naive = mean / se_naive if se_naive else float("nan")
    t_hac = mean / se_hac if se_hac else float("nan")
    dof = max(n - 1, 1)

    return {
        "mean": mean,
        "std": sd,
        "IR": mean / sd if sd else float("nan"),
        "IR_ann": (mean / sd) * np.sqrt(periods_per_year) if sd else float("nan"),
        "t_naive": t_naive,
        "p_naive": 2 * stats.t.sf(abs(t_naive), dof) if np.isfinite(t_naive) else float("nan"),
        "t_HAC": t_hac,
        "p_HAC": 2 * stats.t.sf(abs(t_hac), dof) if np.isfinite(t_hac) else float("nan"),
        "hit_rate": float((x > 0).mean()),
        "n_obs": n,
    }


def effective_sample_size(x, lags: int) -> float:
    """Roughly how many *independent* observations the series is worth.

    ``n_eff = n · (se_naive / se_HAC)²``. A 2,000-day backtest of a 21-day
    overlapping signal is not 2,000 observations, and this says so — useful for
    sanity-checking whether a result has any power behind it at all.
    """
    x = pd.Series(x).dropna()
    n = len(x)
    if n < 2:
        return float("nan")

    se_naive = float(np.std(x, ddof=0)) / np.sqrt(n)
    se_hac = newey_west_se(x, lags)
    if not se_hac or not np.isfinite(se_hac):
        return float("nan")
    return float(n * (se_naive / se_hac) ** 2)
