from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class NumbersTask:
    task_id: int
    title: str
    payload: dict


def year_to_int(year: str) -> int:
    return int(str(year).split("-")[0])


def _ols_with_band(x: np.ndarray, y: np.ndarray) -> dict:
    x = x.astype(float)
    y = y.astype(float)
    n = int(len(x))
    xbar = float(x.mean())
    ybar = float(y.mean())
    sxx = float(((x - xbar) ** 2).sum())
    if sxx == 0:
        return {"n": n, "corr": None, "a": None, "b": None, "rmse": None, "band": None}

    b = float(((x - xbar) * (y - ybar)).sum() / sxx)
    a = float(ybar - b * xbar)
    yhat = a + b * x
    resid = y - yhat
    rmse = float(np.sqrt((resid**2).mean()))

    # 95% CI for mean prediction (normal approx)
    s2 = float((resid**2).sum() / max(n - 2, 1))
    s = float(np.sqrt(s2))
    x_grid = np.linspace(float(x.min()), float(x.max()), 120)
    y_grid = a + b * x_grid
    se_mean = s * np.sqrt(1.0 / n + (x_grid - xbar) ** 2 / sxx)
    z = 1.96

    corr = float(np.corrcoef(x, y)[0, 1]) if n >= 2 else None

    return {
        "n": n,
        "corr": corr,
        "a": a,
        "b": b,
        "rmse": rmse,
        "yhat": yhat,
        "resid": resid,
        "band": {
            "x": x_grid,
            "y": y_grid,
            "lower": y_grid - z * se_mean,
            "upper": y_grid + z * se_mean,
        },
    }


def task1_peak_attrition(
    dropout_long: pd.DataFrame,
    promotion_long: pd.DataFrame,
    repetition_long: pd.DataFrame,
    focus_gender: str = "Girls",
) -> NumbersTask:
    d = dropout_long[dropout_long["gender"].eq(focus_gender)].copy()
    p = promotion_long[promotion_long["gender"].eq(focus_gender)].copy()
    r = repetition_long[repetition_long["gender"].eq(focus_gender)].copy()

    # Peak leakage level per state-year
    wide = d.pivot_table(index=["year", "state_ut"], columns="level", values="rate", aggfunc="first").reset_index()
    level_cols = [c for c in wide.columns if c not in {"year", "state_ut"}]
    wide["peak_level"] = wide[level_cols].idxmax(axis=1)
    wide["peak_rate"] = wide[level_cols].max(axis=1)

    india = wide[wide["state_ut"].eq("India")].copy()
    india["year_int"] = india["year"].map(year_to_int)
    india = india.sort_values("year_int")

    # Cohort survival of 100 (illustrative) for India per year
    surv_rows = []
    for _, row in india.iterrows():
        primary = float(row.get("Primary (1-5)") or 0.0)
        upper = float(row.get("Upper Primary (6-8)") or 0.0)
        secondary = float(row.get("Secondary (9-10)") or 0.0)
        cohort = [100.0]
        cohort.append(cohort[-1] * (1 - primary / 100.0))
        cohort.append(cohort[-1] * (1 - upper / 100.0))
        cohort.append(cohort[-1] * (1 - secondary / 100.0))
        surv_rows.append(
            {
                "year": row["year"],
                "start": 100.0,
                "after_primary": cohort[1],
                "after_upper_primary": cohort[2],
                "after_secondary": cohort[3],
            }
        )

    # Checksum: Promotion + Dropout + Repetition ≈ 100
    chk = (
        d.rename(columns={"rate": "dropout"})
        .merge(p, on=["year", "state_ut", "level", "gender"], how="inner")
        .merge(r, on=["year", "state_ut", "level", "gender"], how="inner")
    )
    chk["sum_rates"] = chk["dropout"] + chk["promotion"] + chk["repetition"]
    chk["abs_dev"] = (chk["sum_rates"] - 100.0).abs()

    worst = (
        chk.sort_values("abs_dev", ascending=False)
        .head(25)
        .loc[:, ["year", "state_ut", "level", "dropout", "promotion", "repetition", "sum_rates", "abs_dev"]]
        .to_dict(orient="records")
    )

    payload = {
        "focus_gender": focus_gender,
        "india_trend": india[["year"] + [c for c in level_cols if c in india.columns]].to_dict(orient="records"),
        "india_peak": india[["year", "peak_level", "peak_rate"]].to_dict(orient="records"),
        "peak_level_counts_india": india["peak_level"].value_counts().to_dict(),
        "peak_level_counts_all_states": wide["peak_level"].value_counts().to_dict(),
        "survival_cohort_100_india": surv_rows,
        "checksum": {
            "rows_checked": int(len(chk)),
            "max_abs_deviation": float(chk["abs_dev"].max()) if len(chk) else None,
            "p95_abs_deviation": float(chk["abs_dev"].quantile(0.95)) if len(chk) else None,
            "rows_over_1pct": int((chk["abs_dev"] > 1.0).sum()) if len(chk) else None,
            "worst_rows": worst,
        },
    }

    return NumbersTask(1, "Peak Attrition Identification (Policy Bottleneck)", payload)


