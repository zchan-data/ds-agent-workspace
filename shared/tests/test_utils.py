"""Tests for the shared utilities.

The purge logic in `WalkForwardSplit` is new code written during promotion (the
project version has no purge), so it gets the most attention here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pytest import approx

from shared.utils import (
    WalkForwardSplit,
    assert_no_lookahead,
    effective_sample_size,
    lookahead_columns,
    mean_significance,
    neutralize_cross_section,
    newey_west_se,
)

N_PERIODS = 600


@pytest.fixture(scope="module")
def panel() -> pd.DataFrame:
    """A small entity x time panel with a trailing feature and a forward label."""
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2020-01-01", periods=N_PERIODS)
    frames = []
    for i in range(8):
        x = rng.normal(size=N_PERIODS).cumsum()
        s = pd.Series(x)
        frames.append(
            pd.DataFrame(
                {
                    "date": dates,
                    "entity": f"E{i}",
                    "level": x,
                    "trailing_mean_10": s.rolling(10).mean().to_numpy(),
                    "target": s.shift(-5).to_numpy() - x,  # 5-period forward label
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------------------------------- #
# leakage
# --------------------------------------------------------------------------- #
def _trailing(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["date", "entity"]].copy()
    out["ma"] = df.groupby("entity")["level"].transform(lambda s: s.rolling(20).mean())
    return out


def _centered(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["date", "entity"]].copy()
    out["ma"] = df.groupby("entity")["level"].transform(
        lambda s: s.rolling(21, center=True, min_periods=1).mean()
    )
    return out


def _full_sample_scaled(df: pd.DataFrame) -> pd.DataFrame:
    """The other classic leak: a scaler fitted on the whole sample."""
    out = df[["date", "entity"]].copy()
    out["z"] = (df["level"] - df["level"].mean()) / df["level"].std()
    return out


def test_trailing_features_pass(panel):
    cutoff = np.sort(panel["date"].unique())[400]
    assert_no_lookahead(_trailing, panel, cutoff, key_cols=("date", "entity"))


def test_centered_window_is_flagged(panel):
    cutoff = np.sort(panel["date"].unique())[400]
    with pytest.raises(AssertionError, match="future information"):
        assert_no_lookahead(_centered, panel, cutoff, key_cols=("date", "entity"))


def test_full_sample_scaler_is_flagged(panel):
    cutoff = np.sort(panel["date"].unique())[400]
    with pytest.raises(AssertionError, match="future information"):
        assert_no_lookahead(_full_sample_scaled, panel, cutoff, key_cols=("date", "entity"))


def _with_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["date", "entity"]].copy()
    g = df.groupby("entity")["level"]
    out["ma"] = g.transform(lambda s: s.rolling(20).mean())
    out["target"] = g.transform(lambda s: s.shift(-5) - s)  # forward label
    return out


def test_forward_label_is_flagged_unless_excluded(panel):
    """The target legitimately peeks — it must be excluded explicitly."""
    cutoff = np.sort(panel["date"].unique())[400]

    with pytest.raises(AssertionError, match="target"):
        assert_no_lookahead(_with_label, panel, cutoff, key_cols=("date", "entity"))

    assert_no_lookahead(
        _with_label, panel, cutoff, key_cols=("date", "entity"), exclude=("target",)
    )


def test_precomputed_columns_are_not_checked(panel):
    """Caveat: the check only covers what `build` recomputes from its input.

    A column that is merely selected through — already computed upstream on full
    history — is identical in both builds and therefore invisible here. Pass raw
    inputs to `build`, not a cached feature panel, or the check is vacuous.
    """
    cutoff = np.sort(panel["date"].unique())[400]

    def passthrough(df):
        return df[["date", "entity", "target"]].copy()

    # `target` peeks 5 periods ahead, yet slips past unflagged.
    assert_no_lookahead(passthrough, panel, cutoff, key_cols=("date", "entity"))


def test_thin_comparison_window_raises_instead_of_passing_vacuously(panel):
    cutoff = np.sort(panel["date"].unique())[2]
    with pytest.raises(AssertionError, match="too thin"):
        assert_no_lookahead(_trailing, panel, cutoff, key_cols=("date", "entity"))


def test_all_nan_window_raises_instead_of_passing_vacuously(panel):
    """Lookbacks that have not filled must not count as agreement."""
    cutoff = np.sort(panel["date"].unique())[150]
    full = _trailing(panel)
    truncated = _trailing(panel[panel["date"] <= cutoff])
    blanked = full.assign(ma=np.nan), truncated.assign(ma=np.nan)
    with pytest.raises(AssertionError, match="vacuously"):
        lookahead_columns(*blanked, cutoff, key_cols=("date", "entity"))


# --------------------------------------------------------------------------- #
# WalkForwardSplit — purging
# --------------------------------------------------------------------------- #
def _positions(df: pd.DataFrame) -> dict:
    return {d: i for i, d in enumerate(np.sort(df["date"].unique()))}


@pytest.mark.parametrize("horizon", [0, 1, 5, 21])
def test_purge_keeps_training_labels_out_of_the_test_window(panel, horizon):
    """The invariant the project's own splitter violates."""
    pos = _positions(panel)
    folds = list(
        WalkForwardSplit(
            label_horizon=horizon, test_size=50, min_train_size=200
        ).split(panel)
    )
    assert folds

    for train_idx, test_idx in folds:
        last_train = max(pos[d] for d in panel.loc[train_idx, "date"].unique())
        first_test = min(pos[d] for d in panel.loc[test_idx, "date"].unique())
        assert last_train + horizon < first_test


