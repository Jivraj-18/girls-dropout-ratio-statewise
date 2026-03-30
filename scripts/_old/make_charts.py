from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


OUT_DIR = Path("outputs")
CHART_DIR = OUT_DIR / "charts"


def pct(x: pd.Series) -> pd.Series:
    return 100.0 * x


def load_panel() -> pd.DataFrame:
    fp = OUT_DIR / "udise_state_caste_year_flow_rates.parquet"
    if not fp.exists():
        raise SystemExit(
            "Missing panel parquet. Run build_outcome_panel.py first to generate outputs/*.parquet"
        )
    return pd.read_parquet(fp)


def plot_national_trend(panel: pd.DataFrame) -> None:
    # National row seems to have location_name == None and caste_id == 5 overall
    nat = panel[(panel["location_name"].isna()) & (panel["caste_id"] == 5)].copy()
    if nat.empty:
        return

    nat = nat.sort_values("year_id")

    series = {
        "Primary": nat["primary_girl_dropout_rate"],
        "Upper Primary": nat["upper_primary_girl_dropout_rate"],
        "Secondary": nat["secondary_girl_dropout_rate"],
    }

    plt.figure(figsize=(10, 5.2))
    for name, s in series.items():
        plt.plot(nat["acad_year"], pct(s), marker="o", label=name)

    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Girls dropout rate (%)")
    plt.xlabel("Academic year")
    plt.title("National girls dropout rate by stage")
    plt.grid(True, axis="y", alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHART_DIR / "national_girls_dropout_trend.png", dpi=200)
    plt.close()


def plot_state_ranking(panel: pd.DataFrame) -> None:
    # latest year in data
    latest = panel[panel["location_name"].notna()]["year_id"].max()
    df = panel[
        (panel["location_name"].notna())
        & (panel["caste_id"] == 5)
        & (panel["year_id"] == latest)
    ].copy()
    if df.empty:
        return

    df["dropout_pct"] = pct(df["secondary_girl_dropout_rate"])
    df = df.sort_values("dropout_pct", ascending=False)

    # Keep top/bottom to make the plot readable
    top_n = 12
    bottom_n = 12
    plot_df = pd.concat([df.head(top_n), df.tail(bottom_n)], ignore_index=True)

    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=plot_df,
        y="location_name",
        x="dropout_pct",
        color=sns.color_palette()[0],
    )
    plt.xlabel(f"Secondary girls dropout rate (%) in {df['acad_year'].iloc[0]}")
    plt.ylabel("State/UT")
    plt.title("Secondary girls dropout: highest vs lowest states/UTs")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "state_ranking_secondary_girls_dropout_latest.png", dpi=200)
    plt.close()


def plot_heatmap(panel: pd.DataFrame) -> None:
    df = panel[(panel["location_name"].notna()) & (panel["caste_id"] == 5)].copy()
    if df.empty:
        return

    df["dropout_pct"] = pct(df["secondary_girl_dropout_rate"])

    # Use a manageable set of states: top variance in the series
    pivot = df.pivot_table(
        index="location_name", columns="acad_year", values="dropout_pct", aggfunc="mean"
    )
    if pivot.empty:
        return

    # sort by latest year (if present)
    last_col = pivot.columns[-1]
    pivot = pivot.sort_values(last_col, ascending=False)

    # limit to 25 rows for readability
    pivot = pivot.head(25)

    plt.figure(figsize=(12, 10))
    sns.heatmap(pivot, cmap="Reds", linewidths=0.2, linecolor="white")
    plt.title("Secondary girls dropout rate (%) — top 25 states/UTs by latest year")
    plt.xlabel("Academic year")
    plt.ylabel("State/UT")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "heatmap_secondary_girls_dropout_top25.png", dpi=200)
    plt.close()


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    panel = load_panel()

    plot_national_trend(panel)
    plot_state_ranking(panel)
    plot_heatmap(panel)

    print("Wrote charts to", CHART_DIR)


if __name__ == "__main__":
    main()