def task2_infra_roi(
    infra_by_year: dict[str, pd.DataFrame],
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> NumbersTask:
    rows = []
    models = []

    for year, infra in infra_by_year.items():
        sec = dropout_long[
            (dropout_long["year"].eq(year))
            & (dropout_long["gender"].eq(focus_gender))
            & (dropout_long["level"].eq(level))
        ].rename(columns={"rate": "dropout"})

        cols = {c: c.lower() for c in infra.columns}
        fg_candidates = [c for c, cl in cols.items() if "functional" in cl and "girls" in cl and "toilet" in cl]
        total_candidates = [c for c, cl in cols.items() if cl == "total_schools" or ("total" in cl and "school" in cl)]
        if not fg_candidates or not total_candidates:
            continue

        fg_col = fg_candidates[0]
        total_col = total_candidates[0]

        xdf = infra[["state_ut", fg_col, total_col]].rename(columns={fg_col: "functional_girls_toilets", total_col: "total_schools"}).copy()
        xdf["functional_girls_toilet_pct"] = 100.0 * xdf["functional_girls_toilets"] / xdf["total_schools"]

        merged = xdf.merge(sec[["state_ut", "dropout"]], on="state_ut", how="inner")
        merged = merged[~merged["state_ut"].eq("India")].dropna(subset=["functional_girls_toilet_pct", "dropout"])

        x = merged["functional_girls_toilet_pct"].to_numpy()
        y = merged["dropout"].to_numpy()
        reg = _ols_with_band(x, y)

        merged = merged.assign(yhat=reg.get("yhat"), resid=reg.get("resid"))
        better = merged.nsmallest(6, "resid")["state_ut"].tolist() if len(merged) else []
        worse = merged.nlargest(6, "resid")["state_ut"].tolist() if len(merged) else []

        models.append(
            {
                "year": year,
                "n": reg["n"],
                "corr": reg["corr"],
                "intercept": reg["a"],
                "slope": reg["b"],
                "rmse": reg["rmse"],
                "outliers": {"better_than_expected": better, "worse_than_expected": worse},
                "band": {
                    "x": reg["band"]["x"].tolist() if reg.get("band") else [],
                    "y": reg["band"]["y"].tolist() if reg.get("band") else [],
                    "lower": reg["band"]["lower"].tolist() if reg.get("band") else [],
                    "upper": reg["band"]["upper"].tolist() if reg.get("band") else [],
                },
            }
        )

        rows.extend(
            merged[["state_ut", "functional_girls_toilet_pct", "dropout"]]
            .assign(year=year)
            .to_dict(orient="records")
        )

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "points": rows,
        "models": models,
    }
    return NumbersTask(2, "Infrastructure ROI (Functional Girls’ Toilets vs Dropout)", payload)


