from __future__ import annotations

import numpy as np
import pandas as pd

from .stats_utils import bootstrap_mean_diff, corr_with_perm_test


def _year_to_int(year: str) -> int:
    return int(str(year).split("-")[0])


def _latest_year(years: list[str]) -> str:
    return sorted(set(years), key=_year_to_int)[-1]


def task1_peak_attrition(
    dropout_long: pd.DataFrame,
    promotion_long: pd.DataFrame,
    repetition_long: pd.DataFrame,
    gender: str = "Girls",
) -> dict:
    """Peak attrition / bottleneck + checksum (promotion+dropout+repetition ~ 100)."""

    years = dropout_long["year"].dropna().astype(str).unique().tolist()
    focus_year = _latest_year(years)

    d = dropout_long[dropout_long["gender"].eq(gender)].copy()
    p = promotion_long[promotion_long["gender"].eq(gender)].copy()
    r = repetition_long[repetition_long["gender"].eq(gender)].copy()

    d = d.rename(columns={"rate": "dropout"})

    chk = d.merge(p, on=["year", "state_ut", "level", "gender"], how="inner").merge(
        r, on=["year", "state_ut", "level", "gender"], how="inner"
    )
    chk["sum_rates"] = chk["dropout"] + chk["promotion"] + chk["repetition"]
    chk["abs_deviation"] = (chk["sum_rates"] - 100.0).abs()

    checksum = {
        "rows_checked": int(len(chk)),
        "max_abs_deviation": float(chk["abs_deviation"].max()) if len(chk) else None,
        "p95_abs_deviation": float(chk["abs_deviation"].quantile(0.95)) if len(chk) else None,
        "rows_over_1pct": int((chk["abs_deviation"] > 1.0).sum()) if len(chk) else None,
        "worst_10_rows": (
            chk.sort_values("abs_deviation", ascending=False)
            .head(10)[["year", "state_ut", "level", "dropout", "promotion", "repetition", "sum_rates", "abs_deviation"]]
            .to_dict(orient="records")
            if len(chk)
            else []
        ),
    }

    # India bottleneck by year
    india = (
        d[d["state_ut"].eq("India")]
        .pivot_table(index="year", columns="level", values="dropout", aggfunc="first")
        .reset_index()
    )
    levels = [c for c in india.columns if c != "year"]
    india["peak_level"] = india[levels].idxmax(axis=1)
    india["peak_rate"] = india[levels].max(axis=1)

    peak_counts = india["peak_level"].value_counts().to_dict()
    bottleneck_level = max(peak_counts.items(), key=lambda kv: kv[1])[0] if peak_counts else None

    # Survival cohort for India focus_year
    india_focus = india[india["year"].eq(focus_year)].iloc[0]
    primary = float(india_focus.get("Primary (1-5)") or 0.0)
    upper = float(india_focus.get("Upper Primary (6-8)") or 0.0)
    secondary = float(india_focus.get("Secondary (9-10)") or 0.0)

    cohort = [100.0]
    cohort.append(cohort[-1] * (1.0 - primary / 100.0))
    cohort.append(cohort[-1] * (1.0 - upper / 100.0))
    cohort.append(cohort[-1] * (1.0 - secondary / 100.0))

    survival_levels = [
        "Start (Class 1)",
        "After Primary (1-5)",
        "After Upper Primary (6-8)",
        "After Secondary (9-10)",
    ]

    # Year-over-year changes (India)
    india_ts = india.copy()
    india_ts["year_int"] = india_ts["year"].map(_year_to_int)
    india_ts = india_ts.sort_values("year_int")
    yoy = india_ts.set_index("year")[levels].pct_change() * 100

    return {
        "task_id": 1,
        "title": "Peak Attrition Identification (Policy Bottleneck)",
        "focus_year": focus_year,
        "gender": gender,
        "findings": {
            "india_peak_level_by_year": india[["year", "peak_level", "peak_rate"]].to_dict(orient="records"),
            "india_peak_level_counts": peak_counts,
            "bottleneck_level_most_years": bottleneck_level,
            "india_yoy_pct_change": yoy.replace([np.inf, -np.inf], np.nan).round(2).fillna(None).to_dict(orient="index"),
            "survival_cohort_100": {
                "levels": survival_levels,
                "girls_remaining": [round(x, 2) for x in cohort],
                "assumption": "Illustrative multiplication of level dropout rates (not a tracked cohort).",
            },
        },
        "checksums": {"promotion_dropout_repetition_sum": checksum},
        "chart_data": {
            "india_dropout_by_level": (
                d[d["state_ut"].eq("India")]
                .sort_values("year", key=lambda s: s.map(_year_to_int))
                [["year", "level", "dropout"]]
                .rename(columns={"dropout": "rate"})
                .to_dict(orient="records")
            ),
            "survival_step": {"x": survival_levels, "y": [round(x, 2) for x in cohort]},
        },
        "narrative": {
            "lede": (
                f"Every system has a narrow door. In India’s dropout profile, that door is usually {bottleneck_level}. "
                "Not because the earlier years are easy — but because the later years are where the system demands more: "
                "more safety, more relevance, more reason to stay."
            ),
            "so_what": "Treat the bottleneck level as mission-mode: that’s where small changes move the headline number.",
        },
    }


