from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT_DIR = Path("outputs")


def pct(x: float) -> float:
    return 100.0 * float(x)


def load_panel() -> pd.DataFrame:
    fp = OUT_DIR / "udise_state_caste_year_flow_rates.parquet"
    if not fp.exists():
        raise SystemExit(
            "Missing panel parquet. Run build_outcome_panel.py first to generate outputs/*.parquet"
        )
    return pd.read_parquet(fp)


def linear_forecast(y: np.ndarray, steps_ahead: int) -> tuple[np.ndarray, np.ndarray]:
    """Fit y = a + b*t on t=0..n-1, forecast next steps."""
    n = len(y)
    t = np.arange(n, dtype=float)
    if n < 2:
        return np.full(steps_ahead, np.nan), np.array([np.nan, np.nan])
    b, a = np.polyfit(t, y, 1)
    t_f = np.arange(n, n + steps_ahead, dtype=float)
    y_f = a + b * t_f
    return y_f, np.array([a, b])


def make_findings(panel: pd.DataFrame) -> dict[str, object]:
    # Focus: overall caste_id=5
    overall = panel[panel["caste_id"] == 5].copy()

    # national row
    nat = overall[overall["location_name"].isna()].sort_values("year_id")
    nat_latest = nat.iloc[-1] if not nat.empty else None

    # state rows
    states = overall[overall["location_name"].notna()].copy()
    latest_year = states["year_id"].max()
    states_latest = states[states["year_id"] == latest_year].copy()

    # latest ranking
    states_latest["secondary_girls_dropout_pct"] = 100.0 * states_latest[
        "secondary_girl_dropout_rate"
    ]
    rank = states_latest.sort_values("secondary_girls_dropout_pct", ascending=False)

    # improvement (first -> last) for secondary girls
    first_year = states["year_id"].min()
    g0 = (
        states[states["year_id"] == first_year]
        .set_index("location_name")["secondary_girl_dropout_rate"]
        .rename("first")
    )
    g1 = (
        states[states["year_id"] == latest_year]
        .set_index("location_name")["secondary_girl_dropout_rate"]
        .rename("last")
    )
    delta = pd.concat([g0, g1], axis=1).dropna()
    delta["pp_change"] = 100.0 * (delta["last"] - delta["first"])  # percentage points
    most_improved = delta.sort_values("pp_change").head(10)
    most_worsened = delta.sort_values("pp_change", ascending=False).head(10)

    # status quo forecast: national and per-state (secondary girls)
    nat_series = (100.0 * nat["secondary_girl_dropout_rate"]).to_numpy() if not nat.empty else np.array([])
    nat_forecast, nat_coef = (
        linear_forecast(nat_series, steps_ahead=3) if len(nat_series) else (np.array([]), np.array([np.nan, np.nan]))
    )

    per_state = []
    for state, sdf in (
        states[["location_name", "year_id", "acad_year", "secondary_girl_dropout_rate"]]
        .sort_values(["location_name", "year_id"])
        .groupby("location_name")
    ):
        y = (100.0 * sdf["secondary_girl_dropout_rate"]).to_numpy()
        y_f, coef = linear_forecast(y, steps_ahead=3)
        if len(y_f) != 3:
            continue
        per_state.append(
            {
                "location_name": state,
                "latest_acad_year": sdf["acad_year"].iloc[-1],
                "latest_dropout_pct": float(y[-1]) if len(y) else np.nan,
                "trend_pp_per_year": float(coef[1]),
                "forecast_1y": float(y_f[0]),
                "forecast_2y": float(y_f[1]),
                "forecast_3y": float(y_f[2]),
            }
        )

    forecast_df = pd.DataFrame(per_state)

    return {
        "latest_year": latest_year,
        "first_year": first_year,
        "nat": nat,
        "nat_latest": nat_latest,
        "rank": rank,
        "most_improved": most_improved,
        "most_worsened": most_worsened,
        "forecast_df": forecast_df,
        "nat_forecast": nat_forecast,
        "nat_coef": nat_coef,
    }