def task3_female_teacher_multiplier(
    female_share_by_year: dict[str, pd.DataFrame],
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> NumbersTask:
    points = []
    per_year = []

    for year, fem in female_share_by_year.items():
        sec = dropout_long[
            (dropout_long["year"].eq(year))
            & (dropout_long["gender"].eq(focus_gender))
            & (dropout_long["level"].eq(level))
        ].rename(columns={"rate": "dropout"})

        merged = fem.merge(sec[["state_ut", "dropout"]], on="state_ut", how="inner")
        merged = merged[(~merged["state_ut"].eq("India"))].dropna(subset=["female_teacher_share", "dropout"])

        x = merged["female_teacher_share"].to_numpy()
        y = merged["dropout"].to_numpy()
        reg = _ols_with_band(x, y)

        # Critical mass scan
        thresholds = np.linspace(0.15, 0.75, 61)
        best = None
        for t in thresholds:
            lo = merged[merged["female_teacher_share"] < t]
            hi = merged[merged["female_teacher_share"] >= t]
            if len(lo) < 8 or len(hi) < 8:
                continue
            diff = float(lo["dropout"].mean() - hi["dropout"].mean())
            cand = {
                "threshold": float(t),
                "n_lo": int(len(lo)),
                "n_hi": int(len(hi)),
                "mean_drop_lo": float(lo["dropout"].mean()),
                "mean_drop_hi": float(hi["dropout"].mean()),
                "difference_lo_minus_hi": diff,
            }
            if best is None or abs(cand["difference_lo_minus_hi"]) > abs(best["difference_lo_minus_hi"]):
                best = cand

        per_year.append(
            {
                "year": year,
                "n": reg["n"],
                "corr": reg["corr"],
                "intercept": reg["a"],
                "slope": reg["b"],
                "rmse": reg["rmse"],
                "best_threshold": best,
            }
        )

        points.extend(
            merged[["state_ut", "female_teacher_share", "dropout"]]
            .assign(year=year)
            .to_dict(orient="records")
        )

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "points": points,
        "models": per_year,
    }

    return NumbersTask(3, "Female Teacher Multiplier (Role Model Effect)", payload)


def task4_peer_benchmarking(
    dropout_long: pd.DataFrame,
    ger_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> NumbersTask:
    # Build per-year peer groups via GER quintiles (secondary girls).
    d = dropout_long[(dropout_long["gender"].eq(focus_gender)) & (dropout_long["level"].eq(level))].rename(columns={"rate": "dropout"})
    g = ger_long[(ger_long["gender"].eq(focus_gender)) & (ger_long["level"].eq(level))].copy()

    years = sorted(set(d["year"]) & set(g["year"]), key=year_to_int)

    peer_rows = []
    deltas = []

    for year in years:
        dy = d[d["year"].eq(year)][["state_ut", "dropout"]]
        gy = g[g["year"].eq(year)][["state_ut", "ger"]]
        merged = dy.merge(gy, on="state_ut", how="inner")
        merged = merged[(~merged["state_ut"].eq("India"))].dropna(subset=["dropout", "ger"])
        if len(merged) < 10:
            continue

        merged["peer_bin"] = pd.qcut(merged["ger"], 5, labels=False, duplicates="drop")
        grp = merged.groupby("peer_bin")["dropout"].median().rename("peer_median_dropout")
        merged = merged.join(grp, on="peer_bin")
        merged["performance_delta"] = merged["dropout"] - merged["peer_median_dropout"]

        peer_rows.extend(
            merged[["state_ut", "ger", "dropout", "peer_bin", "peer_median_dropout", "performance_delta"]]
            .assign(year=year)
            .to_dict(orient="records")
        )

        best = merged.nsmallest(10, "performance_delta")["state_ut"].tolist()
        worst = merged.nlargest(10, "performance_delta")["state_ut"].tolist()
        deltas.append({"year": year, "best_vs_peers": best, "worst_vs_peers": worst})

    # Leaderboard of improvement from first to last year
    if years:
        y0, y1 = years[0], years[-1]
        d0 = d[d["year"].eq(y0)][["state_ut", "dropout"]].rename(columns={"dropout": "dropout_start"})
        d1 = d[d["year"].eq(y1)][["state_ut", "dropout"]].rename(columns={"dropout": "dropout_end"})
        imp = d0.merge(d1, on="state_ut", how="inner")
        imp = imp[(~imp["state_ut"].eq("India"))].dropna()
        imp["improvement_pp"] = imp["dropout_start"] - imp["dropout_end"]
        leaderboard = imp.sort_values("improvement_pp", ascending=False).head(15).to_dict(orient="records")
    else:
        leaderboard = []

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "peer_points": peer_rows,
        "peer_extremes_by_year": deltas,
        "improvement_leaderboard": leaderboard,
        "years": years,
    }

    return NumbersTask(4, "Peer Benchmarking (Competitive Federalism)", payload)