def task2_infrastructure_roi(
    infra: pd.DataFrame,
    dropout_long: pd.DataFrame,
    year: str,
    gender: str = "Girls",
) -> dict:
    sec = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["level"].eq("Secondary (9-10)")) & (dropout_long["gender"].eq(gender))].copy()
    sec = sec.rename(columns={"rate": "secondary_dropout_rate"})

    # Column detection from infra
    cols = {c: str(c).lower() for c in infra.columns}
    fg_candidates = [c for c, cl in cols.items() if "functional" in cl and "girls" in cl and "toilet" in cl]
    total_candidates = [c for c, cl in cols.items() if cl == "total_schools" or ("total" in cl and "school" in cl)]

    if not fg_candidates:
        raise ValueError("No 'Functional Girls' Toilet' column found in infrastructure table")

    fg_col = fg_candidates[0]
    total_col = total_candidates[0] if total_candidates else "total_schools"

    df = infra[["state_ut", fg_col, total_col]].copy()
    df = df.rename(columns={fg_col: "functional_girls_toilets", total_col: "total_schools"})

    df["functional_girls_toilet_pct"] = 100.0 * df["functional_girls_toilets"] / df["total_schools"]

    merged = df.merge(sec[["state_ut", "secondary_dropout_rate"]], on="state_ut", how="inner")
    merged = merged[~merged["state_ut"].eq("India")].dropna(subset=["functional_girls_toilet_pct", "secondary_dropout_rate"])

    x = merged["functional_girls_toilet_pct"].to_numpy()
    y = merged["secondary_dropout_rate"].to_numpy()
    corr = corr_with_perm_test(x, y)

    # OLS y = a + b x
    xbar = float(x.mean())
    ybar = float(y.mean())
    sxx = float(((x - xbar) ** 2).sum())
    b = float(((x - xbar) * (y - ybar)).sum() / sxx) if sxx else float("nan")
    a = float(ybar - b * xbar)

    yhat = a + b * x
    resid = y - yhat

    merged = merged.assign(yhat=yhat, resid=resid)
    outliers_good = merged.nsmallest(6, "resid")["state_ut"].tolist()
    outliers_bad = merged.nlargest(6, "resid")["state_ut"].tolist()

    return {
        "task_id": 2,
        "title": "Infrastructure ROI (Toilets & Retention)",
        "year": year,
        "gender": gender,
        "findings": {
            "n_states": corr.n,
            "correlation": corr.corr,
            "correlation_perm_p": corr.p_perm,
            "regression": {"intercept": a, "slope": b},
            "efficiency_outliers": {
                "better_than_expected_low_dropout": outliers_good,
                "worse_than_expected_high_dropout": outliers_bad,
            },
        },
        "checksums": {
            "join_coverage": {
                "infra_rows": int(len(infra)),
                "dropout_rows_secondary": int(len(sec)),
                "merged_rows": int(len(merged)),
            }
        },
        "chart_data": {
            "points": merged[["state_ut", "functional_girls_toilet_pct", "secondary_dropout_rate", "yhat", "resid"]].to_dict(orient="records")
        },
        "narrative": {
            "lede": "A toilet is not a building feature — it’s a contract. It says a girl’s presence is expected, and her dignity is planned for.",
            "so_what": "The line is less important than the outliers: copy who beats the prediction; audit who fails it.",
            "caveat": "Correlation across states is not causal proof.",
        },
    }


