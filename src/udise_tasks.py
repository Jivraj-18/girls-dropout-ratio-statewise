from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


@dataclass(frozen=True)
class TaskOutput:
    task_id: int
    title: str
    html_files: list[str]
    findings: dict
    checksums: dict


def _year_to_int(year: str) -> int:
    return int(str(year).split("-")[0])


def compute_attrition_and_checksums(
    dropout_long: pd.DataFrame,
    promotion_long: pd.DataFrame,
    repetition_long: pd.DataFrame,
    out_dir: Path,
    focus_gender: str = "Girls",
    focus_year: str | None = None,
) -> TaskOutput:
    """Task 1: Peak Attrition (policy bottleneck) + survival step chart.

    Uses verified level-wise Dropout/Promotion/Repetition rates.
    """

    if focus_year is None:
        focus_year = (
            dropout_long["year"].dropna().astype(str).sort_values(key=lambda s: s.map(_year_to_int)).iloc[-1]
        )

    # Pivot to wide for convenience
    d = dropout_long[dropout_long["gender"].eq(focus_gender)].pivot_table(
        index=["year", "state_ut"],
        columns="level",
        values="rate",
        aggfunc="first",
    ).reset_index()

    # Identify peak leakage level for India (and overall)
    india = d[d["state_ut"].eq("India")].copy()
    level_cols = [c for c in india.columns if c not in {"year", "state_ut"}]
    india["peak_level"] = india[level_cols].idxmax(axis=1)
    india["peak_rate"] = india[level_cols].max(axis=1)

    peak_counts = india["peak_level"].value_counts(dropna=True).to_dict()

    # Year-over-year changes (India)
    india_ts = india[["year"] + level_cols].copy()
    india_ts["year_int"] = india_ts["year"].map(_year_to_int)
    india_ts = india_ts.sort_values("year_int")
    yoy = india_ts.set_index("year")[level_cols].pct_change() * 100

    # Survival (cohort of 100) for India, focus_year
    latest = india_ts[india_ts["year"].eq(focus_year)].iloc[0]
    primary = float(latest.get("Primary (1-5)") or 0.0)
    upper = float(latest.get("Upper Primary (6-8)") or 0.0)
    secondary = float(latest.get("Secondary (9-10)") or 0.0)

    cohort = [100.0]
    cohort.append(cohort[-1] * (1.0 - primary / 100.0))
    cohort.append(cohort[-1] * (1.0 - upper / 100.0))
    cohort.append(cohort[-1] * (1.0 - secondary / 100.0))

    survival_levels = ["Start (Class 1)", "After Primary (1-5)", "After Upper Primary (6-8)", "After Secondary (9-10)"]

    fig_survival = go.Figure()
    fig_survival.add_trace(
        go.Scatter(
            x=survival_levels,
            y=cohort,
            mode="lines+markers",
            line_shape="hv",
            name=f"India cohort survival ({focus_year})",
        )
    )
    fig_survival.update_layout(
        title=f"Cohort survival of 100 girls across levels (illustrative, using level dropout rates) — {focus_year}",
        yaxis_title="Girls remaining out of 100",
        xaxis_title="Education level",
        hovermode="x unified",
    )

    # Trend chart: dropout by level over years (India)
    india_long = india_ts.melt(id_vars=["year", "year_int"], value_vars=level_cols, var_name="level", value_name="dropout_rate")
    fig_trend = px.line(
        india_long.sort_values("year_int"),
        x="year",
        y="dropout_rate",
        color="level",
        markers=True,
        title=f"India: Girls' dropout rate by level (verified tables) — 2018–2025",
    )
    fig_trend.update_layout(yaxis_title="Dropout rate (%)")

    html1 = out_dir / "task1_peak_attrition_survival.html"
    html2 = out_dir / "task1_peak_attrition_trends.html"
    fig_survival.write_html(html1, include_plotlyjs="cdn", full_html=True)
    fig_trend.write_html(html2, include_plotlyjs="cdn", full_html=True)

    # Checksum: Promotion + Dropout + Repetition ~ 100
    def _prep(kind_df: pd.DataFrame, value_col: str) -> pd.DataFrame:
        return (
            kind_df[kind_df["gender"].eq(focus_gender)]
            .rename(columns={value_col: value_col})
            .pivot_table(index=["year", "state_ut", "level"], values=value_col, aggfunc="first")
            .reset_index()
        )

    p = _prep(promotion_long, "promotion")
    r = _prep(repetition_long, "repetition")
    dd = dropout_long[dropout_long["gender"].eq(focus_gender)].rename(columns={"rate": "dropout"})

    chk = dd.merge(p, on=["year", "state_ut", "level"], how="inner").merge(r, on=["year", "state_ut", "level"], how="inner")
    chk["sum_rates"] = chk["dropout"] + chk["promotion"] + chk["repetition"]
    chk["abs_deviation"] = (chk["sum_rates"] - 100.0).abs()

    checksum_summary = {
        "rows_checked": int(len(chk)),
        "max_abs_deviation": float(chk["abs_deviation"].max()) if len(chk) else None,
        "p95_abs_deviation": float(chk["abs_deviation"].quantile(0.95)) if len(chk) else None,
        "rows_over_1pct": int((chk["abs_deviation"] > 1.0).sum()) if len(chk) else None,
    }

    # Identify the bottleneck level (India, most frequent peak)
    bottleneck_level = max(peak_counts.items(), key=lambda kv: kv[1])[0] if peak_counts else None

    findings = {
        "focus_year": focus_year,
        "gender": focus_gender,
        "india_peak_level_by_year": india[["year", "peak_level", "peak_rate"]].to_dict(orient="records"),
        "india_peak_level_counts": peak_counts,
        "bottleneck_level_most_years": bottleneck_level,
        "india_yoy_pct_change": yoy.replace([np.inf, -np.inf], np.nan).round(2).fillna(None).to_dict(orient="index"),
        "survival_cohort_100": {"levels": survival_levels, "girls_remaining": [round(x, 2) for x in cohort]},
        "interpretation": {
            "policy_bottleneck": bottleneck_level,
            "why_this_matters": (
                "When one level repeatedly dominates the dropout profile, it acts like a choke-point: "
                "improvements elsewhere don’t move the headline number unless this bottleneck shifts."
            ),
        },
    }

    return TaskOutput(
        task_id=1,
        title="Peak Attrition Identification (Policy Bottleneck)",
        html_files=[str(html1), str(html2)],
        findings=findings,
        checksums={"promotion_dropout_repetition_sum": checksum_summary},
    )