def task7_single_teacher_risk(
    single_teacher_by_year: dict[str, pd.DataFrame],
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> NumbersTask:
    points = []
    models = []

    for year, st in single_teacher_by_year.items():
        sec = dropout_long[
            (dropout_long["year"].eq(year))
            & (dropout_long["gender"].eq(focus_gender))
            & (dropout_long["level"].eq(level))
        ].rename(columns={"rate": "dropout"})

        merged = st.merge(sec[["state_ut", "dropout"]], on="state_ut", how="inner")
        merged = merged[(~merged["state_ut"].eq("India"))].dropna(subset=["total_schools", "schools_with_single_teacher", "dropout"])

        merged["single_teacher_school_pct"] = 100.0 * merged["schools_with_single_teacher"] / merged["total_schools"]

        x = merged["single_teacher_school_pct"].to_numpy()
        y = merged["dropout"].to_numpy()
        reg = _ols_with_band(x, y)

        models.append({"year": year, "n": reg["n"], "corr": reg["corr"], "intercept": reg["a"], "slope": reg["b"], "rmse": reg["rmse"]})
        points.extend(
            merged[["state_ut", "single_teacher_school_pct", "dropout"]].assign(year=year).to_dict(orient="records")
        )

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "points": points,
        "models": models,
    }

    return NumbersTask(7, "Single-Teacher School Risk Mapping", payload)


def task8_digital_hope(
    ict_by_year: dict[str, pd.DataFrame],
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> NumbersTask:
    points = []
    models = []

    for year, ict in ict_by_year.items():
        sec = dropout_long[
            (dropout_long["year"].eq(year))
            & (dropout_long["gender"].eq(focus_gender))
            & (dropout_long["level"].eq(level))
        ].rename(columns={"rate": "dropout"})

        merged = ict.merge(sec[["state_ut", "dropout"]], on="state_ut", how="inner")
        merged = merged[(~merged["state_ut"].eq("India"))].dropna(subset=["pct_gov_functional_ict_labs", "dropout"])

        # Govt functional labs vs dropout
        x1 = merged["pct_gov_functional_ict_labs"].to_numpy()
        y = merged["dropout"].to_numpy()
        reg1 = _ols_with_band(x1, y)

        # Aided functional labs vs dropout
        x2 = merged["pct_aided_functional_ict_labs"].to_numpy()
        reg2 = _ols_with_band(x2, y)

        models.append(
            {
                "year": year,
                "govt_functional": {"n": reg1["n"], "corr": reg1["corr"], "slope": reg1["b"], "rmse": reg1["rmse"]},
                "aided_functional": {"n": reg2["n"], "corr": reg2["corr"], "slope": reg2["b"], "rmse": reg2["rmse"]},
            }
        )

        points.extend(
            merged[
                [
                    "state_ut",
                    "pct_gov_ict_labs",
                    "pct_gov_functional_ict_labs",
                    "pct_aided_ict_labs",
                    "pct_aided_functional_ict_labs",
                    "dropout",
                ]
            ]
            .assign(year=year)
            .to_dict(orient="records")
        )

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "points": points,
        "models": models,
    }

    return NumbersTask(8, "Digital Hope (ICT Labs vs Dropout)", payload)