def task3_female_teacher_multiplier(
    female_teachers: pd.DataFrame,
    dropout_long: pd.DataFrame,
    year: str,
    gender: str = "Girls",
    level: str = "Secondary (9-10)",
) -> dict:
    sec = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["level"].eq(level)) & (dropout_long["gender"].eq(gender))].copy()
    sec = sec.rename(columns={"rate": "dropout_rate"})

    ft = female_teachers[female_teachers["year"].eq(year)].copy()
    merged = ft.merge(sec[["state_ut", "dropout_rate"]], on="state_ut", how="inner")
    merged = merged[~merged["state_ut"].eq("India")].dropna(subset=["female_teacher_share", "dropout_rate"])

    x = merged["female_teacher_share"].to_numpy() * 100.0
    y = merged["dropout_rate"].to_numpy()
    corr = corr_with_perm_test(x, y)

    # Search a 'critical mass' threshold that maximizes mean dropout gap
    thresholds = np.arange(10, 81, 5)
    best = None
    for t in thresholds:
        low = merged[merged["female_teacher_share"] * 100.0 < t]["dropout_rate"].to_numpy()
        high = merged[merged["female_teacher_share"] * 100.0 >= t]["dropout_rate"].to_numpy()
        if len(low) < 6 or len(high) < 6:
            continue
        diff = float(low.mean() - high.mean())
        if (best is None) or (abs(diff) > abs(best["mean_diff"])):
            boot = bootstrap_mean_diff(low, high)
            best = {"threshold_pct": float(t), **boot}

    return {
        "task_id": 3,
        "title": "Female Teacher Multiplier (Role Model Effect)",
        "year": year,
        "gender": gender,
        "level": level,
        "findings": {
            "n_states": int(len(merged)),
            "correlation": corr.corr,
            "correlation_perm_p": corr.p_perm,
            "critical_mass_scan": best,
        },
        "checksums": {
            "teacher_totals_sanity": {
                "rows": int(len(ft)),
                "rows_with_total_mismatch": int((ft["teachers_male"] + ft["teachers_female"] - ft["teachers_total"]).abs().fillna(0).gt(1).sum()),
            }
        },
        "chart_data": {
            "points": merged[["state_ut", "female_teacher_share", "dropout_rate"]].to_dict(orient="records")
        },
        "narrative": {
            "lede": "In adolescent years, schools don’t just teach — they signal safety and possibility. Female teachers can act like social infrastructure.",
            "so_what": "Recruitment and posting policy is retention policy when it changes who girls see in front of the classroom.",
            "caveat": "This is a cross-state association; treat it as a lead, not a verdict.",
        },
    }


