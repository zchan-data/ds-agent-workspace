# Playbook: Time Series & Forecasting

Use this whenever observations are ordered in time and the goal is to predict
something that has not happened yet: forecasting, cross-sectional ranking of
entities over time, event prediction, anything where a train/test split has a
"before" and an "after".

Everything else in `04-modeling/` still applies — baseline first, honest test
set, serialize the pipeline. This page covers what temporal data breaks.

> **The rules below were paid for.** They come from a cross-sectional equity
> forecasting project built in this workspace, which reported a +1.82 Sharpe
> ratio that collapsed to ≈0 once the evaluation was done properly. Nothing was
> wrong with the model; everything was wrong with how it was measured. Each fix
> below is annotated with what it cost to learn.

---

## The one non-negotiable

**Never use random cross-validation.** `KFold`, `train_test_split(shuffle=True)`,
and any sklearn CV default will train on the future to predict the past. Every
metric they produce is meaningless. Use walk-forward splits only.

```python
from shared.utils import WalkForwardSplit

# label at t depends on data through t+5 -> purge 5 periods per fold
for train_idx, test_idx in WalkForwardSplit(label_horizon=5).split(df):
    ...
```

---

## The four leaks, in the order people hit them

### 1. Feature leakage — a feature that sees its own future

Centered rolling windows, `bfill()`, `resample().interpolate()`, a full-sample
`StandardScaler`, sorting by the target, "helpfully" filling gaps. Each is
invisible in the metrics and each inflates them.

Do not audit these by eye. Test the general property directly: **a feature
computed at time t must be identical whether or not data after t exists.**

```python
from shared.utils import assert_no_lookahead

assert_no_lookahead(build_features, raw_df, cutoff="2023-06-30",
                    key_cols=("date", "entity"), exclude=("target",))
```

Build the panel twice — full history and truncated — and compare everything
before the cutoff. One assertion covers every column, including ones you did not
think to check. Put it in `tests/` and run it on every feature change.

Two things it will not catch, so watch for them yourself:
- **Precomputed inputs.** Pass raw data to `build`, not a cached feature panel.
  A column merely selected through is identical in both builds and slips past.
- **Vintage.** If a value was *revised* after publication (restated financials,
  backfilled sensor data), your database holds today's version, not what was
  knowable then. Truncation cannot detect this — only point-in-time source data
  can. Ask whether your source is as-reported or as-revised.

### 2. Label leakage at fold boundaries — the one everyone misses

If the label at t is a forward window (return over the next h periods, "churned
within 30 days", "failed within a week"), then the last h training rows have
labels built from data inside the test block. The split looks clean; it isn't.

The fix is **purging**: drop those h periods from the end of each training
block. `WalkForwardSplit(label_horizon=h)` does it and makes you declare `h`,
because the default of "not thinking about it" is always wrong.

Add an **embargo** too when entities are strongly correlated across time — a
further gap after the test block before training resumes.

### 3. Preprocessing leakage

Fit every transform on the training fold only, inside a `Pipeline` — imputers,
scalers, encoders, feature selection, resampling.

The clean alternative for panel data is normalizing **within each time period**
rather than across the sample. Each period uses only its own cross-section, so
there is nothing to leak and no train/test fit to track:

```python
from shared.utils import neutralize_cross_section

df = neutralize_cross_section(df, feature_cols, group_col="date", method="rank")
```

### 4. Selection leakage — your universe already knows the future

If you assemble the entity list *today* and apply it backward, you have silently
selected for entities that survived: current customers, listed companies, live
sensors. The failures are missing, so anything you measure looks better than it
was.

Reconstruct **point-in-time** membership: which entities existed and qualified on
each date, including ones that later disappeared. In the case study, fixing this
alone cut the headline result from an implausible figure to a merely optimistic
one — before any of the other corrections had been applied.

---

## Evaluating honestly

**Make the out-of-sample window long enough to mean something.** A single test
block at the end of the sample measures one regime. Walk forward across the whole
remaining history so every period after the initial training window is tested
exactly once. The reversal in the case study came from exactly this: 105
out-of-sample days became 1,861, and the result flipped sign.

**Correct the standard error for overlap.** Sampling a metric every period while
each observation spans h periods means consecutive observations share data. The
naive t-stat is inflated — sometimes by 2-3x. Use a Newey-West (HAC) standard
error with lag ≈ h-1, and report both so the gap is visible:

```python
from shared.utils import mean_significance, effective_sample_size

stats = mean_significance(daily_metric, lags=horizon - 1)
n_eff = effective_sample_size(daily_metric, lags=horizon - 1)  # sobering
```

**Do not report the best of N.** If the result depends on an arbitrary choice —
which day you rebalance, which window offset, which seed — evaluate *all* of
them and report the average plus the spread. A single configuration turned a
+0.81 into a +0.04 once averaged across the 21 it was cherry-picked from.

**Check stability across time, not just the aggregate.** Break results down by
year or regime. A metric that is positive overall but negative in 6 of 8 years
is one lucky period, not a model.

**Compare against the right baseline.** For forecasting that is usually the
naive predictor: last value, seasonal-naive, or the rolling mean. Beating the
sample mean is not evidence of anything.

---

## Metrics

| Situation | Use |
|---|---|
| Point forecast | RMSE / MAE vs. a naive baseline; MASE to compare across series |
| Ranking entities per period | Rank correlation per period, then HAC-tested mean |
| Probabilistic forecast | Pinball loss, CRPS, calibration plots |
| Strategy / decision output | The realized objective **net of cost**, never gross |

If the output drives an action with a cost (trading, inventory, staffing,
outreach), the cost belongs in the metric. A signal that only works before costs
is not a signal.

---

## Models, in order

1. **Naive baseline** — last value / seasonal-naive. Beat this or stop.
2. **Classical statistical** — ARIMA/SARIMAX, exponential smoothing. Strong on
   single series with clear seasonality; `statsmodels` or `statsforecast`.
3. **Gradient boosting on lag features** — LightGBM/XGBoost over lags, rolling
   stats, and calendar features. Usually the best accuracy-per-effort on panel
   data, and the right thing to try before anything deep.
4. **Deep learning** — LSTM, Temporal Fusion Transformer, N-BEATS. Only once you
   have a signal that is significant out-of-sample; see
   [deep-learning.md](deep-learning.md).

Tree models cannot extrapolate beyond the training range — detrend or difference
a trending target before using them.

---

## Checklist

- [ ] Split by time; no random CV anywhere in the pipeline
- [ ] `label_horizon` declared and purged at every fold boundary
- [ ] `assert_no_lookahead` in `tests/`, run on every feature change
- [ ] Point-in-time universe — no entity selected on facts known only later
- [ ] Data is as-reported, or revision risk is documented
- [ ] All preprocessing fitted inside the fold (or done within-period)
- [ ] OOS window spans multiple years/regimes, not one block
- [ ] HAC-corrected significance when observations overlap
- [ ] Results averaged over arbitrary choices, with the spread reported
- [ ] Broken down by period, not just aggregated
- [ ] Beaten a naive baseline, net of any action cost
- [ ] Negative results written up in the README decision log, not deleted
