# Playbook: Modeling — Overview

Read this first to determine which sub-playbook to use.

## Selecting an Approach

| Situation | Sub-playbook |
|---|---|
| **Observations ordered in time; predicting something not yet observed** | [time-series.md](time-series.md) |
| Predicting a category / label | [classification.md](classification.md) |
| Predicting a continuous value | [regression.md](regression.md) |
| Image, text, audio, or sequence data; LLMs; fine-tuning | [deep-learning.md](deep-learning.md) |

**If the data is temporal, read [time-series.md](time-series.md) first** — it
overrides the validation guidance below. Temporal data is a classification or
regression problem *plus* a set of leaks that will silently invalidate your
results, and it is the workspace's most expensively-learned lesson.

## General Principles (apply to all)

1. **Baseline first.** Start with the simplest possible model (logistic regression, linear regression, majority-class predictor). Every subsequent model must beat it.
2. **Cross-validate.** Never tune hyperparameters on the test set. Use `StratifiedKFold` for classification, `KFold` for regression — **but never either one when observations are ordered in time.** Random folds train on the future to predict the past; use `shared.utils.WalkForwardSplit` instead (see [time-series.md](time-series.md)).
3. **Track experiments.** The baseline requirement is a **dated decision log** in the project README: what you changed, what the metric did, what you concluded, and the caveats. Log negative results too — they are the ones that save time later. Add MLflow or W&B on top when a project runs enough tuning sweeps that a log stops scaling. Never rely on notebook output alone.
4. **Serialize the full pipeline.** Save the preprocessor + model together (`.pkl` via joblib, or `.pt` for PyTorch).
5. **Evaluate honestly.** Report metrics on a held-out test set that was not used during any training or tuning decision.

## Experiment Structure

```
models/
├── baselines/
├── experiments/
│   └── exp_001_lgbm_v1/
│       ├── model.pkl
│       ├── params.json
│       └── metrics.json
└── final/
```