def write_outputs(findings: dict[str, object]) -> None:
    OUT_DIR.mkdir(exist_ok=True)

    latest_year = findings["latest_year"]
    first_year = findings["first_year"]
    nat = findings["nat"]
    nat_latest = findings["nat_latest"]
    rank: pd.DataFrame = findings["rank"]
    most_improved: pd.DataFrame = findings["most_improved"]
    most_worsened: pd.DataFrame = findings["most_worsened"]
    forecast_df: pd.DataFrame = findings["forecast_df"]
    nat_forecast: np.ndarray = findings["nat_forecast"]
    nat_coef: np.ndarray = findings["nat_coef"]

    # Forecast CSV
    forecast_out = OUT_DIR / "status_quo_forecast_secondary_girls.csv"
    forecast_df.sort_values("trend_pp_per_year", ascending=False).to_csv(
        forecast_out, index=False
    )

    # Findings markdown
    md = []
    md.append("# UDISE girls dropout — quick findings (derived from cohort-flow tables)\n")
    md.append(
        f"Data: UDISE archive `mapId=117`, years {first_year}–{latest_year}, caste_id=5 (Overall).\n"
    )

    if nat_latest is not None:
        md.append("## National picture (latest year)\n")
        md.append(
            "- Primary girls dropout: "
            f"{pct(nat_latest['primary_girl_dropout_rate']):.2f}%\n"
        )
        md.append(
            "- Upper primary girls dropout: "
            f"{pct(nat_latest['upper_primary_girl_dropout_rate']):.2f}%\n"
        )
        md.append(
            "- Secondary girls dropout: "
            f"{pct(nat_latest['secondary_girl_dropout_rate']):.2f}%\n"
        )

        if len(nat) >= 2 and len(nat_forecast):
            slope = nat_coef[1]
            md.append("## Status-quo forecast (national, secondary girls)\n")
            md.append(
                f"Linear trend over available years implies ~{slope:.2f} pp/year change.\n"
            )
            md.append(
                "Next 3-year projection (percentage): "
                + ", ".join(f"{v:.2f}%" for v in nat_forecast)
                + "\n"
            )

    md.append("## State ranking (secondary girls dropout, latest year)\n")
    show = rank[["location_name", "acad_year", "secondary_girls_dropout_pct"]].copy()
    show = show.rename(
        columns={
            "location_name": "State/UT",
            "acad_year": "Year",
            "secondary_girls_dropout_pct": "Secondary girls dropout (%)",
        }
    )
    md.append(show.head(15).to_markdown(index=False))
    md.append("\n")

    md.append("## Biggest improvements vs. deteriorations (secondary girls, first→latest)\n")

    mi = most_improved.copy()
    mi = mi.reset_index().rename(
        columns={"location_name": "State/UT", "pp_change": "Change (pp)"}
    )
    mi["Change (pp)"] = mi["Change (pp)"].map(lambda x: f"{x:.2f}")
    md.append("### Most improved (dropout fell)\n")
    md.append(mi[["State/UT", "Change (pp)"]].to_markdown(index=False))
    md.append("\n")

    mw = most_worsened.copy()
    mw = mw.reset_index().rename(
        columns={"location_name": "State/UT", "pp_change": "Change (pp)"}
    )
    mw["Change (pp)"] = mw["Change (pp)"].map(lambda x: f"{x:.2f}")
    md.append("### Most worsened (dropout rose)\n")
    md.append(mw[["State/UT", "Change (pp)"]].to_markdown(index=False))
    md.append("\n")

    md.append("## Notes on method\n")
    md.append(
        "Rates are derived from the tabular cohort-flow counts (previous cohort, next-grade current, fresh admissions, repeaters):\n"
    )
    md.append(
        "- Promoted ≈ (next_grade_current_total − next_grade_fresh)\n"
        "- Repeat = same_grade_repeaters\n"
        "- Dropout = previous − promoted − repeat (clipped at 0)\n"
    )

    md_out = OUT_DIR / "findings_udise_secondary_girls.md"
    md_out.write_text("\n".join(md), encoding="utf-8")


def main() -> None:
    panel = load_panel()
    findings = make_findings(panel)
    write_outputs(findings)
    print("Wrote", OUT_DIR / "findings_udise_secondary_girls.md")
    print("Wrote", OUT_DIR / "status_quo_forecast_secondary_girls.csv")


if __name__ == "__main__":
    main()