def _linear_regression_with_band(x: np.ndarray, y: np.ndarray) -> dict:
    """Simple OLS y = a + b x, plus 95% CI band for mean prediction (normal approx)."""

    x = x.astype(float)
    y = y.astype(float)
    n = len(x)
    xbar = x.mean()
    ybar = y.mean()
    sxx = ((x - xbar) ** 2).sum()
    b = ((x - xbar) * (y - ybar)).sum() / sxx
    a = ybar - b * xbar

    yhat = a + b * x
    resid = y - yhat
    s2 = (resid**2).sum() / max(n - 2, 1)
    s = np.sqrt(s2)

    x_grid = np.linspace(x.min(), x.max(), 100)
    y_grid = a + b * x_grid
    se_mean = s * np.sqrt(1.0 / n + (x_grid - xbar) ** 2 / sxx)
    z = 1.96  # normal approx

    return {
        "a": float(a),
        "b": float(b),
        "x_grid": x_grid,
        "y_grid": y_grid,
        "lower": y_grid - z * se_mean,
        "upper": y_grid + z * se_mean,
        "yhat": yhat,
        "resid": resid,
        "rmse": float(np.sqrt((resid**2).mean())),
        "corr": float(np.corrcoef(x, y)[0, 1]),
        "n": int(n),
    }