def task9_red_zone_hotspots(
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
    threshold: float = 15.0,
    min_consecutive_years: int = 3,
) -> NumbersTask:
    d = dropout_long[
        (dropout_long["gender"].eq(focus_gender))
        & (dropout_long["level"].eq(level))
        & (~dropout_long["state_ut"].eq("India"))
    ].copy()
    d["year_int"] = d["year"].map(year_to_int)
    d = d.dropna(subset=["rate", "year_int"])

    # Determine consecutive-year streaks above threshold
    streaks = []
    for state, sdf in d.sort_values("year_int").groupby("state_ut"):
        sdf = sdf.sort_values("year_int")
        above = sdf["rate"] >= threshold
        years = sdf["year_int"].to_numpy()

        best = 0
        current = 0
        for i, is_above in enumerate(above.to_numpy()):
            if is_above:
                # require consecutive years in data
                if current == 0:
                    current = 1
                else:
                    if years[i] == years[i - 1] + 1:
                        current += 1
                    else:
                        current = 1
                best = max(best, current)
            else:
                current = 0

        streaks.append({"state_ut": state, "max_consecutive_years_above": int(best)})

    streak_df = pd.DataFrame(streaks)
    red = streak_df[streak_df["max_consecutive_years_above"] >= min_consecutive_years].sort_values(
        ["max_consecutive_years_above", "state_ut"], ascending=[False, True]
    )

    # Provide a compact time series for red-zone states
    red_states = red["state_ut"].tolist()
    ts = (
        d[d["state_ut"].isin(red_states)]
        .sort_values(["state_ut", "year_int"])
        .rename(columns={"rate": "dropout"})
        .loc[:, ["state_ut", "year", "year_int", "dropout"]]
        .to_dict(orient="records")
    )

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "threshold": threshold,
        "min_consecutive_years": min_consecutive_years,
        "red_zone_states": red.to_dict(orient="records"),
        "red_zone_time_series": ts,
    }

    return NumbersTask(9, "Red Zone Hotspots (Persistent High Dropout)", payload)


def task10_sdg_forecast(
    dropout_long: pd.DataFrame,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
    forecast_year: int = 2030,
) -> NumbersTask:
    df = dropout_long[(dropout_long["gender"].eq(focus_gender)) & (dropout_long["level"].eq(level))].copy()
    df["year_int"] = df["year"].map(year_to_int)

    states = sorted(set(df["state_ut"]) - {"India"})

    rows = []
    for state in states:
        s = df[df["state_ut"].eq(state)].dropna(subset=["rate", "year_int"]).sort_values("year_int")
        if len(s) < 3:
            continue
        x = s["year_int"].to_numpy().astype(float)
        y = s["rate"].to_numpy().astype(float)

        xbar = x.mean()
        ybar = y.mean()
        sxx = ((x - xbar) ** 2).sum()
        if sxx == 0:
            continue
        b = float(((x - xbar) * (y - ybar)).sum() / sxx)
        a = float(ybar - b * xbar)
        pred = float(a + b * float(forecast_year))

        # Fit quality (R^2)
        yhat = a + b * x
        ss_res = float(((y - yhat) ** 2).sum())
        ss_tot = float(((y - ybar) ** 2).sum())
        r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else None

        rows.append(
            {
                "state_ut": state,
                "n_years": int(len(s)),
                "start_year": int(s["year_int"].min()),
                "end_year": int(s["year_int"].max()),
                "latest_rate": float(s.iloc[-1]["rate"]),
                "slope_pp_per_year": float(b),
                "intercept": float(a),
                "r2": r2,
                "forecast_2030": pred,
                "implementation_gap_to_0": float(max(pred, 0.0)),
            }
        )

    out = pd.DataFrame(rows).sort_values("forecast_2030", ascending=False)

    payload = {
        "focus_gender": focus_gender,
        "level": level,
        "forecast_year": forecast_year,
        "states_modeled": int(len(out)),
        "rows": out.to_dict(orient="records"),
    }

    return NumbersTask(10, "2030 SDG Business-as-Usual Forecast", payload)