def task4_peer_benchmarking(
    ger_long: pd.DataFrame,
    dropout_long: pd.DataFrame,
    year: str,
    gender: str = "Girls",
    k_peers: int = 5,
) -> dict:
    """Peer benchmarking using nearest neighbors in GER space, then comparing dropout vs peer mean."""

    # GER tables vary; we expect a long format similar to dropout after parsing.
    # Here we build GER from the raw tables (expected to be loaded as long by caller).

    ger = ger_long[(ger_long["year"].eq(year)) & (ger_long["gender"].eq(gender))].copy()
    dr = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["gender"].eq(gender))].copy()

    # Focus on secondary dropout and 3 GER levels if present
    dr_sec = dr[dr["level"].eq("Secondary (9-10)")][["state_ut", "rate"]].rename(columns={"rate": "dropout_secondary"})

    value_col = "ger" if "ger" in ger.columns else ("value" if "value" in ger.columns else None)
    if value_col is None:
        return {
            "task_id": 4,
            "title": "Peer Benchmarking (Competitive Federalism)",
            "year": year,
            "gender": gender,
            "error": "GER data missing expected value column ('ger' or 'value').",
        }

    ger_wide = ger.pivot_table(index="state_ut", columns="level", values=value_col, aggfunc="first")
    required = ["Primary (1-5)", "Upper Primary (6-8)", "Secondary (9-10)"]
    present = [c for c in required if c in ger_wide.columns]
    if len(present) < 2:
        return {
            "task_id": 4,
            "title": "Peer Benchmarking (Competitive Federalism)",
            "year": year,
            "gender": gender,
            "error": "GER levels missing in parsed GER data; cannot form peer vectors.",
        }

    # Join and compute peers
    df = ger_wide[present].reset_index().merge(dr_sec, on="state_ut", how="inner")
    df = df[~df["state_ut"].eq("India")].dropna()

    X = df[present].to_numpy(dtype=float)
    # Standardize
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)

    state = df["state_ut"].tolist()
    y = df["dropout_secondary"].to_numpy(dtype=float)

    peer_info = []
    for i in range(len(df)):
        dists = np.sqrt(((X - X[i]) ** 2).sum(axis=1))
        idx = np.argsort(dists)
        idx = [j for j in idx if j != i][:k_peers]
        peers = [state[j] for j in idx]
        peer_mean = float(np.mean([y[j] for j in idx])) if idx else float("nan")
        delta = float(y[i] - peer_mean) if np.isfinite(peer_mean) else float("nan")
        peer_info.append({"state_ut": state[i], "peers": peers, "dropout_secondary": float(y[i]), "peer_mean": peer_mean, "performance_delta": delta})

    peer_df = pd.DataFrame(peer_info).sort_values("performance_delta")

    return {
        "task_id": 4,
        "title": "Peer Benchmarking (Competitive Federalism)",
        "year": year,
        "gender": gender,
        "findings": {
            "k_peers": k_peers,
            "best_10_vs_peers": peer_df.head(10).to_dict(orient="records"),
            "worst_10_vs_peers": peer_df.tail(10).sort_values("performance_delta", ascending=False).to_dict(orient="records"),
        },
        "chart_data": {
            "all": peer_df.to_dict(orient="records"),
            "ger_levels_used": present,
        },
        "narrative": {
            "lede": "Peer benchmarking turns ‘big states vs small states’ arguments into ‘states with similar starting points’ learning loops.",
            "so_what": "Use peers as accountability mirrors: same constraints, different outcomes.",
        },
    }