def correlate_infrastructure_vs_dropout(
    infra: pd.DataFrame,
    dropout_long: pd.DataFrame,
    out_dir: Path,
    year: str,
    focus_gender: str = "Girls",
) -> TaskOutput:
    """Task 2: Infrastructure ROI (Functional girls' toilets vs secondary dropout)."""

    # Pull secondary dropout girls
    sec = dropout_long[(dropout_long["year"].eq(year)) & (dropout_long["level"].eq("Secondary (9-10)")) & (dropout_long["gender"].eq(focus_gender))].copy()
    sec = sec.rename(columns={"rate": "secondary_dropout_rate"})

    # Identify infra columns
    cols = {c: c.lower() for c in infra.columns}
    fg_candidates = [c for c, cl in cols.items() if "functional" in cl and "girls" in cl and "toilet" in cl]
    total_candidates = [c for c, cl in cols.items() if cl == "total_schools" or ("total" in cl and "school" in cl)]

    if not fg_candidates:
        raise ValueError("Could not find a 'Functional Girls Toilet' column in Table 2.5 infrastructure")

    functional_girls_toilet_col = fg_candidates[0]
    total_schools_col = total_candidates[0] if total_candidates else "total_schools"

    df = infra[["state_ut", functional_girls_toilet_col, total_schools_col]].copy()
    df = df.rename(columns={functional_girls_toilet_col: "functional_girls_toilets", total_schools_col: "total_schools"})

    df["functional_girls_toilet_pct"] = 100.0 * df["functional_girls_toilets"] / df["total_schools"]

    merged = df.merge(sec[["state_ut", "secondary_dropout_rate"]], on="state_ut", how="inner")
    merged = merged[~merged["state_ut"].eq("India")].dropna(subset=["functional_girls_toilet_pct", "secondary_dropout_rate"])

    x = merged["functional_girls_toilet_pct"].to_numpy()
    y = merged["secondary_dropout_rate"].to_numpy()
    reg = _linear_regression_with_band(x, y)

    merged["yhat"] = reg["yhat"]
    merged["resid"] = reg["resid"]

    outliers_good = merged.nsmallest(6, "resid")["state_ut"].tolist()
    outliers_bad = merged.nlargest(6, "resid")["state_ut"].tolist()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=merged["functional_girls_toilet_pct"],
            y=merged["secondary_dropout_rate"],
            mode="markers+text",
            text=merged["state_ut"],
            textposition="top center",
            name="States/UTs",
            hovertemplate="%{text}<br>Functional girls toilet coverage: %{x:.1f}%<br>Secondary girls dropout: %{y:.1f}%<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=reg["x_grid"],
            y=reg["y_grid"],
            mode="lines",
            name="OLS fit",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=np.concatenate([reg["x_grid"], reg["x_grid"][::-1]]),
            y=np.concatenate([reg["upper"], reg["lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(0,0,0,0.08)",
            line=dict(color="rgba(0,0,0,0)"),
            name="95% confidence band (mean)",
        )
    )

    fig.update_layout(
        title=f"Infrastructure ROI: Functional girls' toilets vs secondary girls dropout ({year})",
        xaxis_title="Functional girls' toilet coverage (% of schools)",
        yaxis_title="Secondary dropout rate (girls, %)",
        hovermode="closest",
    )

    html = out_dir / "task2_infrastructure_roi.html"
    fig.write_html(html, include_plotlyjs="cdn", full_html=True)

    findings = {
        "year": year,
        "gender": focus_gender,
        "n_states": reg["n"],
        "correlation": round(reg["corr"], 3),
        "regression": {"intercept": round(reg["a"], 4), "slope": round(reg["b"], 4), "rmse": round(reg["rmse"], 3)},
        "efficiency_outliers": {
            "better_than_expected_low_dropout": outliers_good,
            "worse_than_expected_high_dropout": outliers_bad,
        },
        "interpretation": {
            "so_what": (
                "Toilets correlate with retention — but not perfectly. The real signal for an officer is in the residuals: "
                "states doing *better than the infrastructure would predict* are policy laboratories worth copying, and "
                "states doing worse are where the last-mile of functionality, safety, and school climate might be failing."
            ),
            "caveat": "This is correlation across states (not causal proof).",
        },
    }

    checksums = {
        "join_coverage": {
            "infra_rows": int(len(infra)),
            "dropout_rows_secondary": int(len(sec)),
            "merged_rows": int(len(merged)),
            "missing_after_join": sorted(set(sec["state_ut"]) - set(merged["state_ut"]))[:20],
        }
    }

    return TaskOutput(
        task_id=2,
        title="Infrastructure ROI (Toilets & Retention)",
        html_files=[str(html)],
        findings=findings,
        checksums=checksums,
    )


def forecast_sdg_2030(
    dropout_long: pd.DataFrame,
    out_dir: Path,
    focus_gender: str = "Girls",
    level: str = "Secondary (9-10)",
    forecast_year: int = 2030,
) -> TaskOutput:
    """Task 10: Business-as-usual forecast to 2030 using per-state linear trends."""

    df = dropout_long[(dropout_long["gender"].eq(focus_gender)) & (dropout_long["level"].eq(level))].copy()
    df["year_int"] = df["year"].map(_year_to_int)

    # Exclude India aggregate from per-state forecast, but keep for context
    states = sorted(set(df["state_ut"]) - {"India"})

    rows = []
    for state in states:
        s = df[df["state_ut"].eq(state)].dropna(subset=["rate", "year_int"]).sort_values("year_int")
        if len(s) < 3:
            continue
        x = s["year_int"].to_numpy().astype(float)
        y = s["rate"].to_numpy().astype(float)

        # OLS
        xbar = x.mean()
        ybar = y.mean()
        sxx = ((x - xbar) ** 2).sum()
        b = ((x - xbar) * (y - ybar)).sum() / sxx
        a = ybar - b * xbar
        pred = a + b * float(forecast_year)

        rows.append(
            {
                "state_ut": state,
                "n_years": int(len(s)),
                "start_year": int(s["year_int"].min()),
                "end_year": int(s["year_int"].max()),
                "latest_rate": float(s.iloc[-1]["rate"]),
                "slope_per_year": float(b),
                "forecast_2030": float(pred),
                "implementation_gap_to_0": float(max(pred, 0.0)),
            }
        )

    out = pd.DataFrame(rows).dropna()
    out = out.sort_values("forecast_2030", ascending=False)

    fig_bar = px.bar(
        out,
        x="forecast_2030",
        y="state_ut",
        orientation="h",
        title=f"2030 forecast (linear trend): Girls' {level} dropout rate by state",
        hover_data={
            "latest_rate": ":.2f",
            "slope_per_year": ":.3f",
            "n_years": True,
            "start_year": True,
            "end_year": True,
        },
    )
    fig_bar.update_layout(xaxis_title="Forecast dropout rate in 2030 (%)", yaxis_title="State/UT", height=900)

    fig_scatter = px.scatter(
        out,
        x="latest_rate",
        y="slope_per_year",
        text="state_ut",
        title=f"Who is improving fast enough? Latest vs slope (girls' {level} dropout)",
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(xaxis_title="Latest dropout rate (%)", yaxis_title="Annual change (pp/year)")

    html = out_dir / "task10_sdg_2030_forecast.html"
    # Combine both figs into one HTML for convenience
    html.write_text(
        "\n".join(
            [
                "<html><head><meta charset='utf-8'></head><body>",
                fig_bar.to_html(include_plotlyjs="cdn", full_html=False),
                "<hr/>",
                fig_scatter.to_html(include_plotlyjs=False, full_html=False),
                "</body></html>",
            ]
        ),
        encoding="utf-8",
    )

    findings = {
        "forecast_year": forecast_year,
        "gender": focus_gender,
        "level": level,
        "states_modeled": int(len(out)),
        "top_10_highest_forecast": out.head(10).to_dict(orient="records"),
        "top_10_fastest_improving": out.sort_values("slope_per_year").head(10).to_dict(orient="records"),
        "interpretation": {
            "so_what": (
                "Forecasts don’t predict destiny; they expose inertia. If a state’s trendline still lands above zero in 2030, "
                "the gap is not a statistic — it’s the officer’s backlog."
            ),
            "caveats": [
                "Linear trend is a simplification; real policy shifts can create breaks.",
                "Dropout rates can be noisy in small populations; interpret small states carefully.",
            ],
        },
    }

    checksums = {
        "coverage": {
            "years_in_data": sorted(df["year"].unique().tolist(), key=_year_to_int),
            "states_total": int(len(states)),
            "states_modeled": int(len(out)),
        }
    }

    return TaskOutput(
        task_id=10,
        title="2030 SDG Business-as-Usual Forecast",
        html_files=[str(html)],
        findings=findings,
        checksums=checksums,
    )


def write_analysis_summary(
    out_path: Path,
    schemas: dict,
    feasibility: dict,
    task_outputs: list[TaskOutput],
    audit_notes: list[str],
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schemas": {
            k: {
                "file": getattr(v, "file", None),
                "header_rows": getattr(v, "header_rows", None),
                "detected_columns": getattr(v, "detected_columns", None),
                "n_rows": getattr(v, "n_rows", None),
                "n_cols": getattr(v, "n_cols", None),
                "sample_states": getattr(v, "sample_states", None),
            }
            for k, v in schemas.items()
        },
        "feasibility": feasibility,
        "insights": [
            {
                "task_id": t.task_id,
                "title": t.title,
                "html_files": [Path(p).name for p in t.html_files],
                "findings": t.findings,
                "checksums": t.checksums,
                "narrative": _to_journalist_narrative(t),
            }
            for t in task_outputs
        ],
        "audit_notes": audit_notes,
    }

    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _to_journalist_narrative(task: TaskOutput) -> dict:
    # Keep this compact but story-driven; the detailed evidence stays in findings + visuals.
    if task.task_id == 1:
        bottleneck = task.findings.get("bottleneck_level_most_years")
        focus_year = task.findings.get("focus_year")
        survival = task.findings.get("survival_cohort_100", {})
        remaining = None
        if survival:
            remaining = survival.get("girls_remaining", [])[-1]
        return {
            "lede": (
                f"Every system has a narrow door. In India’s dropout data, that door is usually {bottleneck}. "
                "Not because the earlier years are easy — but because the later years are where the system demands more: "
                "more safety, more relevance, more reason to stay."
            ),
            "why_now": (
                f"In {focus_year}, a cohort-of-100 thought experiment suggests only about {remaining} girls remain "
                "after running the gauntlet of level-wise dropout. Even if the exact cohort math is illustrative, "
                "the bottleneck is real — and it’s where an IAS officer can change the slope fastest."
            ),
            "what_to_do": [
                "Treat the bottleneck level as a mission-mode priority with specific, local accountability.",
                "Use promotion+repetition+dropout checks as a monthly data-quality guardrail.",
            ],
        }

    if task.task_id == 2:
        corr = task.findings.get("correlation")
        return {
            "lede": (
                "A toilet is not a building feature — it’s a contract. It says a girl’s presence is expected, "
                "and her dignity is planned for."
            ),
            "what_we_found": (
                f"Across states, functional girls’ toilet coverage and secondary girls’ dropout move together (corr={corr}). "
                "But the most important story is not the line — it’s the outliers: who beats the prediction, and who doesn’t."
            ),
            "what_to_do": [
                "Copy ‘efficiency outliers’ with low dropout despite low coverage (implementation playbooks).",
                "In ‘worse-than-expected’ states, audit functionality, maintenance budgets, and school safety climate.",
            ],
        }

    if task.task_id == 10:
        top = task.findings.get("top_10_highest_forecast", [])
        worst = top[0]["state_ut"] if top else None
        return {
            "lede": (
                "Forecasts are a mirror held up to the present. They don’t tell you what will happen — they tell you what "
                "happens if you do nothing different."
            ),
            "sting": (
                f"On current trends, {worst} sits among the hardest cases by 2030 in secondary girls’ dropout. "
                "That ‘implementation gap’ is not abstract — it’s the distance between today’s system and the SDG promise."
            ),
            "what_to_do": [
                "Use the slope chart to identify where existing policy is already working (scale it).",
                "For laggards, set time-bound targets tied to the bottleneck level and infra-functionality audits.",
            ],
        }

    return {"lede": "", "what_to_do": []}
