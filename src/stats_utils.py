from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CorrResult:
    n: int
    corr: float
    p_perm: float | None


def pearson_corr(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    if np.isclose(x.std(ddof=0), 0) or np.isclose(y.std(ddof=0), 0):
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def permutation_pvalue_for_corr(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = 5000,
    seed: int = 42,
) -> float | None:
    """Two-sided permutation p-value for Pearson correlation.

    Robustness check: if correlation looks 'real' vs shuffled labels.
    """

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) != len(y) or len(x) < 5:
        return None

    rng = np.random.default_rng(seed)
    observed = pearson_corr(x, y)
    if np.isnan(observed):
        return None

    more_extreme = 0
    for _ in range(n_perm):
        y_perm = rng.permutation(y)
        c = pearson_corr(x, y_perm)
        if np.isnan(c):
            continue
        if abs(c) >= abs(observed):
            more_extreme += 1

    return float((more_extreme + 1) / (n_perm + 1))


def corr_with_perm_test(
    x: np.ndarray,
    y: np.ndarray,
    n_perm: int = 5000,
    seed: int = 42,
) -> CorrResult:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    corr = pearson_corr(x, y)
    p = permutation_pvalue_for_corr(x, y, n_perm=n_perm, seed=seed)
    return CorrResult(n=int(len(x)), corr=float(corr), p_perm=p)


def bootstrap_mean_diff(
    a: np.ndarray,
    b: np.ndarray,
    n_boot: int = 5000,
    seed: int = 42,
) -> dict:
    """Bootstrap CI for mean(a) - mean(b)."""

    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 3 or len(b) < 3:
        return {"n_a": int(len(a)), "n_b": int(len(b)), "mean_diff": None, "ci95": None}

    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        aa = rng.choice(a, size=len(a), replace=True)
        bb = rng.choice(b, size=len(b), replace=True)
        diffs.append(float(aa.mean() - bb.mean()))

    diffs = np.array(diffs)
    return {
        "n_a": int(len(a)),
        "n_b": int(len(b)),
        "mean_diff": float(a.mean() - b.mean()),
        "ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))],
    }