def task7_single_teacher_risk(
    single_teacher: pd.DataFrame,
    infra: pd.DataFrame,
    dropout_long: pd.DataFrame,
    year: str,
    gender: str = "Girls",
) -> dict:
    # Compute % single-teacher schools.
    # Prefer Table 2.2 totals (already present in loader output) to avoid merge collisions.
    st = single_teacher[single_teacher["year"].eq(year)].copy()

    if "total_schools" not in st.columns or st["total_schools"].isna().all():
        cols = {c: str(c).lower() for c in infra.columns}
        total_candidates = [c for c, cl in cols.items() if cl == "total_schools" or ("total" in cl and "school" in cl)]
        total_col = total_candidates[0] if total_candidates else "total_schools"
        totals = infra[["state_ut", total_col]].rename(columns={total_col: "total_schools"})
        st = st.drop(columns=[c for c in ["total_schools"] if c in st.columns]).merge(totals, on="state_ut", how="inner")

    st = st[~st["state_ut"].eq("India")].dropna(subset=["schools_with_single_teacher", "total_schools"])
    st["single_teacher_pct"] = 100.0 * st["schools_with_single_teacher"] / st["total_schools"]

    sec = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["level"].eq("Secondary (9-10)")) & (dropout_long["gender"].eq(gender))].copy()
    sec = sec.rename(columns={"rate": "secondary_dropout_rate"})

    merged = st.merge(sec[["state_ut", "secondary_dropout_rate"]], on="state_ut", how="inner")
    merged = merged.dropna(subset=["single_teacher_pct", "secondary_dropout_rate"])

    x = merged["single_teacher_pct"].to_numpy(dtype=float)
    y = merged["secondary_dropout_rate"].to_numpy(dtype=float)
    corr = corr_with_perm_test(x, y)

    return {
        "task_id": 7,
        "title": "Single-Teacher School Risk Mapping",
        "year": year,
        "gender": gender,
        "findings": {
            "n_states": corr.n,
            "correlation": corr.corr,
            "correlation_perm_p": corr.p_perm,
            "top_10_single_teacher_pct": merged.sort_values("single_teacher_pct", ascending=False).head(10)[["state_ut", "single_teacher_pct", "secondary_dropout_rate"]].to_dict(orient="records"),
        },
        "chart_data": {
            "points": merged[["state_ut", "single_teacher_pct", "secondary_dropout_rate"]].to_dict(orient="records")
        },
        "narrative": {
            "lede": "Single-teacher schools aren’t just a staffing statistic — they are a fragility signal. When one teacher is absent, the school is absent.",
            "so_what": "Use this as a risk triage: staffing reinforcement beats cosmetic interventions in high-risk states.",
        },
    }


def task8_digital_hope(
    ict_labs_long: pd.DataFrame,
    dropout_long: pd.DataFrame,
    gender: str = "Girls",
) -> dict:
    """Use Table 9.9 (ICT labs) for years where present, compare with dropout."""

    # Expect ict_labs_long with columns: year, state_ut, govt_pct_functional, aided_pct_functional
    years = sorted(ict_labs_long["year"].unique().tolist(), key=_year_to_int)

    rows = []
    for year in years:
        sec = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["level"].eq("Secondary (9-10)")) & (dropout_long["gender"].eq(gender))][["state_ut", "rate"]].rename(columns={"rate": "secondary_dropout_rate"})
        ict = ict_labs_long[ict_labs_long["year"].eq(year)].copy()
        merged = ict.merge(sec, on="state_ut", how="inner")
        merged = merged[~merged["state_ut"].eq("India")].dropna(subset=["govt_pct_functional", "secondary_dropout_rate"])

        corr = corr_with_perm_test(merged["govt_pct_functional"].to_numpy(), merged["secondary_dropout_rate"].to_numpy())
        rows.append({
            "year": year,
            "n_states": corr.n,
            "corr_govt_functional_vs_dropout": corr.corr,
            "p_perm": corr.p_perm,
        })

    return {
        "task_id": 8,
        "title": "Digital Hope Factor (ICT Labs)",
        "gender": gender,
        "findings": {
            "years_available": years,
            "yearly_correlations": rows,
        },
        "chart_data": {
            "by_state_year": ict_labs_long.to_dict(orient="records"),
        },
        "narrative": {
            "lede": "Modernity can be a retention tool if school feels like a bridge to work, not a corridor to nowhere.",
            "so_what": "Look for states where ICT functionality rose and dropout fell — those are the implementation playbooks.",
            "caveat": "ICT tables are only available for 2022-23 and 2023-24 in this dump.",
        },
    }


