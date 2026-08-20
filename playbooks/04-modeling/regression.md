# Playbook: Regression

## Metrics

| Scenario | Primary metric |
|---|---|
| Equal weight on all errors | RMSE |
| Sensitive to outliers | MAE or Huber loss |
| Relative error matters | MAPE (avoid if target includes zeros) |
| Rank of predictions matters | Spearman correlation |

## Model Progression

1. **Baseline**: `DummyRegressor(strategy='mean')`
2. **Linear**: Ridge / Lasso (fast, interpretable, reveals linear structure)
3. **Tree ensemble**: Random Forest → LightGBM / XGBoost (usually best for tabular)
4. **Neural net**: only if tabular methods plateau or data is large

## Checklist

- [ ] Check target distribution; apply log-transform if heavily skewed
- [ ] Choose and justify primary evaluation metric before training
- [ ] Residual analysis: plot residuals vs. fitted values, check for heteroscedasticity
- [ ] Tune hyperparameters with `Optuna` or `GridSearchCV` on CV folds
- [ ] Report final metrics (RMSE, MAE, R²) on held-out test set
- [ ] Plot feature importances or SHAP values
- [ ] Save model artifact to `models/`

## Notes

<!-- Add project-specific notes here -->
