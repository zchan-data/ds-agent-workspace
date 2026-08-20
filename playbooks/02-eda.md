# Playbook: Exploratory Data Analysis

> Stub — fill in with your preferred conventions, gotchas, and checklists as you build them up.

## Goals
- Understand distributions, relationships, and anomalies before modeling.
- Surface insights that inform feature engineering and model selection.
- Produce visualizations suitable for stakeholder communication.

## Checklist

- [ ] Univariate analysis: distributions of all features (histograms, box plots, value counts)
- [ ] Bivariate analysis: feature vs. target relationships (scatter, correlation matrix, grouped stats)
- [ ] Multivariate analysis: pairplots, heatmaps for correlated features
- [ ] Temporal patterns if applicable (time series decomposition, lag plots)
- [ ] Class balance check for classification targets
- [ ] Identify high-cardinality categoricals
- [ ] Flag features with near-zero variance
- [ ] Visualize high-dimensional structure with dimensionality reduction (see below)
- [ ] Document key findings and hypotheses in the notebook markdown cells

## Visualizing High-Dimensional Data

When you have many features, project to 2D/3D to spot clusters, separability, and outliers:

- **PCA** — fast linear projection; check the explained-variance ratio to know how much structure the 2D view captures.
- **UMAP** — nonlinear, preserves both local and global structure; good default for cluster discovery.
- **t-SNE** — nonlinear, strong at local clusters but distorts global distances; **visualization only**, never a model feature.

Color points by the target (or candidate cluster labels) to assess class separability before modeling. For using these as actual model inputs, see the [feature engineering playbook](03-feature-engineering.md#dimensionality-reduction).

## Preferred Libraries

- **matplotlib / seaborn**: static plots, publication-ready figures
- **plotly**: interactive plots, dashboards
- **pandas-profiling / ydata-profiling**: quick automated overview

## Output

Save key plots to `outputs/figures/` and summarize findings in a markdown cell at the top of the EDA notebook.
