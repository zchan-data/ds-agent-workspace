# Playbook: Feature Engineering

> Stub — fill in with your preferred conventions, gotchas, and checklists as you build them up.

## Goals
- Transform raw features into representations that improve model performance.
- Keep transformations reproducible and leakage-free (fit on train, apply to test).

## Checklist

- [ ] Encode categoricals (ordinal encoding, one-hot, target encoding — choose based on cardinality and model type)
- [ ] Scale numerics if needed (StandardScaler for linear models, usually not needed for trees)
- [ ] Create interaction features where domain knowledge suggests it
- [ ] Bin continuous variables if non-linear relationships exist
- [ ] Engineer temporal features (day of week, month, lag features, rolling stats) — if the data is ordered in time, read [04-modeling/time-series.md](04-modeling/time-series.md) **before** writing them; rolling and lag features are the most common source of look-ahead bias, and `shared.utils.assert_no_lookahead` proves you haven't introduced one
- [ ] Handle high-cardinality categoricals (frequency encoding, embedding if deep learning)
- [ ] Build a `sklearn` Pipeline or `ColumnTransformer` to keep transforms reproducible
- [ ] Consider dimensionality reduction if feature count is high or features are correlated (see below)
- [ ] Validate: no data leakage, no NaNs entering the model

## Dimensionality Reduction

Use when you have many features (especially correlated or sparse ones), want to denoise, speed up training, or mitigate the curse of dimensionality. Always **fit on train only** and apply to validation/test — fit it inside the sklearn Pipeline to prevent leakage.

### When to reach for it
- Many correlated numeric features → PCA collapses redundancy
- Very high-dimensional sparse data (text TF-IDF, one-hot) → TruncatedSVD (a.k.a. LSA)
- Need a 2D/3D map for visualization → UMAP or t-SNE (see [EDA playbook](../02-eda.md))
- Supervised separation matters → LDA (uses the target; classification only)

### Method selection

| Method | Linear? | Use for | Notes |
|---|---|---|---|
| **PCA** | Yes | Dense numeric features, decorrelation | Scale features first; choose `n_components` by explained variance (e.g. 95%) |
| **TruncatedSVD** | Yes | Sparse matrices (TF-IDF, one-hot) | Works without centering, so won't densify sparse input |
| **LDA** | Yes | Supervised reduction for classification | Max components = n_classes − 1; uses labels (leakage-safe in a Pipeline) |
| **UMAP** | No | Nonlinear manifolds; embeddings as features or for viz | Faster than t-SNE, preserves global structure better |
| **t-SNE** | No | Visualization only (2D/3D) | Do **not** use as model features — non-parametric, no transform for new data |
| **Autoencoders** | No | Deep/learned compression on large data | Reserve for DL pipelines; overkill for tabular |

### Checklist
- [ ] Standardize numeric features before PCA/UMAP (mean 0, unit variance)
- [ ] Pick `n_components` deliberately — explained-variance threshold for PCA, downstream CV score otherwise
- [ ] Fit the reducer inside the sklearn Pipeline (never fit on the full dataset before splitting)
- [ ] Compare model CV score **with vs. without** reduction — it's not always a win
- [ ] Keep a reference to original features; reduced components are not interpretable
- [ ] For tree-based models, reconsider: they handle high dimensionality well and PCA can hurt them

## Notes

- Prefer `sklearn` pipelines over manual transforms — they serialize cleanly with the model artifact.
- Document every engineered feature and why it was added; remove features that don't improve CV score.
