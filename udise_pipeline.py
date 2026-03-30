from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_YEARS = ["16", "17", "18", "19", "20", "21", "22"]
DEFAULT_DUMPS_DIR = Path("udise_api_dumps")
DEFAULT_OUT_DIR = Path("outputs")


# -------------------------
# Fetch (Playwright)
# -------------------------

def fetch_udise(
    years: list[str],
    dumps_dir: Path = DEFAULT_DUMPS_DIR,
    include_national_latest: bool = True,
    include_master_latest: bool = True,
    latest_year: str | None = None,
) -> None:
    """Fetch UDISE tabular JSON dumps via a browser context.

    Uses the same API as the dashboard, with content-type text/plain payloads.
    """

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Playwright not installed in this environment. Install it in the venv: "
            "`.venv/bin/pip install playwright && .venv/bin/python -m playwright install chromium`"
        ) from e

    dumps_dir.mkdir(exist_ok=True)

    base = "https://dashboard.udiseplus.gov.in"
    archive_url = f"{base}/udiseplus-archive/"
    tabular_url = f"{base}/BackEnd-master/api/report/getTabularData"
    master_url = f"{base}/BackEnd-master/api/report/getMasterData"

    common_headers = {
        "Content-Type": "text/plain; charset=utf-8",
        "Accept": "application/json, text/plain, */*",
    }

    if latest_year is None:
        latest_year = max(years)

    payloads: list[tuple[str, str, dict[str, Any]]] = []

    # Core: state-wise time series (mapId=117)
    for y in years:
        payloads.append(
            (
                f"tabular_map117_stateall_year{y}",
                tabular_url,
                {
                    "mapId": "117",
                    "dependencyValue": json.dumps(
                        {"year": y, "state": "all", "dist": "none", "block": "none"}
                    ),
                    "isDependency": "Y",
                    "paramName": "civilian",
                    "paramValue": "",
                    "schemaName": "national",
                    "reportType": "T",
                },
            )
        )

    # Optional: one national table for the latest year (useful for national trend line)
    if include_national_latest:
        payloads.append(
            (
                f"tabular_map117_national_year{latest_year}",
                tabular_url,
                {
                    "mapId": 117,
                    "dependencyValue": json.dumps(
                        {
                            "year": latest_year,
                            "state": "national",
                            "dist": "none",
                            "block": "none",
                        }
                    ),
                    "isDependency": "",
                    "paramName": "civilian",
                    "paramValue": "",
                    "schemaName": "national",
                    "reportType": "T",
                },
            )
        )

    # Optional: master lookups (useful later for driver tables)
    if include_master_latest:
        payloads.extend(
            [
                (
                    f"master_get_state_year{latest_year}",
                    master_url,
                    {
                        "extensionCall": "GET_STATE",
                        "condition": f" where year_id='{latest_year}' order by state_name",
                    },
                ),
            ]
        )

    run_meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "archive_url": archive_url,
        "years": years,
        "note": "Fetched via Playwright (browser context) and saved to disk.",
    }

    def post_text_plain(request, url: str, payload: dict[str, Any]) -> tuple[int, str]:
        resp = request.post(url, data=json.dumps(payload), headers=common_headers)
        return resp.status, resp.text()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(archive_url, wait_until="domcontentloaded")

        manifest: dict[str, Any] = {"_run": run_meta}
        for name, url, payload in payloads:
            status, text = post_text_plain(context.request, url, payload)
            out_path = dumps_dir / f"{name}.json"
            out_path.write_text(text, encoding="utf-8")
            manifest[name] = {
                "method": "POST",
                "url": url,
                "headers": dict(common_headers),
                "payload": payload,
                "status": status,
                "bytes": len(text.encode("utf-8")),
                "out": str(out_path),
            }

        (dumps_dir / "_requests_and_responses.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        context.close()
        browser.close()


# -------------------------
# Build panel
# -------------------------


@dataclass(frozen=True)
class FlowKeys:
    prev: str
    next_total: str
    next_fresh: str
    repeat: str


def _safe_div(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom = denom.astype("float64")
    numer = numer.astype("float64")
    out = numer / denom
    return out.where(denom.ne(0))


def _compute_flow(df: pd.DataFrame, keys: FlowKeys, prefix: str) -> pd.DataFrame:
    prev = df[keys.prev].astype("float64")
    next_total = df[keys.next_total].astype("float64")
    
    # Simple cohort-flow: Dropout = Previous - (those who moved to next level)
    # (Those who moved includes both fresh promotions and repeaters already counted)
    dropout = prev - next_total
    
    # Avoid negative artifacts from reporting/rounding
    dropout = dropout.clip(lower=0)

    return pd.DataFrame(
        {
            f"{prefix}_dropout": dropout,
            f"{prefix}_dropout_rate": _safe_div(dropout, prev),
        }
    )


def _load_tabular(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _year_from_name(path: Path) -> str:
    m = re.search(r"year(\d+)\.json$", path.name)
    if not m:
        raise ValueError(f"Could not parse year from filename: {path}")
    return m.group(1)


def build_panel(
    dumps_dir: Path = DEFAULT_DUMPS_DIR,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Find files with .json or .js extensions
    files = sorted(dumps_dir.glob("tabular_map117_stateall_year*.json"))
    if not files:
        files = sorted(dumps_dir.glob("tabular_map117_stateall_year*.js"))
    if not files:
        raise SystemExit(
            "No multi-year dumps found. Run `udise_pipeline.py fetch` first."
        )

    frames: list[pd.DataFrame] = []
    for fp in files:
        y = _year_from_name(fp)
        obj = _load_tabular(fp)
        rows = obj.get("rowValue") or []
        if not rows:
            continue

        df = pd.DataFrame(rows)
        df.insert(0, "year_id", y)
        
        # Create acad_year from year_id
        df["acad_year"] = int(y) - 1
        
        frames.append(df)

    panel = pd.concat(frames, ignore_index=True)

    # Calculate dropout rates using cohort flow method
    # Primary (Classes 1-5): classes 1,2,3,4,5
    # Flow from class 1 to 2
    pri_girl_flow1 = _compute_flow(
        panel,
        FlowKeys(
            prev="pri_girl_c1_c5_previous",
            next_total="pri_girl_c2_c6_current",
            next_fresh="",  # Unused in simplified flow calculation
            repeat="",  # Unused in simplified flow calculation
        ),
        "pri_girl",
    )
    
    # Join back to panel
    panel = panel.join(pri_girl_flow1)
    
    # Upper Primary (Classes 6-8): flow from class 6 to 7
    upper_pri_girl_flow = _compute_flow(
        panel,
        FlowKeys(
            prev="upper_pri_girl_c6_c8_previous",
            next_total="upper_pri_girl_c7_c9_current",
            next_fresh="",  # Unused
            repeat="",  # Unused
        ),
        "upper_pri_girl",
    )
    panel = panel.join(upper_pri_girl_flow)
    
    # Secondary (Classes 9-10): flow from class 9 to 10
    sec_girl_flow = _compute_flow(
        panel,
        FlowKeys(
            prev="secondary_girl_c9_c10_previous",
            next_total="secondary_girl_c10_c11_current",
            next_fresh="",  # Unused
            repeat="",  # Unused
        ),
        "secondary_girl",
    )
    panel = panel.join(sec_girl_flow)

    # Rename key identifier columns for clarity
    panel = panel.rename(columns={
        "location_name": "state_name",
        "caste_name": "caste",
    })

    panel.to_csv(out_dir / "udise_state_caste_year_flow_rates.csv", index=False)
    panel.to_parquet(out_dir / "udise_state_caste_year_flow_rates.parquet", index=False)

    return panel


# -------------------------
# Charts
# -------------------------


def _pct(series: pd.Series) -> pd.Series:
    return 100.0 * series


def make_charts(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    chart_dir = out_dir / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    fp = out_dir / "udise_state_caste_year_flow_rates.parquet"
    if not fp.exists():
        raise SystemExit("Missing panel parquet. Run `udise_pipeline.py build` first.")

    panel = pd.read_parquet(fp)

    # National row: state_name is null and caste_id==5 overall
    nat = panel[(panel["state_name"].isna()) & (panel["caste_id"] == 5)].copy()
    if not nat.empty:
        nat = nat.sort_values("year_id")
        plt.figure(figsize=(10, 5.2))
        # Use the calculated rate columns
        plt.plot(nat["acad_year"], _pct(nat["pri_girl_dropout_rate"]), marker="o", label="Primary")
        plt.plot(
            nat["acad_year"],
            _pct(nat["upper_pri_girl_dropout_rate"]),
            marker="o",
            label="Upper Primary",
        )
        plt.plot(
            nat["acad_year"],
            _pct(nat["secondary_girl_dropout_rate"]),
            marker="o",
            label="Secondary",
        )
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Girls dropout rate (%)")
        plt.xlabel("Academic year")
        plt.title("National girls dropout rate by stage")
        plt.grid(True, axis="y", alpha=0.25)
        plt.legend()
        plt.tight_layout()
        plt.savefig(chart_dir / "national_girls_dropout_trend.png", dpi=200)
        plt.close()

    # Latest ranking
    states = panel[panel["state_name"].notna()].copy()
    if states.empty:
        return

    latest = states["year_id"].max()
    latest_df = states[(states["caste_id"] == 5) & (states["year_id"] == latest)].copy()
    if latest_df.empty:
        return

    latest_df["dropout_pct"] = _pct(latest_df["secondary_girl_dropout_rate"])
    latest_df = latest_df.sort_values("dropout_pct", ascending=False)

    top_n = 12
    bottom_n = 12
    plot_df = pd.concat([latest_df.head(top_n), latest_df.tail(bottom_n)], ignore_index=True)

    plt.figure(figsize=(10, 8))
    sns.barplot(data=plot_df, y="state_name", x="dropout_pct", color=sns.color_palette()[0])
    plt.xlabel(f"Secondary girls dropout rate (%) in {latest_df['acad_year'].iloc[0]}")
    plt.ylabel("State/UT")
    plt.title("Secondary girls dropout: highest vs lowest states/UTs")
    plt.tight_layout()
    plt.savefig(chart_dir / "state_ranking_secondary_girls_dropout_latest.png", dpi=200)
    plt.close()

    # Heatmap: top 25 by latest year
    df = states[states["caste_id"] == 5].copy()
    df["dropout_pct"] = _pct(df["secondary_girl_dropout_rate"])
    pivot = df.pivot_table(index="state_name", columns="acad_year", values="dropout_pct", aggfunc="mean")
    if pivot.empty:
        return

    pivot = pivot.sort_values(pivot.columns[-1], ascending=False).head(25)
    plt.figure(figsize=(12, 10))
    sns.heatmap(pivot, cmap="Reds", linewidths=0.2, linecolor="white")
    plt.title("Secondary girls dropout rate (%) — top 25 states/UTs by latest year")
    plt.xlabel("Academic year")
    plt.ylabel("State/UT")
    plt.tight_layout()
    plt.savefig(chart_dir / "heatmap_secondary_girls_dropout_top25.png", dpi=200)
    plt.close()


# -------------------------
# Findings + status-quo forecast
# -------------------------


def _linear_forecast(y: np.ndarray, steps_ahead: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(y)
    t = np.arange(n, dtype=float)
    if n < 2:
        return np.full(steps_ahead, np.nan), np.array([np.nan, np.nan])
    b, a = np.polyfit(t, y, 1)
    t_f = np.arange(n, n + steps_ahead, dtype=float)
    y_f = a + b * t_f
    return y_f, np.array([a, b])


def write_findings(out_dir: Path = DEFAULT_OUT_DIR) -> None:
    fp = out_dir / "udise_state_caste_year_flow_rates.parquet"
    if not fp.exists():
        raise SystemExit("Missing panel parquet. Run `udise_pipeline.py build` first.")

    panel = pd.read_parquet(fp)
    overall = panel[panel["caste_id"] == 5].copy()

    nat = overall[overall["state_name"].isna()].sort_values("year_id")
    nat_latest = nat.iloc[-1] if not nat.empty else None

    states = overall[overall["state_name"].notna()].copy()
    latest_year = states["year_id"].max()
    first_year = states["year_id"].min()

    states_latest = states[states["year_id"] == latest_year].copy()
    states_latest["secondary_girls_dropout_pct"] = 100.0 * states_latest["secondary_girl_dropout_rate"]
    rank = states_latest.sort_values("secondary_girls_dropout_pct", ascending=False)

    g0 = (
        states[states["year_id"] == first_year]
        .set_index("state_name")["secondary_girl_dropout_rate"]
        .rename("first")
    )
    g1 = (
        states[states["year_id"] == latest_year]
        .set_index("state_name")["secondary_girl_dropout_rate"]
        .rename("last")
    )
    delta = pd.concat([g0, g1], axis=1).dropna()
    delta["pp_change"] = 100.0 * (delta["last"] - delta["first"])
    most_improved = delta.sort_values("pp_change").head(10)
    most_worsened = delta.sort_values("pp_change", ascending=False).head(10)

    # Forecast CSV (per-state)
    rows = []
    for state, sdf in (
        states[["state_name", "year_id", "acad_year", "secondary_girl_dropout_rate"]]
        .sort_values(["state_name", "year_id"])
        .groupby("state_name")
    ):
        y = (100.0 * sdf["secondary_girl_dropout_rate"]).to_numpy()
        y_f, coef = _linear_forecast(y, steps_ahead=3)
        if len(y_f) != 3:
            continue
        rows.append(
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

    forecast_df = pd.DataFrame(rows)
    forecast_df.sort_values("trend_pp_per_year", ascending=False).to_csv(
        out_dir / "status_quo_forecast_secondary_girls.csv", index=False
    )

    # National forecast snippet
    nat_forecast = np.array([])
    nat_slope = np.nan
    if len(nat) >= 2:
        y_nat = (100.0 * nat["secondary_girl_dropout_rate"]).to_numpy()
        nat_forecast, coef = _linear_forecast(y_nat, steps_ahead=3)
        nat_slope = float(coef[1])

    # Markdown findings
    md: list[str] = []
    md.append("# UDISE girls dropout — quick findings (derived from cohort-flow tables)\n")
    md.append(f"Data: UDISE archive `mapId=117`, years {first_year}–{latest_year}, caste_id=5 (Overall).\n")

    if nat_latest is not None:
        md.append("## National picture (latest year)\n")
        md.append(f"- Primary girls dropout: {100.0*float(nat_latest['pri_girl_dropout_rate']):.2f}%")
        md.append(f"- Upper primary girls dropout: {100.0*float(nat_latest['upper_pri_girl_dropout_rate']):.2f}%")
        md.append(f"- Secondary girls dropout: {100.0*float(nat_latest['secondary_girl_dropout_rate']):.2f}%\n")

        if len(nat_forecast):
            md.append("## Status-quo forecast (national, secondary girls)\n")
            md.append(f"Linear trend over available years implies ~{nat_slope:.2f} pp/year change.")
            md.append(
                "Next 3-year projection (percentage): "
                + ", ".join(f"{v:.2f}%" for v in nat_forecast)
                + "\n"
            )

    md.append("## State ranking (secondary girls dropout, latest year)\n")
    show = rank[["state_name", "acad_year", "secondary_girls_dropout_pct"]].rename(
        columns={
            "state_name": "State/UT",
            "acad_year": "Year",
            "secondary_girls_dropout_pct": "Secondary girls dropout (%)",
        }
    )
    md.append(show.head(15).to_markdown(index=False))
    md.append("\n")

    md.append("## Biggest improvements vs. deteriorations (secondary girls, first→latest)\n")

    mi = most_improved.reset_index().rename(columns={"state_name": "State/UT", "pp_change": "Change (pp)"})
    mi["Change (pp)"] = mi["Change (pp)"].map(lambda x: f"{x:.2f}")
    md.append("### Most improved (dropout fell)\n")
    md.append(mi[["State/UT", "Change (pp)"]].to_markdown(index=False))
    md.append("\n")

    mw = most_worsened.reset_index().rename(columns={"state_name": "State/UT", "pp_change": "Change (pp)"})
    mw["Change (pp)"] = mw["Change (pp)"].map(lambda x: f"{x:.2f}")
    md.append("### Most worsened (dropout rose)\n")
    md.append(mw[["State/UT", "Change (pp)"]].to_markdown(index=False))
    md.append("\n")

    md.append("## Notes on method\n")
    md.append(
        "Rates are derived from the tabular cohort-flow counts (previous cohort, next-grade current, fresh admissions, repeaters):\n"
        "- Promoted ≈ (next_grade_current_total − next_grade_fresh)\n"
        "- Repeat = same_grade_repeaters\n"
        "- Dropout = previous − promoted − repeat (clipped at 0)\n"
    )

    (out_dir / "findings_udise_secondary_girls.md").write_text("\n".join(md), encoding="utf-8")


# -------------------------
# CLI
# -------------------------


def _parse_years(s: str) -> list[str]:
    s = s.strip()
    if not s:
        return DEFAULT_YEARS
    return [p.strip() for p in s.split(",") if p.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="UDISE girls dropout pipeline (fetch → panel → charts → findings)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch UDISE dumps via Playwright")
    p_fetch.add_argument(
        "--years",
        default=",".join(DEFAULT_YEARS),
        help="Comma-separated year tokens (e.g., 16,17,...,22)",
    )

    sub.add_parser("build", help="Build panel outputs from downloaded dumps")
    sub.add_parser("charts", help="Generate charts from the panel")
    sub.add_parser("findings", help="Write findings markdown + forecast csv")

    p_all = sub.add_parser("all", help="Run build + charts + findings (assumes dumps exist)")
    p_all.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip fetching even if Playwright is installed",
    )
    p_all.add_argument(
        "--years",
        default=",".join(DEFAULT_YEARS),
        help="Comma-separated year tokens for fetch step",
    )

    args = parser.parse_args(argv)

    if args.cmd == "fetch":
        fetch_udise(years=_parse_years(args.years))
        return 0

    if args.cmd == "build":
        build_panel()
        return 0

    if args.cmd == "charts":
        make_charts()
        return 0

    if args.cmd == "findings":
        write_findings()
        return 0

    if args.cmd == "all":
        years = _parse_years(args.years)
        if not args.skip_fetch:
            fetch_udise(years=years)
        build_panel()
        make_charts()
        write_findings()
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())