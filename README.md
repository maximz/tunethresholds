# Tune Decision Thresholds

[![](https://img.shields.io/pypi/v/tunethresholds.svg)](https://pypi.python.org/pypi/tunethresholds)
[![CI](https://github.com/maximz/tunethresholds/actions/workflows/ci.yaml/badge.svg?branch=master)](https://github.com/maximz/tunethresholds/actions/workflows/ci.yaml)
[![](https://img.shields.io/badge/docs-here-blue.svg)](https://tunethresholds.maximz.com)
[![](https://img.shields.io/github/stars/maximz/tunethresholds?style=social)](https://github.com/maximz/tunethresholds)

`tunethresholds` is a small scikit-learn-style utility for tuning multiclass
classification decision thresholds after a model has already been trained. It
wraps a classifier that exposes `predict_proba()` and `classes_`, learns one
multiplicative weight per class on a validation set, and uses those weighted
scores to choose labels.

## Why It Exists

Many classifiers predict the class with the largest raw probability. That
default can be suboptimal when classes have different costs, frequencies, or
validation-set behavior. This package keeps the underlying model fixed and
adjusts only the final decision rule: each class probability is multiplied by a
learned class weight, then the largest adjusted value wins.

## How It Works

The main API is `AdjustedProbabilitiesDerivedModel`.

- `predict_proba(X)` calls the wrapped model's `predict_proba(X)` and multiplies
  each class column by its learned weight.
- `predict(X)` returns the class whose adjusted probability is largest.
- `adjust_model_decision_thresholds(...)` finds class weights with
  `scipy.optimize.differential_evolution`, maximizing a validation-set metric.
  The default metric is `sklearn.metrics.matthews_corrcoef`; custom metrics must
  accept `score_func(y_true, y_pred)`.

The adjusted probabilities are intentionally not renormalized. They may not sum
to 1, and they should be treated as adjusted scores rather than calibrated
probabilities.

## Installation

```bash
pip install tunethresholds
```

The package requires Python 3.8+ and depends on NumPy, SciPy, scikit-learn, and
extendanything.

## Usage

```python
from sklearn.metrics import accuracy_score
from tunethresholds import AdjustedProbabilitiesDerivedModel

# clf is an already-fitted classifier with predict_proba() and classes_.
adjusted_clf = AdjustedProbabilitiesDerivedModel.adjust_model_decision_thresholds(
    model=clf,
    X_validation=X_val,
    y_validation_true=y_val,
    score_func=accuracy_score,
)

y_pred = adjusted_clf.predict(X_test)
adjusted_scores = adjusted_clf.predict_proba(X_test)
```

If validation probabilities have already been computed, pass them directly
instead of `X_validation`:

```python
adjusted_clf = AdjustedProbabilitiesDerivedModel.adjust_model_decision_thresholds(
    model=clf,
    predicted_probabilities_validation=clf.predict_proba(X_val),
    y_validation_true=y_val,
)
```

## Important Behavior

- The wrapped model must expose `predict_proba()` and `classes_`.
- Classes absent from `y_validation_true` are assigned a fixed weight of `0`.
- Present-class weights are optimized within `[1e-5, 1.0]`.
- Multiplying class probabilities by weights does not change ROC AUC (it
  preserves the per-class ranking of examples). But because the adjusted
  `predict_proba()` output is not normalized, tools that require rows to sum to
  1, including scikit-learn's multiclass `roc_auc_score`, will reject it. Do not
  renormalize to work around this: renormalizing can change the rankings and
  therefore the ROC AUC.
- The optimizer is run on validation data only; the underlying classifier is not
  retrained.

## Development

```bash
pip install -r requirements_dev.txt
pip install -e .
pytest
```

Additional local commands are available through the `Makefile`, including
`make test`, `make lint`, `make coverage`, and `make docs`.