def test_purge_drops_exactly_label_horizon_periods(panel):
    unpurged = list(
        WalkForwardSplit(label_horizon=0, test_size=50, min_train_size=200).split(panel)
    )
    purged = list(
        WalkForwardSplit(label_horizon=5, test_size=50, min_train_size=200).split(panel)
    )
    assert len(unpurged) == len(purged)

    for (u_train, _), (p_train, _) in zip(unpurged, purged):
        u_dates = panel.loc[u_train, "date"].nunique()
        p_dates = panel.loc[p_train, "date"].nunique()
        assert u_dates - p_dates == 5


def test_label_horizon_is_required():
    with pytest.raises(TypeError):
        WalkForwardSplit()  # type: ignore[call-arg]


def test_negative_label_horizon_rejected():
    with pytest.raises(ValueError, match="label_horizon"):
        WalkForwardSplit(label_horizon=-1)


def test_train_precedes_test_and_folds_are_disjoint(panel):
    folds = list(
        WalkForwardSplit(label_horizon=5, test_size=50, min_train_size=200).split(panel)
    )
    tested: list = []
    for train_idx, test_idx in folds:
        train_dates = panel.loc[train_idx, "date"]
        test_dates = panel.loc[test_idx, "date"]
        assert train_dates.max() < test_dates.min()
        tested.extend(test_dates.unique())
    assert len(tested) == len(set(tested))


def test_walks_to_the_end_of_the_sample(panel):
    folds = list(
        WalkForwardSplit(label_horizon=5, test_size=50, min_train_size=200).split(panel)
    )
    tested = {d for _, t in folds for d in panel.loc[t, "date"].unique()}
    assert tested == set(np.sort(panel["date"].unique())[200:])


def test_rolling_window_is_capped_after_purging(panel):
    sizes = [
        panel.loc[tr, "date"].nunique()
        for tr, _ in WalkForwardSplit(
            label_horizon=5, test_size=50, min_train_size=200, max_train_size=150
        ).split(panel)
    ]
    assert set(sizes) == {150}


def test_expanding_window_grows(panel):
    sizes = [
        panel.loc[tr, "date"].nunique()
        for tr, _ in WalkForwardSplit(
            label_horizon=5, test_size=50, min_train_size=200
        ).split(panel)
    ]
    assert sizes == sorted(sizes) and sizes[-1] > sizes[0]


def test_n_splits_caps_folds(panel):
    folds = list(
        WalkForwardSplit(
            label_horizon=5, test_size=50, min_train_size=200, n_splits=2
        ).split(panel)
    )
    assert len(folds) == 2


def test_raises_when_history_too_short(panel):
    with pytest.raises(ValueError, match="Not enough distinct periods"):
        list(WalkForwardSplit(label_horizon=5, min_train_size=10_000).split(panel))


def test_raises_when_purge_would_empty_training(panel):
    with pytest.raises(ValueError, match="purges the entire training block"):
        list(
            WalkForwardSplit(
                label_horizon=200, test_size=50, min_train_size=200
            ).split(panel)
        )


