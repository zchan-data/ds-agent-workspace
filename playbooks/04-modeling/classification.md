# Playbook: Classification

## Metrics (pick based on class balance and business cost)

| Scenario | Primary metric |
|---|---|
| Balanced classes | Accuracy, F1-macro |
| Imbalanced classes | PR-AUC, F1-weighted, recall at fixed precision |
| Ranking / probability calibration needed | ROC-AUC, log loss, Brier score |

## Model Progression

1. **Baseline**: `DummyClassifier(strategy='most_frequent')`
2. **Linear**: Logistic Regression (fast, interpretable, good benchmark)
3. **Tree ensemble**: Random Forest → LightGBM / XGBoost (usually best for tabular)
4. **Neural net**: only if tabular methods plateau or data is large

## Checklist

- [ ] Check class balance; apply class weights or oversample (SMOTE) if severely imbalanced
- [ ] Choose and justify primary evaluation metric before training
- [ ] Tune hyperparameters with `Optuna` or `GridSearchCV` on CV, not test set
- [ ] Plot confusion matrix and classification report on held-out test set
- [ ] Plot feature importances or SHAP values for tree models
- [ ] Calibrate probabilities if downstream use requires calibrated scores (`CalibratedClassifierCV`)
- [ ] Save model artifact to `models/`

## Notes

<!-- Add project-specific notes here -->