def task9_red_zone_hotspots(
    dropout_long: pd.DataFrame,
    gender: str = "Girls",
    level: str = "Secondary (9-10)",
    threshold: float = 15.0,
    min_years: int = 3,
) -> dict:
    df = dropout_long[(dropout_long["gender"].eq(gender)) & (dropout_long["level"].eq(level))].copy()
    df = df[~df["state_ut"].eq("India")].dropna(subset=["rate"])  # focus on states
    df["year_int"] = df["year"].map(_year_to_int)
    df = df.sort_values(["state_ut", "year_int"])

    red_states = []
    for state, g in df.groupby("state_ut"):
        rates = g[["year_int", "rate"]].to_numpy()
        # consecutive years above threshold
        above = (rates[:, 1] >= threshold).astype(int)
        best_run = 0
        run = 0
        for v in above:
            if v:
                run += 1
                best_run = max(best_run, run)
            else:
                run = 0
        if best_run >= min_years:
            red_states.append({
                "state_ut": state,
                "max_consecutive_years": int(best_run),
                "latest_rate": float(g.sort_values("year_int").iloc[-1]["rate"]),
            })

    red_states = sorted(red_states, key=lambda r: (-r["max_consecutive_years"], -r["latest_rate"]))

    return {
        "task_id": 9,
        "title": "Geographic Red Zones (Persistent High Dropout)",
        "gender": gender,
        "level": level,
        "threshold": threshold,
        "min_years": min_years,
        "findings": {
            "red_zone_states": red_states,
            "n_red_zone_states": int(len(red_states)),
        },
        "chart_data": {
            "time_series": df[["state_ut", "year", "rate"]].to_dict(orient="records")
        },
        "narrative": {
            "lede": "A one-year spike is a scare. Three years is a system.",
            "so_what": "Persistent red zones are where standard programs bounce off — they need mission-mode diagnostics.",
            "caveat": "This identifies State/UT-level persistence; district-level hotspots require district tables.",
        },
    }


def task10_sdg_forecast(
    dropout_long: pd.DataFrame,
    gender: str = "Girls",
    level: str = "Secondary (9-10)",
    forecast_year: int = 2030,
) -> dict:
    df = dropout_long[(dropout_long["gender"].eq(gender)) & (dropout_long["level"].eq(level))].copy()
    df["year_int"] = df["year"].map(_year_to_int)

    states = sorted(set(df["state_ut"]) - {"India"})

    rows = []
    for state in states:
        s = df[df["state_ut"].eq(state)].dropna(subset=["rate", "year_int"]).sort_values("year_int")
        if len(s) < 3:
            continue
        x = s["year_int"].to_numpy(dtype=float)
        y = s["rate"].to_numpy(dtype=float)

        xbar = x.mean()
        ybar = y.mean()
        sxx = ((x - xbar) ** 2).sum()
        b = ((x - xbar) * (y - ybar)).sum() / sxx
        a = ybar - b * xbar
        pred = float(a + b * float(forecast_year))

        rows.append(
            {
                "state_ut": state,
                "n_years": int(len(s)),
                "start_year": int(s["year_int"].min()),
                "end_year": int(s["year_int"].max()),
                "latest_rate": float(s.iloc[-1]["rate"]),
                "slope_pp_per_year": float(b),
                "forecast_2030": pred,
                "implementation_gap_to_0": float(max(pred, 0.0)),
            }
        )

    out = pd.DataFrame(rows).sort_values("forecast_2030", ascending=False)

    return {
        "task_id": 10,
        "title": "2030 SDG Business-as-Usual Forecast",
        "gender": gender,
        "level": level,
        "forecast_year": forecast_year,
        "findings": {
            "states_modeled": int(len(out)),
            "top_10_highest_forecast": out.head(10).to_dict(orient="records"),
            "top_10_fastest_improving": out.sort_values("slope_pp_per_year").head(10).to_dict(orient="records"),
        },
        "chart_data": {"by_state": out.to_dict(orient="records")},
        "narrative": {
            "lede": "Forecasts are mirrors. They don’t tell you what will happen — they tell you what happens if you do nothing different.",
            "so_what": "The implementation gap is the officer’s backlog, stated in percentage points.",
            "caveats": [
                "Linear trend is a simplification; policy shocks can change slopes.",
                "Small-population states can be noisy.",
            ],
        },
    }