# --------------------------------------------------------------------------- #
# stats
# --------------------------------------------------------------------------- #
def _ar1(n: int, phi: float, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    e = rng.normal(size=n)
    x = np.empty(n)
    x[0] = e[0]
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_newey_west_at_zero_lag_is_the_plain_se():
    x = _ar1(500, 0.5)
    assert newey_west_se(x, 0) == approx(np.std(x, ddof=0) / np.sqrt(len(x)))


def test_newey_west_widens_se_under_positive_autocorrelation():
    x = _ar1(2000, 0.8, seed=1)
    naive = np.std(x, ddof=0) / np.sqrt(len(x))
    assert newey_west_se(x, 4) > naive * 1.3


def test_newey_west_matches_naive_for_iid_noise():
    x = np.random.default_rng(3).normal(size=4000)
    assert newey_west_se(x, 4) == approx(np.std(x, ddof=0) / np.sqrt(len(x)), rel=0.15)


def test_newey_west_clamps_negative_long_run_variance():
    se = newey_west_se(np.array([1.0, -1.0] * 50), 8)
    assert np.isfinite(se) and se >= 0.0


def test_hac_t_is_smaller_than_naive_for_overlapping_observations():
    s = mean_significance(pd.Series(_ar1(1500, 0.8, seed=2) * 0.01 + 0.004), lags=4)
    assert abs(s["t_HAC"]) < abs(s["t_naive"])
    assert s["p_HAC"] > s["p_naive"]
    assert s["n_obs"] == 1500


def test_effective_sample_size_shrinks_with_overlap():
    x = _ar1(2000, 0.8, seed=6)
    assert effective_sample_size(x, 4) < 2000 * 0.6
    assert effective_sample_size(np.random.default_rng(7).normal(size=2000), 4) == approx(
        2000, rel=0.35
    )


# --------------------------------------------------------------------------- #
# panel normalization
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("method", ["zscore", "rank"])
def test_normalization_uses_only_the_contemporaneous_period(panel, method):
    cols = ["level", "trailing_mean_10"]
    df = panel.dropna(subset=cols).reset_index(drop=True)
    dates = np.sort(df["date"].unique())
    cutoff = dates[len(dates) // 2]

    base = neutralize_cross_section(df, cols, method=method)
    tampered = df.copy()
    future = tampered["date"] > cutoff
    tampered.loc[future, cols] = tampered.loc[future, cols] * 9.0 + 4.0
    after = neutralize_cross_section(tampered, cols, method=method)

    past = (base["date"] <= cutoff).to_numpy()
    np.testing.assert_allclose(
        base.loc[past, cols].to_numpy(dtype=float),
        after.loc[past, cols].to_numpy(dtype=float),
        rtol=1e-9,
        atol=1e-12,
    )


def test_zscore_is_centered_within_each_period(panel):
    cols = ["level"]
    df = panel.dropna(subset=cols)
    out = neutralize_cross_section(df, cols, method="zscore", winsor_q=0.0)
    agg = out.groupby("date")[cols].agg(["mean", "std"])
    assert np.nanmax(np.abs(agg.xs("mean", level=1, axis=1).to_numpy())) < 1e-9
    assert np.nanmax(np.abs(agg.xs("std", level=1, axis=1).to_numpy() - 1.0)) < 1e-9


def test_rank_is_bounded_and_monotone(panel):
    out = neutralize_cross_section(panel, ["level"], method="rank", winsor_q=0.0)
    assert out["level"].between(-0.5, 0.5).all()

    day = out[out["date"] == out["date"].iloc[0]].sort_values("level")
    raw = panel[panel["date"] == panel["date"].iloc[0]].set_index("entity")["level"]
    assert list(day["entity"]) == list(raw.sort_values().index)


def test_within_grouping_demeans_by_group(panel):
    df = panel.dropna(subset=["level"]).copy()
    df["sector"] = np.where(df["entity"] < "E4", "A", "B")
    out = neutralize_cross_section(df, ["level"], method="zscore", within="sector")
    per_group = out.groupby(["date", "sector"])["level"].mean()
    assert np.nanmax(np.abs(per_group.to_numpy())) < 1e-9


def test_target_is_left_untouched(panel):
    df = panel.dropna(subset=["level", "target"]).reset_index(drop=True)
    out = neutralize_cross_section(df, ["level"])
    pd.testing.assert_series_equal(out["target"], df["target"])


def test_rejects_unknown_method(panel):
    with pytest.raises(ValueError, match="zscore"):
        neutralize_cross_section(panel, ["level"], method="minmax")
